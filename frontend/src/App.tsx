import {
  type ChangeEvent,
  type FormEvent,
  startTransition,
  useEffect,
  useState,
} from "react";

import {
  fetchDocumentDetail,
  fetchDocuments,
  fetchMarkdownPreview,
  generateAssessment,
  markdownDownloadUrl,
  sendChatMessage,
  uploadDocument,
} from "./api";
import { ChatStage } from "./components/ChatStage";
import { LearningBoardPanel } from "./components/LearningBoard";
import { SourceRail } from "./components/SourceRail";
import { TopBar } from "./components/TopBar";
import type {
  AssessmentSuite,
  DocumentDetail,
  DocumentSummary,
  MarkdownPreview,
} from "./types";

type CompactPane = "notes" | "chat" | "tasks";

const compactPanes: Array<{ label: string; value: CompactPane }> = [
  { label: "笔记", value: "notes" },
  { label: "对话", value: "chat" },
  { label: "任务", value: "tasks" },
];

function App() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [documentDetail, setDocumentDetail] = useState<DocumentDetail | null>(null);
  const [markdownPreview, setMarkdownPreview] = useState<MarkdownPreview | null>(null);
  const [uploading, setUploading] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [question, setQuestion] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [compactPane, setCompactPane] = useState<CompactPane>("chat");
  const [completedTaskIds, setCompletedTaskIds] = useState<Record<string, boolean>>(
    {},
  );
  const [isMarkdownExpanded, setIsMarkdownExpanded] = useState(false);
  const [assessment, setAssessment] = useState<AssessmentSuite | null>(null);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [assessmentAnswers, setAssessmentAnswers] = useState<Record<string, string>>(
    {},
  );
  const [assessmentSubmitted, setAssessmentSubmitted] = useState(false);

  useEffect(() => {
    void refreshDocuments();
  }, []);

  const visibleDocuments = buildVisibleDocuments(documents);

  useEffect(() => {
    if (!selectedDocumentId && visibleDocuments.length > 0) {
      setSelectedDocumentId(visibleDocuments[0].id);
    }
  }, [selectedDocumentId, visibleDocuments]);

  useEffect(() => {
    if (!selectedDocumentId) {
      setDocumentDetail(null);
      setMarkdownPreview(null);
      setCompletedTaskIds({});
      setAssessment(null);
      setAssessmentAnswers({});
      setAssessmentSubmitted(false);
      return;
    }
    void loadDocument(selectedDocumentId);
  }, [selectedDocumentId]);

  const boardStats = getBoardStats(documentDetail, completedTaskIds);
  const isAssessmentUnlocked = boardStats.total > 0 && boardStats.completed >= boardStats.total;

  useEffect(() => {
    if (!documentDetail || !isAssessmentUnlocked || assessment || assessmentLoading) {
      return;
    }
    void loadAssessment(documentDetail.id);
  }, [assessment, assessmentLoading, documentDetail, isAssessmentUnlocked]);

  async function refreshDocuments() {
    try {
      const result = await fetchDocuments();
      setDocuments(result);
    } catch (error) {
      setErrorMessage((error as Error).message);
    }
  }

  async function loadDocument(documentId: string) {
    try {
      setErrorMessage(null);
      setMarkdownPreview(null);
      setCompactPane("chat");
      setIsMarkdownExpanded(false);

      const detail = await fetchDocumentDetail(documentId);
      const markdown = detail.markdown_path
        ? await fetchMarkdownPreview(documentId).catch(() => null)
        : null;

      startTransition(() => {
        setDocumentDetail(detail);
        setCompletedTaskIds({});
        setAssessment(null);
        setAssessmentAnswers({});
        setAssessmentSubmitted(false);
        setMarkdownPreview(markdown);
      });
    } catch (error) {
      setErrorMessage((error as Error).message);
    }
  }

  async function handleFilePick(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    setUploading(true);
    setErrorMessage(null);
    try {
      const response = await uploadDocument(file);
      const markdown = response.document.markdown_path
        ? await fetchMarkdownPreview(response.document.id).catch(() => null)
        : null;

      startTransition(() => {
        setDocuments((previous) => [response.document, ...previous]);
        setSelectedDocumentId(response.document.id);
        setDocumentDetail(response.document);
        setMarkdownPreview(markdown);
        setCompletedTaskIds({});
        setAssessment(null);
        setAssessmentAnswers({});
        setAssessmentSubmitted(false);
        setCompactPane("chat");
      });
    } catch (error) {
      setErrorMessage((error as Error).message);
    } finally {
      setUploading(false);
    }
  }

  async function handleChatSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!documentDetail) {
      setErrorMessage("请先上传或选择一份课件。");
      return;
    }
    if (!question.trim()) {
      setErrorMessage("请输入你想继续追问的问题。");
      return;
    }

    setChatting(true);
    setErrorMessage(null);
    try {
      const answer = await sendChatMessage(documentDetail.id, question.trim(), "all");
      startTransition(() => {
        setDocumentDetail({
          ...documentDetail,
          chats: [...documentDetail.chats, answer],
        });
        setQuestion("");
      });
    } catch (error) {
      setErrorMessage((error as Error).message);
    } finally {
      setChatting(false);
    }
  }

  async function loadAssessment(documentId: string) {
    setAssessmentLoading(true);
    try {
      const suite = await generateAssessment(documentId);
      setAssessment(suite);
      setAssessmentAnswers({});
      setAssessmentSubmitted(false);
      setCompactPane("tasks");
    } catch (error) {
      setErrorMessage((error as Error).message);
    } finally {
      setAssessmentLoading(false);
    }
  }

  function handleSelectDocument(documentId: string) {
    startTransition(() => {
      setSelectedDocumentId(documentId);
    });
  }

  function usePrompt(prompt: string) {
    startTransition(() => {
      setQuestion(prompt);
      setCompactPane("chat");
    });
  }

  function toggleTask(taskId: string) {
    setCompletedTaskIds((currentValue) => ({
      ...currentValue,
      [taskId]: !currentValue[taskId],
    }));
  }

  function updateAssessmentAnswer(questionId: string, value: string) {
    setAssessmentAnswers((currentValue) => ({
      ...currentValue,
      [questionId]: value,
    }));
  }

  function submitAssessment() {
    setAssessmentSubmitted(true);
  }

  function retryAssessment() {
    setAssessmentAnswers({});
    setAssessmentSubmitted(false);
  }

  const uploadInputId = "global-upload-input";
  const exportHref =
    documentDetail?.markdown_path && documentDetail.id
      ? markdownDownloadUrl(documentDetail.id)
      : null;

  return (
    <div className="app-shell">
      <div className="app-backdrop" aria-hidden="true" />
      <a className="skip-link" href="#main-content">
        跳到主内容
      </a>

      <input
        id={uploadInputId}
        className="visually-hidden"
        type="file"
        accept=".pptx,.pdf"
        onChange={(event) => {
          void handleFilePick(event);
        }}
      />

      <TopBar
        documentDetail={documentDetail}
        uploadInputId={uploadInputId}
        uploading={uploading}
        exportHref={exportHref}
      />

      {errorMessage ? (
        <div className="banner banner-error" aria-live="polite">
          {errorMessage}
        </div>
      ) : null}

      <div className="compact-switcher" role="tablist" aria-label="工作台分区切换">
        {compactPanes.map((item) => (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={compactPane === item.value}
            className={`compact-switch ${compactPane === item.value ? "is-active" : ""}`}
            onClick={() => setCompactPane(item.value)}
          >
            {item.label}
          </button>
        ))}
      </div>

      <main className="workspace-grid" id="main-content">
        <aside
          className={`workspace-panel notes-panel ${
            compactPane === "notes" ? "is-visible" : ""
          }`}
          aria-label="课件与学习笔记"
        >
          <SourceRail
            documents={visibleDocuments}
            selectedDocumentId={selectedDocumentId}
            onSelectDocument={handleSelectDocument}
            documentDetail={documentDetail}
            uploadInputId={uploadInputId}
            uploading={uploading}
          />
        </aside>

        <section
          className={`workspace-panel chat-panel ${
            compactPane === "chat" ? "is-visible" : ""
          }`}
          aria-label="研究对话区"
        >
          <ChatStage
            documentDetail={documentDetail}
            introMessage={buildIntroMessage(documentDetail)}
            question={question}
            suggestionPrompts={buildSuggestionPrompts(documentDetail)}
            chatting={chatting}
            onUseSuggestion={usePrompt}
            onQuestionChange={setQuestion}
            onSubmit={handleChatSubmit}
          />
        </section>

        <aside
          className={`workspace-panel tasks-panel ${
            compactPane === "tasks" ? "is-visible" : ""
          }`}
          aria-label="学习任务台与测试环境"
        >
          <LearningBoardPanel
            documentDetail={documentDetail}
            completedTaskIds={completedTaskIds}
            completedTasks={boardStats.completed}
            totalTasks={boardStats.total}
            progressRatio={boardStats.ratio}
            markdownPreview={markdownPreview}
            exportHref={exportHref}
            isMarkdownExpanded={isMarkdownExpanded}
            isAssessmentUnlocked={isAssessmentUnlocked}
            assessment={assessment}
            assessmentLoading={assessmentLoading}
            assessmentAnswers={assessmentAnswers}
            assessmentSubmitted={assessmentSubmitted}
            onToggleTask={toggleTask}
            onUsePrompt={usePrompt}
            onToggleMarkdown={() => setIsMarkdownExpanded((value) => !value)}
            onAnswerChange={updateAssessmentAnswer}
            onSubmitAssessment={submitAssessment}
            onRetryAssessment={retryAssessment}
          />
        </aside>
      </main>
    </div>
  );
}

