from __future__ import annotations

from pathlib import Path
import re
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .database import init_database
from .domain import RetrievalHit
from . import repository
from .schemas import AssessmentSuite, ChatAnswer, ChatRecord, ChatRequest, MarkdownPreview, UploadResponse
from .services.ai_client import AIConfigurationError, QwenClient
from .services.parsers import UnsupportedDocumentError
from .services.pipeline import process_saved_document
from .services.retrieval import build_context_blocks, rank_fragments


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_database()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/documents")
def list_documents():
    return repository.list_documents()


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    detail = repository.get_document_detail(document_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="文档不存在。")
    return detail


@app.post("/api/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pptx", ".pdf"}:
        raise HTTPException(status_code=400, detail="仅支持上传 PPTX 或文本型 PDF。")

    document_id = uuid4().hex[:12]
    saved_path = await _save_upload(document_id, file)
    repository.create_document(
        document_id=document_id,
        title=Path(filename).stem or "未命名课件",
        original_filename=filename,
        file_type=suffix.lstrip("."),
        source_path=str(saved_path.relative_to(settings.root_dir)),
        status="processing",
    )

    try:
        detail = process_saved_document(document_id, saved_path)
    except UnsupportedDocumentError as exc:
        repository.update_document(document_id, status="failed", error_message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        repository.update_document(document_id, status="failed", error_message=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        error_message = str(exc).strip() or "文档处理失败，请检查服务日志。"
        repository.update_document(
            document_id,
            status="failed",
            error_message=error_message,
        )
        raise HTTPException(status_code=500, detail=error_message) from exc

    return UploadResponse(document=detail)


@app.get("/api/documents/{document_id}/markdown", response_model=MarkdownPreview)
def get_markdown(document_id: str, download: bool = Query(default=False)):
    detail = repository.get_document_detail(document_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="文档不存在。")
    if not detail.markdown_path:
        raise HTTPException(status_code=404, detail="Markdown 尚未生成。")

    markdown_path = settings.root_dir / detail.markdown_path
    if not markdown_path.exists():
        raise HTTPException(status_code=404, detail="Markdown 文件不存在。")

    if download:
        return FileResponse(
            markdown_path,
            media_type="text/markdown",
            filename=markdown_path.name,
        )
    return MarkdownPreview(path=detail.markdown_path, content=markdown_path.read_text(encoding="utf-8"))


@app.post("/api/documents/{document_id}/chat", response_model=ChatAnswer)
def chat_with_document(document_id: str, payload: ChatRequest):
    detail = repository.get_document_detail(document_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="文档不存在。")
    if detail.status != "ready":
        raise HTTPException(status_code=400, detail="文档尚未处理完成，暂时无法问答。")

    recent_chats = repository.get_recent_chats(document_id, limit=12)
    question_type = _detect_question_type(payload.question, recent_chats)
    if question_type == "clarify":
        clarification = _build_clarification_answer(recent_chats)
        chat_id = repository.save_chat_message(
            document_id,
            scope="all",
            question=payload.question,
            answer=clarification,
            source_refs=[],
            supplemental=False,
            supplemental_notes=None,
        )
        latest = repository.get_recent_chats(document_id, limit=1)[0]
        return ChatAnswer(id=chat_id, **latest.model_dump(exclude={"id"}))
    if question_type == "exercise":
        grounded_answer, grounded_refs = _build_grounded_exercise_answer(detail)
        if grounded_answer:
            chat_id = repository.save_chat_message(
                document_id,
                scope="all",
                question=payload.question,
                answer=grounded_answer,
                source_refs=grounded_refs,
                supplemental=False,
                supplemental_notes=None,
            )
            latest = repository.get_recent_chats(document_id, limit=1)[0]
            return ChatAnswer(id=chat_id, **latest.model_dump(exclude={"id"}))
    if question_type == "follow_up":
        follow_up_answer = _build_follow_up_solution(recent_chats)
        if follow_up_answer:
            answer_text, answer_refs = follow_up_answer
            chat_id = repository.save_chat_message(
                document_id,
                scope="all",
                question=payload.question,
                answer=answer_text,
                source_refs=answer_refs,
                supplemental=False,
                supplemental_notes=None,
            )
            latest = repository.get_recent_chats(document_id, limit=1)[0]
            return ChatAnswer(id=chat_id, **latest.model_dump(exclude={"id"}))

    search_query = _build_search_query(payload.question, recent_chats, question_type)
    conversation_focus = _build_conversation_focus(payload.question, recent_chats, question_type)
    context_blocks, default_source_refs = _build_chat_context(
        detail,
        search_query=search_query,
        question_type=question_type,
    )
    if not context_blocks:
        fallback_answer = _build_no_hit_answer(question_type)
        chat_id = repository.save_chat_message(
            document_id,
            scope="all",
            question=payload.question,
            answer=fallback_answer,
            source_refs=[],
            supplemental=False,
            supplemental_notes=None,
        )
        recent = repository.get_recent_chats(document_id, limit=1)[0]
        return ChatAnswer(id=chat_id, **recent.model_dump(exclude={"id"}))

    recent_history = [f"Q: {chat.question}\nA: {chat.answer}" for chat in recent_chats]
    answer = QwenClient().answer_question(
        document_title=detail.title,
        question=payload.question,
        question_type=question_type,
        scope_label="课件与学习笔记",
        context_blocks=context_blocks,
        recent_history=recent_history,
        conversation_focus=conversation_focus,
    )
    if not answer.source_refs:
        answer.source_refs = default_source_refs
    chat_id = repository.save_chat_message(
        document_id,
        scope="all",
        question=payload.question,
        answer=answer.answer,
        source_refs=answer.source_refs,
        supplemental=answer.supplemental,
        supplemental_notes=answer.supplemental_notes,
    )
    latest = repository.get_recent_chats(document_id, limit=1)[0]
    return ChatAnswer(id=chat_id, **latest.model_dump(exclude={"id"}))


@app.post("/api/documents/{document_id}/assessment", response_model=AssessmentSuite)
def generate_assessment(document_id: str):
    detail = repository.get_document_detail(document_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="文档不存在。")
    if detail.status != "ready":
        raise HTTPException(status_code=400, detail="文档尚未处理完成，无法生成测试。")
    return QwenClient().generate_assessment(
        document_title=detail.title,
        sections=detail.sections,
        learning_board=detail.learning_board,
    )


async def _save_upload(document_id: str, file: UploadFile) -> Path:
    filename = Path(file.filename or "upload").name
    target_dir = settings.upload_root / document_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    total_size = 0
    with target_path.open("wb") as handle:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > settings.max_upload_size_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小不能超过 {settings.max_upload_size_mb} MB。",
                )
            handle.write(chunk)
    await file.close()
    return target_path


def _build_retrieval_records(detail, scope: str) -> list[dict[str, str | int | None]]:
    records: list[dict[str, str | int | None]] = []
    if scope in {"raw", "all"}:
        records.extend(repository.get_fragments(detail.id))
    if scope in {"notes", "all"}:
        if detail.learning_board.overview:
            records.append(
                {
                    "source_label": "学习任务台总览",
                    "title": "学习任务总览",
                    "content": detail.learning_board.overview,
                }
            )
        for section in detail.sections:
            formula_text = "\n".join(
                filter(
                    None,
                    [
                        f"{item.title}：{item.explanation}\n{item.latex or item.raw_text}"
                        for item in section.formula_notes
                    ],
                )
            )
            example_text = "\n".join(
                filter(
                    None,
                    [
                        "\n".join(
                            [
                                f"{item.title}",
                                item.problem,
                                "步骤：" + "；".join(item.steps),
                                f"答案：{item.final_answer}",
                            ]
                        )
                        for item in section.worked_examples
                    ],
                )
            )
            records.append(
                {
                    "source_label": "、".join(section.source_refs),
                    "title": section.title,
                    "content": "\n".join(
                        [
                            section.detailed_explanation,
                            "关键知识点：" + "；".join(section.key_points),
                            "核心公式：" + formula_text if formula_text else "",
                            "例题步骤：" + example_text if example_text else "",
                        ]
                    ),
                }
            )
            for formula in section.formula_notes:
                records.append(
                    {
                        "source_label": "、".join(formula.source_refs or section.source_refs),
                        "title": f"{section.title} / {formula.title}",
                        "content": "\n".join(
                            filter(
                                None,
                                [
                                    "核心公式",
                                    formula.latex or formula.raw_text,
                                    formula.explanation,
                                ],
                            )
                        ),
                    }
                )
            for example in section.worked_examples:
                records.append(
                    {
                        "source_label": "、".join(example.source_refs or section.source_refs),
                        "title": f"{section.title} / {example.title}",
                        "content": "\n".join(
                            filter(
                                None,
                                [
                                    "例题",
                                    example.problem,
                                    "步骤：" + "；".join(example.steps),
                                    "答案：" + example.final_answer,
                                ],
                            )
                        ),
                    }
                )
        records.append(
            {
                "source_label": "课件目录",
                "title": "章节总览",
                "content": "\n".join(
                    f"{section.title}：{'；'.join(section.key_points[:2]) or section.detailed_explanation[:120]}"
                    for section in detail.sections
                ),
            }
        )
    return records


def _detect_question_type(question: str, recent_chats: list[ChatRecord]) -> str:
    normalized = question.strip().lower()
    if not normalized or re.fullmatch(r"[\d\W_]+", normalized):
        return "clarify"
    if any(token in question for token in ("公式", "数学公式", "推导", "latex", "符号")):
        return "formula"
    if any(token in question for token in ("最重要的 3 个概念", "最重要的三个概念", "3 个概念", "三个概念", "关键概念")):
        return "concepts"
    if any(token in question for token in ("需要掌握", "掌握什么", "重点", "考什么", "复习什么")):
        return "mastery"
    if any(token in question for token in ("练习题", "出个题", "出题", "习题")):
        return "exercise"
    if any(token in question for token in ("怎么解决", "怎么做", "如何求解", "怎么解", "怎么求")) and recent_chats:
        return "follow_up"
    if any(token in question for token in ("总结", "概括", "摘要")):
        return "summary"
    return "general"


def _build_search_query(question: str, recent_chats: list[ChatRecord], question_type: str) -> str:
    query = question.strip()
    if question_type == "formula":
        return f"{query} 公式 符号 变量 约束"
    if question_type in {"mastery", "concepts", "summary"}:
        return f"{query} 章节 关键知识点 概念 重点"
    if question_type == "exercise":
        return f"{query} 例题 步骤 公式 求解"
    if question_type == "follow_up" and recent_chats:
        last_chat = recent_chats[-1]
        return f"{question} {last_chat.question} {last_chat.answer[:300]} 例题 步骤 解题"
    return query


def _build_conversation_focus(
    question: str,
    recent_chats: list[ChatRecord],
    question_type: str,
) -> str:
    if question_type != "follow_up" or not recent_chats:
        return ""
    last_chat = recent_chats[-1]
    return "\n".join(
        [
            "当前问题大概率是在承接上一轮对话，请优先回答上一轮的练习题或未讲完的内容。",
            f"上一轮用户问题：{last_chat.question}",
            f"上一轮助手回答：{last_chat.answer}",
            f"本轮追问：{question}",
        ]
    )


def _build_clarification_answer(recent_chats: list[ChatRecord]) -> str:
    if recent_chats:
        return (
            "这条输入太短，我无法判断你是想继续回答上一题，还是想问新的内容。"
            "如果你想承接上一题，可以直接说“请解上面那道练习题”或“继续用公式讲”。"
        )
    return "这条输入太短，我无法判断你的问题。你可以直接说“请总结这份课件”或“请用公式解释罚函数法”。"


def _build_no_hit_answer(question_type: str) -> str:
    if question_type == "follow_up":
        return "我没有在当前上下文里定位到你要承接的那一步。你可以直接说“请解上面那道练习题”或把题目再贴一次。"
    if question_type == "formula":
        return "我暂时没有检索到足够的公式上下文。你可以直接说“解释外点罚函数公式”或“讲第 10 页那个例题公式”。"
    return "当前没有检索到足够的课件内容，请换一种更具体的问法，或先查看生成的章节讲解。"


def _resolve_retrieval_limit(question_type: str) -> int:
    if question_type in {"formula", "mastery", "concepts", "exercise", "follow_up"}:
        return max(settings.retrieval_limit, 8)
    return settings.retrieval_limit


def _fallback_source_refs_from_hits(hits: list[RetrievalHit]) -> list[str]:
    refs: list[str] = []
    for hit in hits:
        label = hit.source_label.strip()
        if label and label not in refs:
            refs.append(label)
        if len(refs) >= 3:
            break
    return refs


def _build_chat_context(
    detail,
    *,
    search_query: str,
    question_type: str,
) -> tuple[list[str], list[str]]:
    if question_type in {"summary", "mastery", "concepts"}:
        blocks = _build_global_context_blocks(detail)
        refs = _collect_global_source_refs(detail)
        return blocks, refs
    if question_type == "formula":
        blocks = _build_formula_context_blocks(detail)
        refs = _collect_formula_source_refs(detail)
        return blocks, refs
    if question_type == "exercise":
        blocks = _build_exercise_context_blocks(detail)
        refs = _collect_example_source_refs(detail)
        return blocks, refs

    records = _build_retrieval_records(detail, "all")
    retrieval_limit = _resolve_retrieval_limit(question_type)
    hits = rank_fragments(
        search_query,
        records,
        limit=retrieval_limit,
        question_type=question_type,
    )
    return build_context_blocks(hits), _fallback_source_refs_from_hits(hits)


def _build_global_context_blocks(detail) -> list[str]:
    section_lines = [
        f"{section.title}：{'；'.join(section.key_points[:3]) or section.detailed_explanation[:120]}"
        for section in detail.sections
    ]
    formula_lines = [
        f"{section.title} / {item.title}：{item.latex or item.raw_text}"
        for section in detail.sections
        for item in section.formula_notes[:2]
        if item.latex or item.raw_text
    ]
    example_lines = [
        f"{section.title} / {item.title}：{item.problem}"
        for section in detail.sections
        for item in section.worked_examples[:1]
        if item.problem
    ]
    blocks = [
        "\n".join(
            [
                "来源：学习任务台总览",
                "标题：课件总览",
                detail.learning_board.overview or "暂无总览。",
            ]
        ),
        "\n".join(["来源：课件目录", "标题：章节与重点", *section_lines[:12]]),
    ]
    if formula_lines:
        blocks.append("\n".join(["来源：核心公式索引", "标题：公式总览", *formula_lines[:8]]))
    if example_lines:
        blocks.append("\n".join(["来源：例题索引", "标题：例题总览", *example_lines[:6]]))
    return blocks


def _collect_global_source_refs(detail) -> list[str]:
    refs: list[str] = []
    for section in detail.sections:
        for ref in section.source_refs:
            if ref not in refs:
                refs.append(ref)
            if len(refs) >= 4:
                return refs
    return refs


def _build_formula_context_blocks(detail) -> list[str]:
    formula_lines = [
        "\n".join(
            [
                f"来源：{'、'.join(item.source_refs or section.source_refs)}",
                f"标题：{section.title} / {item.title}",
                item.latex or item.raw_text,
                item.explanation,
            ]
        )
        for section in detail.sections
        for item in section.formula_notes
        if item.latex or item.raw_text
    ]
    if not formula_lines:
        return _build_global_context_blocks(detail)
    return formula_lines[:8]


def _build_exercise_context_blocks(detail) -> list[str]:
    example_lines = [
        "\n".join(
            [
                f"来源：{'、'.join(item.source_refs or section.source_refs)}",
                f"标题：{section.title} / {item.title}",
                item.problem,
                "步骤：" + "；".join(item.steps),
                "答案：" + item.final_answer,
            ]
        )
        for section in detail.sections
        for item in section.worked_examples
        if item.problem
    ]
    if not example_lines:
        return _build_global_context_blocks(detail)
    return example_lines[:6] + _build_formula_context_blocks(detail)[:3]


def _collect_formula_source_refs(detail) -> list[str]:
    refs: list[str] = []
    for section in detail.sections:
        for item in section.formula_notes:
            for ref in item.source_refs or section.source_refs:
                if ref not in refs:
                    refs.append(ref)
                if len(refs) >= 4:
                    return refs
    return refs or _collect_global_source_refs(detail)


def _collect_example_source_refs(detail) -> list[str]:
    refs: list[str] = []
    for section in detail.sections:
        for item in section.worked_examples:
            for ref in item.source_refs or section.source_refs:
                if ref not in refs:
                    refs.append(ref)
                if len(refs) >= 4:
                    return refs
    return refs or _collect_global_source_refs(detail)


def _build_grounded_exercise_answer(detail) -> tuple[str, list[str]]:
    raw_fragment = _select_raw_example_fragment(detail.id)
    if raw_fragment is not None:
        answer = _build_exercise_from_raw_fragment(raw_fragment)
        if answer:
            return answer, [str(raw_fragment.get("source_label") or "")]

    best_section = None
    best_example = None
    for section in detail.sections:
        for example in section.worked_examples:
            if "举例" in section.title or "举例" in example.title:
                best_section = section
                best_example = example
                break
        if best_example:
            break
    if best_example is None:
        for section in detail.sections:
            if section.worked_examples:
                best_section = section
                best_example = section.worked_examples[0]
                break
    if best_example is None or best_section is None:
        return "", []

    thinking = (
        "先识别题目对应的约束类型和罚函数形式，再按照课件中的步骤构造罚函数、求极值点，"
        "最后说明参数变化对解的影响。"
    )
    mistakes = (
        "常见错误包括：把罚函数的符号写错；把罚因子放反；只写出罚函数但没有继续求极值点；"
        "或者没有说明结果如何逼近原问题最优解。"
    )
    steps_text = "\n".join(
        f"{index}. {step}" for index, step in enumerate(best_example.steps, start=1)
    )
    answer = "\n".join(
        [
            f"练习题：{best_example.problem}",
            "",
            f"解题思路：{thinking}",
            "",
            "详细解答：",
            steps_text or "1. 请结合课件继续推导。",
            "",
            f"最终答案：{best_example.final_answer or '请结合上面的步骤得到结果。'}",
            "",
            f"易错点：{mistakes}",
        ]
    ).strip()
    return answer, list(best_example.source_refs or best_section.source_refs)


def _build_follow_up_solution(
    recent_chats: list[ChatRecord],
) -> tuple[str, list[str]] | None:
    if not recent_chats:
        return None
    last_chat = recent_chats[-1]
    if "练习题：" not in last_chat.answer or "详细解答：" not in last_chat.answer:
        return None

    solution = _extract_section_text(last_chat.answer, "详细解答：", "最终答案：")
    final_answer = _extract_section_text(last_chat.answer, "最终答案：", "易错点：")
    if not solution:
        return None
    parts = ["根据上一题，我们继续按步骤来解：", "", solution.strip()]
    if final_answer:
        parts.extend(["", f"最终答案：{final_answer.strip()}"])
    return "\n".join(parts).strip(), list(last_chat.source_refs)


def _extract_section_text(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        return ""
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def _select_raw_example_fragment(document_id: str):
    fragments = repository.get_fragments(document_id)
    for fragment in fragments:
        title = str(fragment.get("title") or "")
        text = str(fragment.get("text_content") or "")
        if "等式约束举例" in title or "举例" in title:
            return fragment
        if "罚函数为" in text and "极小点为" in text:
            return fragment
    return None


def _build_exercise_from_raw_fragment(fragment) -> str:
    lines = [line.strip() for line in str(fragment.get("text_content") or "").splitlines() if line.strip()]
    if not lines:
        return ""

    problem_lines = _collect_lines(lines, start_keywords=("min", "s.t"), stop_keywords=("罚函数为",))
    formula_lines = _collect_lines(lines, start_keywords=("罚函数为",), stop_keywords=("极小点为",))
    extreme_lines = _collect_lines(lines, start_keywords=("极小点为",), stop_keywords=("最优化方法",))

    problem = _compact_math_text(problem_lines) or "请根据课件中的举例继续推导。"
    formula = _compact_math_text(formula_lines) or "请根据课件写出罚函数。"
    extreme = _compact_math_text(extreme_lines) or "请根据课件继续推导极小点表达式。"

    return "\n".join(
        [
            f"练习题：{problem}",
            "",
            "解题思路：先直接写出课件中的罚函数，再利用课件给出的极小点表达式观察惩罚因子 σ 对结果的影响。",
            "",
            "详细解答：",
            f"1. 课件中的原问题是：{problem}",
            f"2. 课件给出的罚函数是：{formula}",
            f"3. 课件给出的极小点表达式是：{extreme}",
            "4. 由课件图示与讲解可知，随着 σ 增大，罚函数的极小点会逐渐逼近原问题的最优解。",
            "",
            f"最终答案：{extreme}",
            "",
            "易错点：不要把罚函数里的惩罚项符号和系数写错，也不要忽略“随着 σ 变化，极小点逼近原问题最优解”这一结论。",
        ]
    ).strip()


def _collect_lines(lines: list[str], start_keywords: tuple[str, ...], stop_keywords: tuple[str, ...]) -> list[str]:
    buffer: list[str] = []
    collecting = False
    for line in lines:
        if any(keyword in line for keyword in start_keywords):
            collecting = True
        if not collecting:
            continue
        if buffer and any(keyword in line for keyword in stop_keywords):
            break
        buffer.append(line)
    return buffer


def _compact_math_text(lines: list[str]) -> str:
    if not lines:
        return ""
    return re.sub(r"\s+", " ", " ".join(lines)).strip()
