from __future__ import annotations
import sys
import os

# Fix module resolution so tasks/ and data/ are always found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Optional
import copy

from .models import Action, Observation, StepResult, EpisodeState, Reward
from .tasks.graders import GRADERS
from .data.emails import EASY_EMAILS, MEDIUM_EMAILS, HARD_EMAILS


TASK_EMAIL_MAP = {
    "task_easy": EASY_EMAILS,
    "task_medium": MEDIUM_EMAILS,
    "task_hard": HARD_EMAILS,
}

VALID_TASKS = list(TASK_EMAIL_MAP.keys())


class EmailTriageEnv:
    def __init__(self) -> None:
        self._task_id: Optional[str] = None
        self._emails: list = []
        self._email_index: int = 0
        self._scores: list = []
        self._done: bool = True
        self._step: int = 0

    def reset(self, task_id: str = "task_easy") -> Observation:
        if task_id not in VALID_TASKS:
            raise ValueError(
                f"Unknown task_id '{task_id}'. Valid options: {VALID_TASKS}"
            )
        self._task_id = task_id
        self._emails = copy.deepcopy(TASK_EMAIL_MAP[task_id])
        self._email_index = 0
        self._scores = []
        self._done = False
        self._step = 0
        return self._make_observation()

    def step(self, action: Action) -> StepResult:
        if self._done:
            raise RuntimeError("Episode is done. Call reset() before stepping again.")
        if self._task_id is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")

        current_email = self._emails[self._email_index]
        grader = GRADERS[self._task_id]
        reward: Reward = grader(action, current_email)

        self._scores.append(reward.total)
        self._email_index += 1
        self._step += 1

        done = self._email_index >= len(self._emails)
        self._done = done

        next_obs: Optional[Observation] = None
        if not done:
            next_obs = self._make_observation()

        episode_score = round(sum(self._scores) / len(self._scores), 4)

        return StepResult(
            observation=next_obs,
            reward=reward,
            done=done,
            info={
                "email_id": current_email["email_id"],
                "episode_score_so_far": episode_score,
                "emails_processed": self._email_index,
                "emails_total": len(self._emails),
                "action_taken": action.model_dump(),
                "ground_truth": {
                    "priority": current_email["priority"],
                    "department": current_email["department"],
                },
            },
        )

    def state(self) -> EpisodeState:
        return EpisodeState(
            task_id=self._task_id or "not_started",
            email_index=self._email_index,
            total_emails=len(self._emails),
            scores=list(self._scores),
            done=self._done,
            step=self._step,
        )

    def _make_observation(self) -> Observation:
        email = self._emails[self._email_index]
        current_score = (
            round(sum(self._scores) / len(self._scores), 4)
            if self._scores else 0.0
        )
        return Observation(
            email_id=email["email_id"],
            subject=email["subject"],
            sender=email["sender"],
            body=email["body"],
            timestamp=email["timestamp"],
            task_id=self._task_id,
            emails_remaining=len(self._emails) - self._email_index,
            current_score=current_score,
            step=self._step,
        )