function buildVisibleDocuments(documents: DocumentSummary[]): DocumentSummary[] {
  const seen = new Set<string>();
  const result: DocumentSummary[] = [];
  for (const item of documents) {
    const key = `${item.title}|${item.original_filename}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    result.push(item);
  }
  return result;
}

function buildSuggestionPrompts(detail: DocumentDetail | null): string[] {
  if (!detail) {
    return ["请先总结这份课件", "请告诉我应该怎样复习这份课件"];
  }
  return [
    `请先总结《${detail.title}》`,
    "请告诉我这份课件最重要的 3 个概念",
  ];
}

function buildIntroMessage(detail: DocumentDetail | null): string {
  if (!detail) {
    return "上传课件后，系统会自动生成学习笔记和学习任务台，你可以直接开始复习。";
  }
  if (detail.status === "ready") {
    return "学习笔记已经生成完成。这里的对话默认会综合课件原文和学习笔记回答，不需要再手动切换范围。";
  }
  if (detail.status === "failed") {
    return detail.error_message ?? "课件处理失败，请检查模型配置后重试。";
  }
  return "课件仍在处理中，请稍等片刻。";
}

function getBoardStats(
  detail: DocumentDetail | null,
  completedTaskIds: Record<string, boolean>,
) {
  const total = detail
    ? detail.learning_board.summary.length +
      detail.learning_board.concepts.length +
      detail.learning_board.practice.length +
      detail.learning_board.review_path.length
    : 0;
  const completed = Object.values(completedTaskIds).filter(Boolean).length;
  return { total, completed, ratio: total > 0 ? completed / total : 0 };
}

function readInitialUiState(): {
  documentId: string | null;
  pane: CompactPane;
} {
  if (typeof window === "undefined") {
    return { documentId: null, pane: "chat" };
  }
  const params = new URLSearchParams(window.location.search);
  const pane = params.get("pane");
  return {
    documentId: params.get("doc"),
    pane: pane === "notes" || pane === "tasks" ? pane : "chat",
  };
}

export default App;
