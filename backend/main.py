"""
SentinelBrief — FastAPI Backend with Server-Sent Events (SSE).

Endpoints:
- POST /api/brief         — Stream a competitive intelligence briefing via SSE
- POST /api/brief/sync    — Non-streaming version for testing
- GET  /api/health        — Health check
- POST /api/chaos/*       — Kill switches for resilience demo
  - kill-nemotron / revive-nemotron
  - kill-search    / revive-search
  - simulate-timeout (auto-revives after 8s — simulates brownout, not hard kill)
- GET  /api/chaos/status  — Current chaos state
- GET  /api/gateway-logs  — Gateway event log for resilience dashboard
- GET  /api/history       — Recent completed briefing runs from Neon DB
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.briefing import BriefingRequest
from backend.gateway.llm_client import (
    GatewayClient, kill_nemotron, revive_nemotron,
    kill_search, revive_search, get_chaos_status, get_gateway_logs,
    simulate_timeout,
)
from backend.agents.orchestrator import Orchestrator
from backend.tools.database import init_db, get_recent_briefings
from backend.tools.company_lookup import get_display_name, get_parent_company


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    print("=" * 60)
    print("  SentinelBrief Backend Starting")
    print(f"  Mock Mode: {os.getenv('SENTINELBRIEF_MOCK', 'false')}")
    print("=" * 60)
    
    # Initialize connection to Neon PostgreSQL
    init_db()
    
    yield
    print("SentinelBrief Backend Shutting Down")


app = FastAPI(
    title="SentinelBrief API",
    description="Resilient Autonomous Competitive Intelligence Agent",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ───

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mock_mode": os.getenv("SENTINELBRIEF_MOCK", "false").lower() == "true",
        "chaos_status": get_chaos_status(),
    }


# ─── Briefing Endpoints ───

@app.post("/api/brief")
async def generate_briefing(request: BriefingRequest):
    """Main endpoint. Returns a streaming SSE response."""
    async def event_stream():
        gateway = GatewayClient(chaos_mode=request.chaos_mode)
        orchestrator = Orchestrator(gateway)

        status_queue = asyncio.Queue()

        async def status_callback(update: dict):
            await status_queue.put(update)

        async def run_orchestrator():
            try:
                result = await orchestrator.run(
                    your_company=request.your_company,
                    competitors=request.competitors,
                    research_depth=request.research_depth,
                    status_callback=status_callback,
                )
                await status_queue.put({"type": "_result", "data": result})
            except Exception as e:
                await status_queue.put({
                    "type": "error",
                    "message": f"Pipeline error: {str(e)}",
                })
            finally:
                await status_queue.put(None)

        task = asyncio.create_task(run_orchestrator())

        while True:
            update = await status_queue.get()
            if update is None:
                break
            if update.get("type") == "_result":
                result = update["data"]
                yield f"data: {json.dumps({'type': 'complete', 'briefing': result})}\n\n"
            else:
                yield f"data: {json.dumps(update)}\n\n"

        await task

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/brief/sync")
async def generate_briefing_sync(request: BriefingRequest):
    """Non-streaming version for testing."""
    gateway = GatewayClient(chaos_mode=request.chaos_mode)
    orchestrator = Orchestrator(gateway)
    status_log = []

    async def status_callback(update: dict):
        status_log.append(update)

    result = await orchestrator.run(
        your_company=request.your_company,
        competitors=request.competitors,
        research_depth=request.research_depth,
        status_callback=status_callback,
    )

    return {"briefing": result, "status_log": status_log}


# ─── Chaos Engineering Endpoints (TrueFoundry Prize) ───

@app.post("/api/chaos/kill-nemotron")
async def chaos_kill_nemotron():
    """Kill the primary LLM — forces all calls to fallback."""
    kill_nemotron()
    return {"status": "killed", "message": "Nemotron is now DOWN. All LLM calls will route to fallback."}

@app.post("/api/chaos/revive-nemotron")
async def chaos_revive_nemotron():
    """Revive the primary LLM."""
    revive_nemotron()
    return {"status": "revived", "message": "Nemotron is back ONLINE. Primary routing restored."}

@app.post("/api/chaos/kill-search")
async def chaos_kill_search():
    """Kill all search sources."""
    kill_search()
    return {"status": "killed", "message": "Search sources are now DOWN. Data fetchers will report failures."}

@app.post("/api/chaos/revive-search")
async def chaos_revive_search():
    """Revive search sources."""
    revive_search()
    return {"status": "revived", "message": "Search sources are back ONLINE."}

@app.post("/api/chaos/simulate-timeout")
async def chaos_simulate_timeout():
    """
    Simulate a transient LLM timeout/brownout.
    Unlike kill-nemotron (permanent until revived), this auto-revives after 8 seconds —
    just like a real infrastructure brownout. Shows TrueFoundry's retry+fallback path.
    """
    simulate_timeout()
    asyncio.create_task(_auto_revive_after(8))
    return {
        "status": "timeout_simulated",
        "message": "Timeout injected — Nemotron will appear unresponsive for ~8s then auto-recover. Watch the gateway logs.",
        "auto_revive_seconds": 8,
    }


async def _auto_revive_after(seconds: int):
    """Background task: auto-revive Nemotron after a timeout simulation."""
    await asyncio.sleep(seconds)
    revive_nemotron()


@app.get("/api/chaos/status")
async def chaos_status():
    """Get current chaos engineering state."""
    return get_chaos_status()

@app.get("/api/gateway-logs")
async def gateway_logs():
    """Get gateway event log for resilience dashboard."""
    return get_gateway_logs()


# ─── Company Validation ───

@app.get("/api/validate-company")
async def validate_company(name: str):
    """
    Quick check before running a full briefing.
    Returns parent company info and a warning if the name looks invalid.
    """
    name = name.strip()
    warnings = []

    if len(name) < 2:
        warnings.append("Company name is too short.")
    if any(c.isdigit() for c in name) and len(name) < 4:
        warnings.append("This doesn't look like a real company name.")
    if name.lower() in {"test", "asdf", "abc", "company", "example", "foo", "bar"}:
        warnings.append("This looks like a placeholder — enter a real company name for accurate results.")

    parent = get_parent_company(name)
    display = get_display_name(name)

    return {
        "name": name,
        "display_name": display,
        "parent_company": parent,
        "is_product": parent is not None,
        "warnings": warnings,
        "valid": len(warnings) == 0,
    }


# ─── Run History (Neon PostgreSQL) ───

@app.get("/api/history")
async def run_history(limit: int = 10):
    """Get recent completed briefing runs from Neon PostgreSQL."""
    runs = get_recent_briefings(limit=limit)
    return {"runs": runs, "count": len(runs)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
