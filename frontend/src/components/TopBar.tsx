type TopBarProps = {
  uploadInputId: string;
  uploading: boolean;
  canExport: boolean;
  onExport: () => void;
};

export function TopBar(props: TopBarProps) {
  const { uploadInputId, uploading, canExport, onExport } = props;

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
        <div className="topbar-actions">
          <label className="action-button is-primary" htmlFor={uploadInputId}>
            {uploading ? "处理中…" : "上传课件"}
          </label>
          <button
            type="button"
            className="action-button"
            disabled={!canExport}
            onClick={onExport}
          >
            导出复习记录
          </button>
        </div>
      </div>
    </header>
  );
}
