# Pathwise
### Autonomous Personal Financial Planning Agent
**Built at Hack-a-Claw 2026 · NVIDIA × UCSC Baskin Engineering**

---

## What It Does

Pathwise is an autonomous AI agent that takes your financial situation in plain English and builds a personalized month-by-month roadmap to hit your goals.

You describe your finances. Pathwise does the rest:

- **Live tool use** — fetches real HYSA, mortgage, and S&P 500 rates via Tavily
- **Multi-step reasoning** — reasons through priorities (debt → emergency fund → investing → goals)
- **Month-by-month roadmap** — specific dollar amounts for each phase
- **Persistent memory** — remembers your profile and plan across sessions
- **What-if scenarios** — updates your plan on the fly ("what if I get a raise?")
- **Interactive charts** — visualizes debt payoff, surplus allocation, and net worth trajectory

---

## Demo

> *"I'm a UCSC student, I make $1,200/month from part-time work, I have $4,500 in credit card debt at 24% APR, and I want to graduate debt-free in 2 years."*

Pathwise autonomously:
1. Fetches live HYSA rates, mortgage rates, and S&P 500 outlook
2. Extracts your financial profile
3. Reasons through debt vs. emergency fund vs. investing priorities
4. Builds a 12-month roadmap with specific dollar amounts per phase
5. Saves your plan to memory for future sessions
6. Runs what-if scenarios on demand

---

## Architecture
User Input (plain English)
↓
Live Rate Fetcher (Tavily Search)
- HYSA rates
- Mortgage rates
- S&P 500 outlook
↓
OpenClaw Agent (autonomous reasoning)
- Configured with NVIDIA Nemotron via NIM
- Persistent memory across sessions
- Multi-step financial planning logic
↓
Structured JSON Output
↓
Flask Web UI (charts, timelines, what-if)
---

## Tech Stack

| Component | Technology |
|---|---|
| **Agent Framework** | OpenClaw 2026.5.12 |
| **LLM** | NVIDIA Nemotron (llama-3.3-nemotron-super-49b-v1) via NIM |
| **Live Data** | Tavily Search API |
| **Memory** | JSON persistent storage |
| **Web UI** | Flask + Chart.js |
| **Language** | Python 3.14 |

---

## How to Run

### Prerequisites
- Python 3.10+
- Node.js 22+
- NVIDIA API key (build.nvidia.com/settings/api-keys)
- Tavily API key (tavily.com)

### Install OpenClaw
```bash
npm install -g openclaw
openclaw onboard
# Choose NVIDIA as provider, paste your API key
```

### Clone and Set Up
```bash
git clone https://github.com/saraxjain/pathwise.git
cd pathwise
python3 -m venv venv
source venv/bin/activate
pip install flask openai python-dotenv tavily-python requests
```

### Configure Environment
```bash
echo "NVIDIA_API_KEY=nvapi-..." > .env
echo "TAVILY_API_KEY=tvly-..." >> .env
```

### Run
```bash
# Terminal 1 — OpenClaw agent (keep running)
openclaw tui

# Terminal 2 — web app
python3 app.py
```

Open **http://127.0.0.1:5001**

---

## Prize Tracks

- **Cloud Track** — NVIDIA NIM endpoints via Brev
- **Best for UCSC** — Built for UCSC students managing part-time income, student loans, and post-graduation financial goals

---

## Team
Chintan Patwardhan, Haatim Ali, Sara Jain
Built at Hack-a-Claw 2026 — a 24-hour NVIDIA hackathon at UC Santa Cruz Baskin Engineering.