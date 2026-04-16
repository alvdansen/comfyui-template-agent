"""Intent catalog loader and matcher for /comfy-onboard.

Loads data/onboarding_starters.json and matches a user's natural-language
goal to a starter template. Intentionally dumb — the agent harness (Claude)
does the final judgment. This module only surfaces candidates.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable


CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "onboarding_starters.json"

_WORD_SPLIT_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Starter:
    id: str
    starter_template: str
    why: str
    first_output_expectation: str
    goal_phrases: tuple[str, ...]
    next_hops: tuple[str, ...]
    required_nodes: tuple[str, ...]
    tags: tuple[str, ...]

    def summary(self) -> str:
        hops = "\n    - ".join(self.next_hops) if self.next_hops else "—"
        return (
            f"{self.id}\n"
            f"  template: {self.starter_template}\n"
            f"  why: {self.why}\n"
            f"  first output: {self.first_output_expectation}\n"
            f"  next hops:\n    - {hops}"
        )


@dataclass(frozen=True)
class Match:
    starter: Starter
    score: float
    reason: str


@lru_cache(maxsize=1)
def load_catalog(path: Path | None = None) -> tuple[Starter, ...]:
    p = path or CATALOG_PATH
    raw = json.loads(p.read_text())
    return tuple(
        Starter(
            id=i["id"],
            starter_template=i["starter_template"],
            why=i["why"],
            first_output_expectation=i["first_output_expectation"],
            goal_phrases=tuple(i.get("goal_phrases", [])),
            next_hops=tuple(i.get("next_hops", [])),
            required_nodes=tuple(i.get("required_nodes", [])),
            tags=tuple(i.get("tags", [])),
        )
        for i in raw["intents"]
    )


def load_fallback(path: Path | None = None) -> dict:
    p = path or CATALOG_PATH
    return json.loads(p.read_text()).get("fallback", {})


def _tokens(text: str) -> set[str]:
    return {t for t in _WORD_SPLIT_RE.split(text.lower()) if t}


def _phrase_hit(goal: str, phrase: str) -> bool:
    return phrase.lower() in goal.lower()


def match_goal(goal: str, starters: Iterable[Starter] | None = None) -> list[Match]:
    """Return ranked candidate starters for a user goal.

    Scoring:
        +10 for any exact phrase match on goal_phrases
        + token overlap count between goal and (phrases + tags + template name)

    Returns the full ranked list so the harness can decide whether to ask
    the user to disambiguate or show the fallback.
    """

    pool = tuple(starters) if starters is not None else load_catalog()
    goal_tokens = _tokens(goal)
    if not goal_tokens:
        return []

    out: list[Match] = []
    for s in pool:
        score = 0.0
        reasons: list[str] = []

        for phrase in s.goal_phrases:
            if _phrase_hit(goal, phrase):
                score += 10
                reasons.append(f"phrase:'{phrase}'")
                break

        searchable = " ".join(
            (
                *s.goal_phrases,
                *s.tags,
                s.starter_template.replace("-", " "),
                s.why,
            )
        )
        overlap = goal_tokens & _tokens(searchable)
        if overlap:
            score += len(overlap)
            reasons.append(f"tokens:{sorted(overlap)}")

        if score > 0:
            out.append(Match(starter=s, score=score, reason=", ".join(reasons)))

    out.sort(key=lambda m: m.score, reverse=True)
    return out


def best_match(goal: str) -> Match | None:
    matches = match_goal(goal)
    if not matches:
        return None
    if len(matches) >= 2 and matches[0].score == matches[1].score:
        return None
    return matches[0]


def _format_matches(goal: str, matches: list[Match]) -> str:
    if not matches:
        fb = load_fallback()
        lines = ["no strong match — showing fallback", "", fb.get("message", "")]
        for starter_id in fb.get("list_ids", []):
            lines.append(f"  - {starter_id}")
        return "\n".join(lines)

    lines = [f"matches for: {goal!r}"]
    for i, m in enumerate(matches, 1):
        lines.append(
            f"{i}. {m.starter.id}  (score={m.score:.0f}, {m.reason})"
        )
        lines.append(f"   template: {m.starter.starter_template}")
        lines.append(f"   why: {m.starter.why}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Match a goal to starter templates")
    parser.add_argument("--goal", required=True, help="User goal in natural language")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Max matches to return (default 3)",
    )
    args = parser.parse_args(argv)

    matches = match_goal(args.goal)[: args.top]
    if args.json:
        print(
            json.dumps(
                {
                    "goal": args.goal,
                    "matches": [
                        {
                            "id": m.starter.id,
                            "template": m.starter.starter_template,
                            "score": m.score,
                            "reason": m.reason,
                            "why": m.starter.why,
                            "first_output": m.starter.first_output_expectation,
                            "next_hops": list(m.starter.next_hops),
                            "required_nodes": list(m.starter.required_nodes),
                            "tags": list(m.starter.tags),
                        }
                        for m in matches
                    ],
                },
                indent=2,
            )
        )
    else:
        print(_format_matches(args.goal, matches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
