from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from ..domain import GeneratedSection


def write_markdown(
    output_dir: Path,
    *,
    document_title: str,
    original_filename: str,
    sections: list[GeneratedSection],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    markdown_path = output_dir / f"学习笔记-{timestamp}.md"
    markdown_path.write_text(
        build_markdown(
            document_title=document_title,
            original_filename=original_filename,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sections=sections,
        ),
        encoding="utf-8",
    )
    return markdown_path


def build_markdown(
    *,
    document_title: str,
    original_filename: str,
    generated_at: str,
    sections: list[GeneratedSection],
) -> str:
    toc_lines = [
        f"- [{section.title}](#{_slugify(section.title)})" for section in sections
    ]
    section_blocks: list[str] = []

    for section in sections:
        key_points = "\n".join(f"- {item}" for item in section.key_points)
        sources = "、".join(section.source_refs)
        section_blocks.append(
            "\n".join(
                [
                    f"## {section.title}",
                    "",
                    f"> 来源：{sources}",
                    "",
                    section.detailed_explanation,
                    "",
                    "### 关键知识点",
                    key_points or "- 暂无",
                    "",
                ]
            )
        )

    return "\n".join(
        [
            f"# {document_title} 学习笔记",
            "",
            f"- 原始文件：`{original_filename}`",
            f"- 生成时间：`{generated_at}`",
            "",
            "## 目录",
            "\n".join(toc_lines) or "- 暂无目录",
            "",
            *section_blocks,
        ]
    ).strip() + "\n"


def _slugify(text: str) -> str:
    sanitized = re.sub(r"\s+", "-", text.strip().lower())
    sanitized = re.sub(r"[^\w\-\u4e00-\u9fff]", "", sanitized)
    return sanitized or "section"
