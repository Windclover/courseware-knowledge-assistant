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
  markdownDownloadUrl,
  sendChatMessage,
  uploadDocument,
} from "./api";
import { ChatStage } from "./components/ChatStage";
import { LearningBoardPanel } from "./components/LearningBoard";
import { SourceRail } from "./components/SourceRail";
import { TopBar } from "./components/TopBar";
import { sourceCardId } from "./ui";
import type {
  ChatScope,
  DocumentDetail,
  DocumentSummary,
  MarkdownPreview,
  SourceFragment,
} from "./types";

type CompactPane = "sources" | "chat" | "tasks";

const scopeOptions: Array<{ label: string; value: ChatScope }> = [
  { label: "原始课件", value: "raw" },
  { label: "生成笔记", value: "notes" },
  { label: "全部内容", value: "all" },
];

const compactPanes: Array<{ label: string; value: CompactPane }> = [
  { label: "资料", value: "sources" },
  { label: "对话", value: "chat" },
  { label: "任务", value: "tasks" },
];

function App() {
  const [initialUiState] = useState(readInitialUiState);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    initialUiState.documentId,
  );
  const [documentDetail, setDocumentDetail] = useState<DocumentDetail | null>(null);
  const [markdownPreview, setMarkdownPreview] = useState<MarkdownPreview | null>(null);
  const [uploading, setUploading] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [scope, setScope] = useState<ChatScope>(initialUiState.scope);
  const [question, setQuestion] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [compactPane, setCompactPane] = useState<CompactPane>(initialUiState.pane);
  const [focusedSourceId, setFocusedSourceId] = useState<number | null>(null);
  const [completedTaskIds, setCompletedTaskIds] = useState<Record<string, boolean>>(
    {},
  );
  const [isMarkdownExpanded, setIsMarkdownExpanded] = useState(false);

  useEffect(() => {
    void refreshDocuments();
  }, []);

  const visibleDocuments = buildVisibleDocuments(documents);

  useEffect(() => {
    if (visibleDocuments.length === 0) {
      return;
    }
    if (
      !selectedDocumentId ||
      !visibleDocuments.some((document) => document.id === selectedDocumentId)
    ) {
      startTransition(() => {
        setSelectedDocumentId(visibleDocuments[0].id);
      });
    }
  }, [selectedDocumentId, visibleDocuments]);

  useEffect(() => {
    if (!selectedDocumentId) {
      setDocumentDetail(null);
      setMarkdownPreview(null);
      setFocusedSourceId(null);
      setCompletedTaskIds({});
      return;
    }
    void loadDocument(selectedDocumentId);
  }, [selectedDocumentId]);

  useEffect(() => {
    writeUiStateToUrl({
      documentId: selectedDocumentId,
      pane: compactPane,
      scope,
    });
  }, [compactPane, scope, selectedDocumentId]);

  const focusedSource = getFocusedSource(documentDetail, focusedSourceId);
  const suggestionPrompts = buildSuggestionPrompts(documentDetail, focusedSource);
  const introMessage = buildIntroMessage(documentDetail);
  const boardStats = getBoardStats(documentDetail, completedTaskIds);
  const exportHref =
    documentDetail?.markdown_path && documentDetail.id
      ? markdownDownloadUrl(documentDetail.id)
      : null;

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
        setFocusedSourceId(detail.sources[0]?.fragment_index ?? null);
        setCompletedTaskIds({});
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
        setFocusedSourceId(response.document.sources[0]?.fragment_index ?? null);
        setCompletedTaskIds({});
        setIsMarkdownExpanded(false);
        setMarkdownPreview(markdown);
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
      const answer = await sendChatMessage(documentDetail.id, question.trim(), scope);
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

  function focusSourceByRef(sourceRef: string) {
    const source = findSourceByReference(documentDetail, sourceRef);
    if (!source) {
      return;
    }
    startTransition(() => {
      setFocusedSourceId(source.fragment_index);
      setCompactPane("sources");
    });

    requestAnimationFrame(() => {
      document
        .getElementById(sourceCardId(source.fragment_index))
        ?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function handleSelectDocument(documentId: string) {
    startTransition(() => {
      setSelectedDocumentId(documentId);
    });
  }

  function handleSelectSource(source: SourceFragment) {
    startTransition(() => {
      setFocusedSourceId(source.fragment_index);
      setCompactPane("chat");
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

  const uploadInputId = "global-upload-input";

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
          className={`workspace-panel sources-panel ${
            compactPane === "sources" ? "is-visible" : ""
          }`}
          aria-label="课件资料架"
        >
          <SourceRail
            documents={visibleDocuments}
            selectedDocumentId={selectedDocumentId}
            onSelectDocument={handleSelectDocument}
            documentDetail={documentDetail}
            focusedSourceId={focusedSourceId}
            onSelectSource={handleSelectSource}
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
            focusedSource={focusedSource}
            introMessage={introMessage}
            question={question}
            scope={scope}
            scopeOptions={scopeOptions}
            suggestionPrompts={suggestionPrompts}
            chatting={chatting}
            onScopeChange={setScope}
            onUseSuggestion={usePrompt}
            onSourceRefClick={focusSourceByRef}
            onQuestionChange={setQuestion}
            onClearFocusedSource={() => setFocusedSourceId(null)}
            onSubmit={handleChatSubmit}
          />
        </section>

        <aside
          className={`workspace-panel tasks-panel ${
            compactPane === "tasks" ? "is-visible" : ""
          }`}
          aria-label="学习任务台"
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
            onToggleTask={toggleTask}
            onUsePrompt={usePrompt}
            onSourceRefClick={focusSourceByRef}
            onToggleMarkdown={() => setIsMarkdownExpanded((value) => !value)}
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

function buildSuggestionPrompts(
  detail: DocumentDetail | null,
  focusedSource: SourceFragment | null,
): string[] {
  if (!detail) {
    return ["请先总结这份课件", "请生成 3 个复习问题"];
  }

  return [
    focusedSource
      ? `请解释 ${focusedSource.source_label} 的重点内容`
      : `请先总结《${detail.title}》`,
    detail.learning_board.practice[0]
      ? `请给出“${detail.learning_board.practice[0].prompt}”的解题思路`
      : "请生成 3 个复习问题",
  ];
}

function buildIntroMessage(detail: DocumentDetail | null): string {
  if (!detail) {
    return "上传课件后，这里会成为你的主工作区。";
  }
  if (detail.status === "ready") {
    return `已完成解析。你可以先提问，再回到来源片段或学习任务台继续推进理解。`;
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
    ? detail.learning_board.concepts.length +
      detail.learning_board.practice.length +
      detail.learning_board.review_path.length
    : 0;
  const completed = Object.values(completedTaskIds).filter(Boolean).length;
  return { total, completed, ratio: total > 0 ? completed / total : 0 };
}

function getFocusedSource(
  detail: DocumentDetail | null,
  focusedSourceId: number | null,
): SourceFragment | null {
  if (!detail || focusedSourceId === null) {
    return null;
  }
  return detail.sources.find((source) => source.fragment_index === focusedSourceId) ?? null;
}

function findSourceByReference(
  detail: DocumentDetail | null,
  sourceRef: string,
): SourceFragment | null {
  if (!detail) {
    return null;
  }

  const candidates = [sourceRef, ...sourceRef.split(/[、，,]/).map((item) => item.trim())]
    .map((item) => item.trim())
    .filter(Boolean);

  for (const candidate of candidates) {
    const exact = detail.sources.find((source) => source.source_label === candidate);
    if (exact) {
      return exact;
    }
  }

  for (const candidate of candidates) {
    const partial = detail.sources.find(
      (source) =>
        candidate.includes(source.source_label) || source.source_label.includes(candidate),
    );
    if (partial) {
      return partial;
    }
  }

  return null;
}

function readInitialUiState(): {
  documentId: string | null;
  pane: CompactPane;
  scope: ChatScope;
} {
  if (typeof window === "undefined") {
    return { documentId: null, pane: "chat", scope: "all" };
  }
  const params = new URLSearchParams(window.location.search);
  const pane = params.get("pane");
  const scope = params.get("scope");
  return {
    documentId: params.get("doc"),
    pane: pane === "sources" || pane === "tasks" ? pane : "chat",
    scope: scope === "raw" || scope === "notes" ? scope : "all",
  };
}

function writeUiStateToUrl(state: {
  documentId: string | null;
  pane: CompactPane;
  scope: ChatScope;
}) {
  if (typeof window === "undefined") {
    return;
  }
  const params = new URLSearchParams(window.location.search);
  if (state.documentId) {
    params.set("doc", state.documentId);
  } else {
    params.delete("doc");
  }
  params.set("pane", state.pane);
  params.set("scope", state.scope);
  window.history.replaceState({}, "", `${window.location.pathname}?${params.toString()}`);
}

export default App;
