import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from env import EmailTriageEnv
from models import Action, Reward
from tasks.graders import grade_easy, grade_medium, grade_hard, _score_reply

URGENT_EMAIL = {
    "email_id": "TEST001",
    "subject": "PRODUCTION DOWN",
    "sender": "ops@test.com",
    "body": "Everything is broken. Fix it NOW.",
    "timestamp": "2024-01-01T00:00:00Z",
    "priority": "URGENT",
    "department": "Engineering",
    "reply_keywords": ["escalate", "engineer", "investigating"],
}

LOW_EMAIL = {
    "email_id": "TEST002",
    "subject": "Holiday feedback",
    "sender": "staff@company.com",
    "body": "Great party!",
    "timestamp": "2024-01-01T12:00:00Z",
    "priority": "LOW",
    "department": "HR",
    "reply_keywords": ["thank", "noted"],
}


@pytest.fixture
def env():
    return EmailTriageEnv()


class TestEasyGrader:
    def test_correct_priority(self):
        action = Action(priority="URGENT", department="None")
        reward = grade_easy(action, URGENT_EMAIL)
        assert reward.total == 1.0

    def test_wrong_priority(self):
        action = Action(priority="LOW", department="None")
        reward = grade_easy(action, URGENT_EMAIL)
        assert reward.total == 0.0


class TestMediumGrader:
    def test_both_correct(self):
        action = Action(priority="URGENT", department="Engineering")
        reward = grade_medium(action, URGENT_EMAIL)
        assert reward.total == 1.0

    def test_only_priority(self):
        action = Action(priority="URGENT", department="Sales")
        reward = grade_medium(action, URGENT_EMAIL)
        assert abs(reward.total - 0.40) < 0.001

    def test_only_routing(self):
        action = Action(priority="LOW", department="Engineering")
        reward = grade_medium(action, URGENT_EMAIL)
        assert abs(reward.total - 0.60) < 0.001

    def test_both_wrong(self):
        action = Action(priority="LOW", department="Sales")
        reward = grade_medium(action, URGENT_EMAIL)
        assert reward.total == 0.0


class TestHardGrader:
    def test_all_correct_good_reply(self):
        action = Action(
            priority="URGENT",
            department="Engineering",
            reply="Thank you for flagging this. Escalating to the engineering team immediately. We will investigate and update you within 15 minutes.",
        )
        reward = grade_hard(action, URGENT_EMAIL)
        assert reward.total > 0.75

    def test_no_reply_zero_reply_score(self):
        action = Action(priority="URGENT", department="Engineering", reply=None)
        reward = grade_hard(action, URGENT_EMAIL)
        assert reward.reply_score == 0.0

    def test_within_bounds(self):
        action = Action(priority="URGENT", department="Engineering", reply="We are on it.")
        reward = grade_hard(action, URGENT_EMAIL)
        assert 0.0 <= reward.total <= 1.0


class TestEnvironment:
    def test_reset_returns_observation(self, env):
        obs = env.reset("task_easy")
        assert obs.email_id is not None
        assert obs.task_id == "task_easy"

    def test_step_without_reset_raises(self, env):
        with pytest.raises(RuntimeError):
            env.step(Action(priority="NORMAL", department="None"))

    def test_invalid_task_raises(self, env):
        with pytest.raises(ValueError):
            env.reset("task_nonexistent")

    def test_full_easy_episode(self, env):
        env.reset("task_easy")
        done = False
        steps = 0
        while not done:
            result = env.step(Action(priority="URGENT", department="None"))
            done = result.done
            steps += 1
        assert steps == 6

    def test_full_medium_episode(self, env):
        env.reset("task_medium")
        done = False
        steps = 0
        while not done:
            result = env.step(Action(priority="NORMAL", department="Support"))
            done = result.done
            steps += 1
        assert steps == 8

    def test_full_hard_episode(self, env):
        env.reset("task_hard")
        done = False
        steps = 0
        while not done:
            result = env.step(Action(
                priority="URGENT",
                department="Engineering",
                reply="Thank you. We are resolving this immediately."
            ))
            done = result.done
            steps += 1
        assert steps == 10

    def test_step_after_done_raises(self, env):
        env.reset("task_easy")
        done = False
        while not done:
            result = env.step(Action(priority="NORMAL", department="None"))
            done = result.done
        with pytest.raises(RuntimeError):
            env.step(Action(priority="NORMAL", department="None"))

    def test_reset_clears_state(self, env):
        env.reset("task_easy")
        env.step(Action(priority="URGENT", department="None"))
        env.reset("task_medium")
        state = env.state()
        assert state.email_index == 0
        assert state.scores == []
        assert state.task_id == "task_medium"
