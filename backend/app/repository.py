from __future__ import annotations

from datetime import datetime, UTC
import json
from typing import Iterable

from .database import get_connection
from .domain import GeneratedSection, ParsedFragment
from .services.learning_board import build_learning_board
from .schemas import (
    ChatRecord,
    DocumentDetail,
    DocumentSummary,
    LearningBoard,
    SectionNote,
    SourceFragment,
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def create_document(
    document_id: str,
    title: str,
    original_filename: str,
    file_type: str,
    source_path: str,
    status: str,
) -> None:
    now = _now_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                id, title, original_filename, file_type, status, source_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, title, original_filename, file_type, status, source_path, now, now),
        )


def update_document(
    document_id: str,
    *,
    status: str | None = None,
    title: str | None = None,
    markdown_path: str | None = None,
    error_message: str | None = None,
) -> None:
    fields: list[str] = []
    values: list[str | None] = []
    if status is not None:
        fields.append("status = ?")
        values.append(status)
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if markdown_path is not None:
        fields.append("markdown_path = ?")
        values.append(markdown_path)
    if error_message is not None:
        fields.append("error_message = ?")
        values.append(error_message)
    fields.append("updated_at = ?")
    values.append(_now_iso())
    values.append(document_id)
    with get_connection() as connection:
        connection.execute(
            f"UPDATE documents SET {', '.join(fields)} WHERE id = ?",
            values,
        )


def clear_document_content(document_id: str) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM fragments WHERE document_id = ?", (document_id,))
        connection.execute("DELETE FROM sections WHERE document_id = ?", (document_id,))


def save_fragments(document_id: str, fragments: Iterable[ParsedFragment]) -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO fragments (
                document_id, fragment_index, source_label, source_type, title, text_content
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    document_id,
                    fragment.fragment_index,
                    fragment.source_label,
                    fragment.source_type,
                    fragment.title,
                    fragment.text,
                )
                for fragment in fragments
            ],
        )


def save_sections(document_id: str, sections: Iterable[GeneratedSection]) -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO sections (
                document_id, section_index, title, detailed_explanation, key_points_json, quiz_json, source_refs_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    document_id,
                    section.section_index,
                    section.title,
                    section.detailed_explanation,
                    json.dumps(section.key_points, ensure_ascii=False),
                    json.dumps(section.quiz, ensure_ascii=False),
                    json.dumps(section.source_refs, ensure_ascii=False),
                )
                for section in sections
            ],
        )


def save_chat_message(
    document_id: str,
    *,
    scope: str,
    question: str,
    answer: str,
    source_refs: list[str],
    supplemental: bool,
    supplemental_notes: str | None,
) -> int:
    now = _now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO chat_messages (
                document_id, scope, question, answer, source_refs_json, supplemental, supplemental_notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                scope,
                question,
                answer,
                json.dumps(source_refs, ensure_ascii=False),
                int(supplemental),
                supplemental_notes,
                now,
            ),
        )
        return int(cursor.lastrowid)


def get_document_record(document_id: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return row


def list_documents() -> list[DocumentSummary]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM documents ORDER BY updated_at DESC"
        ).fetchall()
    return [_build_document_summary(row) for row in rows]


def get_fragments(document_id: str) -> list[dict[str, str | int | None]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT fragment_index, source_label, source_type, title, text_content
            FROM fragments
            WHERE document_id = ?
            ORDER BY fragment_index ASC
            """,
            (document_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_recent_chats(document_id: str, limit: int = 4) -> list[ChatRecord]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM chat_messages
            WHERE document_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (document_id, limit),
        ).fetchall()
    return [_build_chat_record(row) for row in reversed(rows)]


def get_document_detail(document_id: str) -> DocumentDetail | None:
    with get_connection() as connection:
        document_row = connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if document_row is None:
            return None
        section_rows = connection.execute(
            """
            SELECT *
            FROM sections
            WHERE document_id = ?
            ORDER BY section_index ASC
            """,
            (document_id,),
        ).fetchall()
        chat_rows = connection.execute(
            """
            SELECT *
            FROM chat_messages
            WHERE document_id = ?
            ORDER BY id ASC
            """,
            (document_id,),
        ).fetchall()
        fragment_rows = connection.execute(
            """
            SELECT fragment_index, source_label, source_type, title, text_content
            FROM fragments
            WHERE document_id = ?
            ORDER BY fragment_index ASC
            """,
            (document_id,),
        ).fetchall()
    summary = _build_document_summary(document_row)
    sections = [_build_section_note(row) for row in section_rows]
    return DocumentDetail(
        **summary.model_dump(),
        sections=sections,
        chats=[_build_chat_record(row) for row in chat_rows],
        sources=[_build_source_fragment(row) for row in fragment_rows],
        learning_board=build_learning_board(summary.title, sections),
    )


def _build_document_summary(row) -> DocumentSummary:
    return DocumentSummary(
        id=row["id"],
        title=row["title"],
        original_filename=row["original_filename"],
        file_type=row["file_type"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        markdown_path=row["markdown_path"],
        error_message=row["error_message"],
    )


def _build_section_note(row) -> SectionNote:
    return SectionNote(
        section_index=row["section_index"],
        title=row["title"],
        detailed_explanation=row["detailed_explanation"],
        key_points=json.loads(row["key_points_json"]),
        quiz=json.loads(row["quiz_json"]),
        source_refs=json.loads(row["source_refs_json"]),
    )


def _build_chat_record(row) -> ChatRecord:
    return ChatRecord(
        id=row["id"],
        scope=row["scope"],
        question=row["question"],
        answer=row["answer"],
        source_refs=json.loads(row["source_refs_json"]),
        supplemental=bool(row["supplemental"]),
        supplemental_notes=row["supplemental_notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _build_source_fragment(row) -> SourceFragment:
    full_text = row["text_content"]
    preview_text = full_text.replace("\n", " ").strip()
    if len(preview_text) > 180:
        preview_text = preview_text[:177].rstrip() + "..."
    return SourceFragment(
        fragment_index=row["fragment_index"],
        source_label=row["source_label"],
        source_type=row["source_type"],
        title=row["title"],
        preview_text=preview_text,
        full_text=full_text,
    )
