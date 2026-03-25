from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ChatScope = Literal["raw", "notes", "all"]


class DocumentSummary(BaseModel):
    id: str
    title: str
    original_filename: str
    file_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    markdown_path: str | None = None
    error_message: str | None = None


class SectionNote(BaseModel):
    section_index: int
    title: str
    detailed_explanation: str
    key_points: list[str] = Field(default_factory=list)
    quiz: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class ChatRecord(BaseModel):
    id: int
    scope: ChatScope
    question: str
    answer: str
    source_refs: list[str] = Field(default_factory=list)
    supplemental: bool = False
    supplemental_notes: str | None = None
    created_at: datetime


class SourceFragment(BaseModel):
    fragment_index: int
    source_label: str
    source_type: str
    title: str | None = None
    preview_text: str
    full_text: str


class LearningSummaryItem(BaseModel):
    id: str
    title: str
    summary: str
    source_refs: list[str] = Field(default_factory=list)


class LearningConceptItem(BaseModel):
    id: str
    term: str
    explanation: str
    section_title: str
    source_refs: list[str] = Field(default_factory=list)


class LearningPracticeItem(BaseModel):
    id: str
    prompt: str
    section_title: str
    source_refs: list[str] = Field(default_factory=list)


class LearningReviewStep(BaseModel):
    id: str
    title: str
    detail: str
    source_refs: list[str] = Field(default_factory=list)


class LearningBoard(BaseModel):
    overview: str = ""
    summary: list[LearningSummaryItem] = Field(default_factory=list)
    concepts: list[LearningConceptItem] = Field(default_factory=list)
    practice: list[LearningPracticeItem] = Field(default_factory=list)
    review_path: list[LearningReviewStep] = Field(default_factory=list)


class DocumentDetail(DocumentSummary):
    sections: list[SectionNote] = Field(default_factory=list)
    chats: list[ChatRecord] = Field(default_factory=list)
    sources: list[SourceFragment] = Field(default_factory=list)
    learning_board: LearningBoard = Field(default_factory=LearningBoard)


class UploadResponse(BaseModel):
    document: DocumentDetail


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    scope: ChatScope = "all"


class ChatAnswer(BaseModel):
    id: int
    scope: ChatScope
    question: str
    answer: str
    source_refs: list[str] = Field(default_factory=list)
    supplemental: bool = False
    supplemental_notes: str | None = None
    created_at: datetime


class MarkdownPreview(BaseModel):
    path: str
    content: str
