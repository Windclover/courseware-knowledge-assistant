from __future__ import annotations

from dataclasses import dataclass

from .schemas import FormulaNote, WorkedExample


@dataclass(slots=True)
class ParsedFragment:
    fragment_index: int
    source_label: str
    source_type: str
    title: str | None
    text: str


@dataclass(slots=True)
class SectionDraft:
    section_index: int
    title: str
    source_refs: list[str]
    source_excerpt: str
    formula_candidates: list[str]
    example_candidates: list[str]


@dataclass(slots=True)
class GeneratedSection:
    section_index: int
    title: str
    detailed_explanation: str
    key_points: list[str]
    formula_notes: list[FormulaNote]
    worked_examples: list[WorkedExample]
    source_refs: list[str]


@dataclass(slots=True)
class RetrievalHit:
    source_label: str
    title: str
    content: str
    score: float


@dataclass(slots=True)
class ChatAnswerResult:
    answer: str
    source_refs: list[str]
    supplemental: bool
    supplemental_notes: str | None
