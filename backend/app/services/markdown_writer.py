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
        formula_block = _build_formula_block(section)
        example_block = _build_example_block(section)
        section_blocks.append(
            "\n".join(
                [
                    f"## {section.title}",
                    "",
                    "### 章节概述",
                    section.key_points[0] if section.key_points else "暂无章节概述。",
                    "",
                    "### 详细讲解",
                    "",
                    "",
                    section.detailed_explanation,
                    "",
                    "### 关键知识点",
                    key_points or "- 暂无",
                    "",
                    "### 核心公式",
                    formula_block,
                    "",
                    "### 例题与计算步骤",
                    example_block,
                    "",
                    f"> 来源：{sources}",
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


def _build_formula_block(section: GeneratedSection) -> str:
    if not section.formula_notes:
        return "- 暂未提取到核心公式。"

    blocks: list[str] = []
    for item in section.formula_notes:
        source_refs = "、".join(item.source_refs) or "未标注来源"
        blocks.append(f"#### {item.title}")
        if item.latex:
            blocks.append("$$")
            blocks.append(item.latex)
            blocks.append("$$")
        elif item.raw_text:
            blocks.append("```text")
            blocks.append(item.raw_text)
            blocks.append("```")
        if item.explanation:
            blocks.append(item.explanation)
        blocks.append(f"> 来源：{source_refs}")
        blocks.append("")
    return "\n".join(blocks).strip()


def _build_example_block(section: GeneratedSection) -> str:
    if not section.worked_examples:
        return "- 暂未整理出例题。"

    blocks: list[str] = []
    for item in section.worked_examples:
        source_refs = "、".join(item.source_refs) or "未标注来源"
        blocks.append(f"#### {item.title}")
        blocks.append("**题目**")
        blocks.append(item.problem)
        blocks.append("")
        blocks.append("**解题步骤**")
        if item.steps:
            blocks.extend(f"{index}. {step}" for index, step in enumerate(item.steps, start=1))
        else:
            blocks.append("1. 暂无步骤。")
        if item.final_answer:
            blocks.append("")
            blocks.append(f"**最终答案**：{item.final_answer}")
        blocks.append(f"> 来源：{source_refs}")
        blocks.append("")
    return "\n".join(blocks).strip()
