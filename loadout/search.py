"""Search query parsing and action ranking."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

from loadout.models import Action

_TAG_RE = re.compile(r"(?:tag:|#)([a-zA-Z0-9_-]+)")
_TOOL_RE = re.compile(r"tool:([a-zA-Z0-9_.-]+)")


@dataclass(frozen=True, slots=True)
class SearchQuery:
    """Parsed search input."""

    text: str
    tag: str | None = None
    tool: str | None = None


@dataclass(frozen=True, slots=True)
class RankedAction:
    """Action with relevance score."""

    action: Action
    score: int


def parse_search_query(raw: str) -> SearchQuery:
    """Extract tag:/#tag and tool: filters; remainder is fuzzy text."""
    tag: str | None = None
    tool: str | None = None
    text = raw.strip()

    tag_match = _TAG_RE.search(text)
    if tag_match:
        tag = tag_match.group(1).lower()
        text = _TAG_RE.sub("", text).strip()

    tool_match = _TOOL_RE.search(text)
    if tool_match:
        tool = tool_match.group(1).lower()
        text = _TOOL_RE.sub("", text).strip()

    return SearchQuery(text=text.lower(), tag=tag, tool=tool)


def score_action(action: Action, query_text: str) -> int:
    """Rank an action; higher is better. Tool/title weighted above tags/cmd/desc."""
    if not query_text:
        return 100

    tool_score = fuzz.partial_ratio(query_text, action.tool.lower())
    title_score = fuzz.partial_ratio(query_text, action.title.lower())
    tag_score = max(
        (fuzz.partial_ratio(query_text, tag.lower()) for tag in action.tags),
        default=0,
    )
    cmd_score = fuzz.partial_ratio(query_text, action.command.lower())
    desc_score = fuzz.partial_ratio(query_text, action.desc.lower())
    blob_score = fuzz.token_set_ratio(query_text, action.search_text)

    weighted = max(
        int(tool_score * 1.2),
        int(title_score * 1.2),
        int(tag_score * 1.0),
        int(cmd_score * 0.85),
        int(desc_score * 0.85),
        blob_score,
    )
    return min(weighted, 100)


def rank_actions(
    actions: list[Action],
    query: SearchQuery,
    *,
    limit: int = 100,
    min_score: int = 40,
) -> list[RankedAction]:
    """Filter by tag/tool and rank by fuzzy text."""
    pool = actions

    if query.tag:
        pool = [a for a in pool if query.tag in {t.lower() for t in a.tags}]

    if query.tool:
        pool = [a for a in pool if a.tool.lower() == query.tool]

    ranked: list[RankedAction] = []
    for action in pool:
        score = score_action(action, query.text)
        if query.text and score < min_score:
            continue
        ranked.append(RankedAction(action=action, score=score))

    ranked.sort(key=lambda r: (-r.score, r.action.tool, r.action.title))
    return ranked[:limit]
