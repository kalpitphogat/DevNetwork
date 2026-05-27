"""
News Agent — 5-source parallel news intelligence.

Sources fired IN PARALLEL, each with independent timeout isolation:
  1. Tavily        — structured web search with source URLs (primary, paid key)
  2. Google News   — RSS feed from Google News (free, no key)
  3. HackerNews    — tech community signals, funding/launch buzz (free)
  4. Reddit        — community discussions, product reactions (free)
  5. Bing News     — Microsoft's index — different coverage from Google (free)

Key guarantees:
  - No single source can block or crash the whole pipeline (_safe wrapper)
  - Each source has its own 14-second timeout
  - Results deduplicated by URL, ranked by source quality
  - Capped at 18 total to keep synthesis prompt focused
  - Parent company lookups for product brands (Confluence→Atlassian)
"""
import asyncio
from backend.tools.tavily_search import search_competitor, search_hackernews
from backend.tools.google_news import search_google_news
from backend.tools.reddit_search import search_reddit
from backend.tools.bing_news import search_bing_news
from backend.tools.company_lookup import get_search_name, get_parent_company

# Per-source timeout (seconds). Each source fails independently if it exceeds this.
_SOURCE_TIMEOUT = 14.0

_EMPTY_RESULT = {
    "results": [], "confidence": "failed",
    "error": "source timed out or raised an unexpected error",
}


async def _safe(coro, label: str = "source") -> dict:
    """
    Isolate a source call: apply a hard timeout and catch ALL exceptions.
    Returns a failed-confidence dict instead of propagating, so one bad
    source never prevents the others from completing.
    """
    try:
        return await asyncio.wait_for(coro, timeout=_SOURCE_TIMEOUT)
    except asyncio.TimeoutError:
        print(f"[NewsAgent] {label} timed out after {_SOURCE_TIMEOUT}s")
        return {**_EMPTY_RESULT, "error": f"{label} timed out after {_SOURCE_TIMEOUT}s"}
    except Exception as e:
        print(f"[NewsAgent] {label} error: {e}")
        return {**_EMPTY_RESULT, "error": str(e)}


class NewsAgent:
    async def run(self, competitor: str) -> dict:
        """
        Run all 5 news sources in parallel and merge results.
        Uses parent company name where appropriate (e.g. Confluence → Atlassian).
        """
        search_name = get_search_name(competitor, "news")
        parent      = get_parent_company(competitor)

        # ── Fire all 5 sources simultaneously, each isolated ──
        tasks = [
            _safe(search_competitor(search_name, "news"),    "tavily"),
            _safe(search_google_news(search_name),           "google_news"),
            _safe(search_hackernews(search_name),            "hackernews"),
            _safe(search_reddit(search_name),                "reddit"),
            _safe(search_bing_news(search_name),             "bing_news"),
        ]

        # If competitor is a product brand, fire parent company on
        # HackerNews + Google News + Bing for extra coverage
        parent_hn_task    = None
        parent_gnews_task = None
        parent_bing_task  = None

        if parent:
            tasks.append(_safe(search_hackernews(parent),    "hackernews_parent"))
            tasks.append(_safe(search_google_news(parent),   "google_news_parent"))
            tasks.append(_safe(search_bing_news(parent),     "bing_news_parent"))
            results = await asyncio.gather(*tasks)
            (
                tavily_result,
                gnews_result,
                hn_result,
                reddit_result,
                bing_result,
                hn_parent_result,
                gnews_parent_result,
                bing_parent_result,
            ) = results

            # Merge parent results in
            hn_result["results"] = (
                hn_result.get("results", []) +
                hn_parent_result.get("results", [])
            )
            gnews_result["results"] = (
                gnews_result.get("results", []) +
                gnews_parent_result.get("results", [])
            )
            bing_result["results"] = (
                bing_result.get("results", []) +
                bing_parent_result.get("results", [])
            )
        else:
            results = await asyncio.gather(*tasks)
            (
                tavily_result,
                gnews_result,
                hn_result,
                reddit_result,
                bing_result,
            ) = results

        # ── Merge & deduplicate by URL ──
        all_results = []
        seen_urls   = set()

        # Priority: Tavily > Google News > Bing News > HackerNews > Reddit
        source_priority = [
            (tavily_result,  "tavily"),
            (gnews_result,   "google_news"),
            (bing_result,    "bing_news"),
            (hn_result,      "hackernews"),
            (reddit_result,  "reddit"),
        ]

        for source_data, source_name in source_priority:
            for r in source_data.get("results", []):
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    r["_source"] = source_name
                    all_results.append(r)

        # Cap at 18 results (5 sources × ~3-6 each)
        all_results = all_results[:18]

        # ── Overall confidence: best-of-5 ──
        source_results = [tavily_result, gnews_result, bing_result,
                          hn_result, reddit_result]
        confidences = [r.get("confidence", "failed") for r in source_results]
        if "high" in confidences:
            confidence = "high"
        elif "partial" in confidences:
            confidence = "partial"
        else:
            confidence = "failed"

        # Track which sources actually returned results
        sources_used = [
            label for label, r in [
                ("tavily",      tavily_result),
                ("google_news", gnews_result),
                ("bing_news",   bing_result),
                ("hackernews",  hn_result),
                ("reddit",      reddit_result),
            ]
            if r.get("confidence") != "failed" and r.get("results")
        ]

        return {
            "category":     "news",
            "competitor":   competitor,
            "search_name":  search_name,
            "parent":       parent,
            "results":      all_results,
            "answer":       tavily_result.get("answer", ""),
            "source":       "+".join(sources_used) if sources_used else "none",
            "sources_used": sources_used,
            "result_count": len(all_results),
            "confidence":   confidence,
            "error":        tavily_result.get("error") if confidence == "failed" else None,
        }
