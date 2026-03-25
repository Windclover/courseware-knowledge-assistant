from __future__ import annotations

from collections.abc import Sequence
import json
import re

from openai import OpenAI

from ..config import get_settings
from ..domain import ChatAnswerResult, GeneratedSection, SectionDraft


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
6. `quiz` 输出 3 道课后自测题。

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
  "quiz": ["问题1", "问题2"],
  "source_refs": ["第 1 张幻灯片"]
}}
        """.strip()
        payload = self._create_json_completion(prompt)
        return GeneratedSection(
            section_index=draft.section_index,
            title=str(payload.get("title") or draft.title),
            detailed_explanation=str(payload.get("detailed_explanation") or "").strip(),
            key_points=_clean_string_list(payload.get("key_points")),
            quiz=_clean_string_list(payload.get("quiz")),
            source_refs=_clean_string_list(payload.get("source_refs")) or draft.source_refs,
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
你是一名学习助手，需要优先基于课件内容回答问题。

要求：
1. 先给出基于课件的结论性回答。
2. 如果课件信息不足，可以补充少量通用常识，但必须放到 `supplemental_notes` 中。
3. 返回 JSON，不要输出额外说明。
4. `source_refs` 必须只包含输入上下文中出现过的来源编号。

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
