---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Email Triage OpenEnv

Real-world email triage environment for RL agents — OpenEnv Hackathon submission by ThinkRay.

## Tasks

| Task ID | Difficulty | What the agent does |
|---|---|---|
| `task_easy` | Easy | Classify priority: URGENT / NORMAL / LOW |
| `task_medium` | Medium | Priority + route to department |
| `task_hard` | Hard | Priority + routing + draft a reply |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the environment server
```bash
python server.py
```
Server runs at http://localhost:7860
API docs at http://localhost:7860/docs

### 3. Run baseline inference

**Windows:**
```cmd
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
set HF_TOKEN=hf_your_token_here
python inference.py
```

**Mac/Linux:**
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="hf_your_token_here"
python inference.py
```

### 4. Run tests
```bash
pip install pytest
pytest tests/ -v
```

## Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/tasks` | List all tasks |
| POST | `/reset` | Start episode `{"task_id": "task_easy"}` |
| POST | `/step` | Submit action `{"priority": ..., "department": ..., "reply": ...}` |
| GET | `/state` | Current environment state |

## Observation Space

```json
{
  "email_id": "E001",
  "subject": "PRODUCTION DOWN",
  "sender": "devops@client.com",
  "body": "...",
  "timestamp": "2024-03-15T09:02:00Z",
  "task_id": "task_easy",
  "emails_remaining": 5,
  "current_score": 0.0,
  "step": 0
}
```

## Action Space

```json
{
  "priority": "URGENT",
  "department": "Engineering",
  "reply": "Thank you for flagging this. Our team is investigating immediately."
}
```

## Reward Structure

| Task | Priority | Routing | Reply |
|---|---|---|---|
| task_easy | 1.00 | 0.00 | 0.00 |
| task_medium | 0.40 | 0.60 | 0.00 |
| task_hard | 0.40 | 0.35 | 0.25 |

## Environment Variables

| Variable | Description |
|---|---|
| `API_BASE_URL` | LLM API endpoint |
| `MODEL_NAME` | Model identifier |
| `HF_TOKEN` | Hugging Face API key |
| `ENV_BASE_URL` | Environment server URL (default: http://localhost:7860) |

## Team
ThinkRay — OpenEnv Hackathon by Scaler x Hugging Face
