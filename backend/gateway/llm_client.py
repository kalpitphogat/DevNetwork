"""
TrueFoundry AI Gateway Client — with Chaos Engineering Kill Switches.

All LLM calls go through here. TrueFoundry acts as the proxy —
it handles fallback, logging, traces. This client adds:
- Kill switches for live demo (simulate Nemotron brownout)
- Gateway event logging (every call recorded for resilience dashboard)
- Automatic fallback to OpenAI when primary fails

The kill switches are what win the TrueFoundry prize — judges can
trigger failures LIVE and watch the system recover.
"""
import os
import json
import asyncio
import time
from datetime import datetime, timezone
from openai import AsyncOpenAI

MOCK_MODE = os.getenv("SENTINELBRIEF_MOCK", "false").lower() == "true"

# ─── Chaos Engineering State ───
_nemotron_killed = False
_search_killed = False
_gateway_log = []  # List of event dicts, max 100 entries
_MAX_LOG_SIZE = 100


def kill_nemotron():
    global _nemotron_killed
    _nemotron_killed = True
    _log_event("CHAOS", "nemotron", None, 0, False, "Nemotron KILLED by operator")

def revive_nemotron():
    global _nemotron_killed
    _nemotron_killed = False
    _log_event("REVIVE", "nemotron", "nemotron", 0, False, "Nemotron REVIVED by operator")

def simulate_timeout():
    """
    Simulate a transient brownout: kills Nemotron temporarily.
    The /api/chaos/simulate-timeout endpoint auto-revives after 8 seconds.
    Produces a TIMEOUT event in the gateway log (not CHAOS) for cleaner demo narration.
    """
    global _nemotron_killed
    _nemotron_killed = True
    _log_event("TIMEOUT", "nemotron", None, 0, True,
               "Brownout injected — gateway detecting timeout, routing to fallback")

def kill_search():
    global _search_killed
    _search_killed = True
    _log_event("CHAOS", "search", None, 0, False, "Search sources KILLED by operator")

def revive_search():
    global _search_killed
    _search_killed = False
    _log_event("REVIVE", "search", "search", 0, False, "Search sources REVIVED by operator")

def is_search_killed() -> bool:
    return _search_killed

def get_chaos_status() -> dict:
    return {"nemotron_killed": _nemotron_killed, "search_killed": _search_killed}

def get_gateway_logs() -> list:
    return list(_gateway_log)

def _log_event(event_type: str, model_attempted: str, model_used: str,
               latency_ms: float, fallback_triggered: bool, message: str = ""):
    global _gateway_log
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "model_attempted": model_attempted,
        "model_used": model_used,
        "latency_ms": round(latency_ms, 1),
        "fallback_triggered": fallback_triggered,
        "message": message,
        "success": event_type not in ("ERROR", "CHAOS"),
    }
    _gateway_log.append(entry)
    if len(_gateway_log) > _MAX_LOG_SIZE:
        _gateway_log.pop(0)


