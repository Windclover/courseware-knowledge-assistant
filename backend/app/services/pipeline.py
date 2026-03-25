from __future__ import annotations

from pathlib import Path

from ..config import get_settings
from ..domain import GeneratedSection
from .. import repository
from ..schemas import DocumentDetail
from .ai_client import QwenClient
from .markdown_writer import write_markdown
from .parsers import parse_document
from .section_builder import build_sections


def process_saved_document(document_id: str, file_path: Path) -> DocumentDetail:
    document_title, _, fragments = parse_document(file_path)
    repository.clear_document_content(document_id)
    repository.save_fragments(document_id, fragments)
    repository.update_document(document_id, title=document_title)

    ai_client = QwenClient()
    section_drafts = build_sections(fragments)
    generated_sections: list[GeneratedSection] = [
        ai_client.generate_section(document_title, draft) for draft in section_drafts
    ]
    repository.save_sections(document_id, generated_sections)

    settings = get_settings()
    markdown_path = write_markdown(
        settings.output_root / document_id,
        document_title=document_title,
        original_filename=file_path.name,
        sections=generated_sections,
    )
    repository.update_document(
        document_id,
        status="ready",
        markdown_path=str(markdown_path.relative_to(settings.root_dir)),
        error_message="",
    )
    detail = repository.get_document_detail(document_id)
    if detail is None:
        raise RuntimeError("文档处理完成后未能读取详情。")
    return detail
