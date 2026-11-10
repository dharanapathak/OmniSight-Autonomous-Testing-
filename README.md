# OmniSight — Multimodal UI Self-Healing & RPA Agent

A Python browser-automation application that accepts natural-language tasks, plans browser actions, inspects page structure and screenshots, retries failed interactions with alternative locators, and records an execution log.

## Features
- Streamlit control panel for natural-language browser tasks
- Playwright-powered browser automation
- Optional OpenAI planning and screenshot interpretation (vision)
- Rule-based fallback planner when no API key is configured
- Self-healing locator strategy: accessible role/name, label, placeholder, text, test id, and CSS candidates
- Safe action allowlist (navigate, click, fill, select, wait, extract, screenshot)
- Execution log, extracted text, and screenshot preview
- Demo HTML page and basic unit tests

## Requirements
- Python 3.10+
- Chromium browser installed through Playwright
- Optional OpenAI API key for LLM and vision planning

## Setup (Windows PowerShell)
```powershell
cd OmniSight
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```
Edit `.env` and add `OPENAI_API_KEY` if you want AI planning and screenshot analysis. The app can still run with the deterministic fallback planner.

## Run
```powershell
streamlit run app.py
```
Open the local URL printed by Streamlit (usually http://localhost:8501).

## Quick demo
1. Start the app.
2. Set the start URL to `http://127.0.0.1:8000/demo/index.html`.
3. In another terminal, run:
   ```powershell
   python -m http.server 8000
   ```
   from the project folder.
4. Enter:
   `Open the demo page, fill the name field with Dharana, fill the email field with dharana@example.com, choose AI from the interest dropdown, and submit the form.`
5. Review the action log and extracted result.

## Project structure
```text
OmniSight/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── omnisight/
│   ├── __init__.py
│   ├── agent.py
│   ├── browser.py
│   ├── planner.py
│   ├── self_healing.py
│   ├── vision.py
│   └── safety.py
├── demo/index.html
└── tests/
    ├── test_planner.py
    └── test_safety.py
```

## How it works
1. The user describes a task in plain language.
2. The planner converts the task into a constrained JSON action plan.
3. Playwright opens the page and exposes its DOM and screenshot.
4. The agent executes only supported actions.
5. If a locator fails, the self-healing module tries semantic alternatives and reports which strategy succeeded.
6. The agent records results and returns extracted text and screenshots.

## Safety notes
- This is a local development prototype, not an unattended production agent.
- Review the task and target website before running it.
- Do not use it to bypass authentication, CAPTCHAs, access controls, or website restrictions.
- Avoid entering passwords, payment details, or sensitive personal information.
- The agent does not execute arbitrary Python or JavaScript from an LLM response.
- Some sites block automation or change their markup; self-healing is best-effort, not guaranteed.

## Configuration
See `.env.example`. `HEADLESS=true` runs the browser without a visible window. For initial testing, use `HEADLESS=false`.

## Troubleshooting
- `playwright` browser missing: run `playwright install chromium`.
- Browser launch fails: close stale Chromium processes and retry.
- AI planning unavailable: verify `OPENAI_API_KEY`; otherwise the fallback planner is used.
- A task is not understood by fallback mode: use clear verbs such as navigate, click, fill, select, wait, extract, and screenshot, or configure an OpenAI key.
