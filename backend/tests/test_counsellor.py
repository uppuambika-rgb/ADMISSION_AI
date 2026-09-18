import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.models.student import StudentProfile
from app.services.ranker import generate_recommendations
from app.services.evaluator import evaluate_admission_likelihood
from app.services.matcher import calculate_curriculum_match
from app.services.ai_counsellor import extract_profile_from_text, generate_chat_reply

def test_evaluation():
    print("Testing Evaluator...")
    from app.services.ranker import load_college_programs
    programs = load_college_programs()
    assert len(programs) > 0, "No programs loaded!"

    # Pick first NIT CSE record from the expanded dataset
    nit_cse = next(
        p for p in programs
        if p.college_type == "NIT" and "Computer Science" in p.branch_name
    )
    gen_cutoff = nit_cse.category_cutoffs["General"].closing_rank
    print(f"Using: {nit_cse.college_name} CSE, General closing rank: {gen_cutoff}")

    # Rank well below closing → Safe
    safe_rank = max(1, round(gen_cutoff * 0.5))
    tier, l_range, margin, _ = evaluate_admission_likelihood(safe_rank, "General", nit_cse)
    print(f"Rank {safe_rank}: Tier={tier.value}, Margin={margin}%")
    assert tier.value == "Safe", f"Expected Safe for rank {safe_rank} vs cutoff {gen_cutoff}"

    # Rank just above closing → Aspirational or Reach
    hard_rank = round(gen_cutoff * 1.2)
    tier2, l_range2, margin2, _ = evaluate_admission_likelihood(hard_rank, "General", nit_cse)
    print(f"Rank {hard_rank}: Tier={tier2.value}, Margin={margin2}%")
    assert tier2.value in ["Aspirational", "Reach", "Likely"]
    print(" Evaluator passed!")

def test_extraction():
    print("Testing Text Extraction...")
    profile = StudentProfile()
    text = "Hi, my rank is 4200 and category is OBC-NCL. I am really interested in artificial intelligence and robotics. I want to become a software engineer."
    extracted, missing = extract_profile_from_text(text, profile)
    print(f"Extracted: Rank={extracted.rank}, Cat={extracted.category}, Interests={extracted.interests}, Goals={extracted.career_goals}")
    assert extracted.rank == 4200
    assert extracted.category == "OBC-NCL"
    assert "Artificial Intelligence" in extracted.interests
    assert "Robotics & Automation" in extracted.interests
    assert "Software Engineering" in extracted.career_goals
    print(" Extraction passed!")

def test_recommendations():
    print("Testing Full Recommendation Pipeline...")
    student = StudentProfile(
        rank=7500,
        category="General",
        academic_strengths=["Mathematics", "Coding"],
        interests=["Artificial Intelligence", "Machine Learning", "Software Engineering"],
        career_goals=["Software Engineering"]
    )
    res = generate_recommendations(student)
    print(f"Evaluated {res.total_evaluated} colleges. Generated {len(res.preferences)} recommendations.")
    print("Top Recommendations:")
    for idx, pref in enumerate(res.preferences, 1):
        print(f"  {idx}. [{pref.tier.value}] {pref.program.college_name} - {pref.program.branch_name} ({pref.likelihood_range}) Score: {pref.composite_score}")
    
    assert len(res.preferences) >= 5
    # Verify tier presence
    tiers = [p.tier.value for p in res.preferences]
    print("Tiers in preferences:", set(tiers))
    print(" Recommendation pipeline passed!")

if __name__ == "__main__":
    test_evaluation()
    test_extraction()
    test_recommendations()
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")
