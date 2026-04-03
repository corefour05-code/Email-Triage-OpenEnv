from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Observation(BaseModel):
    email_id: str = Field(..., description="Unique identifier for the current email")
    subject: str = Field(..., description="Email subject line")
    sender: str = Field(..., description="Sender email address")
    body: str = Field(..., description="Full email body text")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the email")
    task_id: str = Field(..., description="Current task identifier")
    emails_remaining: int = Field(..., description="Number of emails left in this episode")
    current_score: float = Field(..., description="Running average score so far")
    step: int = Field(..., description="Current step number")


class Action(BaseModel):
    priority: Literal["URGENT", "NORMAL", "LOW"] = Field(
        ..., description="Priority level assigned to the email"
    )
    department: Literal["Sales", "Support", "Billing", "HR", "Engineering", "None"] = Field(
        ..., description="Department to route the email to"
    )
    reply: Optional[str] = Field(
        default=None,
        description="Optional short reply draft. Required for task_hard."
    )


class Reward(BaseModel):
    total: float = Field(..., description="Total reward for this step (0.0 - 1.0)")
    priority_score: float = Field(..., description="Score for priority classification")
    routing_score: float = Field(..., description="Score for department routing")
    reply_score: float = Field(..., description="Score for reply quality")
    feedback: str = Field(..., description="Human-readable explanation of the reward")


class StepResult(BaseModel):
    observation: Optional[Observation] = Field(
        None, description="Next observation. None if episode is done."
    )
    reward: Reward
    done: bool = Field(..., description="True if the episode has ended")
    info: dict = Field(default_factory=dict, description="Auxiliary diagnostic information")


class EpisodeState(BaseModel):
    task_id: str
    email_index: int
    total_emails: int
    scores: List[float]
    done: bool
    step: int