class GatewayClient:
    def __init__(self, chaos_mode: bool = False):
        self.chaos_mode = chaos_mode

        gateway_url = os.getenv("TRUEFOUNDRY_GATEWAY_URL", "")
        gateway_key = os.getenv("TRUEFOUNDRY_API_KEY", "")

        if not gateway_url:
            gateway_url = os.getenv("CRUSOE_BASE_URL", "https://api.inference.crusoecloud.com/v1")
            gateway_key = os.getenv("CRUSOE_API_KEY", "")

        self.client = AsyncOpenAI(
            base_url=gateway_url,
            api_key=gateway_key,
        ) if not MOCK_MODE else None

        self.primary_model = "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8"
        self.fallback_model = "gpt-4o"

    async def chat(self, messages: list, stream: bool = False) -> dict:
        """
        Single entry point for all LLM calls.
        Checks kill switch → tries primary → falls back → logs everything.
        """
        if MOCK_MODE:
            return await self._mock_chat(messages)

        # Check kill switch FIRST — simulates Nemotron being down
        if _nemotron_killed or self.chaos_mode:
            _log_event("BLOCKED", self.primary_model, None, 0, True,
                       "Primary model killed — routing to fallback")
            return await self._fallback_chat(messages)

        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=4096,
            )
            latency = (time.time() - start) * 1000
            used_fallback = self._check_fallback_used(response)
            model_used = response.model or self.primary_model

            _log_event("SUCCESS", self.primary_model, model_used,
                       latency, used_fallback,
                       f"Completed in {latency:.0f}ms")

            return {
                "content": self._extract_content(response.choices[0].message),
                "used_fallback": used_fallback,
                "model_used": model_used,
            }
        except Exception as e:
            latency = (time.time() - start) * 1000
            _log_event("ERROR", self.primary_model, None, latency, True,
                       f"Primary failed: {str(e)[:100]}")
            print(f"[GatewayClient] Primary LLM failed: {e}")
            return await self._fallback_chat(messages)

    async def _fallback_chat(self, messages: list) -> dict:
        """Direct fallback to OpenAI when primary fails."""
        start = time.time()
        try:
            fallback_client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY", ""),
            )
            response = await fallback_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            latency = (time.time() - start) * 1000
            _log_event("FALLBACK", "gpt-4o", "gpt-4o", latency, True,
                       f"Fallback completed in {latency:.0f}ms")

            return {
                "content": response.choices[0].message.content,
                "used_fallback": True,
                "model_used": "gpt-4o (fallback)",
            }
        except Exception as e:
            latency = (time.time() - start) * 1000
            _log_event("ERROR", "gpt-4o", None, latency, True,
                       f"Fallback also failed: {str(e)[:100]}")
            return {
                "content": None,
                "error": str(e),
                "used_fallback": True,
                "model_used": "none — all LLMs unavailable",
            }

    async def _mock_chat(self, messages: list) -> dict:
        """Return realistic mock response for UI development."""
        await asyncio.sleep(1.5)
        user_msg = messages[-1]["content"] if messages else ""

        # Extract company and competitors if present
        your_company = "Notion"
        competitors = ["Coda", "Confluence"]

        for line in user_msg.split("\n"):
            line = line.strip()
            if line.lower().startswith("company being monitored:"):
                your_company = line.split(":", 1)[1].strip()
            elif line.lower().startswith("company:"):
                your_company = line.split(":", 1)[1].strip()
            elif line.startswith("===") and line.endswith("==="):
                comp_name = line.replace("===", "").strip().title()
                if comp_name and comp_name not in competitors and comp_name.upper() != your_company.upper():
                    if competitors == ["Coda", "Confluence"]:
                        competitors = []
                    competitors.append(comp_name)

        # Simulate kill switch in mock mode
        if _nemotron_killed or self.chaos_mode:
            _log_event("BLOCKED", "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8", None, 0, True,
                       "Primary model unavailable — triggering fallback")
            await asyncio.sleep(0.5)
            _log_event("FALLBACK", "openai/gpt-4o", "openai/gpt-4o", 800, True,
                       "Fallback routing completed successfully")
            model_name = "openai/gpt-4o"
            used_fallback = True
        else:
            _log_event("SUCCESS", "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8", "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8",
                       1200, False, "Primary model completed request")
            model_name = "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8"
            used_fallback = False

        if "research plan" in user_msg.lower() or "prioriti" in user_msg.lower():
            mock_content = self._get_mock_planner_response(user_msg)
        elif "synthesis" in user_msg.lower() or "competitive intelligence" in user_msg.lower():
            mock_content = self._get_mock_synthesis(your_company, competitors)
        else:
            mock_content = self._get_mock_analysis(user_msg)

        return {
            "content": mock_content,
            "used_fallback": used_fallback,
            "model_used": model_name,
        }

    def _extract_content(self, message) -> str:
        """
        Extract text content from an LLM response message.
        Nemotron-3-Nano is a reasoning model: it returns content in the
        'reasoning' field instead of 'content'. This method checks both.
        """
        # Standard content field
        if message.content:
            return message.content
        # Reasoning model: content is in the 'reasoning' attribute
        reasoning = getattr(message, "reasoning", None)
        if reasoning:
            return reasoning
        # Last resort: check raw dict if available
        raw = None
        if hasattr(message, "model_dump"):
            raw = message.model_dump()
        elif hasattr(message, "__dict__"):
            raw = message.__dict__
        if raw and raw.get("reasoning"):
            return raw["reasoning"]
        return message.content or ""

    def _check_fallback_used(self, response) -> bool:
        return "gpt" in (response.model or "").lower()

    def _get_mock_planner_response(self, context: str) -> str:
        return json.dumps([
            {"query": "Coda Series D funding 2026 announcement", "category": "news", "priority": 1,
             "rationale": "Recent funding signals aggressive expansion and runway extension"},
            {"query": "Coda AI automation builder features launch 2026", "category": "product", "priority": 1,
             "rationale": "AI feature launches directly threaten our core value proposition"},
            {"query": "Coda pricing plans enterprise cost 2026", "category": "pricing", "priority": 2,
             "rationale": "Pricing changes indicate go-to-market strategy shifts"},
            {"query": "Coda hiring engineering jobs careers AI", "category": "hiring", "priority": 2,
             "rationale": "Engineering hires reveal product roadmap 6-12 months out"},
            {"query": "Confluence Atlassian layoffs restructuring 2026", "category": "news", "priority": 1,
             "rationale": "Competitor weakness creates market opportunity windows"},
            {"query": "Confluence product updates features 2026", "category": "product", "priority": 3,
             "rationale": "Stalled product development confirms restructuring hypothesis"},
            {"query": "Confluence pricing enterprise changes", "category": "pricing", "priority": 3,
             "rationale": "Price increases during restructuring could drive customer churn to us"},
        ])

    def _get_mock_synthesis(self, your_company: str, competitors: list) -> str:
        # Title case everything for beauty
        yc = your_company.strip().title()
        comps = [c.strip().title() for c in competitors] if competitors else ["Coda", "Confluence"]
        
        # Build key findings
        key_findings = []
        if len(comps) >= 1:
            c1 = comps[0]
            key_findings.append(f"{c1} raised major capital round — signals aggressive expansion into enterprise AI [VERIFIED: https://techcrunch.com/2026/05/{c1.lower().replace(' ', '-')}-funding]")
            key_findings.append(f"{c1} launched free AI entry tier — direct attack on {yc}'s core acquisition channel [VERIFIED: https://{c1.lower().replace(' ', '')}.com/blog/ai-free]")
        if len(comps) >= 2:
            c2 = comps[1]
            key_findings.append(f"{c2} parent company announced corporate restructuring — creates a 6-month customer migration window for {yc} [VERIFIED: https://reuters.com/{c2.lower().replace(' ', '-')}-restructuring]")
            key_findings.append(f"{c2} hiring freeze confirms strategic retreat from core collaboration space [INFERRED]")
        else:
            key_findings.append(f"Competitor pricing adjustments indicate defensive product positioning [INFERRED]")
            
        key_findings.append(f"Market consolidation accelerating — competitors moving rapidly in AI-native capabilities [INFERRED]")

        # Build competitor detailed entries
        competitor_entries = []
        for i, comp in enumerate(comps):
            urgency = "HIGH" if i == 0 else "MEDIUM"
            comp_domain = comp.lower().replace(' ', '')
            
            entry = {
                "name": comp,
                "urgency": urgency,
                "news": {
                    "summary": (
                        f"5-source intelligence sweep (Tavily, Google News, Bing News, HackerNews, Reddit) confirms {comp} is accelerating its Enterprise AI pivot [VERIFIED: https://techcrunch.com/2026/05/{comp_domain}-news]. "
                        f"Community signals on Reddit and HackerNews corroborate a strategic shift [VERIFIED: https://news.google.com/rss/search?q={comp_domain}]. "
                        f"Bing News surfaces executive hiring and earnings beat coverage not indexed by Google [VERIFIED: https://venturebeat.com/ai/{comp_domain}-ai-platform-2026]."
                    ),
                    "key_points": [
                        f"Google News: 3 articles this week covering {comp}'s enterprise expansion [VERIFIED: https://news.google.com/rss/search?q={comp_domain}+enterprise]",
                        f"Bing News: {comp} poached 3 senior execs from rival — signals aggressive product cycle ahead [VERIFIED: https://businessinsider.com/{comp_domain}-executive-hires-2026]",
                        f"Reddit r/SaaS: Community reports {comp} quietly updated pricing — no announcement email [VERIFIED: https://reddit.com/r/SaaS/search?q={comp_domain}]",
                        f"HackerNews: {comp} launch post reached top 10 — 400+ upvotes signal strong developer interest [VERIFIED: https://news.ycombinator.com/item?id=4012{i}456]",
                    ],
                    "confidence": "green",
                    "sources_used": ["tavily", "google_news", "bing_news", "hackernews", "reddit"],
                },
                "product": {
                    "summary": f"Launched new generative AI templates and automated design tools [VERIFIED: https://{comp_domain}.com/product/ai-tools]. The entry tier now includes complimentary AI credits [VERIFIED: https://{comp_domain}.com/pricing].",
                    "key_points": [
                        f"Lower barriers to user acquisition and testing [VERIFIED: https://{comp_domain}.com/pricing]",
                        f"New developer API platform for ecosystem growth [INFERRED]"
                    ],
                    "confidence": "green"
                },
                "pricing": {
                    "summary": f"Introduced highly competitive pricing for enterprise seats starting at $25/user/month [VERIFIED: https://{comp_domain}.com/pricing]. Team plans restructured to attract mid-market accounts [INFERRED].",
                    "key_points": [
                        f"Enterprise seat pricing aggressively undercuts {yc} list prices [INFERRED]"
                    ],
                    "confidence": "green"
                },
                "hiring": {
                    "summary": f"Posted 10+ new product engineering and strategic sales positions globally [VERIFIED: https://linkedin.com/company/{comp_domain}/jobs]. Signal: upmarket enterprise push [INFERRED].",
                    "key_points": [
                        f"Increased hiring in machine learning and core AI teams [INFERRED]"
                    ],
                    "confidence": "amber"
                },
                "strategic_implication": f"{comp} is executing an aggressive land-and-expand strategy in enterprise AI [INFERRED]. The new low-barrier entry tier and dedicated sales hires signal intent to capture {yc}'s premium customer segments. Response: accelerate product feature launch and protect high-value cohorts."
            }
            competitor_entries.append(entry)

        # Top action recommendation
        top_action = f"Launch targeted product response to {comps[0]}'s new AI capabilities and optimize marketing campaigns to capture search volume within 30 days."

        strategic_implications = [
            f"URGENT: {comps[0]}'s new free AI features are a direct attack on {yc}'s user acquisition. Respond rapidly or risk top-of-funnel contraction [INFERRED].",
            f"OPPORTUNITY: Market consolidation and competitor pivots create a 6-month window to win over churned enterprise accounts. Consider dedicated migration landing pages [INFERRED].",
            f"SIGNAL: Rapid adoption of generative features indicates a permanent market shift towards AI-native collaboration workflows [INFERRED]."
        ]

        nemotron_synthesis = [
            f"URGENT: {comps[0]}'s AI feature launch threatens {yc}'s entry funnel. Mitigate with rapid counter-features.",
            f"OPPORTUNITY: Leverage integration advantages to capture users migrating from legacy systems.",
            f"SIGNAL: Market consolidation is accelerating, bifurcation between AI-native and static suites is confirmed."
        ]

        return json.dumps({
            "executive_summary": {
                "key_findings": key_findings,
                "landscape_shift": "SHIFTING",
                "top_action": top_action,
                "overall_confidence": "green"
            },
            "competitors": competitor_entries,
            "strategic_implications": strategic_implications,
            "nemotron_synthesis": nemotron_synthesis
        })

    def _get_mock_analysis(self, context: str) -> str:
        return "Based on the available data, this competitor is showing moderate activity in the market with no immediate threats detected. Monitoring should continue on a weekly cadence. [INFERRED]"
