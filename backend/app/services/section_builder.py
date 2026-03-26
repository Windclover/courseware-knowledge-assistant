from __future__ import annotations

import re

from ..domain import ParsedFragment, SectionDraft


def build_sections(fragments: list[ParsedFragment]) -> list[SectionDraft]:
    sections: list[SectionDraft] = []
    buffer_fragments: list[ParsedFragment] = []
    explicit_title: str | None = None

    def flush_buffer() -> None:
        nonlocal buffer_fragments, explicit_title
        if not buffer_fragments:
            return
        section_index = len(sections) + 1
        title = explicit_title or f"第 {section_index} 部分"
        excerpt_parts = [
            f"[{fragment.source_label}] {fragment.text}" for fragment in buffer_fragments
        ]
        sections.append(
            SectionDraft(
                section_index=section_index,
                title=title,
                source_refs=[fragment.source_label for fragment in buffer_fragments],
                source_excerpt="\n\n".join(excerpt_parts),
                formula_candidates=_extract_formula_candidates(buffer_fragments),
                example_candidates=_extract_example_candidates(buffer_fragments),
            )
        )
        buffer_fragments = []
        explicit_title = None

    for fragment in fragments:
        title = _normalize_section_title(fragment.title)
        should_split_for_title = bool(
            buffer_fragments and title and explicit_title and title != explicit_title
        )
        should_split_for_size = bool(
            buffer_fragments
            and not title
            and (
                len(buffer_fragments) >= 2
                or sum(len(item.text) for item in buffer_fragments) > 1800
            )
        )

        if should_split_for_title or should_split_for_size:
            flush_buffer()

        if not buffer_fragments and title:
            explicit_title = title
        elif not explicit_title and title:
            explicit_title = title

        buffer_fragments.append(fragment)

    flush_buffer()
    return sections


def _normalize_section_title(title: str | None) -> str | None:
    if not title:
        return None
    cleaned = title.strip()
    if not cleaned or cleaned == "目录":
        return None
    return cleaned


def _extract_formula_candidates(fragments: list[ParsedFragment]) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    for fragment in fragments:
        lines = [line.strip() for line in fragment.text.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            if not _is_formula_anchor(line):
                continue
            start = max(0, index - 1)
            end = min(len(lines), index + 5)
            block = "\n".join(lines[start:end]).strip()
            normalized = _normalize_block(block)
            if normalized in seen:
                continue
            seen.add(normalized)
            candidates.append(block)
    return candidates[:6]


def _extract_example_candidates(fragments: list[ParsedFragment]) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    keywords = ("举例", "例", "算法", "步骤", "求解", "极小点")
    for fragment in fragments:
        title = fragment.title or ""
        text = fragment.text
        if not any(keyword in title or keyword in text for keyword in keywords):
            continue
        block = "\n".join(text.splitlines()[:18]).strip()
        normalized = _normalize_block(block)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(block)
    return candidates[:4]


def _is_formula_anchor(text: str) -> bool:
    math_tokens = ("=", "min", "argmin", "s.t", "∈", "∇", "σ", "λ", "μ", "||", "⩽")
    if any(token in text for token in math_tokens):
        return True
    if re.search(r"[A-Za-z]\w*\(.*\)", text):
        return True
    if re.search(r"x\d|c\d|g\d|h\d", text):
        return True
    return False


def _normalize_block(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())
