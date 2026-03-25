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
            overview=f"《{document_title}》解析完成后，这里会自动生成摘要、概念、练习和复习路径。"
        )

    summary = [
        LearningSummaryItem(
            id=f"summary-{section.section_index}",
            title=section.title,
            summary=_first_sentence(section.detailed_explanation),
            source_refs=section.source_refs,
        )
        for section in sections
    ]

    concepts = [
        LearningConceptItem(
            id=f"concept-{section.section_index}-{index}",
            term=point[:18].strip("。"),
            explanation=point,
            section_title=section.title,
            source_refs=section.source_refs,
        )
        for section in sections
        for index, point in enumerate(section.key_points[:2], start=1)
    ]

    practice = [
        LearningPracticeItem(
            id=f"practice-{index}",
            prompt=f"请解释《{section.title}》最容易混淆的点，并举一个判断题示例。",
            section_title=section.title,
            source_refs=section.source_refs,
        )
        for index, section in enumerate(sections[:3], start=1)
    ]

    review_path = [
        LearningReviewStep(
            id=f"review-{index}",
            title=step_title,
            detail=detail,
            source_refs=sections[min(index - 1, len(sections) - 1)].source_refs,
        )
        for index, (step_title, detail) in enumerate(
            [
                (
                    "先读摘要",
                    f"先快速浏览《{document_title}》的章节摘要，确认全局脉络。",
                ),
                (
                    "再看概念",
                    "先梳理最重要的术语和定义，再判断它们之间的关系。",
                ),
                (
                    "最后做练习",
                    "完成练习任务后，再回到对话区验证自己是否真正理解。",
                ),
            ],
            start=1,
        )
    ]

    return LearningBoard(
        overview=(
            f"《{document_title}》已经整理成可复习的学习笔记。建议顺序：先看摘要，再梳理概念，"
            "然后完成练习，最后进入测试环境。"
        ),
        summary=summary,
        concepts=concepts,
        practice=practice,
        review_path=review_path,
    )


def _first_sentence(text: str) -> str:
    for separator in ("。", "\n", "！", "？"):
        if separator in text:
            head = text.split(separator, maxsplit=1)[0].strip()
            if head:
                return head + "。"
    cleaned = text.strip()
    return f"{cleaned}。" if cleaned else "暂无摘要。"
