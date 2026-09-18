"""
evaluator.py — Deterministic admission likelihood engine.

Schema-migration changes (2024-07):
  - Added CutoffResolutionResult dataclass.
  - Added resolve_cutoff() — single authoritative lookup that:
      1. Prefers cutoff_history[year][category] when available.
      2. Falls back to legacy category_cutoffs[category] when
         cutoff_history is absent (backward-compat path).
      3. NEVER silently substitutes General for a missing category.
         Missing data is surfaced as an explicit unavailable result.
  - evaluate_admission_likelihood() now delegates to resolve_cutoff()
    so the rest of the codebase (ranker, query_service) is unchanged.
  - filter_and_evaluate_admission() is unchanged in signature and
    return shape; it calls evaluate_admission_likelihood() as before.
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict, Any, Optional

from app.models.program import CollegeProgram, LikelihoodTier, CategoryCutoff


# ── Cutoff resolution result ──────────────────────────────────────────────────

@dataclass
class CutoffResolutionResult:
    """
    Explicit result of a cutoff lookup.

    ``available``  — True  → valid opening/closing ranks are present.
                     False → no verified data exists for this
                             category + year combination.
    ``opening_rank`` / ``closing_rank`` — only meaningful when available=True.
    ``source``     — 'cutoff_history' | 'category_cutoffs' | 'unavailable'
    ``message``    — human-readable explanation (surfaced to the student
                     when available=False instead of a silent fallback).
    """
    available: bool
    opening_rank: int = 0
    closing_rank: int = 0
    source: str = "unavailable"
    message: str = ""


# ── Single authoritative cutoff lookup ───────────────────────────────────────

def resolve_cutoff(
    program: CollegeProgram,
    category: str,
    year: str = "2024",
) -> CutoffResolutionResult:
    """
    Resolve the cutoff for a given program / category / year.

    Lookup order
    ────────────
    1. ``program.cutoff_history[year].categories[category]``
       (new multi-year structure — preferred when present)
    2. ``program.category_cutoffs[category]``
       (legacy flat map — used only when cutoff_history is absent
        or does not contain the requested year)

    CATEGORY MAPPING FOR AP EAPCET
    ───────────────────────────────
    AP EAPCET uses different category names. We auto-map:
    - "General" → "OC", "OBC"/"OBC-NCL" → "BC-A"

    EXPLICIT MISSING-CATEGORY RULE
    ───────────────────────────────
    If the requested category is absent from the resolved data source,
    we return ``available=False`` with a descriptive message.
    We do NOT fall back to General, OBC-NCL, or any other category.
    The caller decides what to do (typically: surface the message
    to the student and skip the program for that category).
    """
    
    # ── Category mapping for AP EAPCET colleges ────────────────────────────────
    mapped_category = category
    available_categories = list(program.category_cutoffs.keys())
    
    # Detect AP EAPCET by presence of "OC" or "BC-A" categories
    is_ap_eapcet = "OC" in available_categories or "BC-A" in available_categories
    
    if is_ap_eapcet and category not in available_categories:
        # Map JEE categories to AP EAPCET categories
        category_map = {
            "General": "OC",
            "OBC": "BC-A",
            "OBC-NCL": "BC-A",
            "EWS": "OC",  # EWS doesn't exist in AP EAPCET, use OC
        }
        mapped_category = category_map.get(category, category)

    # ── Path 1: cutoff_history present and contains the requested year ────────
    if program.cutoff_history and year in program.cutoff_history:
        year_data = program.cutoff_history[year]

        # Try mapped category first, then original
        for cat_attempt in [mapped_category, category]:
            if cat_attempt in year_data.categories:
                entry = year_data.categories[cat_attempt]
                return CutoffResolutionResult(
                    available=True,
                    opening_rank=entry.opening_rank,
                    closing_rank=entry.closing_rank,
                    source="cutoff_history",
                    message=(
                        f"Verified {year} {year_data.round} cutoff "
                        f"for {cat_attempt} category."
                    ),
                )

        # Category not in this year's verified data
        return CutoffResolutionResult(
            available=False,
            source="unavailable",
            message=(
                f"Verified cutoff data for category '{category}' is unavailable "
                f"in {year} {year_data.round} records for "
                f"{program.college_name} — {program.branch_name}. "
                "This category_cutoff_available: false. "
                "Do NOT treat this as equivalent to General category data."
            ),
        )

    # ── Path 2: cutoff_history absent or year not present — use legacy map ────
    if program.cutoff_history and year not in program.cutoff_history:
        # cutoff_history exists but the specific year has no record
        return CutoffResolutionResult(
            available=False,
            source="unavailable",
            message=(
                f"cutoff_history is present for {program.college_name} — "
                f"{program.branch_name} but does not contain year '{year}'. "
                "No data invented. category_cutoff_available: false."
            ),
        )

    # cutoff_history is None → fall back to legacy category_cutoffs
    # Try mapped category first, then original
    for cat_attempt in [mapped_category, category]:
        legacy_entry: Optional[CategoryCutoff] = program.category_cutoffs.get(cat_attempt)
        if legacy_entry is not None:
            return CutoffResolutionResult(
                available=True,
                opening_rank=legacy_entry.opening_rank,
                closing_rank=legacy_entry.closing_rank,
                source="category_cutoffs",
                message=(
                f"Legacy category_cutoffs ({program.cutoff_year_round}) "
                f"used for {category}. "
                "Migrate to cutoff_history for multi-year support."
            ),
        )

    # Category missing from legacy map too — explicit unavailable
    return CutoffResolutionResult(
        available=False,
        source="unavailable",
        message=(
            f"No verified cutoff data found for category '{category}' "
            f"in {program.college_name} — {program.branch_name}. "
            "category_cutoff_available: false. "
            "Do NOT treat this as equivalent to General category data."
        ),
    )


# ── Core evaluation function (signature unchanged) ───────────────────────────

def evaluate_admission_likelihood(
    student_rank: int,
    category: str,
    program: CollegeProgram,
    year: str = "2024",
) -> Tuple[LikelihoodTier, str, float, str]:
    """
    Deterministic admission likelihood evaluation.

    Returns
    -------
    (tier, likelihood_range_str, margin_percent, uncertainty_note)

    Delegates cutoff resolution to resolve_cutoff() so the explicit
    missing-category policy is enforced uniformly.

    ``year`` defaults to "2024".  Callers that already pass three
    positional args are unaffected (year is keyword-only in practice).
    """
    resolution = resolve_cutoff(program, category, year)

    if not resolution.available:
        return (
            LikelihoodTier.REACH,
            "Data unavailable",
            -100.0,
            (
                f"Cutoff data unavailable: {resolution.message} "
                "Admission likelihood cannot be estimated without verified data."
            ),
        )

    closing_rank = resolution.closing_rank

    # Margin: positive → student rank is numerically better than closing rank
    margin_percent = round(
        ((closing_rank - student_rank) / closing_rank) * 100, 1
    )

    if margin_percent >= 12.0:
        tier = LikelihoodTier.SAFE
        likelihood_range = "80% - 95%"
        uncertainty = (
            f"Strong historical cushion (+{margin_percent}% margin relative to "
            f"closing rank {closing_rank:,}). "
            "Categorised as Safe based on past trends; seat matrix changes or "
            "applicant surges can still shift cutoffs."
        )
    elif margin_percent >= -10.0:
        tier = LikelihoodTier.LIKELY
        likelihood_range = "50% - 75%"
        uncertainty = (
            f"Within competitive range (margin {margin_percent}% vs closing rank "
            f"{closing_rank:,}). "
            "Realistic contender in standard counselling rounds, subject to "
            "year-on-year cutoff shifts of ±5-8%."
        )
    elif margin_percent >= -30.0:
        tier = LikelihoodTier.ASPIRATIONAL
        likelihood_range = "20% - 40%"
        uncertainty = (
            f"Aspirational reach (rank {student_rank:,} is "
            f"{abs(margin_percent)}% above {year} closing rank of "
            f"{closing_rank:,}). "
            "Plausible during late or spot rounds if candidate choices deviate "
            "from historical patterns."
        )
    else:
        tier = LikelihoodTier.REACH
        likelihood_range = "< 15%"
        uncertainty = (
            f"High reach (rank {student_rank:,} is significantly above {year} "
            f"closing rank of {closing_rank:,}). "
            "Statistically low historical probability; recommended only as an "
            "ambitious moonshot."
        )

    return tier, likelihood_range, margin_percent, uncertainty


# ── Filtering helper (signature and return shape unchanged) ──────────────────

def filter_and_evaluate_admission(
    student_rank: int,
    category: str,
    programs: List[CollegeProgram],
    college_type: Optional[str] = None,
    branch_keyword: Optional[str] = None,
    tier_filter: Optional[str] = None,
    year: str = "2024",
    entrance_exam: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter programs by criteria and return structured rows with
    deterministic admission likelihood for each.

    ``entrance_exam`` — when provided, only programs whose ``exam``
    field matches are evaluated.  This prevents JEE Main ranks from
    being compared against IIT (JEE Advanced) cutoffs and vice-versa.

    Matching rules
    ──────────────
    • "JEE Advanced" → only programs with exam == "JEE Advanced" (IITs)
    • "JEE Main"     → programs with exam == "JEE Main" or exam that
                       contains "JEE Main" (NITs, IIITs, GFTIs, some private)
    • Any other exam → programs whose exam field contains that string
    • None           → no exam filter (backward-compat default)

    Return shape is identical to the pre-migration version so
    query_service.py and all callers require no changes.
    """
    results = []

    for p in programs:
        # ── Strict exam + institute-type gate ────────────────────────────────
        # This is the single authoritative enforcement point for:
        #   JEE Main    → NIT only
        #   JEE Advanced → IIT only
        #   AP EAPCET   → no matching records (empty result; caller handles message)
        # The gate runs BEFORE the college_type filter below so the explicit
        # college_type arg can only narrow further, never widen to wrong types.
        if entrance_exam:
            exam_lower = entrance_exam.lower().strip()
            if exam_lower == "jee advanced":
                if p.college_type != "IIT":
                    continue
            elif exam_lower in ("jee main", "jee mains"):
                if p.college_type != "NIT":
                    continue
            elif exam_lower in ("ap eapcet", "eapcet"):
                # No AP EAPCET records in dataset — skip every program.
                # Returning an empty list signals the caller to show the
                # explicit "data unavailable" message.
                continue
            # Unknown exam: fall through — caller already guarded this in ranker.py
        # ── College type filter ───────────────────────────────────────────────
        if college_type:
            ct_upper = college_type.upper()
            if ct_upper in ("NIT", "IIT", "IIIT"):
                if p.college_type != ct_upper:
                    continue
            elif college_type.lower() not in p.college_type.lower():
                continue

        # ── Branch keyword filter ─────────────────────────────────────────────
        if branch_keyword:
            bk = branch_keyword.lower()
            if bk in ("cse", "computer science", "cs"):
                if not any(
                    k in p.branch_name.lower()
                    for k in ["computer", "software", "information technology"]
                ):
                    continue
            elif bk in ("ece", "electronics"):
                if not any(
                    k in p.branch_name.lower()
                    for k in ["electronics", "electrical"]
                ):
                    continue
            elif bk in ("mech", "mechanical"):
                if "mechanical" not in p.branch_name.lower():
                    continue
            elif bk not in p.branch_name.lower():
                continue

        tier, likelihood_range, margin_percent, uncertainty = evaluate_admission_likelihood(
            student_rank, category, p, year
        )

        # ── Tier filter ───────────────────────────────────────────────────────
        if tier_filter and tier.value.lower() != tier_filter.lower():
            continue

        # Resolve closing rank for display (same path as above)
        resolution = resolve_cutoff(p, category, year)
        closing_rank = resolution.closing_rank if resolution.available else 0

        rank_diff = closing_rank - student_rank
        diff_str = f"+{rank_diff:,}" if rank_diff >= 0 else f"{rank_diff:,}"

        # Surface year label in the output row
        cutoff_label = (
            f"{year} (cutoff_history — {p.cutoff_history[year].round})"
            if p.cutoff_history and year in p.cutoff_history
            else p.cutoff_year_round
        )

        results.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "type": p.college_type,
            "exam": p.exam,
            "category": category,
            "candidate_rank": f"#{student_rank:,}",
            "historical_cutoff": f"{closing_rank:,}" if resolution.available else "N/A",
            "cutoff_year_round": cutoff_label,
            "rank_difference": diff_str if resolution.available else "N/A",
            "likelihood_range": likelihood_range,
            "tier": tier.value,
            "uncertainty_note": uncertainty,
            "median_ctc": f"₹{p.placement_stats.median_salary_lpa} LPA",
            "placement_rate": f"{p.placement_stats.placement_percentage}%",
            "tuition_fee": (
                f"₹{p.annual_tuition_fee_inr:,} / yr"
                if p.annual_tuition_fee_inr
                else "Not available"
            ),
            "location": p.location,
            # New field — explicit data availability signal
            "category_cutoff_available": resolution.available,
            "cutoff_source": resolution.source,
        })

    # Sort: Safe → Likely → Aspirational → Reach, then by rank margin desc
    tier_order = {"Safe": 1, "Likely": 2, "Aspirational": 3, "Reach": 4}

    def _sort_key(r: Dict[str, Any]) -> Tuple[int, int]:
        tier_rank = tier_order.get(r["tier"], 5)
        diff_raw = r["rank_difference"]
        if diff_raw == "N/A":
            return (tier_rank, -999_999)
        return (tier_rank, -int(diff_raw.replace("+", "").replace(",", "")))

    results.sort(key=_sort_key)
    return results
