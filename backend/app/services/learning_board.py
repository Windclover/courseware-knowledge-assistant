from __future__ import annotations

from ..schemas import (
    LearningBoard,
    LearningConceptItem,
    LearningPracticeItem,
    LearningReviewStep,
    LearningSummaryItem,
    SectionNote,
)


def build_learning_board(
    document_title: str,
    sections: list[SectionNote],
) -> LearningBoard:
    if not sections:
        return LearningBoard(
            overview="上传并解析课件后，这里会自动生成学习摘要、概念、练习和复习路径。"
        )

    summary_items = [
        LearningSummaryItem(
            id=f"summary-{section.section_index}",
            title=section.title,
            summary=_build_section_digest(section),
            source_refs=section.source_refs,
        )
        for section in sections
    ]
    concepts = _build_concepts(sections)
    practice = _build_practice(sections)
    review_path = _build_review_path(document_title, sections)

    overview_titles = "、".join(section.title for section in sections[:4])
    overview = (
        f"《{document_title}》围绕 {overview_titles} 展开。"
        f" 优先先读总览摘要，再梳理概念，随后完成练习并按复习路径回看重点。"
    )

    return LearningBoard(
        overview=overview,
        summary=summary_items,
        concepts=concepts,
        practice=practice,
        review_path=review_path,
    )


def _build_section_digest(section: SectionNote) -> str:
    if section.key_points:
        head = section.key_points[0]
    else:
        head = _first_sentence(section.detailed_explanation)
    return head.rstrip("。；;") + "。"


def _build_concepts(sections: list[SectionNote]) -> list[LearningConceptItem]:
    items: list[LearningConceptItem] = []
    for section in sections:
        concept_sources = section.source_refs
        section_anchor = _first_sentence(section.detailed_explanation)
        for index, point in enumerate(section.key_points[:3], start=1):
            items.append(
                LearningConceptItem(
                    id=f"concept-{section.section_index}-{index}",
                    term=_extract_term(point),
                    explanation=(
                        f"{point.rstrip('。；;')}。"
                        f" 在“{section.title}”中，它关联到：{section_anchor.rstrip('。；;')}。"
                    ),
                    section_title=section.title,
                    source_refs=concept_sources,
                )
            )
    return items


def _build_practice(sections: list[SectionNote]) -> list[LearningPracticeItem]:
    items: list[LearningPracticeItem] = []
    for section in sections:
        for index, prompt in enumerate(section.quiz, start=1):
            items.append(
                LearningPracticeItem(
                    id=f"practice-{section.section_index}-{index}",
                    prompt=prompt,
                    section_title=section.title,
                    source_refs=section.source_refs,
                )
            )
    return items


def _build_review_path(
    document_title: str,
    sections: list[SectionNote],
) -> list[LearningReviewStep]:
    steps: list[LearningReviewStep] = [
        LearningReviewStep(
            id="review-overview",
            title="先建立整份课件的心智地图",
            detail=f"先用 3-5 分钟快速浏览《{document_title}》的摘要，确认章节关系和重点分布。",
            source_refs=sections[0].source_refs if sections else [],
        )
    ]

    for section in sections[:3]:
        steps.append(
            LearningReviewStep(
                id=f"review-section-{section.section_index}",
                title=f"精读《{section.title}》",
                detail=(
                    f"先掌握 {section.title} 的核心概念，再完成这一节对应的练习题，"
                    "最后回到对话区验证自己是否真正理解。"
                ),
                source_refs=section.source_refs,
            )
        )

    steps.append(
        LearningReviewStep(
            id="review-practice",
            title="完成整份课件的练习与回顾",
            detail="把练习题按章节完成一遍，再挑选最难的概念回到来源片段进行复盘。",
            source_refs=[ref for section in sections for ref in section.source_refs[:1]],
        )
    )
    return steps


def _extract_term(text: str) -> str:
    cleaned = text.strip().strip("。")
    for separator in ("：", ":", "，", ",", "（", "("):
        if separator in cleaned:
            head = cleaned.split(separator, maxsplit=1)[0].strip()
            if head:
                return head
    if len(cleaned) > 18:
        return cleaned[:18].rstrip()
    return cleaned


def _first_sentence(text: str) -> str:
    for separator in ("。", "\n", "！", "？"):
        if separator in text:
            head = text.split(separator, maxsplit=1)[0].strip()
            if head:
                return head
    return text.strip()
