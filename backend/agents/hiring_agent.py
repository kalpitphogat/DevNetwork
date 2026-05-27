"""Hiring Agent — searches for competitor hiring signals and job postings.

Uses parent company lookup so that product brands (e.g. Confluence → Atlassian)
return meaningful hiring signals instead of near-zero results.
"""
from backend.tools.tavily_search import search_competitor
from backend.tools.company_lookup import get_parent_company, get_search_name


class HiringAgent:
    async def run(self, competitor: str) -> dict:
        search_name = get_search_name(competitor, "hiring")
        parent = get_parent_company(competitor)

        result = await search_competitor(search_name, "hiring")

        return {
            "category": "hiring",
            "competitor": competitor,
            "parent_company": parent,
            "search_name": search_name,
            "results": result.get("results", []),
            "answer": result.get("answer", ""),
            "source": result.get("source", "unknown"),
            "confidence": result.get("confidence", "failed"),
            "error": result.get("error"),
        }
