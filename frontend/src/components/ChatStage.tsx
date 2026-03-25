import type { FormEvent } from "react";

import type { ChatRecord, DocumentDetail } from "../types";

type ChatStageProps = {
  documentDetail: DocumentDetail | null;
  introMessage: string;
  question: string;
  suggestionPrompts: string[];
  chatting: boolean;
  onUseSuggestion: (prompt: string) => void;
  onQuestionChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function ChatStage(props: ChatStageProps) {
  const {
    documentDetail,
    introMessage,
    question,
    suggestionPrompts,
    chatting,
    onUseSuggestion,
    onQuestionChange,
    onSubmit,
  } = props;

  return (
    <div className="panel-shell chat-stage">
      <section className="panel-block chat-stage-header">
        <div className="panel-heading">
          <div>
            <p className="panel-label">研究对话区</p>
            <h2>围绕学习笔记继续提问</h2>
          </div>
        </div>

        <div className="chat-helper">
          <p>{introMessage}</p>
        </div>

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
            documentDetail.chats.length === 0 ? (
              <div className="empty-card large">
                <p>学习笔记已经生成，可以直接开始提问。</p>
                <span>例如：这份课件最先应该掌握哪些概念？</span>
              </div>
            ) : (
              documentDetail.chats.map((chat) => <ChatTurn key={chat.id} chat={chat} />)
            )
          ) : (
            <div className="empty-card large">
              <p>上传课件后，这里会成为你的主复习区。</p>
              <span>系统会自动整理学习笔记，你只需要围绕内容继续提问。</span>
            </div>
          )}
        </div>
      </section>

      <section className="panel-block composer-block">
        <form className="composer" onSubmit={onSubmit}>
          <label className="visually-hidden" htmlFor="review-question">
            复习问题输入框
          </label>
          <textarea
            id="review-question"
            name="question"
            autoComplete="off"
            value={question}
            onChange={(event) => onQuestionChange(event.target.value)}
            placeholder="例如：这一讲里最先应该掌握哪些概念？"
            rows={4}
          />
          <div className="composer-footer">
            <span className="composer-hint">
              当前默认基于课件原文 + 学习笔记一起回答
            </span>
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

function ChatTurn(props: { chat: ChatRecord }) {
  const { chat } = props;

  return (
    <div className="chat-turn">
      <div className="message-card user">
        <span className="message-label">提问</span>
        <p>{chat.question}</p>
      </div>

      <article className="message-card assistant">
        <span className="message-label">回答</span>
        <div className="assistant-copy">
          {chat.answer
            .split("\n")
            .filter(Boolean)
            .map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
        </div>

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
