import type { DocumentDetail, DocumentSummary } from "../types";

type SourceRailProps = {
  documents: DocumentSummary[];
  selectedDocumentId: string | null;
  onSelectDocument: (documentId: string) => void;
  documentDetail: DocumentDetail | null;
};

export function SourceRail(props: SourceRailProps) {
  const {
    documents,
    selectedDocumentId,
    onSelectDocument,
    documentDetail,
  } = props;

  const currentDocument = documents.find((item) => item.id === selectedDocumentId) ?? null;
  const otherDocuments = documents.filter((item) => item.id !== selectedDocumentId);

  return (
    <div className="panel-shell source-rail">
      <section className="panel-block rail-header">
        <div className="panel-heading">
          <div>
            <p className="panel-label">课件与笔记</p>
            <h2>复习资料</h2>
          </div>
        </div>
        <p className="support-copy">
          上传课件后会自动生成学习笔记。这里保留当前课件、章节笔记摘要和切换入口，不再展示片段来源。
        </p>
      </section>

      <section className="panel-block rail-section">
        <div className="subhead">
          <strong>当前课件</strong>
          <span>{documents.length}</span>
        </div>
        <div className="document-stack">
          {currentDocument ? (
            <button
              type="button"
              className="document-card is-current"
              onClick={() => onSelectDocument(currentDocument.id)}
            >
              <div className="document-card-main">
                <strong>{currentDocument.title}</strong>
                <p>{currentDocument.original_filename}</p>
              </div>
              <span className={`status-badge status-${currentDocument.status}`}>
                {statusLabel(currentDocument.status)}
              </span>
            </button>
          ) : (
            <div className="empty-card compact">
              <p>还没有课件。</p>
              <span>从一份 PPTX 或 PDF 开始。</span>
            </div>
          )}

          {otherDocuments.map((item) => (
            <button
              key={item.id}
              type="button"
              className="document-row"
              onClick={() => onSelectDocument(item.id)}
            >
              <div className="document-row-main">
                <strong>{item.title}</strong>
                <p>{item.original_filename}</p>
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="panel-block rail-section rail-grow">
        <div className="subhead">
          <strong>学习笔记</strong>
          <span>{documentDetail?.learning_board.summary.length ?? 0}</span>
        </div>
        <div className="note-list">
          {documentDetail?.learning_board.summary.length ? (
            documentDetail.learning_board.summary.map((item) => (
              <article key={item.id} className="note-card">
                <span className="note-index">{item.id.replace("summary-", "第 ")}</span>
                <strong>{item.title}</strong>
                <p>{item.summary}</p>
              </article>
            ))
          ) : (
            <div className="empty-card compact">
              <p>学习笔记尚未生成。</p>
              <span>上传课件后会自动整理章节摘要。</span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function statusLabel(status: string): string {
  if (status === "ready") {
    return "已生成";
  }
  if (status === "processing") {
    return "处理中";
  }
  if (status === "failed") {
    return "失败";
  }
  return status;
}
