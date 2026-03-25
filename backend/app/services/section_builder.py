from __future__ import annotations

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
            )
        )
        buffer_fragments = []
        explicit_title = None

    for fragment in fragments:
        title = fragment.title.strip() if fragment.title else None
        should_split_for_title = bool(
            buffer_fragments and title and explicit_title and title != explicit_title
        )
        should_split_for_size = bool(
            buffer_fragments
            and not title
            and (len(buffer_fragments) >= 2 or sum(len(item.text) for item in buffer_fragments) > 1800)
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
