# SentinelBrief — Resilient Autonomous Competitive Intelligence

> **The competitive intelligence agent that never silently fails** — powered by Nemotron on Crusoe Cloud, hardened by TrueFoundry AI Gateway.

[![DevNetwork Hackathon 2026](https://img.shields.io/badge/DevNetwork-AI%20%2B%20ML%20Hackathon%202026-blueviolet)]()
[![Nemotron on Crusoe](https://img.shields.io/badge/LLM-Nemotron%2049B%20on%20Crusoe-green)]()
[![TrueFoundry Gateway](https://img.shields.io/badge/Resilience-TrueFoundry%20AI%20Gateway-orange)]()

---

## 💡 Inspiration

Every founder spends **4–6 hours per week** tracking competitors manually — scouring news sites, Reddit threads, job boards, and pricing pages. When they turn to AI agents for help, those agents **fail silently**: returning partial output with no warning, hallucinating claims without sources, and crashing mid-run with no recovery. SentinelBrief was born to solve both problems — delivering autonomous competitive research that is *reliable, verifiable, and resilient*.

## 🔍 What It Does

Give SentinelBrief a company profile and up to **5 competitors**. It autonomously:

1. **Plans** targeted research queries via a multi-step reasoning planner.
2. **Fetches** intelligence in parallel across **5 independent sources** — Tavily, Google News, Bing News, HackerNews, and Reddit.
3. **Synthesizes** findings into structured briefings with **VeracityAI confidence tags** (`VERIFIED`, `INFERRED`, `UNVERIFIED`) on every single claim, each backed by source URLs.
4. **Scores** competitive threats on 5 dimensions and renders an interactive radar chart.

Every LLM call routes through **TrueFoundry AI Gateway** for automatic failover, rate-limit protection, and full observability — so the agent *never silently fails*.

---

## ⚡ Key Features

| Feature | Description |
|---|---|
| 🌐 **5-Source Parallel Intelligence** | Tavily + Google News + Bing News + HackerNews + Reddit — researched concurrently for maximum coverage |
| 🏷️ **VeracityAI Confidence Scoring** | Every claim tagged `[VERIFIED: url]`, `[INFERRED]`, or `[UNVERIFIED]` — no more hallucinated facts |
| 🛡️ **TrueFoundry-Powered Resilience** | Kill-switch chaos demo, automatic Nemotron → GPT-4o fallback, gateway event logs |
| 🕸️ **Competitive Threat Radar** | 5-dimension spider chart (Product, Pricing, Hiring, Funding, Market) via Recharts |
| 📡 **Live Agent Pipeline** | Real-time SSE progress feed — watch every agent node execute live |
| 💾 **Checkpoint Resume** | Upstash Redis crash recovery — mid-run failures resume from the last completed node |
| 🗄️ **DB Persistence** | Neon PostgreSQL briefing storage — every report is saved and retrievable |

---

## 🏗️ Architecture

```
          Vercel [Static Hosting]
                    ↓ (API Proxy Rewrites)
          Render [FastAPI Service]
                    ↓ (LangGraph Checkpoints / Neon DB Storage)
    ┌───────────────┴───────────────┐
    ▼                               ▼
Neon [PostgreSQL]           Upstash [Redis]
(Briefings Storage)       (Checkpoints & Queues)
    │
    ▼
TrueFoundry AI Gateway
    ↓ (Fallback Routing & Failover)
nvidia/nemotron-3-super-49b-v1 (Crusoe Cloud) ──► openai/gpt-4o (Fallback)
```

**Pipeline**: `Planner Agent` → `5× Parallel Fetcher Agents` → `Synthesizer Agent` → `VeracityAI Scorer` → `Structured Briefing`

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 + React 19 + Recharts |
| **Backend** | FastAPI + Python 3.12 |
| **LLM Inference** | Nemotron-49B on Crusoe Cloud (NVIDIA DGX) |
| **Resilience** | TrueFoundry AI Gateway (failover + observability) |
| **Search** | Tavily API + Google News + Bing News + HackerNews + Reddit |
| **State & Cache** | Upstash Redis (checkpoints + queues) |
| **Database** | Neon PostgreSQL (briefing persistence) |
| **Deployment** | Vercel (frontend) + Render (backend) |

---

## 🔨 How We Built It

We designed SentinelBrief as a **stateful multi-agent pipeline** with crash resilience baked in from day one:

1. **Research Planner** — The Nemotron LLM generates prioritized, competitor-specific search queries before any fetching begins, ensuring targeted coverage rather than generic searches.
2. **5-Source News Agent** — Five specialized fetcher agents (Tavily, Google News, Bing News, HackerNews, Reddit) run **in parallel** using `asyncio.gather`, each with independent retry logic. If one source is down, the other four still deliver.
3. **Synthesizer Agent** — Raw results are merged and deduplicated, then fed to Nemotron for structured synthesis into briefing sections (Product, Pricing, Hiring, Funding, Market).
4. **VeracityAI Scorer** — A dedicated scoring pass tags every claim with confidence levels and source attribution. We use constrained prompting to enforce consistent `[VERIFIED]` / `[INFERRED]` / `[UNVERIFIED]` formatting.
5. **Chaos Engineering System** — A live control panel lets judges inject failures (kill the LLM connection, spike latency) to demonstrate TrueFoundry Gateway's automatic fallback from Nemotron → GPT-4o in real-time.
6. **Checkpoint Resume** — Every agent node writes its output to Upstash Redis. If the pipeline crashes at node 3, it resumes from node 3 — not from scratch.

---

## 🧗 Challenges We Faced

- **Consistent confidence tags from LLMs** — Getting Nemotron to reliably output structured `[VERIFIED: url]` tags required multiple prompt engineering iterations and output validation layers.
- **5 parallel sources without blocking** — Coordinating five independent APIs with different rate limits, response formats, and failure modes into a single async pipeline was a significant engineering challenge.
- **Checkpoint resume across Redis** — Serializing and deserializing intermediate LangGraph state to Upstash Redis — while handling partial writes and TTL expiry — required careful state management.
- **Spider chart normalization** — Scoring competitors on 5 dimensions with consistent 0–10 scales from free-form LLM output needed structured extraction and fallback defaults.

---

## 🔮 What's Next

| Phase | Timeline | Goal |
|---|---|---|
| 🚀 **Beta Launch** | June 2026 | Onboard 50 founders for weekly automated briefings |
| 💰 **Monetize** | Q3 2026 | Starter ($49/mo — 3 competitors) and Pro ($199/mo — 10 competitors + alerts) |
| 🔗 **Expand** | Q4 2026 | CRM integrations (Salesforce, HubSpot), Slack/Teams delivery, PDF export |
| 🧠 **Deepen** | 2027 | Longitudinal trend analysis, patent monitoring, earnings call summarization |

---

## 🛠️ Built With

`Nemotron` · `Crusoe Cloud` · `TrueFoundry AI Gateway` · `FastAPI` · `Next.js` · `React` · `Recharts` · `Upstash Redis` · `Neon PostgreSQL` · `Tavily API` · `Python` · `TypeScript` · `LangGraph`

---

## 🚀 Quick Start — Local Development

1. **Configure environment** — Copy `.env.example` to `.env` and fill in your keys (or set `SENTINELBRIEF_MOCK=true` to run without API keys).

2. **Start the backend:**
   ```bash
   pip install -r requirements.txt
   python -m uvicorn backend.main:app --reload --port 8000
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open `http://localhost:3000`, enter a company and competitors, and watch the agent pipeline run live.

---

## 🏆 Sponsor Track Alignment

- **Crusoe Cloud (NVIDIA DGX Track)** — Core reasoning executed using `nvidia/nemotron-3-super-49b-v1` across both Research Planning and Synthesis nodes. All inference runs on Crusoe Cloud GPU infrastructure.
- **TrueFoundry (Resilient Agents Track)** — Robust failover, error checkpoints, and event log routing transparently via TrueFoundry AI Gateway to protect critical agent runs. Live chaos demo proves resilience under failure.

---

<p align="center"><b>SentinelBrief</b> — Because competitive intelligence shouldn't fail silently.</p>
