# SentinelBrief — Resilient Autonomous Competitive Intelligence

> **The competitive intelligence agent that never silently fails** — powered by Nemotron-3-Nano on Crusoe Cloud, hardened by TrueFoundry AI Gateway.

[![DevNetwork Hackathon 2026](https://img.shields.io/badge/DevNetwork-AI%20%2B%20ML%20Hackathon%202026-blueviolet)]()
[![Nemotron on Crusoe](https://img.shields.io/badge/LLM-Nemotron--3--Nano--30B%20on%20Crusoe-green)]()
[![TrueFoundry Gateway](https://img.shields.io/badge/Resilience-TrueFoundry%20AI%20Gateway-orange)]()

---

## 💡 Inspiration

Every founder spends **4–6 hours per week** tracking competitors manually — scouring news sites, Reddit threads, job boards, and pricing pages. When they turn to AI agents for help, those agents **fail silently**: returning partial output with no warning, hallucinating claims without sources, and crashing mid-run with no recovery. SentinelBrief was born to solve both problems — delivering autonomous competitive research that is *reliable, verifiable, and resilient*.

## 🔍 What It Does

Give SentinelBrief a company profile and up to **5 competitors**. It autonomously:

1. **Plans** targeted research queries via a Nemotron-powered reasoning planner.
2. **Fetches** intelligence in parallel across **5 independent sources** — Tavily, Google News, Bing News, HackerNews, and Reddit.
3. **Synthesizes** findings into structured briefings with **VeracityAI confidence tags** (`VERIFIED`, `INFERRED`, `UNVERIFIED`) on every single claim, each backed by source URLs.
4. **Scores** competitive threats on 5 dimensions and renders an interactive radar chart.

Every LLM call routes through **TrueFoundry AI Gateway** for automatic failover, rate-limit protection, and full observability — so the agent *never silently fails*.

---

## ⚡ Key Features

| Feature | Description |
|---|---|
| 🌐 **5-Source Parallel Intelligence** | Tavily + Google News + Bing News + HackerNews + Reddit — researched concurrently with independent timeout isolation |
| 🏷️ **VeracityAI Confidence Scoring** | Every claim tagged `[VERIFIED: url]`, `[INFERRED]`, or `[UNVERIFIED]` — no more hallucinated facts |
| 🛡️ **TrueFoundry-Powered Resilience** | Kill-switch chaos demo, automatic Nemotron → GPT-4o fallback, gateway event logs |
| 🕸️ **Competitive Threat Radar** | 5-dimension spider chart (Pricing, Hiring, Funding, Product, Social) via Recharts |
| 📡 **Live Agent Pipeline** | Real-time SSE progress feed — watch every agent node execute live with progress bar |
| 💾 **Checkpoint Resume** | Upstash Redis crash recovery — mid-run failures resume from the last completed node |
| 🗄️ **DB Persistence** | Neon PostgreSQL briefing storage — every report is saved and retrievable |
| 💰 **Pricing Comparison** | Interactive pricing cards showing SentinelBrief ($49–$999/mo) vs legacy CI tools ($2,000+/mo) |

---

## 🏗️ Architecture

```
          Vercel [Static Hosting]
                    ↓ (API Proxy Rewrites)
          Render [FastAPI Service]
                    ↓ (Stateful Checkpoints / Neon DB Storage)
    ┌───────────────┴───────────────┐
    ▼                               ▼
Neon [PostgreSQL]           Upstash [Redis]
(Briefings Storage)       (Checkpoints & Cache)
    │
    ▼
TrueFoundry AI Gateway
    ↓ (Fallback Routing & Failover)
hack-crusoe/Nemotron-3-Nano-30B (Crusoe Cloud) ──► openai/gpt-4o (Fallback)
```

**Agent Pipeline**: `Planner Agent` → `5× Parallel Fetcher Agents (News·Product·Pricing·Hiring)` → `Synthesizer Agent` → `VeracityAI Scorer` → `Structured Briefing`

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 + React 19 + Recharts |
| **Backend** | FastAPI + Python 3.11 + async orchestration |
| **LLM Inference** | `hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8` on Crusoe Cloud |
| **Resilience** | TrueFoundry AI Gateway (failover + observability) |
| **Search** | Tavily API + Google News RSS + Bing News + HackerNews Algolia + Reddit |
| **State & Cache** | Upstash Redis (checkpoints) |
| **Database** | Neon PostgreSQL (briefing persistence) |
| **Deployment** | Vercel (frontend) + Render (backend via Docker) |

---

## 🔨 How We Built It

We designed SentinelBrief as a **stateful multi-agent pipeline** with crash resilience baked in from day one:

1. **Research Planner** — Nemotron-3-Nano generates prioritized, competitor-specific search queries before any fetching begins. Supports 3 research depths: Quick (3 queries), Standard (7 queries), Deep (12 queries).
2. **5-Source News Agent** — Five specialized fetcher sources (Tavily, Google News, Bing News, HackerNews, Reddit) run **in parallel** using `asyncio.gather`, each with independent 14-second timeout isolation. If one source fails, the others still deliver. Results are deduplicated by URL and ranked by source quality.
3. **Product/Pricing/Hiring Agents** — Three additional specialized agents fetch competitor product launches, pricing changes, and hiring signals. The hiring agent uses parent company lookup (e.g., Confluence → Atlassian) for accurate results.
4. **Synthesizer Agent** — All research data is merged and fed to Nemotron for structured synthesis. The prompt enforces `[VERIFIED: url]` / `[INFERRED]` / `[UNVERIFIED]` tagging on every factual claim.
5. **VeracityAI Scorer** — A dedicated scoring pass uses regex parsing to count and validate all confidence tags, computing per-competitor and overall confidence badge colors (green/amber/red).
6. **Chaos Engineering System** — A live Resilience Dashboard lets judges inject failures: Kill Nemotron, Kill Search, Simulate Timeout. The system recovers automatically via TrueFoundry Gateway fallback routing.
7. **Checkpoint Resume** — Every agent node writes its output to Upstash Redis with 24-hour TTL. If the pipeline crashes mid-run, it resumes from the last completed node.

---

## 🧗 Challenges We Faced

- **Reasoning model response format** — Nemotron-3-Nano returns output in a `reasoning` field instead of `content`. We had to build a custom content extractor that checks both fields to handle this transparently.
- **Consistent confidence tags from LLMs** — Getting Nemotron to reliably output structured `[VERIFIED: url]` tags required multiple prompt engineering iterations and a dedicated regex-based validation layer.
- **5 parallel sources without blocking** — Coordinating five independent APIs with different rate limits, response formats, and failure modes into a single async pipeline with per-source timeout isolation.
- **Parent company resolution** — Products like "Confluence" need to search for "Atlassian" for hiring data. We built a product-to-parent lookup system that operates across both frontend and backend.
- **Spider chart normalization** — Scoring competitors on 5 dimensions with consistent 0–100 scales from free-form LLM output needed structured extraction and fallback defaults.

---

## 📁 Project Structure

```
DevNetwork/
├── backend/
│   ├── main.py                    # FastAPI app — SSE streaming, chaos endpoints, health checks
│   ├── agents/
│   │   ├── orchestrator.py        # Pipeline conductor — coordinates all agents
│   │   ├── planner_agent.py       # Research Planner — Nemotron generates search queries
│   │   ├── news_agent.py          # 5-source parallel news intelligence
│   │   ├── product_agent.py       # Product launch & feature tracker
│   │   ├── pricing_agent.py       # Pricing change detector
│   │   ├── hiring_agent.py        # Hiring signal analyzer (with parent company lookup)
│   │   ├── synthesis_agent.py     # Nemotron synthesis with confidence tagging
│   │   └── confidence_scorer.py   # VeracityAI — regex-based claim scoring
│   ├── gateway/
│   │   └── llm_client.py          # TrueFoundry Gateway client + chaos kill switches
│   ├── models/
│   │   └── briefing.py            # Pydantic models (request/response schemas)
│   └── tools/
│       ├── tavily_search.py       # Tavily + SerpAPI fallback + HackerNews
│       ├── google_news.py         # Google News RSS feed parser
│       ├── bing_news.py           # Bing News search
│       ├── reddit_search.py       # Reddit search
│       ├── company_lookup.py      # Product → parent company resolution
│       ├── checkpoints.py         # Upstash Redis checkpoint store
│       └── database.py            # Neon PostgreSQL connector
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main app — SSE streaming, tab navigation
│   │   ├── app/
│   │   │   ├── layout.jsx         # Root layout with Google Fonts
│   │   │   └── page.jsx           # Home page entry
│   │   ├── components/
│   │   │   ├── InputForm.jsx      # Company input + presets + depth selector
│   │   │   ├── AgentStatus.jsx    # Live pipeline progress with agent grid
│   │   │   ├── Briefing.jsx       # Intelligence output + confidence badges + source popup
│   │   │   ├── ThreatRadar.jsx    # Recharts spider/radar chart
│   │   │   ├── SystemHealth.jsx   # Infrastructure health display
│   │   │   ├── ResilienceDashboard.jsx  # Kill switches + gateway event log
│   │   │   └── PricingCard.jsx    # Pricing tiers + competitor comparison
│   │   └── index.css              # 1500+ line premium dark theme CSS
│   ├── next.config.mjs            # API proxy rewrites for local dev
│   └── vercel.json                # Production API proxy to Render backend
├── Dockerfile                     # Production Docker image (Python 3.11-slim)
├── render.yaml                    # Render Blueprint for 1-click backend deploy
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment variable template
```

---

## 🔮 What's Next

| Phase | Timeline | Goal |
|---|---|---|
| 🚀 **Beta Launch** | June 2026 | Onboard 50 founders for weekly automated briefings |
| 💰 **Monetize** | Q3 2026 | Solo ($49/mo), Team ($199/mo), Enterprise ($999/mo) |
| 🔗 **Expand** | Q4 2026 | CRM integrations (Salesforce, HubSpot), Slack/Teams delivery, PDF export |
| 🧠 **Deepen** | 2027 | Longitudinal trend analysis, patent monitoring, earnings call summarization |

---

## 🛠️ Built With

`Nemotron-3-Nano-30B` · `Crusoe Cloud` · `TrueFoundry AI Gateway` · `FastAPI` · `Next.js 15` · `React 19` · `Recharts` · `Upstash Redis` · `Neon PostgreSQL` · `Tavily API` · `Python` · `OpenAI SDK` · `Docker`

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

## ☁️ Production Deployment

### Backend → Render
1. Push to GitHub → Sign in to [Render.com](https://render.com) → **New → Blueprint** → select this repo.
2. Render reads `render.yaml` and creates the service. Set environment variables when prompted.

### Frontend → Vercel
1. Sign in to [Vercel.com](https://vercel.com) → Import this repo → Set root directory to `frontend`.
2. Vercel reads `vercel.json` to proxy `/api` requests to your Render backend.

---

## 🏆 Sponsor Track Alignment

- **Crusoe Cloud (NVIDIA DGX Track)** — Core reasoning executed using `hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8` across both Research Planning and Synthesis nodes. All inference runs on Crusoe Cloud GPU infrastructure via the OpenAI-compatible API at `api.inference.crusoecloud.com`.
- **TrueFoundry (Resilient Agents Track)** — Robust failover, error checkpoints, and event log routing transparently via TrueFoundry AI Gateway to protect critical agent runs. Live chaos demo (Kill Nemotron / Kill Search / Simulate Timeout) proves resilience under real infrastructure failure.

---

<p align="center"><b>SentinelBrief</b> — Because competitive intelligence shouldn't fail silently.</p>
