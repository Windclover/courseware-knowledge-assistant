import type { DocumentDetail, DocumentSummary, SourceFragment } from "../types";
import { sourceCardId } from "../ui";

type SourceRailProps = {
  documents: DocumentSummary[];
  selectedDocumentId: string | null;
  onSelectDocument: (documentId: string) => void;
  documentDetail: DocumentDetail | null;
  focusedSourceId: number | null;
  onSelectSource: (source: SourceFragment) => void;
  uploadInputId: string;
  uploading: boolean;
};

export function SourceRail(props: SourceRailProps) {
  const {
    documents,
    selectedDocumentId,
    onSelectDocument,
    documentDetail,
    focusedSourceId,
    onSelectSource,
    uploadInputId,
    uploading,
  } = props;

  const currentDocument = documents.find((item) => item.id === selectedDocumentId) ?? null;
  const otherDocuments = documents.filter((item) => item.id !== selectedDocumentId);

  return (
    <div className="panel-shell source-rail">
      <section className="panel-block rail-header">
        <div className="panel-heading">
          <div>
            <p className="panel-label">资料架</p>
            <h2>来源与课件</h2>
          </div>
          <label className="mini-action" htmlFor={uploadInputId}>
            {uploading ? "处理中" : "上传"}
          </label>
        </div>
        <p className="support-copy">
          把原始课件、来源片段和页码依据收纳在一起。点击任何片段，中央对话区和右侧学习任务台会同步聚焦。
        </p>
      </section>

      <section className="panel-block rail-section">
        <div className="subhead">
          <strong>课件列表</strong>
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
          ) : null}

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
              <span className={`status-badge compact status-${item.status}`}>
                {statusLabel(item.status)}
              </span>
            </button>
          ))}

          {documents.length === 0 ? (
            <div className="empty-card compact">
              <p>还没有课件。</p>
              <span>从一份 PPTX 或 PDF 开始。</span>
            </div>
          ) : null}
        </div>
      </section>

      <section className="panel-block rail-section rail-grow">
        <div className="subhead">
          <strong>来源片段</strong>
          <span>{documentDetail?.sources.length ?? 0}</span>
        </div>
        <div className="source-list">
          {documentDetail?.sources.length ? (
            documentDetail.sources.map((source) => (
              <button
                id={sourceCardId(source.fragment_index)}
                key={source.fragment_index}
                type="button"
                className={`source-card ${
                  focusedSourceId === source.fragment_index ? "is-active" : ""
                }`}
                onClick={() => onSelectSource(source)}
              >
                <div className="source-index">
                  {String(source.fragment_index).padStart(2, "0")}
                </div>
                <div className="source-card-body">
                  <div className="source-card-head">
                    <span>{source.source_label}</span>
                    <small>{source.source_type === "slide" ? "PPT" : "PDF"}</small>
                  </div>
                  <strong>{source.title || "未命名片段"}</strong>
                  <p>{source.preview_text}</p>
                </div>
              </button>
            ))
          ) : (
            <div className="empty-card compact">
              <p>暂无来源片段。</p>
              <span>上传完成后会在这里展示每页摘要。</span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function statusLabel(status: string): string {
  if (status === "ready") {
    return "进行中";
  }
  if (status === "processing") {
    return "处理中";
  }
  if (status === "failed") {
    return "失败";
  }
  return status;
}
