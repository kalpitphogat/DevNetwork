"""
Google News RSS Scraper — free, no API key needed.

Fetches the Google News RSS feed for a company name.
Returns structured results with title, URL, source, and publish date.

Google News RSS endpoint:
  https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en

Robustness:
  - Browser-like User-Agent avoids 403 Forbidden responses
  - 1 automatic retry on transient errors (429, 5xx, network hiccup)
  - Hard timeout handled externally by news_agent._safe()
"""
import asyncio
import re
import httpx
from xml.etree import ElementTree
from backend.tools.tavily_search import _is_search_killed


def _mock_mode() -> bool:
    import os
    return os.getenv("SENTINELBRIEF_MOCK", "false").lower() == "true"


# Browser-like headers — Google News rejects obvious bot User-Agents with 403
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


async def search_google_news(company: str, max_results: int = 8) -> dict:
    """
    Search Google News RSS for a company.
    Returns up to max_results articles with title, url, source, published_date.
    Retries once on transient failure before giving up.
    """
    if _mock_mode():
        if _is_search_killed():
            return {"results": [], "source": "google_news", "confidence": "failed",
                    "error": "Search killed (chaos mode)"}
        return await _mock_google_news(company)

    if _is_search_killed():
        return {"results": [], "source": "google_news", "confidence": "failed",
                "error": "Search killed by operator"}

    query = f'"{company}" funding OR "product launch" OR announcement OR partnership 2026'
    url   = "https://news.google.com/rss/search"
    params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}

    for attempt in range(2):   # try once, retry once on failure
        try:
            async with httpx.AsyncClient(
                timeout=13.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                root = ElementTree.fromstring(resp.content)

            results = []
            for item in root.findall(".//item")[:max_results]:
                title       = _text(item, "title")
                link        = _text(item, "link")
                desc        = _text(item, "description") or ""
                pub         = _text(item, "pubDate") or ""
                src_el      = item.find("source")
                source_name = src_el.text if src_el is not None else "Google News"
                desc_clean  = re.sub(r"<[^>]+>", "", desc)[:250]

                if title and link:
                    results.append({
                        "title":          title,
                        "content":        desc_clean or title,
                        "url":            link,
                        "source_name":    source_name,
                        "published_date": pub,
                    })

            confidence = "high" if results else "partial"
            return {"results": results, "source": "google_news", "confidence": confidence}

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503) and attempt == 0:
                await asyncio.sleep(1.0)
                continue
            print(f"[GoogleNews] HTTP {e.response.status_code} for {company}")
            return {"results": [], "source": "google_news", "confidence": "failed",
                    "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            if attempt == 0:
                await asyncio.sleep(0.8)
                continue
            print(f"[GoogleNews] Failed for {company}: {e}")
            return {"results": [], "source": "google_news", "confidence": "failed",
                    "error": str(e)}

    return {"results": [], "source": "google_news", "confidence": "failed",
            "error": "All retries exhausted"}


def _text(el, tag: str) -> str:
    child = el.find(tag)
    return (child.text or "").strip() if child is not None else ""


async def _mock_google_news(company: str) -> dict:
    await asyncio.sleep(0.4)
    return {
        "results": [
            {
                "title": f"{company} announces major AI partnership with enterprise clients",
                "content": f"{company} has entered into a strategic partnership to expand AI capabilities across enterprise verticals, signalling a pivot toward B2B growth.",
                "url": f"https://techcrunch.com/2026/05/{company.lower().replace(' ','-')}-ai-partnership",
                "source_name": "TechCrunch",
                "published_date": "Sun, 24 May 2026 08:00:00 GMT",
            },
            {
                "title": f"{company} Q1 2026 revenue beats analyst expectations by 12%",
                "content": f"{company} reported strong Q1 results driven by enterprise adoption, beating consensus estimates on both revenue and operating margin.",
                "url": f"https://reuters.com/technology/{company.lower().replace(' ','-')}-earnings-2026",
                "source_name": "Reuters",
                "published_date": "Fri, 22 May 2026 14:00:00 GMT",
            },
            {
                "title": f"{company} expands into APAC markets with new regional headquarters",
                "content": f"{company} opened a new regional office in Singapore to accelerate growth across Southeast Asia and India.",
                "url": f"https://venturebeat.com/{company.lower().replace(' ','-')}-apac-expansion",
                "source_name": "VentureBeat",
                "published_date": "Wed, 20 May 2026 10:30:00 GMT",
            },
        ],
        "source": "google_news",
        "confidence": "high",
    }
