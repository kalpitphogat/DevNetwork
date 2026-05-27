"""Pricing Agent — searches for competitor pricing and plan changes."""
from backend.tools.tavily_search import search_competitor


class PricingAgent:
    async def run(self, competitor: str) -> dict:
        result = await search_competitor(competitor, "pricing")
        return {
            "category": "pricing",
            "competitor": competitor,
            "results": result.get("results", []),
            "answer": result.get("answer", ""),
            "source": result.get("source", "unknown"),
            "confidence": result.get("confidence", "failed"),
            "error": result.get("error"),
        }
