"""
Research Planner Agent — The strategist of SentinelBrief.

This is the SECOND Nemotron call site (critical for Crusoe prize track).
Before any data fetching happens, the Planner asks Nemotron:
"What should we research, in what order, and why?"

This transforms SentinelBrief from a dumb search-and-summarize tool
into an intelligent research system that REASONS about what to look for.
"""
import json
import asyncio


class PlannerAgent:
    def __init__(self, gateway_client):
        self.llm = gateway_client

    async def plan(self, your_company: str, competitors: list,
                   research_depth: str = "standard") -> dict:
        """
        Generate a prioritized research plan using Nemotron.
        This is the first LLM call in the pipeline — before any searching.
        """
        depth_config = {
            "quick": {"num_queries": 3, "description": "Quick scan — top signals only"},
            "standard": {"num_queries": 7, "description": "Standard weekly briefing"},
            "deep": {"num_queries": 12, "description": "Deep dive — comprehensive analysis"},
        }
        config = depth_config.get(research_depth, depth_config["standard"])

        messages = [
            {
                "role": "system",
                "content": f"""You are SentinelBrief's Research Planner — an elite competitive intelligence strategist.

Your job: Given a company and its competitors, generate exactly {config['num_queries']} prioritized research queries.
These queries will be executed by specialized search agents.

Return a JSON array of objects, each with:
- "query": the exact search query string
- "category": one of "news", "product", "pricing", "hiring"
- "priority": 1 (highest) to 5 (lowest)
- "rationale": one sentence explaining WHY this query matters strategically

Rules:
- Prioritize signals that indicate strategic shifts (funding, leadership changes, pricing moves)
- Include at least one query per category (news, product, pricing, hiring)
- Queries should be specific and time-bounded (e.g., "2025 2026" in the query)
- Think like a CEO — what would change your next board deck?

Respond ONLY with the JSON array. No markdown fences, no commentary."""
            },
            {
                "role": "user",
                "content": f"""Company: {your_company}
Competitors: {', '.join(competitors)}
Research depth: {config['description']}

Generate {config['num_queries']} prioritized research queries."""
            }
        ]

        response = await self.llm.chat(messages)
        queries = self._parse_queries(response.get("content", ""), competitors)

        return {
            "queries": queries,
            "num_queries": len(queries),
            "research_depth": research_depth,
            "used_fallback": response.get("used_fallback", False),
            "model_used": response.get("model_used", "unknown"),
        }

    def _parse_queries(self, content: str, competitors: list) -> list:
        """Parse Nemotron's response into structured queries."""
        if not content:
            return self._default_queries(competitors)

        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            queries = json.loads(cleaned)
            if isinstance(queries, list):
                return queries
        except json.JSONDecodeError:
            pass

        return self._default_queries(competitors)

    def _default_queries(self, competitors: list) -> list:
        """Fallback queries if Nemotron parsing fails."""
        queries = []
        for comp in competitors[:3]:
            queries.extend([
                {"query": f"{comp} latest news funding announcement 2025 2026",
                 "category": "news", "priority": 1,
                 "rationale": f"Track {comp}'s recent funding and major announcements"},
                {"query": f"{comp} product launch features update changelog",
                 "category": "product", "priority": 2,
                 "rationale": f"Monitor {comp}'s product velocity and feature direction"},
                {"query": f"{comp} pricing plans cost",
                 "category": "pricing", "priority": 3,
                 "rationale": f"Track {comp}'s pricing strategy changes"},
                {"query": f"{comp} hiring jobs careers engineering",
                 "category": "hiring", "priority": 4,
                 "rationale": f"Infer {comp}'s strategic priorities from hiring patterns"},
            ])
        return queries[:7]

    async def mock_plan(self, your_company: str, competitors: list,
                        research_depth: str = "standard") -> dict:
        """Return realistic mock queries for UI development."""
        await asyncio.sleep(1.0)
        queries = []
        for i, comp in enumerate(competitors[:3]):
            queries.extend([
                {
                    "query": f"{comp} Series funding round 2025 2026 announcement",
                    "category": "news", "priority": 1,
                    "rationale": f"Funding signals indicate {comp}'s runway and aggression level"
                },
                {
                    "query": f"{comp} new product feature launch AI automation 2026",
                    "category": "product", "priority": 2,
                    "rationale": f"Product launches reveal {comp}'s strategic direction and feature parity threats"
                },
                {
                    "query": f"{comp} pricing page plans enterprise cost per seat",
                    "category": "pricing", "priority": 2,
                    "rationale": f"Pricing changes signal go-to-market strategy shifts"
                },
                {
                    "query": f"{comp} careers jobs hiring engineering AI machine learning",
                    "category": "hiring", "priority": 3,
                    "rationale": f"Hiring patterns reveal what {comp} is building 6-12 months from now"
                },
            ])

        return {
            "queries": queries[:7] if research_depth == "standard" else queries[:12],
            "num_queries": min(7, len(queries)),
            "research_depth": research_depth,
            "used_fallback": False,
            "model_used": "hack-crusoe/Nemotron-3-Nano-30B-A3B-FP8",
        }
