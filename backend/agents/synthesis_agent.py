"""
Synthesis Agent — The brain of SentinelBrief.

This is NOT summarization. This is REASONING with VeracityAI.

The prompt instructs Nemotron to:
1. Identify what each competitor is doing
2. Reason about the IMPLICATIONS for your company
3. Tag EVERY factual claim as [VERIFIED: url], [INFERRED], or [UNVERIFIED]
4. Generate an executive summary with landscape shift rating
5. Provide specific action recommendations

This two-pass approach (synthesis → tag validation) is what makes
SentinelBrief's confidence scoring reliable.
"""
import json


class SynthesisAgent:
    def __init__(self, gateway_client):
        self.llm = gateway_client

    async def synthesize(self, your_company: str, research: dict,
                         status_callback=None) -> dict:

        context = self._format_research(research)

        messages = [
            {
                "role": "system",
                "content": """You are SentinelBrief, an elite competitive intelligence analyst. Today is May 2026.
Your job is not to summarize — it is to REASON about implications and threats.

CRITICAL RULES FOR CONFIDENCE TAGGING:
For EVERY factual claim in your output, you MUST append one of these tags:
  [VERIFIED: <url>]  — claim directly supported by a retrieved source with that URL.
                       Every "Source URL:" line in the research data is a valid VERIFIED URL.
                       Use as many VERIFIED tags as possible — aim for at least 4 per competitor.
  [INFERRED]         — claim derived by cross-referencing 2+ sources or logical reasoning
  [UNVERIFIED]       — claim based on model knowledge only, no source in the data
Never omit the tag. If uncertain, use [UNVERIFIED].
ALWAYS prefer [VERIFIED: url] over [INFERRED] when any Source URL exists for the claim.

OUTPUT QUALITY STANDARDS:
- key_findings: at least 4 findings, each with a confidence tag
- Each competitor news summary: mention specific articles/posts from the research data
- top_action: concrete, specific, time-bound (e.g. "Within 2 weeks, launch X to counter Y")
- nemotron_synthesis: exactly 3 high-signal strategic insights; each must be actionable
- urgency: HIGH if competitor shows funding + product launch in data; MEDIUM otherwise

You MUST respond with valid JSON matching this exact schema:
{
  "executive_summary": {
    "key_findings": ["Finding 1 [VERIFIED: url]", "Finding 2 [INFERRED]", ...],
    "landscape_shift": "STABLE" | "SHIFTING" | "MAJOR_CHANGE",
    "top_action": "The single most important thing the CEO should do this week",
    "overall_confidence": "green" | "amber" | "red"
  },
  "competitors": [
    {
      "name": "CompetitorName",
      "urgency": "HIGH" | "MEDIUM" | "LOW",
      "news": {"summary": "...", "key_points": ["point [VERIFIED: url]"], "confidence": "green|amber|red"},
      "product": {"summary": "...", "key_points": ["..."], "confidence": "green|amber|red"},
      "pricing": {"summary": "...", "key_points": ["..."], "confidence": "green|amber|red"},
      "hiring": {"summary": "...", "key_points": ["..."], "confidence": "green|amber|red"},
      "strategic_implication": "Your opinionated analysis [INFERRED]"
    }
  ],
  "strategic_implications": [
    "Implication 1 [INFERRED]",
    "Implication 2 [INFERRED]"
  ],
  "nemotron_synthesis": [
    "Top strategic insight #1",
    "Top strategic insight #2",
    "Top strategic insight #3"
  ]
}

Where data was incomplete or confidence was 'partial' or 'failed',
explicitly note it (e.g., "⚠️ Data unavailable — search source failed [UNVERIFIED]").
Set section confidence to "red" when data was unavailable."""
            },
            {
                "role": "user",
                "content": f"""Company being monitored: {your_company}

Research gathered this week:
{context}

Generate the competitive intelligence briefing.
Tag EVERY factual claim with [VERIFIED: url], [INFERRED], or [UNVERIFIED].
Include the executive_summary with landscape_shift rating.
Include strategic_implications (always [INFERRED]).
Respond ONLY with the JSON object, no markdown fences."""
            }
        ]

        response = await self.llm.chat(messages)

        if response.get("used_fallback") and status_callback:
            await status_callback({
                "type": "fallback_triggered",
                "message": f"⚠️ Nemotron timeout detected\n→ Switching to {response.get('model_used', 'GPT-4o')} fallback\n→ Recovery successful",
                "fallback_model": response.get("model_used", "GPT-4o"),
                "icon": "⚠️",
            })

        briefing_data = self._parse_response(response.get("content", ""))

        return {
            "briefing_data": briefing_data,
            "raw_content": response.get("content", ""),
            "used_fallback": response.get("used_fallback", False),
            "model_used": response.get("model_used", "unknown"),
        }

    def _format_research(self, research: dict) -> str:
        """Format all competitor research into context with source URLs for VERIFIED tagging."""
        formatted = []
        for competitor, data in research.items():
            formatted.append(f"\n=== {competitor.upper()} ===")
            for category, result in data.items():
                confidence    = result.get("confidence", "unknown")
                source        = result.get("source", "unknown")
                sources_used  = result.get("sources_used", [])
                source_label  = (
                    f"{source} [{', '.join(sources_used)}]"
                    if sources_used else source
                )
                formatted.append(
                    f"\n[{category.upper()}] (sources: {source_label}, confidence: {confidence})"
                )
                if result.get("error"):
                    formatted.append(f"  ⚠️ Data unavailable: {result['error']}")
                if result.get("answer"):
                    formatted.append(f"  Summary: {result['answer']}")
                # Include up to 10 results for news (4 parallel sources), 6 for others
                limit = 10 if category == "news" else 6
                for r in result.get("results", [])[:limit]:
                    title       = r.get("title", "")
                    content     = r.get("content", "")[:200]
                    url         = r.get("url", "")
                    src_name    = r.get("_source", r.get("source_name", ""))
                    src_tag     = f" [{src_name}]" if src_name else ""
                    formatted.append(f"  -{src_tag} [{title}] {content}")
                    if url:
                        formatted.append(f"    Source URL: {url}")
        return "\n".join(formatted)

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from LLM response.

        Nemotron-3-Nano is a reasoning model — it may prefix the JSON with a
        chain-of-thought reasoning block. We try several extraction strategies:
          1. Direct parse (clean JSON response)
          2. Strip markdown fences then parse
          3. Extract largest {...} block (handles reasoning prefix/suffix)
          4. Walk forward from first '{' to find valid JSON
        """
        if not content:
            return self._empty_briefing()

        cleaned = content.strip()

        # Strategy 1: direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Strategy 2: strip markdown fences
        if "```" in cleaned:
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            stripped = "\n".join(lines).strip()
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

        # Strategy 3: extract from first '{' to last '}' — handles reasoning prefix
        first_brace = content.find('{')
        last_brace  = content.rfind('}')
        if first_brace != -1 and last_brace > first_brace:
            candidate = content[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Strategy 4: scan for JSON block boundaries (tolerates trailing text)
        import re as _re
        for match in _re.finditer(r'\{', content):
            start = match.start()
            depth = 0
            for i, ch in enumerate(content[start:], start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(content[start:i + 1])
                        except json.JSONDecodeError:
                            break

        return {
                "executive_summary": {
                    "key_findings": ["Raw analysis (JSON parsing failed) [UNVERIFIED]"],
                    "landscape_shift": "STABLE",
                    "top_action": "Manual review required — synthesis output was malformed",
                    "overall_confidence": "red",
                },
                "competitors": [],
                "strategic_implications": [content[:500] + " [UNVERIFIED]"],
                "nemotron_synthesis": [
                    "Raw analysis returned — JSON parsing failed",
                    content[:300],
                ],
            }

    def _empty_briefing(self) -> dict:
        return {
            "executive_summary": {
                "key_findings": ["Analysis unavailable — LLM returned empty response [UNVERIFIED]"],
                "landscape_shift": "STABLE",
                "top_action": "Re-run analysis — no data was generated",
                "overall_confidence": "red",
            },
            "competitors": [],
            "strategic_implications": [],
            "nemotron_synthesis": ["Analysis unavailable — LLM returned empty response."],
        }
