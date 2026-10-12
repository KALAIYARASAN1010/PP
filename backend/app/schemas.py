from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

# --- Auth & User Schemas ---
class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    department: str
    badge_number: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None


# --- Proposal Schemas ---
ALLOWED_CATEGORIES = {"Administrative", "Technical", "Procurement", "Infrastructure", "Operational"}
ALLOWED_STATUSES = {"Draft", "Submitted", "Under Review", "Changes Requested", "Approved", "Rejected", "Closed"}

class ProposalBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    category: str
    department: str = Field(..., min_length=2)
    cost: float = Field(..., ge=0.0)
    justification: str = Field(..., min_length=10)
    parent_proposal_id: Optional[int] = None
    document_ref: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")
        return v

class ProposalCreate(ProposalBase):
    status: Optional[str] = "Draft"

    @field_validator("status")
    @classmethod
    def validate_initial_status(cls, v: Optional[str]) -> str:
        if v and v not in {"Draft", "Submitted"}:
            raise ValueError("New proposal initial status must be 'Draft' or 'Submitted'")
        return v or "Draft"

class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    cost: Optional[float] = None
    justification: Optional[str] = None
    document_ref: Optional[str] = None
    implementation_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")
        return v

class DecisionResponse(BaseModel):
    id: int
    proposal_id: int
    reviewer_id: int
    reviewer_name: Optional[str] = None
    action: str
    reason: str
    previous_status: str
    new_status: str
    created_at: datetime

    model_config = {"from_attributes": True}

class DecisionCreate(BaseModel):
    action: str = Field(..., description="Approved, Rejected, or Changes Requested")
    reason: str = Field(..., min_length=5, description="Mandatory decision reason")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        allowed = {"Approved", "Rejected", "Changes Requested", "Under Review", "Closed"}
        if v not in allowed:
            raise ValueError(f"Action must be one of: {', '.join(sorted(allowed))}")
        return v

class ProposalResponse(BaseModel):
    id: int
    proposal_code: str
    title: str
    description: str
    category: str
    department: str
    cost: float
    justification: str
    date: datetime
    status: str
    document_ref: Optional[str] = None
    submitter_id: int
    submitter_name: Optional[str] = None
    parent_proposal_id: Optional[int] = None
    implementation_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None
    decisions: List[DecisionResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Precedent Retrieval & Search Schemas ---
class PrecedentSearchQuery(BaseModel):
    query: str = Field(..., min_length=2)
    category: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
    top_k: int = 5
    threshold: Optional[float] = 0.35

class PrecedentResultItem(BaseModel):
    id: int
    proposal_code: str
    title: str
    category: str
    department: str
    cost: float
    decision: Optional[str] = None  # Never invented!
    reason: Optional[str] = None    # Never invented!
    date: datetime
    source_link: str
    similarity_score: float         # 0.0 to 1.0
    is_strong_precedent: bool
    highlighted_matches: List[str]
    why_matched: str
    implementation_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None

class PrecedentSearchResponse(BaseModel):
    results: List[PrecedentResultItem]
    active_engine: str
    total_candidates: int
    query: str
    similarity_disclaimer: str = (
        "LEGAL & POLICY NOTICE: Similarity score measures textual & institutional overlap; "
        "similarity does NOT indicate approval probability. Decisions rest solely with authorized human reviewers."
    )
    strong_precedent_count: int
    warning_message: Optional[str] = None


# --- Side by Side Comparison ---
class SideBySideItem(BaseModel):
    proposal_code: str
    title: str
    category: str
    department: str
    cost: float
    justification: str
    description: str
    status: str
    decision: Optional[str] = None
    reason: Optional[str] = None
    implementation_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None

class SideBySideResponse(BaseModel):
    current: SideBySideItem
    precedent: SideBySideItem
    cost_difference: float
    cost_ratio: float
    key_overlap_terms: List[str]
    structural_comparison: Dict[str, Any]


# --- Innovation Feature Schemas ---
class DuplicateWarningItem(BaseModel):
    proposal_code: str
    title: str
    status: str
    similarity_score: float
    decision: Optional[str] = None
    outcome_summary: str

class DuplicateCheckResponse(BaseModel):
    has_potential_duplicate: bool
    highest_similarity: float
    duplicates: List[DuplicateWarningItem]
    recommendation: str

class RiskChecklistItem(BaseModel):
    risk_title: str
    risk_category: str
    past_rejection_reason: str
    frequency_in_past_rejections: int
    relevance_explanation: str
    mitigation_suggestion: str

class RiskChecklistResponse(BaseModel):
    proposal_id: Optional[int] = None
    category: str
    identified_risks: List[RiskChecklistItem]
    overall_risk_level: str  # "Low", "Moderate", "Elevated"

class CostBenchmarkResponse(BaseModel):
    requested_cost: float
    category: str
    similar_proposals_count: int
    benchmark_average: float
    benchmark_median: float
    benchmark_min: float
    benchmark_max: float
    z_score: float
    is_outlier: bool
    cost_assessment: str  # e.g., "Normal", "Higher than 80% of category precedents", "Flagged Outlier"

class ConflictPrecedentItem(BaseModel):
    approved_proposal_code: str
    approved_title: str
    approved_reason: str
    rejected_proposal_code: str
    rejected_title: str
    rejected_reason: str
    topic_summary: str
    conflict_analysis: str

class ConflictAlertResponse(BaseModel):
    has_conflicts: bool
    conflict_count: int
    conflicts: List[ConflictPrecedentItem]

class LineageNode(BaseModel):
    id: int
    proposal_code: str
    title: str
    status: str
    date: datetime
    cost: float
    is_current: bool

class LineageEdge(BaseModel):
    source_code: str
    target_code: str
    relationship: str  # "Resubmission", "Successor", "Revision"

class LineageGraphResponse(BaseModel):
    nodes: List[LineageNode]
    edges: List[LineageEdge]
    chain_length: int

class ReviewerBriefResponse(BaseModel):
    brief_generated_at: datetime
    proposal_code: str
    title: str
    category: str
    department: str
    submitter_name: str
    cost: float
    justification_summary: str
    stored_citations: List[Dict[str, Any]]
    cost_benchmark_summary: Dict[str, Any]
    historical_risk_factors: List[str]
    conflict_summary: Optional[str]
    printable_formatted_html: Optional[str] = None

class BottleneckStageStat(BaseModel):
    status: str
    count: int
    average_days_in_status: float
    sla_threshold_days: int
    sla_breaches_count: int

class BottleneckAnalyticsResponse(BaseModel):
    total_active_proposals: int
    stages: List[BottleneckStageStat]
    overall_avg_turnaround_days: float
    longest_stalled_proposal: Optional[Dict[str, Any]] = None


# --- Audit Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    timestamp: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    details_json: str
    previous_hash: str
    current_hash: str

    model_config = {"from_attributes": True}

class AuditVerifyResponse(BaseModel):
    is_valid: bool
    total_records: int
    verified_at: datetime
    tampered_record_id: Optional[int] = None
    error_message: Optional[str] = None
