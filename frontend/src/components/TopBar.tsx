import type { DocumentDetail } from "../types";

type TopBarProps = {
  documentDetail: DocumentDetail | null;
  uploadInputId: string;
  uploading: boolean;
  exportHref: string | null;
};

export function TopBar(props: TopBarProps) {
  const { documentDetail, uploadInputId, uploading, exportHref } = props;

  return (
    <header className="topbar">
      <div className="brand-block">
        <div className="brand-mark" aria-hidden="true">
          研
        </div>
        <div className="brand-copy">
          <p className="brand-kicker">Courseware Review Desk</p>
          <h1>课件智能知识点复习助手</h1>
        </div>
      </div>

      <div className="topbar-meta">
        <div className="document-summary-chip">
          <span className="chip-label">当前课件</span>
          <strong>{documentDetail?.title ?? "未选择课件"}</strong>
          <small>{documentDetail?.original_filename ?? "上传后自动生成学习笔记"}</small>
        </div>
        <div className="topbar-actions">
          <label className="action-button is-primary" htmlFor={uploadInputId}>
            {uploading ? "处理中…" : "上传课件"}
          </label>
          {exportHref ? (
            <a className="action-button" href={exportHref}>
              导出 Markdown
            </a>
          ) : null}
        </div>
      </div>
    </header>
  );
}
