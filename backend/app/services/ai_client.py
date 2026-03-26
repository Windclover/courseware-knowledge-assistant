from __future__ import annotations

from collections.abc import Sequence
import json
import re

import httpx

from ..config import get_settings
from ..domain import ChatAnswerResult, GeneratedSection, SectionDraft
from ..schemas import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentSuite,
    FormulaNote,
    LearningBoard,
    LearningConceptItem,
    LearningPracticeItem,
    LearningReviewStep,
    LearningSummaryItem,
    SectionNote,
    WorkedExample,
)


class AIConfigurationError(RuntimeError):
    pass


class QwenClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise AIConfigurationError("缺少 OPENAI_API_KEY，请先在 .env 中配置 OpenAI API Key。")
        self._api_key = settings.openai_api_key
        self._base_url = settings.openai_base_url.rstrip("/")
        self._model = settings.openai_model
        self._reasoning_effort = settings.openai_reasoning_effort

    def generate_section(self, document_title: str, draft: SectionDraft) -> GeneratedSection:
        prompt = f"""
你是一名严谨的数学课程内容整理助手。请基于给定课件原文，生成适合复习的结构化学习笔记。

约束：
1. 只能依据输入内容，不得编造课件中不存在的事实。
2. 输出使用中文。
3. 返回 JSON 对象，不要添加额外解释。
4. `detailed_explanation` 要写成真正的课程笔记，至少覆盖：定义 / 方法思想 / 参数作用 / 适用条件 / 常见误区。
5. `detailed_explanation` 默认写成 3-5 段，不要只写一段摘要。
6. `key_points` 输出 4-6 条。
7. 如果原文里出现公式、约束形式、算法步骤、例题，请尽量提取到 `formula_notes` 和 `worked_examples`。
8. `formula_notes.latex` 优先重建成 Markdown LaTeX，不要包含外围 `$$`；如果无法稳定重建，则留空并把原式放进 `raw_text`。
9. `worked_examples.steps` 要尽量写成分步说明。

文档标题：{document_title}
章节标题：{draft.title}
来源编号：{", ".join(draft.source_refs)}

课件原文：
{draft.source_excerpt}

公式候选：
{json.dumps(draft.formula_candidates, ensure_ascii=False)}

例题/算法候选：
{json.dumps(draft.example_candidates, ensure_ascii=False)}

请严格返回如下 JSON 结构：
{{
  "title": "章节标题",
  "detailed_explanation": "详细讲解",
  "key_points": ["要点1", "要点2"],
  "formula_notes": [
    {{
      "title": "公式标题",
      "latex": "P_E(x, \\sigma) = f(x) + ...",
      "raw_text": "原始公式文本",
      "explanation": "公式含义与使用场景",
      "source_refs": ["第 6 页"]
    }}
  ],
  "worked_examples": [
    {{
      "title": "例题标题",
      "problem": "题目描述",
      "steps": ["步骤1", "步骤2"],
      "final_answer": "最终答案",
      "source_refs": ["第 10 页"]
    }}
  ],
  "source_refs": ["第 1 张幻灯片"]
}}
        """.strip()
        payload = self._create_json_completion(prompt, max_tokens=2400)
        formula_notes = _coerce_formula_notes(
            payload.get("formula_notes"),
            fallback_candidates=draft.formula_candidates,
            default_source_refs=draft.source_refs,
        )
        worked_examples = _coerce_worked_examples(
            payload.get("worked_examples"),
            fallback_candidates=draft.example_candidates,
            default_source_refs=draft.source_refs,
        )
        return GeneratedSection(
            section_index=draft.section_index,
            title=str(payload.get("title") or draft.title),
            detailed_explanation=str(payload.get("detailed_explanation") or "").strip(),
            key_points=_clean_string_list(payload.get("key_points")),
            formula_notes=formula_notes,
            worked_examples=worked_examples,
            source_refs=_filter_source_refs(payload.get("source_refs"), draft.source_refs),
        )

    def generate_learning_board(
        self,
        *,
        document_title: str,
        sections: Sequence[SectionNote],
    ) -> LearningBoard:
        sections_payload = [
            {
                "section_index": section.section_index,
                "title": section.title,
                "detailed_explanation": section.detailed_explanation,
                "key_points": section.key_points,
                "formula_notes": [item.model_dump() for item in section.formula_notes],
                "worked_examples": [item.model_dump() for item in section.worked_examples],
                "source_refs": section.source_refs,
            }
            for section in sections
        ]
        prompt = f"""
你是一名课程复习规划助手。请根据学习笔记，生成一个结构化的复习任务台。

约束：
1. 输出中文。
2. 只依据输入内容规划，不要编造课件之外的知识点。
3. `summary` 输出每个章节的一句话摘要。
4. `concepts` 输出 2-4 个最重要概念，每个概念说明为什么重要。
5. `practice` 输出 3 个练习任务，先不要生成具体选择题或填空题。
6. `review_path` 输出 3-4 步复习顺序。
7. 返回 JSON 对象，不要输出额外说明。

文档标题：{document_title}
章节笔记：
{json.dumps(sections_payload, ensure_ascii=False)}

请严格返回如下 JSON：
{{
  "overview": "总览复习建议",
  "summary": [
    {{"id":"summary-1","title":"章节标题","summary":"一句话摘要","source_refs":["第 1 页"]}}
  ],
  "concepts": [
    {{"id":"concept-1","term":"核心概念","explanation":"解释","section_title":"章节标题","source_refs":["第 1 页"]}}
  ],
  "practice": [
    {{"id":"practice-1","prompt":"练习任务","section_title":"章节标题","source_refs":["第 1 页"]}}
  ],
  "review_path": [
    {{"id":"review-1","title":"步骤标题","detail":"步骤说明","source_refs":["第 1 页"]}}
  ]
}}
        """.strip()
        payload = self._create_json_completion(prompt, max_tokens=2000)
        return LearningBoard(
            overview=str(payload.get("overview") or "").strip(),
            summary=[
                LearningSummaryItem(**item)
                for item in _safe_list(payload.get("summary"))
                if _is_mapping(item)
            ],
            concepts=[
                LearningConceptItem(**item)
                for item in _safe_list(payload.get("concepts"))
                if _is_mapping(item)
            ],
            practice=[
                LearningPracticeItem(**item)
                for item in _safe_list(payload.get("practice"))
                if _is_mapping(item)
            ],
            review_path=[
                LearningReviewStep(**item)
                for item in _safe_list(payload.get("review_path"))
                if _is_mapping(item)
            ],
        )

    def generate_assessment(
        self,
        *,
        document_title: str,
        sections: Sequence[SectionNote],
        learning_board: LearningBoard,
    ) -> AssessmentSuite:
        sections_payload = [
            {
                "title": section.title,
                "detailed_explanation": section.detailed_explanation,
                "key_points": section.key_points,
                "formula_notes": [item.model_dump() for item in section.formula_notes],
                "worked_examples": [item.model_dump() for item in section.worked_examples],
            }
            for section in sections
        ]
        has_math_material = any(
            section.formula_notes or section.worked_examples for section in sections
        )
        prompt = f"""
你是一名课程测验出题助手。请根据课件学习笔记和复习任务，生成测验题目。

要求：
1. 输出中文。
2. 题目只能依据输入内容。
3. 如果输入里存在公式或例题，必须生成 2 道单选题、1 道填空题、2 道计算题；否则回退为 3 道单选题和 2 道填空题。
4. 每题必须有答案和解析。
5. 单选题 `answer` 填正确选项的 `id`。
6. 填空题和计算题 `acceptable_answers` 给出可接受答案列表，`answer` 填主答案。
7. 计算题 `type` 必须为 `calculation`，并补充 `solution_steps` 与 `display_answer`。
8. 计算题不要只问纯概念，优先围绕公式代入、算法步骤、极小点结果、参数变化分析出题。
9. 返回 JSON 对象，不要输出额外说明。

文档标题：{document_title}
是否存在公式或例题：{"是" if has_math_material else "否"}
章节笔记：
{json.dumps(sections_payload, ensure_ascii=False)}
学习任务台：
{json.dumps(learning_board.model_dump(), ensure_ascii=False)}

请严格返回如下 JSON：
{{
  "title":"测验标题",
  "intro":"测验说明",
  "questions":[
    {{
      "id":"q1",
      "type":"choice",
      "prompt":"题目",
      "options":[
        {{"id":"A","text":"选项A"}},
        {{"id":"B","text":"选项B"}}
      ],
      "answer":"A",
      "display_answer":"A. 选项A",
      "acceptable_answers":[],
      "explanation":"解析",
      "solution_steps":[]
    }},
    {{
      "id":"q4",
      "type":"calculation",
      "prompt":"题目",
      "options":[],
      "answer":"主答案",
      "display_answer":"主答案",
      "acceptable_answers":["主答案","可接受答案2"],
      "explanation":"解析",
      "solution_steps":["步骤1","步骤2"]
    }}
  ]
}}
        """.strip()
        payload = self._create_json_completion(prompt, max_tokens=2800)
        questions: list[AssessmentQuestion] = []
        for item in _safe_list(payload.get("questions")):
            if not _is_mapping(item):
                continue
            options = [
                AssessmentQuestionOption(**option)
                for option in _safe_list(item.get("options"))
                if _is_mapping(option)
            ]
            questions.append(
                AssessmentQuestion(
                    id=str(item.get("id") or ""),
                    type=str(item.get("type") or "choice"),
                    prompt=str(item.get("prompt") or "").strip(),
                    options=options,
                    answer=str(item.get("answer") or "").strip(),
                    display_answer=_build_display_answer(item, options),
                    acceptable_answers=_clean_string_list(item.get("acceptable_answers")),
                    explanation=str(item.get("explanation") or "").strip(),
                    solution_steps=_clean_string_list(item.get("solution_steps")),
                )
            )
        if has_math_material:
            questions = _ensure_calculation_questions(questions, sections)
        return AssessmentSuite(
            title=str(payload.get("title") or f"{document_title} 测试环境").strip(),
            intro=str(payload.get("intro") or "完成学习任务后，进入测试环境检验掌握程度。").strip(),
            questions=questions,
        )

    def answer_question(
        self,
        *,
        document_title: str,
        question: str,
        question_type: str,
        scope_label: str,
        context_blocks: Sequence[str],
        recent_history: Sequence[str],
        conversation_focus: str,
    ) -> ChatAnswerResult:
        history_text = "\n".join(recent_history) if recent_history else "无"
        context_text = "\n\n".join(context_blocks) if context_blocks else "无可用上下文"
        focus_text = conversation_focus or "无"
        answer_format_hint = _build_answer_format_hint(question_type)
        prompt = f"""
你是一名学习助手，需要优先基于课件内容和已经生成的学习笔记回答问题。

要求：
1. 先给出基于课件的结论性回答。
2. 如果历史对话里已经形成了上下文，请延续前文，不要把每次问题都当成全新话题。
3. 如果学习任务台里的总结能帮助用户理解，可以自然整合进去。
4. 如果课件信息不足，可以补充少量通用常识，但必须放到 `supplemental_notes` 中。
5. 除非用户明确要求“简短回答”，否则回答不要只有 1-2 句。
6. 默认写成 2 段或 3 个要点，建议 180-320 字；如果问题包含“为什么 / 如何 / 区别 / 原理 / 详细”等词，尽量展开到 220-420 字。
7. 回答时优先补足“概念定义 + 机制原因 + 课件中的例子或对比”，不要只给结论。
8. 如果用户问题已经聚焦到公式、练习、概念、步骤，就不要再重复整份课件的总述。
9. `summary`：用 3-5 个要点总结，不要长篇重复背景。
10. `mastery`：按“需要掌握的内容”列出 4-6 点，并点出哪一部分最重要。
11. `concepts`：明确列出最重要的 3 个概念，逐条解释，不要泛泛总结。
12. `formula`：必须至少写出 1 个数学公式，并解释符号含义、公式作用和使用场景。
13. `exercise`：先给一题贴合课件的练习题，再给“解题思路”“详细解答”“易错点”。
14. `follow_up`：把当前问题视为延续上一轮，优先回答上一轮练习题或上一轮未讲完的点，不要退回整份课件总述。
15. 如果要回答计算或练习问题，尽量按步骤展开，必要时直接给出结果。
16. 在聊天回答中，涉及数学公式时优先使用纯文本数学表达式，例如 `(1/(2σ))`、`sum`、`argmin`、`||c(x)||`，尽量不要使用 `\frac`、`\text`、`\times` 这类 LaTeX 命令，避免 JSON 转义损坏。
17. 严格遵守下面的回答骨架。
18. 返回 JSON，不要输出额外说明。
19. `source_refs` 必须只包含输入上下文中出现过的来源编号。
20. 如果用户使用“这个/那个/上一个概念/刚才那题”这类指代，优先从历史对话和“当前对话焦点”中解析真实指向。

文档标题：{document_title}
问题类型：{question_type}
问答范围：{scope_label}
当前对话焦点：
{focus_text}

回答骨架：
{answer_format_hint}

历史对话：
{history_text}

检索到的上下文：
{context_text}

用户问题：{question}

请返回：
{{
  "answer": "回答正文",
  "source_refs": ["第 2 页"],
  "supplemental": false,
  "supplemental_notes": null
}}
        """.strip()
        payload = self._create_json_completion(prompt, max_tokens=1200)
        supplemental = bool(payload.get("supplemental"))
        notes = payload.get("supplemental_notes")
        return ChatAnswerResult(
            answer=str(payload.get("answer") or "当前未能生成回答，请稍后重试。").strip(),
            source_refs=_clean_string_list(payload.get("source_refs")),
            supplemental=supplemental,
            supplemental_notes=str(notes).strip() if notes else None,
        )

    def _create_json_completion(self, prompt: str, *, max_tokens: int) -> dict:
        payload = {
            "model": self._model,
            "stream": True,
            "max_output_tokens": max_tokens,
            "reasoning": {"effort": self._reasoning_effort},
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "你是一个严谨、清晰、愿意适度展开解释、遵守输入边界的中文学习助手。",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                },
            ],
        }
        content = self._stream_response_text(payload)
        try:
            return _extract_json(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("模型返回格式异常，请稍后重试。") from exc

    def _stream_response_text(self, payload: dict) -> str:
        url = f"{self._base_url}/responses"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        deltas: list[str] = []
        completed_text = ""
        try:
            with httpx.Client(timeout=180.0) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    for raw_line in response.iter_lines():
                        line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                        if not line or not line.startswith("data: "):
                            continue
                        data = line[6:].strip()
                        if not data or data == "[DONE]":
                            continue
                        try:
                            event = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        event_type = str(event.get("type") or "")
                        if event_type == "response.output_text.delta":
                            delta = str(event.get("delta") or "")
                            if delta:
                                deltas.append(delta)
                        elif event_type == "response.completed":
                            completed_text = _extract_response_output_text(event)
        except httpx.TimeoutException as exc:
            raise RuntimeError("模型服务请求超时，请稍后重试。") from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            raise RuntimeError(f"模型服务返回错误（HTTP {status_code}）。") from exc
        except httpx.RequestError as exc:
            raise RuntimeError("模型服务连接失败，请检查网络或接口配置。") from exc
        text = completed_text.strip() or "".join(deltas).strip()
        if not text:
            raise RuntimeError("模型没有返回可用内容。")
        return text


def _coerce_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    return str(content)


def _extract_json(raw_text: str) -> dict:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        sanitized = _sanitize_json_text(raw_text)
        if sanitized != raw_text:
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return json.loads(_sanitize_json_text(candidate))


def _clean_string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def _safe_list(value) -> list:
    if isinstance(value, list):
        return value
    return []


def _is_mapping(value) -> bool:
    return isinstance(value, dict)


def _filter_source_refs(value, allowed_refs: Sequence[str]) -> list[str]:
    allowed = set(allowed_refs)
    cleaned = [item for item in _clean_string_list(value) if item in allowed]
    return cleaned or list(allowed_refs)


def _coerce_formula_notes(
    value,
    *,
    fallback_candidates: Sequence[str],
    default_source_refs: Sequence[str],
) -> list[FormulaNote]:
    notes: list[FormulaNote] = []
    for item in _safe_list(value):
        if not _is_mapping(item):
            continue
        note = FormulaNote(
            title=str(item.get("title") or "核心公式").strip() or "核心公式",
            latex=str(item.get("latex") or "").strip(),
            raw_text=str(item.get("raw_text") or "").strip(),
            explanation=str(item.get("explanation") or "").strip(),
            source_refs=_filter_source_refs(item.get("source_refs"), default_source_refs),
        )
        if note.latex or note.raw_text:
            notes.append(note)
    if notes:
        return notes
    fallback: list[FormulaNote] = []
    for index, candidate in enumerate(fallback_candidates[:4], start=1):
        fallback.append(
            FormulaNote(
                title=f"公式 {index}",
                latex="",
                raw_text=str(candidate).strip(),
                explanation="根据课件原文抽取的公式片段，可结合章节讲解理解其含义。",
                source_refs=list(default_source_refs),
            )
        )
    return fallback


def _coerce_worked_examples(
    value,
    *,
    fallback_candidates: Sequence[str],
    default_source_refs: Sequence[str],
) -> list[WorkedExample]:
    examples: list[WorkedExample] = []
    for item in _safe_list(value):
        if not _is_mapping(item):
            continue
        example = WorkedExample(
            title=str(item.get("title") or "例题").strip() or "例题",
            problem=str(item.get("problem") or "").strip(),
            steps=_clean_string_list(item.get("steps")),
            final_answer=str(item.get("final_answer") or "").strip(),
            source_refs=_filter_source_refs(item.get("source_refs"), default_source_refs),
        )
        if example.problem or example.steps or example.final_answer:
            examples.append(example)
    if examples:
        return examples
    fallback: list[WorkedExample] = []
    for index, candidate in enumerate(fallback_candidates[:3], start=1):
        lines = [line.strip() for line in str(candidate).splitlines() if line.strip()]
        fallback.append(
            WorkedExample(
                title=f"例题 {index}",
                problem=lines[0] if lines else str(candidate).strip(),
                steps=lines[1:] if len(lines) > 1 else ["请结合原文继续推导。"],
                final_answer="",
                source_refs=list(default_source_refs),
            )
        )
    return fallback


def _build_display_answer(item: dict, options: Sequence[AssessmentQuestionOption]) -> str:
    display_answer = str(item.get("display_answer") or "").strip()
    if display_answer:
        return display_answer
    answer = str(item.get("answer") or "").strip()
    if not answer:
        return ""
    for option in options:
        if option.id == answer:
            return f"{option.id}. {option.text}"
    return answer


def _ensure_calculation_questions(
    questions: list[AssessmentQuestion],
    sections: Sequence[SectionNote],
) -> list[AssessmentQuestion]:
    calculation_count = sum(1 for item in questions if item.type == "calculation")
    if calculation_count >= 2:
        return questions

    fallback_questions: list[AssessmentQuestion] = []
    next_index = len(questions) + 1
    for section in sections:
        for example in section.worked_examples:
            fallback_questions.append(
                AssessmentQuestion(
                    id=f"q{next_index}",
                    type="calculation",
                    prompt=(
                        f"根据《{section.title}》中的例题“{example.title}”，"
                        "请写出该题的最终结果。"
                    ),
                    options=[],
                    answer=example.final_answer or "请参考解析中的最终结果",
                    display_answer=example.final_answer or "请参考解析中的最终结果",
                    acceptable_answers=[example.final_answer] if example.final_answer else [],
                    explanation=(
                        "这道计算题来自课件中的例题整理。"
                        if not example.steps
                        else "这道计算题来自课件中的例题整理，参考步骤如下。"
                    ),
                    solution_steps=example.steps,
                )
            )
            next_index += 1
            if calculation_count + len(fallback_questions) >= 2:
                return questions + fallback_questions

    for section in sections:
        for formula in section.formula_notes:
            fallback_questions.append(
                AssessmentQuestion(
                    id=f"q{next_index}",
                    type="calculation",
                    prompt=(
                        f"请根据《{section.title}》中的公式“{formula.title}”，"
                        "写出该公式的关键结果或表达式。"
                    ),
                    options=[],
                    answer=formula.raw_text or formula.latex or "请参考解析",
                    display_answer=formula.raw_text or formula.latex or "请参考解析",
                    acceptable_answers=[
                        value
                        for value in [formula.raw_text, formula.latex]
                        if value
                    ],
                    explanation=formula.explanation or "请结合课件中的公式说明理解该结果。",
                    solution_steps=[],
                )
            )
            next_index += 1
            if calculation_count + len(fallback_questions) >= 2:
                return questions + fallback_questions

    return questions + fallback_questions


def _build_answer_format_hint(question_type: str) -> str:
    if question_type == "summary":
        return (
            "先用一句话概括，再列 3-5 个要点。"
            "不要重复铺垫，不要把整段都写成一个大段落。"
        )
    if question_type == "mastery":
        return (
            "直接以编号列表回答“需要掌握的内容”。"
            "至少 4 点，每点说明为什么重要，并尽量点出相关公式或例题。"
        )
    if question_type == "concepts":
        return (
            "直接列出最重要的 3 个概念，格式固定为“1. 概念名：解释”。"
            "不要额外先写泛化总述。"
        )
    if question_type == "formula":
        return (
            "按“核心公式 / 符号含义 / 怎么理解或怎么用”三段回答。"
            "公式请使用纯文本数学表达式，不要使用 LaTeX 命令。"
        )
    if question_type == "exercise":
        return (
            "按以下固定结构回答："
            "“练习题：...；解题思路：...；详细解答：...；易错点：...”。"
            "不要先重复整份课件总结。"
        )
    if question_type == "follow_up":
        return (
            "把当前问题当成“继续解上一题”。"
            "按步骤直接解答，最后单独给“最终答案”。"
        )
    return "先直接回答问题，再补充必要解释。避免重复整份课件概述。"


def _sanitize_json_text(raw_text: str) -> str:
    latex_commands = (
        "frac",
        "tfrac",
        "sigma",
        "mu",
        "lambda",
        "sum",
        "text",
        "times",
        "cdot",
        "left",
        "right",
        "leq",
        "geq",
        "min",
        "argmin",
    )
    result: list[str] = []
    in_string = False
    escape = False
    index = 0
    while index < len(raw_text):
        char = raw_text[index]
        if in_string:
            if escape:
                result.append(char)
                escape = False
                index += 1
                continue
            if char == "\\":
                remainder = raw_text[index + 1 :]
                if any(remainder.startswith(command) for command in latex_commands):
                    result.append("\\\\")
                else:
                    result.append(char)
                    escape = True
                index += 1
                continue
            if char == '"':
                in_string = False
                result.append(char)
                index += 1
                continue
            if char == "\n":
                result.append("\\n")
            elif char == "\r":
                result.append("\\r")
            elif ord(char) < 32:
                result.append(" ")
            else:
                result.append(char)
            index += 1
            continue
        if char == '"':
            in_string = True
        result.append(char)
        index += 1
    return "".join(result)


def _extract_response_output_text(event: dict) -> str:
    response = event.get("response")
    if not isinstance(response, dict):
        return ""
    parts: list[str] = []
    for item in response.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"}:
                text = str(content.get("text") or "")
                if text:
                    parts.append(text)
    return "\n".join(parts).strip()
