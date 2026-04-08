from __future__ import annotations
from typing import Optional, List
from models import Action, Reward


def _score_reply(reply: Optional[str], keywords: List[str], email_body: str) -> float:
    if not reply or not reply.strip():
        return 0.0

    reply_lower = reply.lower()
    words = reply.split()
    word_count = len(words)

    if keywords:
        matched = sum(1 for kw in keywords if kw.lower() in reply_lower)
        keyword_score = min(matched / max(len(keywords), 1), 1.0) * 0.10
    else:
        keyword_score = 0.08

    negative_phrases = [
        "i can't", "not my problem", "deal with it", "too bad",
        "whatever", "i don't care", "stupid", "idiot"
    ]
    positive_phrases = [
        "thank", "apolog", "understand", "help", "assist",
        "team", "resolv", "contact", "support", "escalat", "look into"
    ]
    has_negative = any(p in reply_lower for p in negative_phrases)
    has_positive = sum(1 for p in positive_phrases if p in reply_lower)
    tone_score = 0.0 if has_negative else min(has_positive / 3, 1.0) * 0.08

    if 10 <= word_count <= 120:
        length_score = 0.07
    elif word_count < 5:
        length_score = 0.0
    else:
        length_score = 0.03

    return round(keyword_score + tone_score + length_score, 4)


def grade_easy(action: Action, ground_truth: dict) -> Reward:
    correct_priority = action.priority == ground_truth["priority"]

    if correct_priority:
        return Reward(
            total=1.0,
            priority_score=1.0,
            routing_score=0.0,
            reply_score=0.0,
            feedback=f"Correct priority ({action.priority}).",
        )
    else:
        return Reward(
            total=0.0,
            priority_score=0.0,
            routing_score=0.0,
            reply_score=0.0,
            feedback=(
                f"Wrong priority. Got '{action.priority}', "
                f"expected '{ground_truth['priority']}'."
            ),
        )


def grade_medium(action: Action, ground_truth: dict) -> Reward:
    correct_priority = action.priority == ground_truth["priority"]
    correct_dept = action.department == ground_truth["department"]

    priority_score = 0.40 if correct_priority else 0.0
    routing_score = 0.60 if correct_dept else 0.0
    total = round(priority_score + routing_score, 4)

    parts = []
    parts.append(
        f"Priority OK ({action.priority})" if correct_priority
        else f"Wrong priority: got '{action.priority}', expected '{ground_truth['priority']}'"
    )
    parts.append(
        f"Routing OK -> {action.department}" if correct_dept
        else f"Wrong routing: got '{action.department}', expected '{ground_truth['department']}'"
    )

    return Reward(
        total=total,
        priority_score=priority_score,
        routing_score=routing_score,
        reply_score=0.0,
        feedback=" | ".join(parts),
    )


def grade_hard(action: Action, ground_truth: dict) -> Reward:
    correct_priority = action.priority == ground_truth["priority"]
    correct_dept = action.department == ground_truth["department"]

    priority_score = 0.40 if correct_priority else 0.0
    routing_score = 0.35 if correct_dept else 0.0
    reply_score = _score_reply(
        action.reply,
        ground_truth.get("reply_keywords", []),
        ground_truth.get("body", ""),
    )
    total = round(priority_score + routing_score + reply_score, 4)

    parts = []
    parts.append(
        f"Priority OK ({action.priority})" if correct_priority
        else f"Wrong priority: got '{action.priority}', expected '{ground_truth['priority']}'"
    )
    parts.append(
        f"Routing OK -> {action.department}" if correct_dept
        else f"Wrong routing: got '{action.department}', expected '{ground_truth['department']}'"
    )
    reply_pct = round(reply_score / 0.25 * 100) if reply_score else 0
    parts.append(f"Reply quality: {reply_pct}% ({reply_score:.3f}/0.25)")

    return Reward(
        total=total,
        priority_score=priority_score,
        routing_score=routing_score,
        reply_score=reply_score,
        feedback=" | ".join(parts),
    )


GRADERS = {
    "task_easy": grade_easy,
    "task_medium": grade_medium,
    "task_hard": grade_hard,
}
