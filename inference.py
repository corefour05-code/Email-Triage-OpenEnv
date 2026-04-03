"""
inference.py
============
Baseline inference script for Email Triage OpenEnv.

Usage:
  1. Start the server first:   python server.py
  2. Set environment variables:
       set API_BASE_URL=https://router.huggingface.co/v1
       set MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
       set HF_TOKEN=hf_your_token_here
  3. Run:  python inference.py
"""

import os
import sys
import json
import time

# Fix module resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config from environment variables (mandatory per hackathon spec)
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "hf_dummy")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

MAX_STEPS   = 25
TEMPERATURE = 0.1
MAX_TOKENS  = 300
TASKS       = ["task_easy", "task_medium", "task_hard"]

# ---------------------------------------------------------------------------
# OpenAI client (mandatory per spec - must use OpenAI client)
# ---------------------------------------------------------------------------
client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert email triage assistant.

For each email, respond ONLY with a valid JSON object. No extra text, no markdown.

{
  "priority": "<URGENT|NORMAL|LOW>",
  "department": "<Sales|Support|Billing|HR|Engineering|None>",
  "reply": "<professional reply, between 30-100 words>"
}

Priority guidelines:
- URGENT: outages, security breaches, hot sales leads, executive requests, angry clients.
- NORMAL: support tickets, billing inquiries, product questions, recruitment.
- LOW: newsletters, general feedback, internal updates.

Department guidelines:
- Sales: demos, partnerships, pricing, new deals.
- Support: login issues, bugs, refunds, user help.
- Billing: invoices, payments, renewals.
- HR: applications, employee feedback, onboarding.
- Engineering: server issues, security bugs, technical failure.
- None: broad newsletters or spam.

Reply Draft Rules:
- Must be between 30 and 100 words.
- Be professional and helpful.
- Mention the department you are routing to.

IMPORTANT: Respond with the JSON object ONLY."""


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------
def env_reset(task_id: str) -> dict:
    r = requests.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id}, timeout=30)
    r.raise_for_status()
    return r.json()


def env_step(priority: str, department: str, reply: str = None) -> dict:
    payload = {"priority": priority, "department": department}
    if reply:
        payload["reply"] = reply
    r = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# LLM agent
# ---------------------------------------------------------------------------
def call_llm(obs: dict) -> dict:
    user_msg = f"""Triage this email:

From: {obs['sender']}
Subject: {obs['subject']}
Date: {obs['timestamp']}

{obs['body']}

Task: {obs['task_id']}
Emails remaining: {obs['emails_remaining']}
Current score: {obs['current_score']:.3f}

Reply with JSON only."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    raw = response.choices[0].message.content.strip()

    # Robust JSON extraction
    if "{" in raw and "}" in raw:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            raw_json = raw[start:end]
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            parsed = {}
    else:
        parsed = {}

    # Default fallback values
    if not parsed:
        print(f"  [WARN] Using default fallback for: {raw[:100]}")
        parsed = {"priority": "NORMAL", "department": "None", "reply": ""}

    # Sanitise types and missing fields
    final = {
        "priority": str(parsed.get("priority", "NORMAL")).upper(),
        "department": str(parsed.get("department", "None")).title(),
        "reply": str(parsed.get("reply", ""))
    }

    # Map department casing to match Literals
    dept_map = {
        "Sales": "Sales", "Support": "Support", "Billing": "Billing",
        "Hr": "HR", "Engineering": "Engineering", "None": "None"
    }
    final["department"] = dept_map.get(final["department"], "None")

    # Map priority casing
    if final["priority"] not in {"URGENT", "NORMAL", "LOW"}:
        final["priority"] = "NORMAL"

    return final


# ---------------------------------------------------------------------------
# Run one task episode
# ---------------------------------------------------------------------------
def run_task(task_id: str) -> float:
    print(f"\n{'='*55}")
    print(f"  TASK: {task_id.upper()}")
    print(f"{'='*55}")
    print(f"[START] {task_id}")

    obs = env_reset(task_id)
    total_reward = 0.0
    step = 0

    while True:
        step += 1
        print(f"\n  Step {step} | {obs['email_id']} | {obs['subject'][:45]}")

        t0 = time.time()
        action = call_llm(obs)
        elapsed = time.time() - t0

        print(f"    Priority:   {action['priority']}")
        print(f"    Department: {action['department']}")
        if action.get("reply"):
            print(f"    Reply:      {str(action['reply'])[:70]}...")
        print(f"    LLM time:   {elapsed:.2f}s")

        result = env_step(
            priority=action["priority"],
            department=action["department"],
            reply=action.get("reply"),
        )

        reward = result["reward"]
        total_reward += reward["total"]
        print(f"    Reward:     {reward['total']:.3f} | {reward['feedback']}")
        print(f"[STEP] {task_id} | score: {reward['total']:.3f} | step: {step}")

        if result["done"]:
            break

        obs = result["observation"]

        if step >= MAX_STEPS:
            print("  [WARN] Safety cap reached.")
            break

    episode_score = total_reward / step if step > 0 else 0.0
    print(f"\n  DONE | Steps: {step} | Score: {episode_score:.4f}")
    print(f"[END] {task_id} | average: {episode_score:.4f}")
    return episode_score


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n" + "="*55)
    print("  EMAIL TRIAGE OPENENV - BASELINE INFERENCE")
    print("="*55)
    print(f"  Model:   {MODEL_NAME}")
    print(f"  API:     {API_BASE_URL}")
    print(f"  Env:     {ENV_BASE_URL}")
    print("="*55)

    # Check server is running
    try:
        r = requests.get(f"{ENV_BASE_URL}/health", timeout=10)
        r.raise_for_status()
        print(f"\n  Environment server is live.")
    except Exception as e:
        print(f"\n  ERROR: Cannot reach environment server at {ENV_BASE_URL}")
        print(f"  Make sure you ran: python server.py")
        print(f"  Details: {e}")
        sys.exit(1)

    results = {}
    for task_id in TASKS:
        try:
            score = run_task(task_id)
            results[task_id] = score
        except Exception as e:
            print(f"\n  ERROR on {task_id}: {e}")
            results[task_id] = 0.0

    # Summary
    print("\n" + "="*55)
    print("  FINAL SCORES")
    print("="*55)
    for task_id, score in results.items():
        bar = "=" * int(score * 20)
        print(f"  {task_id:<15} {score:.4f}  [{bar:<20}]")
    avg = sum(results.values()) / len(results)
    print(f"  {'AVERAGE':<15} {avg:.4f}")
    print("="*55)

    # Save results
    output = {
        "model": MODEL_NAME,
        "api_base_url": API_BASE_URL,
        "scores": results,
        "average": avg,
    }
    with open("baseline_scores.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to baseline_scores.json")


if __name__ == "__main__":
    main()
