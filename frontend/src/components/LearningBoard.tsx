import type { DocumentDetail, MarkdownPreview } from "../types";

type LearningBoardPanelProps = {
  documentDetail: DocumentDetail | null;
  completedTaskIds: Record<string, boolean>;
  completedTasks: number;
  totalTasks: number;
  progressRatio: number;
  markdownPreview: MarkdownPreview | null;
  exportHref: string | null;
  isMarkdownExpanded: boolean;
  onToggleTask: (taskId: string) => void;
  onUsePrompt: (prompt: string) => void;
  onSourceRefClick: (sourceRef: string) => void;
  onToggleMarkdown: () => void;
};

export function LearningBoardPanel(props: LearningBoardPanelProps) {
  const {
    documentDetail,
    completedTaskIds,
    completedTasks,
    totalTasks,
    progressRatio,
    markdownPreview,
    exportHref,
    isMarkdownExpanded,
    onToggleTask,
    onUsePrompt,
    onSourceRefClick,
    onToggleMarkdown,
  } = props;

  return (
    <div className="panel-shell learning-board">
      <section className="panel-block board-header">
        <div className="board-intro">
          <div className="board-intro-copy">
            <p className="panel-label">学习任务台</p>
            <h2>Learning Board</h2>
          </div>
          <div className="progress-stat">
            <strong>{completedTasks}</strong>
            <span>/ {totalTasks || 0} 已完成</span>
          </div>
        </div>
        <div
          className="progress-rail"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={totalTasks || 1}
          aria-valuenow={completedTasks}
          aria-label="学习任务完成进度"
        >
          <span style={{ width: `${Math.round(progressRatio * 100)}%` }} />
        </div>
      </section>

      {!documentDetail ? (
        <section className="panel-block board-scroll">
          <div className="empty-card large">
            <p>上传课件后，这里会自动生成学习任务。</p>
            <span>摘要、概念、练习和复习路径都会按顺序出现。</span>
          </div>
        </section>
      ) : null}

      {documentDetail ? (
        <section className="panel-block board-scroll">
          <div className="board-stack">
            <article className="board-module summary-module">
              <header className="board-module-head">
                <div>
                  <p className="module-kicker">摘要</p>
                  <h3>快速总览</h3>
                </div>
              </header>

              <p className="overview-paragraph">{documentDetail.learning_board.overview}</p>

              {documentDetail.learning_board.summary[0] ? (
                <div className="summary-item">
                  <div className="summary-item-head">
                    <strong>{documentDetail.learning_board.summary[0].title}</strong>
                    <span className="summary-page-pill">第 1 部分</span>
                  </div>
                  <p className="summary-item-copy">
                    {documentDetail.learning_board.summary[0].summary}
                  </p>
                  <div className="citation-row compact">
                    {documentDetail.learning_board.summary[0].source_refs.map((sourceRef) => (
                      <button
                        key={`summary-${sourceRef}`}
                        type="button"
                        className="citation-link"
                        onClick={() => onSourceRefClick(sourceRef)}
                      >
                        {sourceRef}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </article>

            {documentDetail.learning_board.concepts[0] ? (
              <TaskCard
                variant="concept"
                checked={Boolean(completedTaskIds[documentDetail.learning_board.concepts[0].id])}
                title={documentDetail.learning_board.concepts[0].term}
                subtitle={`概念 / ${documentDetail.learning_board.concepts[0].section_title}`}
                body={documentDetail.learning_board.concepts[0].explanation}
                sourceRefs={documentDetail.learning_board.concepts[0].source_refs}
                onToggle={() => onToggleTask(documentDetail.learning_board.concepts[0].id)}
                onSourceRefClick={onSourceRefClick}
                onAsk={() =>
                  onUsePrompt(
                    `请解释“${documentDetail.learning_board.concepts[0].term}”在本课件中的含义`,
                  )
                }
                askLabel="围绕概念追问"
              />
            ) : null}

            {documentDetail.learning_board.practice[0] ? (
              <TaskCard
                variant="practice"
                checked={Boolean(completedTaskIds[documentDetail.learning_board.practice[0].id])}
                title={documentDetail.learning_board.practice[0].prompt}
                subtitle={`练习 / ${documentDetail.learning_board.practice[0].section_title}`}
                body="先独立作答，再回到对话区请求解题思路。"
                sourceRefs={documentDetail.learning_board.practice[0].source_refs}
                onToggle={() => onToggleTask(documentDetail.learning_board.practice[0].id)}
                onSourceRefClick={onSourceRefClick}
                onAsk={() =>
                  onUsePrompt(
                    `请给出“${documentDetail.learning_board.practice[0].prompt}”的解题思路`,
                  )
                }
                askLabel="请求解题思路"
              />
            ) : null}

            {documentDetail.learning_board.review_path[0] ? (
              <TaskCard
                variant="review"
                checked={Boolean(completedTaskIds[documentDetail.learning_board.review_path[0].id])}
                title={documentDetail.learning_board.review_path[0].title}
                subtitle="复习路径"
                body={documentDetail.learning_board.review_path[0].detail}
                sourceRefs={documentDetail.learning_board.review_path[0].source_refs}
                onToggle={() => onToggleTask(documentDetail.learning_board.review_path[0].id)}
                onSourceRefClick={onSourceRefClick}
                onAsk={() =>
                  onUsePrompt(
                    `请根据“${documentDetail.learning_board.review_path[0].title}”详细说明我应该怎样学习`,
                  )
                }
                askLabel="继续这一步"
              />
            ) : null}

            <article className="board-module export-module">
              <header className="board-module-head">
                <div>
                  <p className="module-kicker">导出</p>
                  <h3>Markdown 仍保留为次级能力</h3>
                </div>
              </header>
              <p className="export-copy">
                学习优先，导出退后。需要时再下载工作笔记，不让导出打断主要学习流程。
              </p>
              <div className="export-actions">
                {exportHref ? (
                  <a className="action-button export-primary" href={exportHref}>
                    下载 Markdown
                  </a>
                ) : null}
                {markdownPreview ? (
                  <button
                    type="button"
                    className="action-button export-secondary"
                    onClick={onToggleMarkdown}
                  >
                    {isMarkdownExpanded ? "收起预览" : "展开预览"}
                  </button>
                ) : null}
              </div>
              {isMarkdownExpanded && markdownPreview ? (
                <pre className="markdown-preview">{markdownPreview.content}</pre>
              ) : null}
            </article>
          </div>
        </section>
      ) : null}
    </div>
  );
}

type TaskCardProps = {
  variant: "concept" | "practice" | "review";
  checked: boolean;
  title: string;
  subtitle: string;
  body: string;
  sourceRefs: string[];
  onToggle: () => void;
  onSourceRefClick: (sourceRef: string) => void;
  onAsk: () => void;
  askLabel: string;
};

function TaskCard(props: TaskCardProps) {
  const {
    variant,
    checked,
    title,
    subtitle,
    body,
    sourceRefs,
    onToggle,
    onSourceRefClick,
    onAsk,
    askLabel,
  } = props;

  return (
    <article className={`task-card ${checked ? "is-complete" : ""} is-${variant}`}>
      <div className="task-card-main">
        <button
          type="button"
          className={`task-check ${checked ? "is-complete" : ""}`}
          aria-pressed={checked}
          onClick={onToggle}
        >
          <span />
        </button>

        <div className="task-copy">
          <span className="task-subtitle">{subtitle}</span>
          <strong>{title}</strong>
          <p>{body}</p>

          {sourceRefs.length ? (
            <div className="citation-row compact">
              {sourceRefs.map((sourceRef) => (
                <button
                  key={`${title}-${sourceRef}`}
                  type="button"
                  className="citation-link"
                  onClick={() => onSourceRefClick(sourceRef)}
                >
                  {sourceRef}
                </button>
              ))}
            </div>
          ) : null}

          <div className="task-card-footer">
            <button type="button" className="mini-text-button" onClick={onAsk}>
              {askLabel}
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
