"""
Pydantic models for SentinelBrief API.
"""
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class ConfidenceTag(str, Enum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"


class LandscapeShift(str, Enum):
    STABLE = "STABLE"
    SHIFTING = "SHIFTING"
    MAJOR_CHANGE = "MAJOR_CHANGE"


class ConfidenceBadge(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class Urgency(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BriefingRequest(BaseModel):
    """Input model for generating a competitive intelligence briefing."""
    your_company: str = Field(..., min_length=1, description="Your company name")
    # Pydantic v2: use min_length/max_length on Field for list length constraints
    competitors: Annotated[list[str], Field(min_length=1, max_length=5,
                                            description="List of competitor names (1–5)")]
    chaos_mode: bool = Field(default=False,
                             description="Enable chaos mode to simulate primary LLM failure")
    research_depth: ResearchDepth = Field(default=ResearchDepth.STANDARD,
                                          description="Research depth: quick, standard, or deep")


class CategoryIntel(BaseModel):
    """Intelligence for one category of one competitor."""
    summary: str
    key_points: list[str] = []
    confidence: Optional[str] = None


class CompetitorIntel(BaseModel):
    """Full intelligence for one competitor."""
    name: str
    urgency: Urgency = Urgency.MEDIUM
    news: CategoryIntel = CategoryIntel(summary="No data available")
    product: CategoryIntel = CategoryIntel(summary="No data available")
    pricing: CategoryIntel = CategoryIntel(summary="No data available")
    hiring: CategoryIntel = CategoryIntel(summary="No data available")
    strategic_implication: str = ""


class ExecutiveSummary(BaseModel):
    """Top-level briefing summary."""
    key_findings: list[str] = []
    landscape_shift: str = LandscapeShift.STABLE
    top_action: str = ""
    overall_confidence: str = ConfidenceBadge.AMBER


class SystemStatus(BaseModel):
    """System health and infrastructure status."""
    primary_llm: str = "Nemotron 3 Super / Crusoe Cloud"
    primary_llm_ok: bool = True
    search_engine: str = "Tavily · Google News · Bing News · HackerNews · Reddit"
    search_engine_ok: bool = True
    fallback_triggered: bool = False
    fallback_model: Optional[str] = None
    overall_confidence: str = "high"
    generation_time_seconds: float = 0.0
    partial_sources: list[str] = []


class BriefingOutput(BaseModel):
    """Complete briefing output."""
    briefing_data: dict = {}
    raw_content: str = ""
    used_fallback: bool = False
    model_used: str = "unknown"
    confidence_metadata: dict = {}
    threat_radar_data: dict = {}
    system_status: dict = {}
