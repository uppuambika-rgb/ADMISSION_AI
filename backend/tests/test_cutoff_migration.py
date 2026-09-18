"""
test_cutoff_migration.py
────────────────────────
Validates every contract stated in the migration spec:

  1. Existing 2024 recommendations still work (legacy category_cutoffs path).
  2. Existing category_cutoffs still resolve correctly.
  3. cutoff_history can be loaded from the JSON file.
  4. cutoff_history 2024 returns the exact same numbers as category_cutoffs.
  5. Missing category → available=False, NOT a silent General fallback.
  6. Missing year  → available=False, NOT invented values.
  7. PwD categories (absent from data) never become General.
  8. evaluate_admission_likelihood honours the explicit unavailable result.
  9. filter_and_evaluate_admission exposes category_cutoff_available field.
 10. Legacy-only records (cutoff_history=None) still work through category_cutoffs.

Run from the backend directory:
    python -m pytest tests/test_cutoff_migration.py -v
"""

import sys
import os
import json
import pytest
from pathlib import Path

# ── Make sure the backend package is importable ────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.models.program import (
    CategoryCutoff,
    CutoffEntry,
    YearCutoffData,
    CollegeProgram,
    PlacementStats,
    LikelihoodTier,
)
from app.services.evaluator import (
    resolve_cutoff,
    evaluate_admission_likelihood,
    filter_and_evaluate_admission,
    CutoffResolutionResult,
)
from app.services.ranker import load_college_programs


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

def _make_placement() -> PlacementStats:
    return PlacementStats(
        median_salary_lpa=15.0,
        placement_percentage=90.0,
        top_recruiters=["Recruiter A"],
        key_career_domains=["Software"],
    )


def _make_program_with_history(
    closing_rank_general: int = 5000,
    categories: dict | None = None,
) -> CollegeProgram:
    """Program that has BOTH category_cutoffs AND cutoff_history (2024)."""
    if categories is None:
        categories = {
            "General": CutoffEntry(opening_rank=1000, closing_rank=closing_rank_general),
            "OBC-NCL": CutoffEntry(opening_rank=600,  closing_rank=2500),
            "SC":      CutoffEntry(opening_rank=200,  closing_rank=900),
            "ST":      CutoffEntry(opening_rank=100,  closing_rank=450),
            "EWS":     CutoffEntry(opening_rank=350,  closing_rank=1200),
        }
    legacy = {
        cat: CategoryCutoff(
            opening_rank=entry.opening_rank,
            closing_rank=entry.closing_rank,
        )
        for cat, entry in categories.items()
    }
    return CollegeProgram(
        id="TEST-PROG",
        college_name="Test College",
        branch_name="Computer Science and Engineering",
        college_type="NIT",
        exam="JEE Main",
        location="Test City",
        tier_rating="Tier-1",
        category_cutoffs=legacy,
        cutoff_year_round="2024 (Round 6 Closing)",
        cutoff_history={
            "2024": YearCutoffData(
                round="Round 6 Closing",
                categories=categories,
            )
        },
        curriculum_keywords=["Algorithms", "Machine Learning"],
        placement_stats=_make_placement(),
    )


