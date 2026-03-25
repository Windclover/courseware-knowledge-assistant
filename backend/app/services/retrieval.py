from __future__ import annotations

from collections import Counter
import re

from ..domain import RetrievalHit


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+")


def rank_fragments(
    question: str,
    records: list[dict[str, str | int | None]],
    *,
    limit: int,
) -> list[RetrievalHit]:
    query_counter = Counter(_tokenize(question))
    hits: list[RetrievalHit] = []
    for record in records:
        content = str(record.get("text_content") or record.get("content") or "")
        title = str(record.get("title") or "")
        source_label = str(record.get("source_label") or "")
        if not content:
            continue
        score = _score_text(query_counter, f"{title}\n{content}")
        if title and any(token in title for token in query_counter):
            score += 1.5
        if score <= 0:
            continue
        hits.append(
            RetrievalHit(
                source_label=source_label,
                title=title or source_label,
                content=content,
                score=score,
            )
        )
    hits.sort(key=lambda item: item.score, reverse=True)
    return hits[:limit]


def build_context_blocks(hits: list[RetrievalHit]) -> list[str]:
    blocks: list[str] = []
    for hit in hits:
        blocks.append(
            "\n".join(
                [
                    f"来源：{hit.source_label}",
                    f"标题：{hit.title}",
                    hit.content[:1800],
                ]
            )
        )
    return blocks


def _score_text(query_counter: Counter[str], text: str) -> float:
    text_counter = Counter(_tokenize(text))
    score = 0.0
    for token, count in query_counter.items():
        score += min(count, text_counter.get(token, 0))
    return score


def _tokenize(text: str) -> list[str]:
    base_tokens = TOKEN_PATTERN.findall(text.lower())
    tokens: list[str] = []
    for token in base_tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(token)
            if len(token) > 1:
                tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
        else:
            tokens.append(token)
    return tokens
