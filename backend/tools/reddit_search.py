"""
Reddit Search — free JSON API, no key needed.

Reddit's public search endpoint returns posts mentioning a company.
Great for catching community buzz, product launches, and complaints
that don't appear in traditional news.

Endpoint:
  https://www.reddit.com/search.json?q={query}&sort=relevance&limit=18&t=year

Robustness:
  - Descriptive User-Agent (Reddit 429s generic bots faster than named ones)
  - 1 automatic retry with backoff on rate-limit (429) or server errors
  - Hard timeout handled externally by news_agent._safe()
"""
import asyncio
import httpx
from backend.tools.tavily_search import _is_search_killed


def _mock_mode() -> bool:
    import os
    return os.getenv("SENTINELBRIEF_MOCK", "false").lower() == "true"


# Reddit is more lenient with descriptive User-Agents that include contact info
_HEADERS = {
    "User-Agent": (
        "SentinelBrief/2.0 (Hackathon competitive-intelligence bot; "
        "contact: sentinelbrief@devnetwork.ai)"
    ),
}


async def search_reddit(company: str, max_results: int = 6) -> dict:
    """
    Search Reddit for posts mentioning the company.
    Retries once on 429 / 5xx before giving up.
    """
    if _mock_mode():
        if _is_search_killed():
            return {"results": [], "source": "reddit", "confidence": "failed",
                    "error": "Search killed (chaos mode)"}
        return await _mock_reddit(company)

    if _is_search_killed():
        return {"results": [], "source": "reddit", "confidence": "failed",
                "error": "Search killed by operator"}

    query = f"{company} product launch funding pricing announcement news"
    url   = "https://www.reddit.com/search.json"
    params = {
        "q":     query,
        "sort":  "relevance",
        "limit": max_results * 3,   # over-fetch; filter low-score posts below
        "t":     "year",
        "type":  "link",
    }

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(
                timeout=12.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

            posts = data.get("data", {}).get("children", [])
            results = []
            for post in posts:
                d         = post.get("data", {})
                title     = d.get("title", "")
                subreddit = d.get("subreddit", "")
                score     = d.get("score", 0)
                url_post  = f"https://reddit.com{d.get('permalink', '')}"
                selftext  = (d.get("selftext", "") or "")[:200]
                content   = selftext if selftext else title

                if title and score >= 1:
                    results.append({
                        "title":          f"[r/{subreddit}] {title}",
                        "content":        content,
                        "url":            url_post,
                        "score":          score,
                        "published_date": "",
                    })

            # Sort by score and take best max_results
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:max_results]

            confidence = "high" if results else "partial"
            return {"results": results, "source": "reddit", "confidence": confidence}

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503) and attempt == 0:
                await asyncio.sleep(1.5)
                continue
            print(f"[Reddit] HTTP {e.response.status_code} for {company}")
            return {"results": [], "source": "reddit", "confidence": "failed",
                    "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            if attempt == 0:
                await asyncio.sleep(0.8)
                continue
            print(f"[Reddit] Failed for {company}: {e}")
            return {"results": [], "source": "reddit", "confidence": "failed",
                    "error": str(e)}

    return {"results": [], "source": "reddit", "confidence": "failed",
            "error": "All retries exhausted"}


async def _mock_reddit(company: str) -> dict:
    await asyncio.sleep(0.3)
    slug = company.lower().replace(" ", "")
    return {
        "results": [
            {
                "title": f"[r/SaaS] Anyone else noticed {company} changed their pricing this week?",
                "content": f"Just saw that {company} quietly updated their pricing page. Team plan went from $12 to $15/user. No announcement email. Thoughts?",
                "url": f"https://reddit.com/r/SaaS/comments/{slug}_pricing_change",
                "score": 312,
                "published_date": "",
            },
            {
                "title": f"[r/startups] {company} just launched a feature that kills our entire product",
                "content": f"We've been building X for 8 months and {company} just shipped it natively. Back to the drawing board. At least the validation is there...",
                "url": f"https://reddit.com/r/startups/comments/{slug}_feature_launch",
                "score": 847,
                "published_date": "",
            },
            {
                "title": f"[r/entrepreneur] {company} raised another round — anyone have the deck?",
                "content": f"Heard {company} closed a significant round. The velocity of their hiring suggests they are going very aggressive on enterprise sales.",
                "url": f"https://reddit.com/r/entrepreneur/comments/{slug}_funding",
                "score": 156,
                "published_date": "",
            },
        ],
        "source": "reddit",
        "confidence": "high",
    }
