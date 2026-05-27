# SentinelBrief — Resilient Autonomous Competitive Intelligence Agent

A resilient multi-agent intelligence system powered by **Nemotron-70B on Crusoe Cloud**, orchestrated with stateful checkpoints, and hardened by **TrueFoundry AI Gateway** — that autonomously researches competitors and delivers structured briefings.

---

## 🏗️ Production Tech Stack & Architecture

SentinelBrief is built to be production-grade and fully resilient to infrastructure failures, utilizing the following architecture:

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

### Infrastructure Mapping:
1. **Frontend**: Next.js / Vite deployed to **Vercel**
2. **API Layer**: Python FastAPI deployed to **Render**
3. **Persistant DB**: PostgreSQL hosted on **Neon**
4. **Checkpoints & Caching**: Redis hosted on **Upstash**
5. **Resilience Gateway**: **TrueFoundry AI Gateway** managing inference timeouts and fallback switching.

---

## ⚡ Key Features

*   **Research Planner**: Generating prioritized multi-agent queries before searching.
*   **Parallel Fetcher Agents**: 4 specialized scrapers (News, Product, Pricing, Hiring) run concurrently.
*   **VeracityAI Confidence Scoring**: Claim-level tag evaluations (`[VERIFIED: url]`, `[INFERRED]`).
*   **Live Checkpoint Resume**: Mid-run crashes automatically resume from the last completed node via Redis state caching.
*   **Infrastructure Chaos Demo**: Live control panel to inject failover triggers in real-time.

---

## 🚀 1-Click Deployment Guide

Follow these steps to deploy SentinelBrief to production in under 5 minutes:

### 1. Database Setup (Neon PostgreSQL)
1. Register for a free PostgreSQL database at [Neon.tech](https://neon.tech).
2. Copy your connection string (`postgresql://...`).
3. Set this as `DATABASE_URL` in your backend environment variables.

### 2. State & Cache Setup (Upstash Redis)
1. Register for a free serverless Redis cluster at [Upstash.com](https://upstash.com).
2. Copy your Redis URL (`rediss://...`).
3. Set this as `REDIS_URL` in your backend environment variables.

### 3. Backend Deployment (Render)
1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com) and link your GitHub account.
3. Click **"New" -> "Blueprint"** and select your repository.
4. Render will read the `render.yaml` specification, create your backend service, and prompt you to input the environment keys:
   * `DATABASE_URL` (Neon Connection string)
   * `REDIS_URL` (Upstash connection string)
   * `TAVILY_API_KEY` (Tavily search API)
   * `TRUEFOUNDRY_GATEWAY_URL` & `TRUEFOUNDRY_API_KEY` (TrueFoundry Gateway credentials)

### 4. Frontend Deployment (Vercel)
1. Register/Login at [Vercel.com](https://vercel.com).
2. Import your GitHub repository.
3. Select `frontend` as the root directory for the build.
4. Set environment variables if needed, then hit **Deploy**.
5. Vercel automatically reads `vercel.json` to proxy all `/api` requests to your Render backend endpoint.

---

## 🛠️ Local Development Setup

1. Copy `.env.example` to `.env` and fill in keys (or set `SENTINELBRIEF_MOCK=true` to run without API keys).
2. Install & Start Backend:
   ```bash
   pip install -r requirements.txt
   python -m uvicorn backend.main:app --reload --port 8000
   ```
3. Install & Start Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🏆 sponsor track alignment

*   **Crusoe Cloud (NVIDIA DGX Track)**: Core reasoning executed using `nvidia/nemotron-3-super-49b-v1` across both Research Planning and Synthesis nodes.
*   **TrueFoundry (Resilient Agents Track)**: Robust failover, error checkpoints, and event logs routing transparently via TrueFoundry Gateway to protect critical runs.
