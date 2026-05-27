"""
Bing News RSS — free, no API key needed, different index from Google News.

Microsoft's Bing News RSS endpoint gives structured news from a completely
different crawler and index than Google, so it catches stories the other
sources miss.

Endpoint:
  https://www.bing.com/news/search?q={query}&format=rss
"""
import asyncio
import re
import httpx
from xml.etree import ElementTree
from backend.tools.tavily_search import _is_search_killed


def _mock_mode() -> bool:
    import os
    return os.getenv("SENTINELBRIEF_MOCK", "false").lower() == "true"


# Browser-like headers to avoid 403 from Bing
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


async def search_bing_news(company: str, max_results: int = 6) -> dict:
    """
    Search Bing News RSS for a company.
    Returns up to max_results articles with title, url, source, snippet.
    """
    if _mock_mode():
        if _is_search_killed():
            return {"results": [], "source": "bing_news", "confidence": "failed",
                    "error": "Search killed (chaos mode)"}
        return await _mock_bing_news(company)

    if _is_search_killed():
        return {"results": [], "source": "bing_news", "confidence": "failed",
                "error": "Search killed by operator"}

    # Bing News RSS returns best results with a short query.
    # Long keyword-stuffed queries return 0 results.
    # Quoting the name keeps Bing focused when the name is also a common word.
    query = f'"{company}"'
    url   = "https://www.bing.com/news/search"
    params = {"q": query, "format": "rss"}

    # Try with retry on transient failures
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(
                timeout=14.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                root = ElementTree.fromstring(resp.content)

            results = []
            items = root.findall(".//item")[:max_results]
            for item in items:
                title      = _text(item, "title")
                link       = _text(item, "link")
                desc       = _text(item, "description") or ""
                pub        = _text(item, "pubDate") or ""
                # Bing uses <source> element for publication name
                src_el     = item.find("source")
                source_name = src_el.text if src_el is not None else "Bing News"
                desc_clean = re.sub(r"<[^>]+>", "", desc)[:250]

                if title and link:
                    results.append({
                        "title": title,
                        "content": desc_clean or title,
                        "url": link,
                        "source_name": source_name,
                        "published_date": pub,
                    })

            if results:
                return {
                    "results": results,
                    "source": "bing_news",
                    "confidence": "high",
                }

            # Got empty results — Bing returns 200 with an empty feed sometimes
            if attempt == 0:
                await asyncio.sleep(0.5)
                continue
            return {"results": [], "source": "bing_news", "confidence": "partial",
                    "error": "No results from Bing News RSS"}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt == 0:
                await asyncio.sleep(1.0)
                continue
            print(f"[BingNews] HTTP error for {company}: {e.response.status_code}")
            return {"results": [], "source": "bing_news", "confidence": "failed",
                    "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            if attempt == 0:
                await asyncio.sleep(0.5)
                continue
            print(f"[BingNews] Failed for {company}: {e}")
            return {"results": [], "source": "bing_news", "confidence": "failed",
                    "error": str(e)}

    return {"results": [], "source": "bing_news", "confidence": "failed",
            "error": "All retries exhausted"}


def _text(el, tag: str) -> str:
    child = el.find(tag)
    return (child.text or "").strip() if child is not None else ""


async def _mock_bing_news(company: str) -> dict:
    await asyncio.sleep(0.35)
    slug = company.lower().replace(" ", "-")
    return {
        "results": [
            {
                "title": f"{company} unveils next-generation AI platform at developer conference",
                "content": (
                    f"{company} revealed its expanded AI platform including autonomous "
                    f"agents, real-time data connectors, and native LLM integration at "
                    f"its annual developer summit this month."
                ),
                "url": f"https://venturebeat.com/ai/{slug}-ai-platform-2026",
                "source_name": "VentureBeat",
                "published_date": "Mon, 26 May 2026 10:00:00 GMT",
            },
            {
                "title": f"{company} poaches three senior executives from rival firm",
                "content": (
                    f"{company} has hired a new VP of Engineering, Chief Revenue Officer, "
                    f"and Head of Product from a direct competitor, signalling aggressive "
                    f"talent acquisition ahead of a major product cycle."
                ),
                "url": f"https://businessinsider.com/{slug}-executive-hires-2026",
                "source_name": "Business Insider",
                "published_date": "Sat, 24 May 2026 16:30:00 GMT",
            },
            {
                "title": f"Why analysts are upgrading {company} after its latest earnings beat",
                "content": (
                    f"Multiple sell-side analysts raised price targets on {company} after "
                    f"it reported ARR growth of 41% YoY, beating consensus by 9 points "
                    f"and raising full-year guidance."
                ),
                "url": f"https://seekingalpha.com/{slug}-earnings-upgrade-2026",
                "source_name": "Seeking Alpha",
                "published_date": "Thu, 22 May 2026 09:15:00 GMT",
            },
        ],
        "source": "bing_news",
        "confidence": "high",
    }
