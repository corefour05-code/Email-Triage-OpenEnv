from __future__ import annotations
import sys
import os

# Fix module resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from env import EmailTriageEnv
from models import Action, Observation, StepResult, EpisodeState

app = FastAPI(
    title="Email Triage OpenEnv",
    description="Real-world email triage environment for RL agents.",
    version="1.0.0",
)

env = EmailTriageEnv()


class ResetRequest(BaseModel):
    task_id: str = "task_easy"


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Triage - OpenEnv Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --secondary: #a855f7;
                --bg: #0f172a;
                --card-bg: rgba(30, 41, 59, 0.7);
                --text: #f8fafc;
                --text-dim: #94a3b8;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: var(--text);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow-x: hidden;
            }
            .container {
                max-width: 900px;
                width: 90%;
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 48px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                animation: fadeIn 0.8s ease-out;
            }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .header { text-align: center; margin-bottom: 40px; }
            h1 { font-family: 'Outfit', sans-serif; font-size: 3rem; margin-bottom: 8px; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
            .badge { display: inline-block; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 12px; }
            .description { color: var(--text-dim); font-size: 1.1rem; line-height: 1.6; }
            .task-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
            .task-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 24px; transition: all 0.3s ease; }
            .task-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.05); border-color: var(--primary); box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3); }
            .task-card h3 { font-size: 1.25rem; margin-bottom: 8px; color: #fff; }
            .task-card p { color: var(--text-dim); font-size: 0.95rem; }
            .diff { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8; margin-bottom: 12px; }
            .easy { color: #4ade80; } .medium { color: #facc15; } .hard { color: #f87171; }
            .actions { display: flex; gap: 16px; justify-content: center; margin-top: 24px; }
            .btn { text-decoration: none; padding: 12px 28px; border-radius: 12px; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; }
            .btn-primary { background: var(--primary); color: white; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4); }
            .btn-primary:hover { background: #4f46e5; transform: scale(1.02); }
            .btn-outline { border: 1px solid rgba(255, 255, 255, 0.2); color: var(--text); }
            .btn-outline:hover { background: rgba(255, 255, 255, 0.05); border-color: rgba(255, 255, 255, 0.5); }
            .footer { text-align: center; margin-top: 48px; color: var(--text-dim); font-size: 0.85rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="badge">OpenEnv Hackathon</span>
                <h1>Email Triage AI</h1>
                <p class="description">Real-world email automation environment. Train agents to prioritize, route, and draft replies to business communications.</p>
            </div>
            
            <div class="task-grid">
                <div class="task-card">
                    <div class="diff easy">Level: Easy</div>
                    <h3>Classification</h3>
                    <p>Identify priority levels (URGENT, NORMAL, LOW) from semantic content.</p>
                </div>
                <div class="task-card">
                    <div class="diff medium">Level: Medium</div>
                    <h3>Smart Routing</h3>
                    <p>Categorize emails and route them to one of 6 business departments.</p>
                </div>
                <div class="task-card">
                    <div class="diff hard">Level: Hard</div>
                    <h3>Full Triage</h3>
                    <p>Complete priority, routing, and a high-quality human-like reply draft.</p>
                </div>
            </div>

            <div class="actions">
                <a href="/docs" class="btn btn-primary">Interactive API Docs</a>
                <a href="/health" class="btn btn-outline">Check Health</a>
            </div>

            <div class="footer">
                Built by Team ThinkRay for OpenEnv Hackathon 2024
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "env": "email-triage-env", "version": "1.0.0"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "task_easy",
                "name": "Email Priority Classification",
                "difficulty": "easy",
                "description": "Classify each email as URGENT, NORMAL, or LOW priority.",
            },
            {
                "id": "task_medium",
                "name": "Email Triage with Routing",
                "difficulty": "medium",
                "description": "Classify priority AND route to the correct department.",
            },
            {
                "id": "task_hard",
                "name": "Full Triage with Reply Draft",
                "difficulty": "hard",
                "description": "Classify priority, route department, and draft a reply.",
            },
        ]
    }


@app.post("/reset", response_model=Observation)
def reset(request: ResetRequest):
    try:
        obs = env.reset(task_id=request.task_id)
        return obs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResult)
def step(action: Action):
    try:
        result = env.step(action)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state", response_model=EpisodeState)
def state():
    return env.state()


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=7860, reload=False)
