from __future__ import annotations

from pathlib import Path
import re

import fitz
from pptx import Presentation

from ..domain import ParsedFragment


class UnsupportedDocumentError(ValueError):
    pass


def parse_document(file_path: Path) -> tuple[str, str, list[ParsedFragment]]:
    suffix = file_path.suffix.lower()
    if suffix == ".pptx":
        return _parse_pptx(file_path)
    if suffix == ".pdf":
        return _parse_pdf(file_path)
    raise UnsupportedDocumentError("仅支持 PPTX 或文本型 PDF。")


def _parse_pptx(file_path: Path) -> tuple[str, str, list[ParsedFragment]]:
    presentation = Presentation(file_path)
    document_title = presentation.core_properties.title or file_path.stem
    fragments: list[ParsedFragment] = []

    for index, slide in enumerate(presentation.slides, start=1):
        title = None
        if slide.shapes.title and slide.shapes.title.text:
            title = _clean_text(slide.shapes.title.text)
        texts: list[str] = []
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            text = _clean_text(shape.text)
            if not text:
                continue
            if title and text == title:
                continue
            texts.append(text)
        slide_text = "\n".join(texts).strip()
        if not slide_text and title:
            slide_text = title
        if not slide_text:
            continue
        fragments.append(
            ParsedFragment(
                fragment_index=index,
                source_label=f"第 {index} 张幻灯片",
                source_type="slide",
                title=title,
                text=slide_text,
            )
        )

    if not fragments:
        raise UnsupportedDocumentError("PPTX 中未提取到有效文本。")
    return document_title, "pptx", fragments


def _parse_pdf(file_path: Path) -> tuple[str, str, list[ParsedFragment]]:
    document = fitz.open(file_path)
    metadata_title = (document.metadata or {}).get("title") if document.metadata else None
    document_title = metadata_title or file_path.stem
    fragments: list[ParsedFragment] = []

    for index, page in enumerate(document, start=1):
        text = _clean_text(page.get_text("text"))
        if not text:
            continue
        title = _detect_pdf_page_title(text)
        fragments.append(
            ParsedFragment(
                fragment_index=index,
                source_label=f"第 {index} 页",
                source_type="page",
                title=title,
                text=text,
            )
        )

    document.close()
    if not fragments:
        raise UnsupportedDocumentError(
            "未检测到可提取文本，可能是扫描版 PDF。首版暂不支持 OCR。"
        )
    return document_title, "pdf", fragments


def _detect_pdf_page_title(text: str) -> str | None:
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    if not first_line:
        return None
    if len(first_line) <= 28 and re.search(r"[\u4e00-\u9fffA-Za-z]", first_line):
        return first_line
    return None


def _clean_text(text: str) -> str:
    normalized = text.replace("\x0b", "\n").replace("\u3000", " ")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    return normalized.strip()
