from typing import List, Literal, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field

StrategyType = Literal[
    "Retire",
    "Retain",
    "Rehost",
    "Relocate",
    "Replatform",
    "Repurchase",
    "Refactor",
]

PatternType = Literal[
    "StranglerFig",
    "EventDriven",
    "CQRS",
    "Serverless",
    "Containerized",
    "ManagedDB",
    "APIGateway",
    "SaaS",
]


class DissentItem(BaseModel):
    agent: str
    position: str
    reason: str


class SpecialistOpinion(BaseModel):
    agent: str
    strategy: StrategyType
    target_pattern: List[PatternType] = Field(default_factory=list)
    target_services: List[str] = Field(default_factory=list)
    rationale: str
    risks: List[str] = Field(default_factory=list)
    effort_weeks: Tuple[float, float, float]
    evidence_node_ids: List[str] = Field(default_factory=list)


class CouncilDecision(BaseModel):
    cluster_id: str
    strategy: StrategyType
    target_pattern: List[PatternType]
    target_services: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str
    risks: List[str]
    dissent: List[DissentItem] = Field(default_factory=list)
    evidence_node_ids: List[str]
    effort_weeks: Tuple[float, float, float]  # (optimistic, likely, pessimistic)
    model_id: str = "claude-3-5-sonnet-20241022"
    offline_simulated: bool = False
    status: str = "PROPOSED"  # PROPOSED, APPROVED, REJECTED
    decision_id: Optional[str] = None


class CouncilDebate(BaseModel):
    cluster_id: str
    cluster_name: Optional[str] = None
    gxp_tier: str = "LOW"
    opinions: List[SpecialistOpinion] = Field(default_factory=list)
    rebuttals: List[Dict[str, str]] = Field(default_factory=list)
    decision: CouncilDecision
