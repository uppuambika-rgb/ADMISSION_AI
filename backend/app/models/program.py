from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.models.student import StudentProfile


# ── Existing cutoff model (unchanged — backward compat) ───────────────────────
class CategoryCutoff(BaseModel):
    """Single category cutoff record — opening and closing rank."""
    opening_rank: int
    closing_rank: int


# ── New multi-year cutoff models ───────────────────────────────────────────────

class CutoffEntry(BaseModel):
    """
    Opening and closing rank for a single category in a single round.
    Identical shape to CategoryCutoff; kept as a separate class so
    it can carry additional year-level fields in the future without
    affecting the legacy CategoryCutoff.
    """
    opening_rank: int
    closing_rank: int


class YearCutoffData(BaseModel):
    """
    All available category cutoffs for one exam year / round.

    ``round`` — human-readable round identifier, e.g. "Round 6 Closing".
    ``categories`` — mapping of category name → CutoffEntry.
      Only categories for which **verified** data actually exists are
      present.  Missing categories must NOT be assumed equal to General.
    """
    round: str = Field(..., description="Counselling round, e.g. 'Round 6 Closing'")
    categories: Dict[str, CutoffEntry] = Field(
        default_factory=dict,
        description="Verified category cutoffs for this year. Keys are category strings."
    )


# ── Placement & program models (unchanged) ────────────────────────────────────

class PlacementStats(BaseModel):
    median_salary_lpa: float
    placement_percentage: float
    top_recruiters: List[str]
    key_career_domains: List[str] = Field(default_factory=list)


class CollegeProgram(BaseModel):
    id: str
    college_name: str
    branch_name: str
    college_type: str = Field(
        default="College",
        description="e.g. NIT, IIT, IIIT, State University, Private University"
    )
    exam: str = Field(default="JEE Main", description="Accepted entrance exam")
    location: str
    tier_rating: str  # "Tier-1", "Tier-2"
    annual_tuition_fee_inr: Optional[int] = Field(
        default=None, description="Annual tuition fee in INR"
    )
    hostel_available: bool = Field(
        default=True, description="Whether on-campus hostel is available"
    )
    annual_hostel_fee_inr: Optional[int] = Field(
        default=None, description="Annual hostel and mess fee in INR"
    )
    scholarships: Optional[str] = Field(
        default=None, description="Factual scholarship and fee-remission schemes"
    )
    higher_study_opportunities: Optional[str] = Field(
        default=None, description="Higher studies & international admits profile"
    )
    entrepreneurship_opportunities: Optional[str] = Field(
        default=None, description="Incubation and startup support"
    )

    # ── Legacy single-year cutoff (kept for backward compat) ──────────────────
    cutoff_year_round: str = Field(
        default="2024 (Round 6 Closing)",
        description="Year and round label for the legacy category_cutoffs snapshot."
    )
    category_cutoffs: Dict[str, CategoryCutoff] = Field(
        description=(
            "Legacy flat cutoff map — single year snapshot. "
            "Prefer cutoff_history when multi-year data is needed. "
            "Will be retired once cutoff_history is fully populated."
        )
    )

    # ── New optional multi-year cutoff history ─────────────────────────────────
    cutoff_history: Optional[Dict[str, YearCutoffData]] = Field(
        default=None,
        description=(
            "Multi-year cutoff history. "
            "Keys are year strings ('2024', '2023', ...). "
            "Each value contains the round label and a per-category CutoffEntry. "
            "Only categories with verified data are present — missing categories "
            "must NOT be treated as equivalent to General."
        )
    )

    typical_roles: List[str] = Field(default_factory=list)
    curriculum_keywords: List[str]
    placement_stats: PlacementStats
    admission_notes: Optional[str] = None


# ── Recommendation models (unchanged) ────────────────────────────────────────

class LikelihoodTier(str, Enum):
    SAFE         = "Safe"
    LIKELY       = "Likely"
    ASPIRATIONAL = "Aspirational"
    REACH        = "Reach"


class RecommendationItem(BaseModel):
    program: CollegeProgram
    tier: LikelihoodTier
    likelihood_range: str
    composite_score: float
    cutoff_margin_percent: float
    interest_alignment_tags: List[str]
    placement_score: float
    ai_explanation: str
    uncertainty_note: str


class RecommendationResponse(BaseModel):
    student_profile: StudentProfile
    total_evaluated: int
    preferences: List[RecommendationItem]
    tier_summary: Dict[str, int]
    disclaimer: str
