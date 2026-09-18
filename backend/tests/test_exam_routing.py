"""
test_exam_routing.py
────────────────────
Validates the strict exam → institute-type routing introduced in the
JEE Main / JEE Advanced / AP EAPCET upgrade.

Rules enforced:
  JEE Main    → college_type == "NIT"  ONLY  (5 records)
  JEE Advanced → college_type == "IIT"  ONLY  (3 records)
  AP EAPCET   → no data → total_evaluated == 0, non-empty disclaimer
  Unknown exam → total_evaluated == 0, non-empty disclaimer
  No exam set → all programs evaluated (backward-compat, 15 records)

Also tests:
  - same rank with different exams produces different college sets
  - evaluator filter_and_evaluate_admission enforces the same gate
  - AP EAPCET never returns NIT or IIT rows
  - missing category cutoff path still works within exam routing

Run from the project root:
    .\\backend\\venv\\Scripts\\python.exe -m pytest backend/tests/test_exam_routing.py -v
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from app.models.student import StudentProfile
from app.models.program import LikelihoodTier
from app.services.ranker import generate_recommendations, load_college_programs
from app.services.evaluator import filter_and_evaluate_admission

# ── Dataset counts (verified from sample_colleges.json) ──────────────────────
NIT_COUNT  = 160   # 32 NITs × 5 branches
IIT_COUNT  = 115   # 23 IITs × 5 branches
TOTAL      = 275   # all records (IIT + NIT)


# ══════════════════════════════════════════════════════════════════════════════
# 1. JEE Main → NITs ONLY
# ══════════════════════════════════════════════════════════════════════════════
class TestJEEMainNITsOnly:

    def _student(self, rank=5000, category="General"):
        return StudentProfile(
            entrance_exam="JEE Main",
            rank=rank,
            category=category,
        )

    def test_total_evaluated_equals_nit_count(self):
        result = generate_recommendations(self._student())
        assert result.total_evaluated == NIT_COUNT, (
            f"JEE Main should evaluate only {NIT_COUNT} NITs, "
            f"got {result.total_evaluated}"
        )

    def test_all_preferences_are_nits(self):
        result = generate_recommendations(self._student())
        for pref in result.preferences:
            assert pref.program.college_type == "NIT", (
                f"JEE Main returned non-NIT: {pref.program.college_name} "
                f"(type={pref.program.college_type})"
            )

    def test_no_iit_in_preferences(self):
        result = generate_recommendations(self._student(rank=100))
        iit_names = [p.program.college_name for p in result.preferences
                     if p.program.college_type == "IIT"]
        assert not iit_names, (
            f"JEE Main recommendations contained IITs: {iit_names}"
        )

    def test_no_private_or_state_in_preferences(self):
        result = generate_recommendations(self._student())
        bad = [p.program.college_name for p in result.preferences
               if p.program.college_type not in ("NIT",)]
        assert not bad, (
            f"JEE Main returned non-NIT colleges: {bad}"
        )

    def test_has_recommendations(self):
        result = generate_recommendations(self._student(rank=10000))
        assert len(result.preferences) >= 1, (
            "JEE Main rank 10000 should produce at least 1 NIT recommendation"
        )

    def test_obc_ncl_category(self):
        result = generate_recommendations(self._student(rank=3000, category="OBC-NCL"))
        assert result.total_evaluated == NIT_COUNT
        for pref in result.preferences:
            assert pref.program.college_type == "NIT"

    def test_sc_category(self):
        result = generate_recommendations(self._student(rank=1500, category="SC"))
        assert result.total_evaluated == NIT_COUNT


# ══════════════════════════════════════════════════════════════════════════════
# 2. JEE Advanced → IITs ONLY
# ══════════════════════════════════════════════════════════════════════════════
class TestJEEAdvancedIITsOnly:

    def _student(self, rank=500, category="General"):
        return StudentProfile(
            entrance_exam="JEE Advanced",
            rank=rank,
            category=category,
        )

    def test_total_evaluated_equals_iit_count(self):
        result = generate_recommendations(self._student())
        assert result.total_evaluated == IIT_COUNT, (
            f"JEE Advanced should evaluate only {IIT_COUNT} IITs, "
            f"got {result.total_evaluated}"
        )

    def test_all_preferences_are_iits(self):
        result = generate_recommendations(self._student())
        for pref in result.preferences:
            assert pref.program.college_type == "IIT", (
                f"JEE Advanced returned non-IIT: {pref.program.college_name} "
                f"(type={pref.program.college_type})"
            )

    def test_no_nit_in_preferences(self):
        result = generate_recommendations(self._student(rank=50000))
        nit_names = [p.program.college_name for p in result.preferences
                     if p.program.college_type == "NIT"]
        assert not nit_names, (
            f"JEE Advanced recommendations contained NITs: {nit_names}"
        )

    def test_has_recommendations(self):
        result = generate_recommendations(self._student(rank=1000))
        assert len(result.preferences) >= 1

    def test_sc_category(self):
        result = generate_recommendations(self._student(rank=200, category="SC"))
        assert result.total_evaluated == IIT_COUNT
        for pref in result.preferences:
            assert pref.program.college_type == "IIT"


# ══════════════════════════════════════════════════════════════════════════════
# 3. AP EAPCET → explicit unavailable, NEVER NITs or IITs
# ══════════════════════════════════════════════════════════════════════════════
class TestAPEAPCETUnavailable:

    def _student(self, rank=5000):
        return StudentProfile(
            entrance_exam="AP EAPCET",
            rank=rank,
            category="General",
        )

    def test_total_evaluated_is_zero(self):
        result = generate_recommendations(self._student())
        assert result.total_evaluated == 0, (
            f"AP EAPCET should return 0 evaluated programmes (no data), "
            f"got {result.total_evaluated}"
        )

    def test_preferences_list_is_empty(self):
        result = generate_recommendations(self._student())
        assert result.preferences == [], (
            f"AP EAPCET should return empty preferences, got {result.preferences}"
        )

    def test_disclaimer_signals_unavailable(self):
        result = generate_recommendations(self._student())
        disc = result.disclaimer.lower()
        assert "unavailable" in disc or "ap eapcet" in disc, (
            f"AP EAPCET disclaimer should mention unavailability. Got: {result.disclaimer}"
        )

    def test_no_nit_in_result(self):
        result = generate_recommendations(self._student())
        nits = [p.program.college_name for p in result.preferences
                if p.program.college_type == "NIT"]
        assert not nits, f"AP EAPCET must NEVER return NITs. Got: {nits}"

    def test_no_iit_in_result(self):
        result = generate_recommendations(self._student())
        iits = [p.program.college_name for p in result.preferences
                if p.program.college_type == "IIT"]
        assert not iits, f"AP EAPCET must NEVER return IITs. Got: {iits}"

    def test_eapcet_alias_also_works(self):
        """'EAPCET' (without AP prefix) must also be treated as unavailable."""
        student = StudentProfile(entrance_exam="EAPCET", rank=5000, category="General")
        result = generate_recommendations(student)
        assert result.total_evaluated == 0
        assert result.preferences == []

    def test_tier_summary_all_zeros(self):
        result = generate_recommendations(self._student())
        for tier, count in result.tier_summary.items():
            assert count == 0, (
                f"AP EAPCET tier_summary should be all zeros, "
                f"got {tier}={count}"
            )


# ══════════════════════════════════════════════════════════════════════════════
# 4. Unknown / unsupported exam
# ══════════════════════════════════════════════════════════════════════════════
class TestUnknownExam:

    def test_unknown_exam_returns_zero_evaluated(self):
        student = StudentProfile(entrance_exam="BITSAT", rank=200, category="General")
        result = generate_recommendations(student)
        assert result.total_evaluated == 0, (
            f"Unknown exam 'BITSAT' should return 0 evaluated, got {result.total_evaluated}"
        )

    def test_unknown_exam_preferences_empty(self):
        student = StudentProfile(entrance_exam="WBJEE", rank=1000, category="General")
        result = generate_recommendations(student)
        assert result.preferences == []

    def test_unknown_exam_disclaimer_mentions_unsupported(self):
        student = StudentProfile(entrance_exam="KCET", rank=1000, category="General")
        result = generate_recommendations(student)
        disc = result.disclaimer.lower()
        assert "unsupported" in disc or "kcet" in disc or "unavailable" in disc, (
            f"Unknown exam disclaimer should signal unsupported. Got: {result.disclaimer}"
        )

    def test_unknown_exam_never_returns_nit(self):
        student = StudentProfile(entrance_exam="MHT-CET", rank=500, category="General")
        result = generate_recommendations(student)
        nits = [p.program.college_name for p in result.preferences
                if p.program.college_type == "NIT"]
        assert not nits

    def test_unknown_exam_never_returns_iit(self):
        student = StudentProfile(entrance_exam="VITEEE", rank=500, category="General")
        result = generate_recommendations(student)
        iits = [p.program.college_name for p in result.preferences
                if p.program.college_type == "IIT"]
        assert not iits


# ══════════════════════════════════════════════════════════════════════════════
# 5. No exam set → backward-compat (all 15 programs)
# ══════════════════════════════════════════════════════════════════════════════
class TestNoExamBackwardCompat:

    def test_no_exam_evaluates_all_programs(self):
        student = StudentProfile(rank=5000, category="General")
        result = generate_recommendations(student)
        assert result.total_evaluated == TOTAL, (
            f"No-exam path should evaluate all {TOTAL} programs, "
            f"got {result.total_evaluated}"
        )

    def test_entrance_exam_none_evaluates_all(self):
        student = StudentProfile(entrance_exam=None, rank=5000, category="General")
        result = generate_recommendations(student)
        assert result.total_evaluated == TOTAL

    def test_entrance_exam_empty_string_evaluates_all(self):
        student = StudentProfile(entrance_exam="", rank=5000, category="General")
        result = generate_recommendations(student)
        assert result.total_evaluated == TOTAL


# ══════════════════════════════════════════════════════════════════════════════
# 6. Same rank, different exams → completely different result sets
# ══════════════════════════════════════════════════════════════════════════════
class TestSameRankDifferentExams:

    RANK = 5000

    def test_jee_main_and_advanced_give_different_colleges(self):
        main_result = generate_recommendations(
            StudentProfile(entrance_exam="JEE Main", rank=self.RANK, category="General")
        )
        adv_result = generate_recommendations(
            StudentProfile(entrance_exam="JEE Advanced", rank=self.RANK, category="General")
        )
        main_ids = {p.program.id for p in main_result.preferences}
        adv_ids  = {p.program.id for p in adv_result.preferences}
        # The two sets must be completely disjoint
        overlap = main_ids & adv_ids
        assert not overlap, (
            f"JEE Main and JEE Advanced recommendations overlap — "
            f"shared program IDs: {overlap}. Cross-exam contamination detected."
        )

    def test_jee_main_colleges_are_all_nits(self):
        result = generate_recommendations(
            StudentProfile(entrance_exam="JEE Main", rank=self.RANK, category="General")
        )
        for pref in result.preferences:
            assert pref.program.college_type == "NIT"

    def test_jee_advanced_colleges_are_all_iits(self):
        result = generate_recommendations(
            StudentProfile(entrance_exam="JEE Advanced", rank=self.RANK, category="General")
        )
        for pref in result.preferences:
            assert pref.program.college_type == "IIT"

    def test_ap_eapcet_gives_zero_results_vs_jee_main_nits(self):
        jee_result = generate_recommendations(
            StudentProfile(entrance_exam="JEE Main", rank=self.RANK, category="General")
        )
        ap_result = generate_recommendations(
            StudentProfile(entrance_exam="AP EAPCET", rank=self.RANK, category="General")
        )
        assert jee_result.total_evaluated == NIT_COUNT
        assert ap_result.total_evaluated == 0
        # AP result must share no colleges with JEE Main result
        jee_ids = {p.program.id for p in jee_result.preferences}
        ap_ids  = {p.program.id for p in ap_result.preferences}
        assert not (jee_ids & ap_ids)


# ══════════════════════════════════════════════════════════════════════════════
# 7. filter_and_evaluate_admission — strict exam gate
# ══════════════════════════════════════════════════════════════════════════════
class TestEvaluatorExamGate:

    def setup_method(self):
        self.programs = load_college_programs()

    def test_jee_main_returns_only_nit_rows(self):
        rows = filter_and_evaluate_admission(
            5000, "General", self.programs, entrance_exam="JEE Main"
        )
        for r in rows:
            assert r["type"] == "NIT", (
                f"JEE Main evaluator returned non-NIT: {r['college']} (type={r['type']})"
            )

    def test_jee_advanced_returns_only_iit_rows(self):
        rows = filter_and_evaluate_admission(
            500, "General", self.programs, entrance_exam="JEE Advanced"
        )
        for r in rows:
            assert r["type"] == "IIT", (
                f"JEE Advanced evaluator returned non-IIT: {r['college']} (type={r['type']})"
            )

    def test_ap_eapcet_returns_empty_list(self):
        rows = filter_and_evaluate_admission(
            5000, "General", self.programs, entrance_exam="AP EAPCET"
        )
        assert rows == [], (
            f"AP EAPCET evaluator should return [], got {len(rows)} rows"
        )

    def test_no_exam_returns_all_programs(self):
        rows = filter_and_evaluate_admission(5000, "General", self.programs)
        assert len(rows) == TOTAL

    def test_jee_main_nit_count_is_correct(self):
        rows = filter_and_evaluate_admission(
            5000, "General", self.programs, entrance_exam="JEE Main"
        )
        assert len(rows) == NIT_COUNT, (
            f"Expected {NIT_COUNT} NIT rows for JEE Main, got {len(rows)}"
        )

    def test_jee_advanced_iit_count_is_correct(self):
        rows = filter_and_evaluate_admission(
            500, "General", self.programs, entrance_exam="JEE Advanced"
        )
        assert len(rows) == IIT_COUNT, (
            f"Expected {IIT_COUNT} IIT rows for JEE Advanced, got {len(rows)}"
        )

    def test_college_type_filter_within_exam_gate(self):
        """Explicit college_type='NIT' with JEE Main should still return NITs only."""
        rows = filter_and_evaluate_admission(
            5000, "General", self.programs,
            college_type="NIT", entrance_exam="JEE Main"
        )
        assert len(rows) == NIT_COUNT
        for r in rows:
            assert r["type"] == "NIT"

    def test_jee_main_with_iit_type_filter_returns_empty(self):
        """JEE Main + college_type='IIT' must return empty — exam gate blocks IITs."""
        rows = filter_and_evaluate_admission(
            500, "General", self.programs,
            college_type="IIT", entrance_exam="JEE Main"
        )
        assert rows == [], (
            "JEE Main with college_type='IIT' should return [] due to exam gate. "
            f"Got {len(rows)} rows."
        )


# ══════════════════════════════════════════════════════════════════════════════
# 8. Missing category cutoff within valid exam routing
# ══════════════════════════════════════════════════════════════════════════════
class TestMissingCategoryWithinExamRouting:

    def test_jee_main_pwd_category_returns_reach_only(self):
        """PwD category has no verified cutoff data — all NIT results must be REACH."""
        student = StudentProfile(
            entrance_exam="JEE Main",
            rank=5000,
            category="General-PwD",
        )
        result = generate_recommendations(student)
        assert result.total_evaluated == NIT_COUNT
        for pref in result.preferences:
            assert pref.tier == LikelihoodTier.REACH, (
                f"Expected REACH for PwD (no cutoff data), "
                f"got {pref.tier} for {pref.program.college_name}"
            )

    def test_jee_advanced_pwd_category_returns_reach_only(self):
        student = StudentProfile(
            entrance_exam="JEE Advanced",
            rank=500,
            category="SC-PwD",
        )
        result = generate_recommendations(student)
        assert result.total_evaluated == IIT_COUNT
        for pref in result.preferences:
            assert pref.tier == LikelihoodTier.REACH
