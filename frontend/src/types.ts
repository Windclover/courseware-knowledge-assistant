export type ChatScope = "raw" | "notes" | "all";

export interface DocumentSummary {
  id: string;
  title: string;
  original_filename: string;
  file_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  markdown_path: string | null;
  error_message: string | null;
}

export interface SectionNote {
  section_index: number;
  title: string;
  detailed_explanation: string;
  key_points: string[];
  formula_notes: FormulaNote[];
  worked_examples: WorkedExample[];
  source_refs: string[];
}

export interface FormulaNote {
  title: string;
  latex: string;
  raw_text: string;
  explanation: string;
  source_refs: string[];
}

export interface WorkedExample {
  title: string;
  problem: string;
  steps: string[];
  final_answer: string;
  source_refs: string[];
}

export interface ChatRecord {
  id: number;
  scope: ChatScope;
  question: string;
  answer: string;
  source_refs: string[];
  supplemental: boolean;
  supplemental_notes: string | null;
  created_at: string;
}

export interface SourceFragment {
  fragment_index: number;
  source_label: string;
  source_type: string;
  title: string | null;
  preview_text: string;
  full_text: string;
}

export interface LearningSummaryItem {
  id: string;
  title: string;
  summary: string;
  source_refs: string[];
}

export interface LearningConceptItem {
  id: string;
  term: string;
  explanation: string;
  section_title: string;
  source_refs: string[];
}

export interface LearningPracticeItem {
  id: string;
  prompt: string;
  section_title: string;
  source_refs: string[];
}

export interface LearningReviewStep {
  id: string;
  title: string;
  detail: string;
  source_refs: string[];
}

export interface LearningBoard {
  overview: string;
  summary: LearningSummaryItem[];
  concepts: LearningConceptItem[];
  practice: LearningPracticeItem[];
  review_path: LearningReviewStep[];
}

export interface AssessmentQuestionOption {
  id: string;
  text: string;
}

export interface AssessmentQuestion {
  id: string;
  type: "choice" | "blank" | "calculation";
  prompt: string;
  options: AssessmentQuestionOption[];
  answer: string;
  display_answer: string;
  acceptable_answers: string[];
  explanation: string;
  solution_steps: string[];
}

export interface AssessmentSuite {
  title: string;
  intro: string;
  questions: AssessmentQuestion[];
}

export interface DocumentDetail extends DocumentSummary {
  sections: SectionNote[];
  chats: ChatRecord[];
  sources: SourceFragment[];
  learning_board: LearningBoard;
}

export interface UploadResponse {
  document: DocumentDetail;
}

export interface MarkdownPreview {
  path: string;
  content: string;
}
