import { useMemo } from "react";

import type { AssessmentSuite, DocumentDetail, MarkdownPreview } from "../types";

type LearningBoardPanelProps = {
  documentDetail: DocumentDetail | null;
  completedTaskIds: Record<string, boolean>;
  completedTasks: number;
  totalTasks: number;
  progressRatio: number;
  markdownPreview: MarkdownPreview | null;
  isAssessmentUnlocked: boolean;
  assessment: AssessmentSuite | null;
  assessmentLoading: boolean;
  assessmentAnswers: Record<string, string>;
  assessmentSubmitted: boolean;
  onToggleTask: (taskId: string) => void;
  onUsePrompt: (prompt: string) => void;
  onAnswerChange: (questionId: string, value: string) => void;
  onSubmitAssessment: () => void;
  onRetryAssessment: () => void;
};

export function LearningBoardPanel(props: LearningBoardPanelProps) {
  const {
    documentDetail,
    completedTaskIds,
    completedTasks,
    totalTasks,
    progressRatio,
    markdownPreview,
    isAssessmentUnlocked,
    assessment,
    assessmentLoading,
    assessmentAnswers,
    assessmentSubmitted,
    onToggleTask,
    onUsePrompt,
    onAnswerChange,
    onSubmitAssessment,
    onRetryAssessment,
  } = props;

  const assessmentResults = useMemo(() => {
    if (!assessmentSubmitted || !assessment) {
      return null;
    }
    return assessment.questions.map((question) => {
      const rawValue = (assessmentAnswers[question.id] ?? "").trim();
      if (question.type === "choice") {
        return rawValue === question.answer;
      }
      const acceptable = [question.answer, ...question.acceptable_answers].map((item) =>
        normalizeAnswer(item),
      );
      return acceptable.includes(normalizeAnswer(rawValue));
    });
  }, [assessment, assessmentAnswers, assessmentSubmitted]);

  return (
    <div className="panel-shell learning-board">
      <section className="panel-block board-header">
        <div className="board-intro">
          <div className="board-intro-copy">
            <p className="panel-label">
              {isAssessmentUnlocked ? "测试环境" : "学习任务台"}
            </p>
            <h2>{isAssessmentUnlocked ? "Assessment Lab" : "Learning Board"}</h2>
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
            <p>上传课件后，这里会自动生成复习任务。</p>
            <span>完成任务后会自动进入测试环境。</span>
          </div>
        </section>
      ) : null}

      {documentDetail ? (
        <section className="panel-block board-scroll">
          {!isAssessmentUnlocked ? (
            <div className="board-stack">
              <article className="board-module summary-module">
                <header className="board-module-head">
                  <div>
                    <p className="module-kicker">摘要</p>
                    <h3>快速总览</h3>
                  </div>
                </header>

                <p className="overview-paragraph">{documentDetail.learning_board.overview}</p>

                {documentDetail.learning_board.summary.map((item) => (
                  <TaskCard
                    key={item.id}
                    checked={Boolean(completedTaskIds[item.id])}
                    title={item.title}
                    subtitle="摘要"
                    body={item.summary}
                    onToggle={() => onToggleTask(item.id)}
                    onAsk={() => onUsePrompt(`请根据摘要进一步解释《${item.title}》`)}
                    askLabel="围绕摘要追问"
                  />
                ))}
              </article>

              <article className="board-module concepts-module">
                <header className="board-module-head">
                  <div>
                    <p className="module-kicker">概念</p>
                    <h3>核心概念与易混点</h3>
                  </div>
                </header>

                {documentDetail.learning_board.concepts.map((item) => (
                  <TaskCard
                    key={item.id}
                    checked={Boolean(completedTaskIds[item.id])}
                    title={item.term}
                    subtitle={`概念 / ${item.section_title}`}
                    body={item.explanation}
                    onToggle={() => onToggleTask(item.id)}
                    onAsk={() => onUsePrompt(`请解释“${item.term}”在本课件中的含义`)}
                    askLabel="围绕概念追问"
                  />
                ))}
              </article>

              <article className="board-module practice-module">
                <header className="board-module-head">
                  <div>
                    <p className="module-kicker">练习</p>
                    <h3>任务式练习清单</h3>
                  </div>
                </header>

                {documentDetail.learning_board.practice.map((item) => (
                  <TaskCard
                    key={item.id}
                    checked={Boolean(completedTaskIds[item.id])}
                    title={item.prompt}
                    subtitle={`练习 / ${item.section_title}`}
                    body="先自己思考，再回到对话区请求提示或讲解。"
                    onToggle={() => onToggleTask(item.id)}
                    onAsk={() => onUsePrompt(`请给出“${item.prompt}”的解题思路`)}
                    askLabel="请求练习提示"
                  />
                ))}
              </article>

              <article className="board-module review-module">
                <header className="board-module-head">
                  <div>
                    <p className="module-kicker">复习路径</p>
                    <h3>建议推进顺序</h3>
                  </div>
                </header>

                {documentDetail.learning_board.review_path.map((item) => (
                  <TaskCard
                    key={item.id}
                    checked={Boolean(completedTaskIds[item.id])}
                    title={item.title}
                    subtitle="复习路径"
                    body={item.detail}
                    onToggle={() => onToggleTask(item.id)}
                    onAsk={() => onUsePrompt(`请根据“${item.title}”详细说明我应该怎样学习`)}
                    askLabel="继续这一步"
                  />
                ))}
              </article>

            <article className="board-module export-module">
              <header className="board-module-head">
                <div>
                  <p className="module-kicker">学习笔记</p>
                  <h3>复习记录导出</h3>
                </div>
              </header>
              <p className="export-copy">
                下载按钮统一保留在顶部工具栏。导出时会包含学习笔记、Learning Board 完成情况，以及测试环境里的答题结果和解析。
              </p>
              {markdownPreview ? (
                <pre className="markdown-preview">{markdownPreview.content}</pre>
              ) : null}
            </article>
            </div>
          ) : (
            <div className="assessment-shell">
              <article className="board-module assessment-intro">
                <header className="board-module-head">
                  <div>
                    <p className="module-kicker">测试环境</p>
                    <h3>{assessment?.title ?? "正在准备测试题目"}</h3>
                  </div>
                </header>
                <p className="overview-paragraph">
                  {assessmentLoading
                    ? "正在根据课件内容生成选择题、填空题和计算题，请稍等。"
                    : assessment?.intro ??
                      "完成学习任务后，这里会自动生成测试题帮助你检查掌握程度。"}
                </p>
              </article>

              {assessmentLoading ? (
                <div className="empty-card compact">
                  <p>测试题生成中…</p>
                </div>
              ) : null}

              {assessment ? (
                <div className="assessment-list">
                  {assessment.questions.map((question, index) => (
                    <article key={question.id} className="assessment-card">
                      <div className="assessment-head">
                        <span className="module-kicker">
                          {question.type === "choice"
                            ? "选择题"
                            : question.type === "blank"
                              ? "填空题"
                              : "计算题"}{" "}
                          · 第 {index + 1} 题
                        </span>
                        {assessmentSubmitted && assessmentResults ? (
                          <span
                            className={`status-badge ${
                              assessmentResults[index] ? "status-ready" : "status-failed"
                            }`}
                          >
                            {assessmentResults[index] ? "正确" : "错误"}
                          </span>
                        ) : null}
                      </div>

                      <strong className="assessment-prompt">{question.prompt}</strong>

                      {question.type === "choice" ? (
                        <div className="assessment-options">
                          {question.options.map((option) => (
                            <label key={option.id} className="option-row">
                              <input
                                type="radio"
                                name={question.id}
                                value={option.id}
                                checked={assessmentAnswers[question.id] === option.id}
                                onChange={(event) =>
                                  onAnswerChange(question.id, event.target.value)
                                }
                                disabled={assessmentSubmitted}
                              />
                              <span>
                                {option.id}. {option.text}
                              </span>
                            </label>
                          ))}
                        </div>
                      ) : (
                        <input
                          className="blank-input"
                          type="text"
                          value={assessmentAnswers[question.id] ?? ""}
                          onChange={(event) =>
                            onAnswerChange(question.id, event.target.value)
                          }
                          disabled={assessmentSubmitted}
                          placeholder={
                            question.type === "calculation" ? "输入计算结果" : "输入你的答案"
                          }
                        />
                      )}

                      {assessmentSubmitted ? (
                        <div className="explanation-box">
                          <p>
                            <strong>标准答案：</strong>
                            {question.display_answer || question.answer}
                          </p>
                          <strong>题目解析</strong>
                          <p>{question.explanation}</p>
                          {question.solution_steps.length ? (
                            <div className="solution-steps">
                              <strong>参考步骤</strong>
                              <ol>
                                {question.solution_steps.map((step, stepIndex) => (
                                  <li key={`${question.id}-${stepIndex}`}>{step}</li>
                                ))}
                              </ol>
                            </div>
                          ) : null}
                        </div>
                      ) : null}
                    </article>
                  ))}

                  <div className="assessment-actions">
                    {!assessmentSubmitted ? (
                      <button
                        type="button"
                        className="action-button is-primary"
                        onClick={onSubmitAssessment}
                      >
                        提交答案
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="action-button"
                        onClick={onRetryAssessment}
                      >
                        重新作答
                      </button>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}

type TaskCardProps = {
  checked: boolean;
  title: string;
  subtitle: string;
  body: string;
  onToggle: () => void;
  onAsk: () => void;
  askLabel: string;
};

function TaskCard(props: TaskCardProps) {
  const { checked, title, subtitle, body, onToggle, onAsk, askLabel } = props;

  return (
    <article className={`task-card ${checked ? "is-complete" : ""}`}>
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

function normalizeAnswer(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, "");
}
