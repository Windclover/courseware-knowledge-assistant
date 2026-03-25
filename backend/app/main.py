from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .database import init_database
from . import repository
from .schemas import AssessmentSuite, ChatAnswer, ChatRequest, MarkdownPreview, UploadResponse
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
        repository.update_document(
            document_id,
            status="failed",
            error_message="文档处理失败，请检查服务日志。",
        )
        raise HTTPException(status_code=500, detail="文档处理失败，请稍后重试。") from exc

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

    records = _build_retrieval_records(detail, "all")
    hits = rank_fragments(payload.question, records, limit=settings.retrieval_limit)
    if not hits:
        fallback_answer = "当前没有检索到足够的课件内容，请换一种问法，或先查看生成的章节讲解。"
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

    recent_history = [
        f"Q: {chat.question}\nA: {chat.answer}"
        for chat in repository.get_recent_chats(document_id, limit=3)
    ]
    answer = QwenClient().answer_question(
        document_title=detail.title,
        question=payload.question,
        scope_label="课件与学习笔记",
        context_blocks=build_context_blocks(hits),
        recent_history=recent_history,
    )
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
        for section in detail.sections:
            records.append(
                {
                    "source_label": "、".join(section.source_refs),
                    "title": section.title,
                    "content": "\n".join(
                        [
                            section.detailed_explanation,
                            "关键知识点：" + "；".join(section.key_points),
                        ]
                    ),
                }
            )
    return records