def _make_program_legacy_only() -> CollegeProgram:
    """Program that has ONLY category_cutoffs — no cutoff_history."""
    return CollegeProgram(
        id="LEGACY-PROG",
        college_name="Legacy College",
        branch_name="Mechanical Engineering",
        college_type="NIT",
        exam="JEE Main",
        location="Legacy City",
        tier_rating="Tier-2",
        category_cutoffs={
            "General": CategoryCutoff(opening_rank=8000,  closing_rank=20000),
            "OBC-NCL": CategoryCutoff(opening_rank=5000,  closing_rank=12000),
            "SC":      CategoryCutoff(opening_rank=2000,  closing_rank=6000),
            "ST":      CategoryCutoff(opening_rank=1000,  closing_rank=3500),
            "EWS":     CategoryCutoff(opening_rank=3000,  closing_rank=8000),
        },
        cutoff_year_round="2024 (Round 6 Closing)",
        cutoff_history=None,   # ← no history
        curriculum_keywords=["Thermodynamics", "Fluid Mechanics"],
        placement_stats=_make_placement(),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. JSON loading — all 15 records parse without error
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonLoading:

    def test_load_all_programs(self):
        programs = load_college_programs()
        # Dataset now has 275 records: 115 IIT + 160 NIT
        assert len(programs) == 275, f"Expected 275 programs, got {len(programs)}"

    def test_all_have_category_cutoffs(self):
        for p in load_college_programs():
            assert p.category_cutoffs, f"{p.id} is missing category_cutoffs"

    def test_all_have_cutoff_history(self):
        for p in load_college_programs():
            assert p.cutoff_history is not None, (
                f"{p.id} is missing cutoff_history — "
                "was the JSON updated correctly?"
            )

    def test_all_have_2024_in_history(self):
        for p in load_college_programs():
            assert "2024" in p.cutoff_history, (
                f"{p.id} cutoff_history has no '2024' key"
            )

    def test_2024_round_label(self):
        for p in load_college_programs():
            assert p.cutoff_history["2024"].round == "Round 6 Closing", (
                f"{p.id} unexpected round label: {p.cutoff_history['2024'].round}"
            )


# ══════════════════════════════════════════════════════════════════════════════
# 2. Numbers in cutoff_history["2024"] match category_cutoffs exactly
# ══════════════════════════════════════════════════════════════════════════════

class TestHistoryMatchesLegacy:

    def test_all_records_numbers_match(self):
        mismatches = []
        for p in load_college_programs():
            year_data = p.cutoff_history["2024"]
            for cat, legacy in p.category_cutoffs.items():
                hist_entry = year_data.categories.get(cat)
                if hist_entry is None:
                    mismatches.append(
                        f"{p.id}: category '{cat}' present in category_cutoffs "
                        "but missing from cutoff_history['2024']"
                    )
                    continue
                if hist_entry.opening_rank != legacy.opening_rank:
                    mismatches.append(
                        f"{p.id}[{cat}] opening_rank mismatch: "
                        f"history={hist_entry.opening_rank} "
                        f"legacy={legacy.opening_rank}"
                    )
                if hist_entry.closing_rank != legacy.closing_rank:
                    mismatches.append(
                        f"{p.id}[{cat}] closing_rank mismatch: "
                        f"history={hist_entry.closing_rank} "
                        f"legacy={legacy.closing_rank}"
                    )
        assert not mismatches, "\n".join(mismatches)


# ══════════════════════════════════════════════════════════════════════════════
# 3. resolve_cutoff — happy path via cutoff_history
# ══════════════════════════════════════════════════════════════════════════════

class TestResolveCutoffHistory:

    def test_general_2024_from_history(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        result = resolve_cutoff(prog, "General", year="2024")
        assert result.available is True
        assert result.closing_rank == 5000
        assert result.source == "cutoff_history"

    def test_sc_2024_from_history(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "SC", year="2024")
        assert result.available is True
        assert result.closing_rank == 900
        assert result.source == "cutoff_history"

    def test_ews_2024_from_history(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "EWS", year="2024")
        assert result.available is True
        assert result.closing_rank == 1200


# ══════════════════════════════════════════════════════════════════════════════
# 4. resolve_cutoff — happy path via legacy category_cutoffs
# ══════════════════════════════════════════════════════════════════════════════

class TestResolveCutoffLegacy:

    def test_general_from_legacy(self):
        prog = _make_program_legacy_only()
        result = resolve_cutoff(prog, "General", year="2024")
        assert result.available is True
        assert result.closing_rank == 20000
        assert result.source == "category_cutoffs"

    def test_sc_from_legacy(self):
        prog = _make_program_legacy_only()
        result = resolve_cutoff(prog, "SC", year="2024")
        assert result.available is True
        assert result.closing_rank == 6000
        assert result.source == "category_cutoffs"


# ══════════════════════════════════════════════════════════════════════════════
# 5. CRITICAL — missing category must NEVER silently become General
# ══════════════════════════════════════════════════════════════════════════════

class TestMissingCategoryNoSilentFallback:

    def test_pwd_missing_from_history_returns_unavailable(self):
        """General-PwD is not in our verified data — must return available=False."""
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General-PwD", year="2024")
        assert result.available is False, (
            "General-PwD has no verified data but resolve_cutoff returned "
            f"available=True with closing_rank={result.closing_rank}. "
            "This is a silent fallback — it must NOT happen."
        )
        assert result.source == "unavailable"
        assert result.closing_rank == 0  # no rank should be set when unavailable

    def test_obc_pwd_missing_from_history_returns_unavailable(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "OBC-NCL-PwD", year="2024")
        assert result.available is False
        assert result.source == "unavailable"

    def test_sc_pwd_missing_returns_unavailable(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "SC-PwD", year="2024")
        assert result.available is False

    def test_pwd_missing_from_legacy_returns_unavailable(self):
        """Same check on legacy-only programs."""
        prog = _make_program_legacy_only()
        result = resolve_cutoff(prog, "General-PwD", year="2024")
        assert result.available is False
        assert result.source == "unavailable"

    def test_missing_category_is_not_general(self):
        """
        Prove the unavailable result does NOT contain General's closing_rank.
        If it did, it would mean a silent General substitution occurred.
        """
        prog = _make_program_with_history(closing_rank_general=5000)
        result = resolve_cutoff(prog, "General-PwD", year="2024")
        assert result.closing_rank != 5000, (
            "resolve_cutoff returned General's closing_rank (5000) for "
            "General-PwD — this is a silent General fallback, which is "
            "explicitly forbidden by the migration spec."
        )

    def test_message_contains_category_cutoff_available_false(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General-PwD", year="2024")
        assert "category_cutoff_available: false" in result.message.lower() or \
               "unavailable" in result.message.lower(), (
            f"Expected message to indicate unavailability, got: {result.message}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 6. CRITICAL — missing year must return unavailable, not invented data
# ══════════════════════════════════════════════════════════════════════════════

class TestMissingYearNoInventedData:

    def test_2023_not_in_history_returns_unavailable(self):
        """2023 data has not been added yet — must be explicitly unavailable."""
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General", year="2023")
        assert result.available is False, (
            "Year 2023 is not in cutoff_history but resolve_cutoff returned "
            f"available=True with closing_rank={result.closing_rank}. "
            "This would be invented data — it must NOT happen."
        )
        assert result.source == "unavailable"
        assert result.closing_rank == 0

    def test_2022_not_in_history_returns_unavailable(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General", year="2022")
        assert result.available is False

    def test_future_year_not_in_history_returns_unavailable(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General", year="2026")
        assert result.available is False

    def test_missing_year_message_mentions_year(self):
        prog = _make_program_with_history()
        result = resolve_cutoff(prog, "General", year="2023")
        assert "2023" in result.message, (
            f"Expected '2023' in the unavailability message. Got: {result.message}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 7. evaluate_admission_likelihood — 2024 recommendations still work
# ══════════════════════════════════════════════════════════════════════════════

class TestEvaluateAdmissionLikelihood:

    def test_safe_tier_rank_well_below_cutoff(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=2000, category="General", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.SAFE
        assert "80%" in likelihood
        assert margin > 12.0

    def test_likely_tier_rank_near_cutoff(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=4600, category="General", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.LIKELY
        assert "50%" in likelihood

    def test_aspirational_tier_rank_above_cutoff(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=6000, category="General", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.ASPIRATIONAL

    def test_reach_tier_rank_far_above_cutoff(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=9000, category="General", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.REACH

    def test_missing_pwd_category_returns_reach_with_note(self):
        prog = _make_program_with_history(closing_rank_general=5000)
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=3000, category="General-PwD", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.REACH
        assert margin == -100.0
        assert "unavailable" in note.lower() or "cannot be estimated" in note.lower()

    def test_missing_2023_returns_reach_with_note(self):
        prog = _make_program_with_history()
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=3000, category="General", program=prog, year="2023"
        )
        assert tier == LikelihoodTier.REACH
        assert margin == -100.0

    def test_legacy_program_still_works(self):
        """Legacy program (no cutoff_history) falls back to category_cutoffs."""
        prog = _make_program_legacy_only()
        tier, likelihood, margin, note = evaluate_admission_likelihood(
            student_rank=5000, category="General", program=prog, year="2024"
        )
        assert tier == LikelihoodTier.SAFE
        assert margin > 12.0

    def test_results_match_between_history_and_legacy_paths(self):
        """
        For the same college data accessed via cutoff_history vs category_cutoffs,
        the tier and margin must be identical.
        """
        prog_with = _make_program_with_history(closing_rank_general=10000)
        prog_without = _make_program_legacy_only()
        # Override legacy closing_rank to match
        prog_without.category_cutoffs["General"] = CategoryCutoff(
            opening_rank=3000, closing_rank=10000
        )

        tier_h, _, margin_h, _ = evaluate_admission_likelihood(
            5000, "General", prog_with, year="2024"
        )
        tier_l, _, margin_l, _ = evaluate_admission_likelihood(
            5000, "General", prog_without, year="2024"
        )
        assert tier_h == tier_l
        assert margin_h == margin_l


# ══════════════════════════════════════════════════════════════════════════════
# 8. filter_and_evaluate_admission — output shape and new fields
# ══════════════════════════════════════════════════════════════════════════════

class TestFilterAndEvaluate:

    def _two_programs(self):
        return [
            _make_program_with_history(closing_rank_general=5000),
            _make_program_legacy_only(),
        ]

    def test_returns_list(self):
        rows = filter_and_evaluate_admission(3000, "General", self._two_programs())
        assert isinstance(rows, list)

    def test_category_cutoff_available_field_present(self):
        rows = filter_and_evaluate_admission(3000, "General", self._two_programs())
        for row in rows:
            assert "category_cutoff_available" in row, (
                f"Row missing 'category_cutoff_available': {row}"
            )

    def test_cutoff_source_field_present(self):
        rows = filter_and_evaluate_admission(3000, "General", self._two_programs())
        for row in rows:
            assert "cutoff_source" in row

    def test_pwd_rows_marked_unavailable(self):
        rows = filter_and_evaluate_admission(
            3000, "General-PwD", self._two_programs()
        )
        for row in rows:
            assert row["category_cutoff_available"] is False, (
                f"Expected category_cutoff_available=False for PwD but got True: {row}"
            )

    def test_valid_category_rows_marked_available(self):
        rows = filter_and_evaluate_admission(3000, "General", self._two_programs())
        for row in rows:
            assert row["category_cutoff_available"] is True

    def test_college_type_filter_still_works(self):
        programs = load_college_programs()
        nit_rows = filter_and_evaluate_admission(5000, "General", programs, college_type="NIT")
        for row in nit_rows:
            assert row["type"] == "NIT"

    def test_existing_output_fields_present(self):
        """Existing callers (query_service) expect these fields — must not break."""
        rows = filter_and_evaluate_admission(3000, "General", self._two_programs())
        required = {
            "college", "branch", "type", "exam", "category",
            "candidate_rank", "historical_cutoff", "cutoff_year_round",
            "rank_difference", "likelihood_range", "tier",
            "uncertainty_note", "median_ctc", "placement_rate",
            "tuition_fee", "location",
        }
        for row in rows:
            missing = required - row.keys()
            assert not missing, f"Row missing fields {missing}: {row}"


# ══════════════════════════════════════════════════════════════════════════════
# 9. End-to-end: real JSON → recommendations still work
# ══════════════════════════════════════════════════════════════════════════════

class TestEndToEnd:

    def test_general_5000_gets_recommendations(self):
        from app.models.student import StudentProfile
        from app.services.ranker import generate_recommendations

        student = StudentProfile(
            rank=5000,
            category="General",
            interests=["Artificial Intelligence"],
            career_goals=["Software Engineering"],
        )
        result = generate_recommendations(student)
        assert result.total_evaluated == 275
        assert len(result.preferences) >= 5
        # Must have at least one tier populated
        assert any(v > 0 for v in result.tier_summary.values())

    def test_obc_ncl_2000_gets_recommendations(self):
        from app.models.student import StudentProfile
        from app.services.ranker import generate_recommendations

        student = StudentProfile(
            rank=2000,
            category="OBC-NCL",
            interests=["Machine Learning"],
            career_goals=["Research"],
        )
        result = generate_recommendations(student)
        assert result.total_evaluated == 275
        assert len(result.preferences) >= 3

    def test_all_five_standard_categories_produce_results(self):
        from app.models.student import StudentProfile
        from app.services.ranker import generate_recommendations

        for cat in ("General", "OBC-NCL", "SC", "ST", "EWS"):
            student = StudentProfile(rank=8000, category=cat)
            result = generate_recommendations(student)
            assert result.total_evaluated == 275, (
                f"Category {cat}: expected 275 evaluated, got {result.total_evaluated}"
            )

    def test_pwd_category_does_not_crash_recommendations(self):
        """
        PwD categories must not cause an exception — they should just
        produce REACH results with unavailable notes.
        """
        from app.models.student import StudentProfile
        from app.services.ranker import generate_recommendations

        student = StudentProfile(rank=5000, category="General-PwD")
        result = generate_recommendations(student)
        assert result.total_evaluated == 275
        # All should be REACH since data is unavailable
        for pref in result.preferences:
            assert pref.tier == LikelihoodTier.REACH, (
                f"Expected REACH for General-PwD (no data), "
                f"got {pref.tier} for {pref.program.college_name}"
            )

    def test_disclaimer_present(self):
        from app.models.student import StudentProfile
        from app.services.ranker import generate_recommendations

        result = generate_recommendations(StudentProfile(rank=4000, category="General"))
        assert result.disclaimer
        assert len(result.disclaimer) > 20
