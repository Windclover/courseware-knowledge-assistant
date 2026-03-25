import type { FormEvent } from "react";

import type {
  ChatRecord,
  ChatScope,
  DocumentDetail,
  SourceFragment,
} from "../types";

type ChatStageProps = {
  documentDetail: DocumentDetail | null;
  focusedSource: SourceFragment | null;
  introMessage: string;
  question: string;
  scope: ChatScope;
  scopeOptions: Array<{ label: string; value: ChatScope }>;
  suggestionPrompts: string[];
  chatting: boolean;
  onScopeChange: (scope: ChatScope) => void;
  onUseSuggestion: (prompt: string) => void;
  onSourceRefClick: (sourceRef: string) => void;
  onQuestionChange: (value: string) => void;
  onClearFocusedSource: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function ChatStage(props: ChatStageProps) {
  const {
    documentDetail,
    focusedSource,
    introMessage,
    question,
    scope,
    scopeOptions,
    suggestionPrompts,
    chatting,
    onScopeChange,
    onUseSuggestion,
    onSourceRefClick,
    onQuestionChange,
    onClearFocusedSource,
    onSubmit,
  } = props;

  return (
    <div className="panel-shell chat-stage">
      <section className="panel-block chat-stage-header">
        <div className="panel-heading">
          <div>
            <p className="panel-label">研究对话区</p>
            <h2>问题驱动学习</h2>
          </div>
          <div className="scope-segment" role="tablist" aria-label="问答范围">
            {scopeOptions.map((item) => (
              <button
                key={item.value}
                type="button"
                role="tab"
                aria-selected={scope === item.value}
                className={scope === item.value ? "is-active" : ""}
                onClick={() => onScopeChange(item.value)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {focusedSource ? (
          <div className="focus-strip">
            <div className="focus-copy">
              <span className="chip-label">当前来源</span>
              <strong>
                {focusedSource.source_label}
                {focusedSource.title ? ` · ${focusedSource.title}` : ""}
              </strong>
              <p>聚焦这一页，直接围绕概念、定义和例子继续追问。</p>
            </div>
            <div className="focus-actions">
              <button
                type="button"
                className="mini-text-button"
                onClick={() =>
                  onUseSuggestion(`请解释 ${focusedSource.source_label} 的重点内容`)
                }
              >
                继续追问
              </button>
              <button
                type="button"
                className="mini-text-button"
                onClick={onClearFocusedSource}
              >
                清除聚焦
              </button>
            </div>
          </div>
        ) : null}

        <div className="suggestion-row">
          {suggestionPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="suggestion-chip"
              onClick={() => onUseSuggestion(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </section>

      <section className="panel-block chat-history-block">
        <div className="chat-history">
          {documentDetail ? (
            <>
              <article className="message-card system">
                <span className="message-label">系统提示</span>
                <p>{introMessage}</p>
              </article>

              {documentDetail.chats.length === 0 ? (
                <div className="message-card user">
                  <span className="message-label">提问</span>
                  <p>这一讲里最先应该掌握哪些概念？</p>
                </div>
              ) : (
                documentDetail.chats.map((chat) => (
                  <ChatTurn
                    key={chat.id}
                    chat={chat}
                    onSourceRefClick={onSourceRefClick}
                  />
                ))
              )}
            </>
          ) : (
            <div className="empty-card large">
              <p>上传课件后，这里会成为你的主工作区。</p>
              <span>你可以围绕来源片段、概念、练习和复习路径持续追问。</span>
            </div>
          )}
        </div>
      </section>

      <section className="panel-block composer-block">
        <form className="composer" onSubmit={onSubmit}>
          <label className="visually-hidden" htmlFor="research-question">
            研究问题输入框
          </label>
          <textarea
            id="research-question"
            name="question"
            autoComplete="off"
            value={question}
            onChange={(event) => onQuestionChange(event.target.value)}
            placeholder="例如：这一部分和上一章之间的逻辑关系是什么？…"
            rows={4}
          />
          <div className="composer-footer">
            <span className="composer-hint">{scopeHint(scope)}</span>
            <button
              type="submit"
              className="action-button is-primary"
              disabled={chatting || !documentDetail}
            >
              {chatting ? "正在回答…" : "发送问题"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function ChatTurn(props: {
  chat: ChatRecord;
  onSourceRefClick: (sourceRef: string) => void;
}) {
  const { chat, onSourceRefClick } = props;

  return (
    <div className="chat-turn">
      <div className="message-card user">
        <span className="message-label">提问</span>
        <p>{chat.question}</p>
      </div>

      <article className="message-card assistant">
        <span className="message-label">回答 · {scopeLabel(chat.scope)}</span>
        <div className="assistant-copy">
          {chat.answer
            .split("\n")
            .filter(Boolean)
            .map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
        </div>

        {chat.source_refs.length ? (
          <div className="citation-row">
            {chat.source_refs.map((sourceRef, index) => (
              <button
                key={`${chat.id}-${sourceRef}`}
                type="button"
                className="citation-link"
                onClick={() => onSourceRefClick(sourceRef)}
              >
                [{index + 1}] {sourceRef}
              </button>
            ))}
          </div>
        ) : null}

        {chat.supplemental_notes ? (
          <div className="supplement-note">
            <strong>补充说明</strong>
            <p>{chat.supplemental_notes}</p>
          </div>
        ) : null}
      </article>
    </div>
  );
}

function scopeLabel(scope: ChatScope): string {
  if (scope === "raw") {
    return "原始课件";
  }
  if (scope === "notes") {
    return "生成笔记";
  }
  return "全部内容";
}

function scopeHint(scope: ChatScope): string {
  if (scope === "raw") {
    return "当前仅基于原始课件回答";
  }
  if (scope === "notes") {
    return "当前优先基于生成笔记回答";
  }
  return "当前综合原始课件与生成笔记回答";
}
