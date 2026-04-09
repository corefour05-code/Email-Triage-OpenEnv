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
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Config from environment variables (Matched to Judge's Sample Script)
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME   = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
ENV_BASE_URL = os.getenv("ENV_BASE_URL") or "http://localhost:7860"

# Initialize constants safely
MAX_STEPS   = 25
TEMPERATURE = 0.1
MAX_TOKENS  = 300
TASKS       = ["task_easy", "task_medium", "task_hard"]

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


def parse_action(raw: str) -> dict:
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

    if not parsed:
        print(f"  [WARN] Using default fallback for: {raw[:100]}")
        parsed = {"priority": "NORMAL", "department": "None", "reply": ""}

    final = {
        "priority": str(parsed.get("priority", "NORMAL")).upper(),
        "department": str(parsed.get("department", "None")).title(),
        "reply": str(parsed.get("reply", ""))
    }

    dept_map = {
        "Sales": "Sales", "Support": "Support", "Billing": "Billing",
        "Hr": "HR", "Engineering": "Engineering", "None": "None"
    }
    final["department"] = dept_map.get(final["department"], "None")

    if final["priority"] not in {"URGENT", "NORMAL", "LOW"}:
        final["priority"] = "NORMAL"

    return final


def call_llm(obs: dict) -> dict:
    # Direct HTTP implementation for max stability
    url = f"{API_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    user_msg = f"Triage this email:\n\nFrom: {obs['sender']}\nSubject: {obs['subject']}\nBody: {obs['body']}"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return parse_action(content)
    except Exception as e:
        print(f"[ERROR] LLM Request failed: {e}")
        return {"priority": "NORMAL", "department": "None", "reply": f"API Error: {e}"}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str = "null") -> None:
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def run_task(task_id: str) -> float:
    print(f"\n{'='*55}")
    print(f"  TASK: {task_id.upper()}")
    print(f"{'='*55}")
    log_start(task_id, "email-triage-env", MODEL_NAME)

    obs = env_reset(task_id)
    total_reward = 0.0
    all_rewards = []
    step = 0

    while True:
        step += 1
        print(f"\n  Step {step} | {obs['email_id']} | {obs['subject'][:45]}")

        t0 = time.time()
        action_data = call_llm(obs)
        elapsed = time.time() - t0

        action_summary = f"{action_data['priority']}/{action_data['department']}"
        
        result = env_step(
            priority=action_data["priority"],
            department=action_data["department"],
            reply=action_data.get("reply"),
        )

        reward = result["reward"]
        total_reward += reward["total"]
        all_rewards.append(reward["total"])
        
        log_step(step, action_summary, reward["total"], result["done"])

        if result["done"]:
            break

        obs = result["observation"]

        if step >= MAX_STEPS:
            break

    episode_score = total_reward / step if step > 0 else 0.0
    success = episode_score >= 0.1
    log_end(success, step, episode_score, all_rewards)
    return episode_score


def main():
    print("\n" + "="*55)
    print("  EMAIL TRIAGE OPENENV - BASELINE INFERENCE")
    print("="*55)
    print(f"  Model:   {MODEL_NAME}")
    print(f"  API:     {API_BASE_URL}")
    print(f"  Env:     {ENV_BASE_URL}")
    print("="*55)

    try:
        r = requests.get(f"{ENV_BASE_URL}/health", timeout=10)
        r.raise_for_status()
        print(f"\n  Environment server is live.")
    except Exception as e:
        print(f"\n  ERROR: Cannot reach environment server at {ENV_BASE_URL}")
        sys.exit(1)

    results = {}
    for task_id in TASKS:
        try:
            score = run_task(task_id)
            results[task_id] = score
        except Exception as e:
            print(f"\n  ERROR on {task_id}: {e}")
            results[task_id] = 0.0

    avg = sum(results.values()) / len(results)
    print(f"\n  AVERAGE SCORE: {avg:.4f}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Unhandled exception in inference.py: {e}")
        sys.exit(0)
