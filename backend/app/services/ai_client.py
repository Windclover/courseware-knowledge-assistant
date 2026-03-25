from __future__ import annotations

from collections.abc import Sequence
import json
import re

from openai import OpenAI

from ..config import get_settings
from ..domain import ChatAnswerResult, GeneratedSection, SectionDraft
from ..schemas import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentSuite,
    LearningBoard,
    LearningConceptItem,
    LearningPracticeItem,
    LearningReviewStep,
    LearningSummaryItem,
    SectionNote,
)


class AIConfigurationError(RuntimeError):
    pass


class QwenClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.qwen_api_key:
            raise AIConfigurationError("缺少 QWEN_API_KEY，请先在 .env 中配置百炼 API Key。")
        self._client = OpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )
        self._model = settings.qwen_model

    def generate_section(self, document_title: str, draft: SectionDraft) -> GeneratedSection:
        prompt = f"""
你是一名严谨的课程内容整理助手。请基于给定课件原文，生成结构化学习笔记。

约束：
1. 只能依据输入内容，不得编造课件中不存在的事实。
2. 输出使用中文。
3. 返回 JSON 对象，不要添加额外解释。
4. `detailed_explanation` 需要写成适合复习的详细讲解，2-4 段。
5. `key_points` 输出 3-5 条。

文档标题：{document_title}
章节标题：{draft.title}
来源编号：{", ".join(draft.source_refs)}

课件原文：
{draft.source_excerpt}

请严格返回如下 JSON 结构：
{{
  "title": "章节标题",
  "detailed_explanation": "详细讲解",
  "key_points": ["要点1", "要点2"],
  "source_refs": ["第 1 张幻灯片"]
}}
        """.strip()
        payload = self._create_json_completion(prompt)
        return GeneratedSection(
            section_index=draft.section_index,
            title=str(payload.get("title") or draft.title),
            detailed_explanation=str(payload.get("detailed_explanation") or "").strip(),
            key_points=_clean_string_list(payload.get("key_points")),
            source_refs=_clean_string_list(payload.get("source_refs")) or draft.source_refs,
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
        payload = self._create_json_completion(prompt)
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
            }
            for section in sections
        ]
        prompt = f"""
你是一名课程测验出题助手。请根据课件学习笔记和复习任务，生成测验题目。

要求：
1. 输出中文。
2. 题目只能依据输入内容。
3. 生成 3 道单选题和 2 道填空题。
4. 每题必须有答案和解析。
5. 单选题 `answer` 填正确选项的 `id`。
6. 填空题 `acceptable_answers` 给出可接受答案列表，`answer` 填主答案。
7. 返回 JSON 对象，不要输出额外说明。

文档标题：{document_title}
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
      "acceptable_answers":[],
      "explanation":"解析"
    }},
    {{
      "id":"q4",
      "type":"blank",
      "prompt":"题目",
      "options":[],
      "answer":"主答案",
      "acceptable_answers":["主答案","可接受答案2"],
      "explanation":"解析"
    }}
  ]
}}
        """.strip()
        payload = self._create_json_completion(prompt)
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
                    acceptable_answers=_clean_string_list(item.get("acceptable_answers")),
                    explanation=str(item.get("explanation") or "").strip(),
                )
            )
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
        scope_label: str,
        context_blocks: Sequence[str],
        recent_history: Sequence[str],
    ) -> ChatAnswerResult:
        history_text = "\n".join(recent_history) if recent_history else "无"
        context_text = "\n\n".join(context_blocks) if context_blocks else "无可用上下文"
        prompt = f"""
你是一名学习助手，需要优先基于课件内容和已经生成的学习笔记回答问题。

要求：
1. 先给出基于课件的结论性回答。
2. 如果历史对话里已经形成了上下文，请延续前文，不要把每次问题都当成全新话题。
3. 如果学习任务台里的总结能帮助用户理解，可以自然整合进去。
4. 如果课件信息不足，可以补充少量通用常识，但必须放到 `supplemental_notes` 中。
5. 返回 JSON，不要输出额外说明。
6. `source_refs` 必须只包含输入上下文中出现过的来源编号。

文档标题：{document_title}
问答范围：{scope_label}
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
        payload = self._create_json_completion(prompt)
        supplemental = bool(payload.get("supplemental"))
        notes = payload.get("supplemental_notes")
        return ChatAnswerResult(
            answer=str(payload.get("answer") or "当前未能生成回答，请稍后重试。").strip(),
            source_refs=_clean_string_list(payload.get("source_refs")),
            supplemental=supplemental,
            supplemental_notes=str(notes).strip() if notes else None,
        )

    def _create_json_completion(self, prompt: str) -> dict:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严谨、简洁、遵守输入边界的中文学习助手。",
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = _coerce_content(response.choices[0].message.content)
        return _extract_json(content)


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
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


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
