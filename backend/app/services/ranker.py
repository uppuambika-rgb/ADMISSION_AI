import json
from pathlib import Path
from typing import List, Dict, Any
from app.models.student import StudentProfile
from app.models.program import (
    CollegeProgram,
    RecommendationItem,
    RecommendationResponse,
    LikelihoodTier
)
from app.services.evaluator import evaluate_admission_likelihood
from app.services.matcher import calculate_curriculum_match, calculate_placement_score

DATA_FILE         = Path(__file__).resolve().parent.parent / "data" / "sample_colleges.json"
AP_EAPCET_FILE    = Path(__file__).resolve().parent.parent / "data" / "ap_eapcet_colleges.json"

def load_college_programs() -> List[CollegeProgram]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CollegeProgram(**item) for item in data]

def load_ap_eapcet_programs() -> List[CollegeProgram]:
    """Load the AP EAPCET college dataset (separate file, AP-specific categories)."""
    if not AP_EAPCET_FILE.exists():
        return []
    with open(AP_EAPCET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CollegeProgram(**item) for item in data]

def generate_recommendations(
    student: StudentProfile,
    programs: List[CollegeProgram] = None
) -> RecommendationResponse:
    """
    Deterministically evaluates programs and builds a preference list.

    STRICT EXAM ROUTING (enforced before any cutoff comparison):
    ─────────────────────────────────────────────────────────────
    • JEE Main    → college_type == "NIT"  ONLY
    • JEE Advanced → college_type == "IIT"  ONLY
    • AP EAPCET   → no verified dataset exists → returns explicit
                    unavailable response; NEVER substitutes NITs/IITs
    • No exam set → evaluates all programs (backward-compat / tests)
    • Any other exam → returns explicit unsupported-exam response
    """
    if programs is None:
        programs = load_college_programs()

    exam_raw  = (student.entrance_exam or "").strip()
    exam_lower = exam_raw.lower()
    
    print(f"[DEBUG] Received exam: '{exam_raw}' -> lowercase: '{exam_lower}'")

    # ── Strict exam routing ───────────────────────────────────────────────────
    if exam_lower == "ap eapcet" or exam_lower == "eapcet":
        print(f"[DEBUG] Matched AP EAPCET routing")
        ap_programs = load_ap_eapcet_programs()
        print(f"[DEBUG] Loaded {len(ap_programs)} AP EAPCET programs")
        if not ap_programs:
            return RecommendationResponse(
                student_profile=student,
                total_evaluated=0,
                preferences=[],
                tier_summary={
                    LikelihoodTier.SAFE.value: 0,
                    LikelihoodTier.LIKELY.value: 0,
                    LikelihoodTier.ASPIRATIONAL.value: 0,
                    LikelihoodTier.REACH.value: 0,
                },
                disclaimer=(
                    "AP EAPCET DATA UNAVAILABLE: Verified AP EAPCET participating-college "
                    "cutoff data is not yet in our database. "
                    "Do NOT use JEE Main or JEE Advanced cutoffs for AP EAPCET admission. "
                    "Please refer to the official AP EAPCET counselling portal: "
                    "https://cets.apsche.ap.gov.in"
                ),
            )
        # Use AP EAPCET data — override the programs list and continue to evaluation
        eligible = ap_programs
        print(f"[DEBUG] Set eligible to {len(eligible)} AP EAPCET programs")

    elif exam_lower == "jee advanced":
        # IITs only — strict
        print(f"[DEBUG] Matched JEE Advanced routing")
        eligible = [p for p in programs if p.college_type == "IIT"]
        print(f"[DEBUG] Filtered to {len(eligible)} IIT programs")

    elif exam_lower in ("jee main", "jee mains"):
        # NITs only — strict
        print(f"[DEBUG] Matched JEE Main routing")
        eligible = [p for p in programs if p.college_type == "NIT"]
        print(f"[DEBUG] Filtered to {len(eligible)} NIT programs")

    elif exam_lower == "":
        # No exam provided — evaluate all (backward-compat for callers
        # that don't set entrance_exam, e.g. existing tests)
        eligible = list(programs)

    else:
        # Unsupported exam — return explicit error response
        return RecommendationResponse(
            student_profile=student,
            total_evaluated=0,
            preferences=[],
            tier_summary={
                LikelihoodTier.SAFE.value: 0,
                LikelihoodTier.LIKELY.value: 0,
                LikelihoodTier.ASPIRATIONAL.value: 0,
                LikelihoodTier.REACH.value: 0,
            },
            disclaimer=(
                f"UNSUPPORTED EXAM '{exam_raw}': This system currently supports "
                "JEE Main (NITs), JEE Advanced (IITs), and AP EAPCET only. "
                "No recommendations can be generated for other exams without verified data."
            ),
        )

    evaluated_items: List[RecommendationItem] = []

    # Map tier to baseline feasibility score for composite ranking
    tier_feasibility_map = {
        LikelihoodTier.SAFE: 90.0,
        LikelihoodTier.LIKELY: 75.0,
        LikelihoodTier.ASPIRATIONAL: 55.0,
        LikelihoodTier.REACH: 25.0
    }

    tier_counts = {
        LikelihoodTier.SAFE.value: 0,
        LikelihoodTier.LIKELY.value: 0,
        LikelihoodTier.ASPIRATIONAL.value: 0,
        LikelihoodTier.REACH.value: 0
    }

    rank = student.rank if student.rank is not None else 10000

    for program in eligible:
        tier, likelihood_range, margin, uncertainty_note = evaluate_admission_likelihood(
            student_rank=rank,
            category=student.category,
            program=program
        )
        tier_counts[tier.value] += 1

        interest_score, matched_tags = calculate_curriculum_match(student, program)
        placement_score = calculate_placement_score(program, student)

        feasibility_score = tier_feasibility_map.get(tier, 50.0)
        # Composite score blends feasibility (40%), curriculum fit (35%), and placement outcomes (25%)
        composite = (feasibility_score * 0.40) + (interest_score * 0.35) + (placement_score * 0.25)

        # Get cutoff for explanation (with safe fallback)
        cutoff_data = program.category_cutoffs.get(student.category)
        if not cutoff_data:
            # Try common fallback categories
            for fallback_cat in ['General', 'OC', 'OPEN']:
                cutoff_data = program.category_cutoffs.get(fallback_cat)
                if cutoff_data:
                    break
        
        if cutoff_data:
            closing_rank_str = str(cutoff_data.closing_rank)
        else:
            closing_rank_str = "N/A"

        # Baseline explanation template (can be enriched by AI service)
        base_explanation = (
            f"Categorized as {tier.value} based on your rank of {rank} (closing cutoff: "
            f"{closing_rank_str}). "
            f"Curriculum aligns well with your interest in {', '.join(matched_tags[:2])}. "
            f"Offers {program.placement_stats.placement_percentage}% placement rate with a median CTC of ₹{program.placement_stats.median_salary_lpa} LPA."
        )

        item = RecommendationItem(
            program=program,
            tier=tier,
            likelihood_range=likelihood_range,
            composite_score=round(composite, 1),
            cutoff_margin_percent=margin,
            interest_alignment_tags=matched_tags,
            placement_score=placement_score,
            ai_explanation=base_explanation,
            uncertainty_note=uncertainty_note
        )
        evaluated_items.append(item)

    # Separate items by tier
    aspirational = [i for i in evaluated_items if i.tier == LikelihoodTier.ASPIRATIONAL]
    likely = [i for i in evaluated_items if i.tier == LikelihoodTier.LIKELY]
    safe = [i for i in evaluated_items if i.tier == LikelihoodTier.SAFE]
    reach = [i for i in evaluated_items if i.tier == LikelihoodTier.REACH]

    # Sort each tier internally by composite score (highest match & placement first)
    aspirational.sort(key=lambda x: x.composite_score, reverse=True)
    likely.sort(key=lambda x: x.composite_score, reverse=True)
    safe.sort(key=lambda x: x.composite_score, reverse=True)
    reach.sort(key=lambda x: x.composite_score, reverse=True)

    # Build preference sequence — return ALL evaluated items, sorted by tier and score
    # Frontend will handle filtering and pagination
    preference_list: List[RecommendationItem] = []
    
    # Add all tiers, sorted by composite score within each tier
    preference_list.extend(aspirational)
    preference_list.extend(likely)
    preference_list.extend(safe)
    preference_list.extend(reach)

    disclaimer_text = (
        "Advisory Disclaimer: Historical cutoffs and seat allotments are subject to annual changes in applicant volumes, "
        "seat matrix alterations, and examination difficulty. These estimates represent probabilistic likelihood ranges "
        "and do not constitute an admission or placement guarantee. Verify official counselling authority guidelines before submitting your final preference sheet."
    )

    return RecommendationResponse(
        student_profile=student,
        total_evaluated=len(eligible),
        preferences=preference_list,
        tier_summary=tier_counts,
        disclaimer=disclaimer_text
    )
