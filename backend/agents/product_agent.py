"""Product Agent — searches for competitor product updates and launches."""
from backend.tools.tavily_search import search_competitor


class ProductAgent:
    async def run(self, competitor: str) -> dict:
        result = await search_competitor(competitor, "product")
        return {
            "category": "product",
            "competitor": competitor,
            "results": result.get("results", []),
            "answer": result.get("answer", ""),
            "source": result.get("source", "unknown"),
            "confidence": result.get("confidence", "failed"),
            "error": result.get("error"),
        }
