import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.models.student import StudentProfile

client = TestClient(app)

BASE_STUDENT = {
    "rank": 4800,
    "category": "General",
    "entrance_exam": "JEE Main",
    "academic_strengths": ["Mathematics", "Programming"],
    "interests": ["Artificial Intelligence", "Software Engineering"],
    "career_goals": ["Software Engineering"],
    "placement_priorities": ["High Placement CTC"],
    "higher_study_interest": "Interested in MS abroad",
    "entrepreneurship_interest": "Interested in startups",
    "preferred_locations": []
}

QUESTIONS_TO_TEST = [
    ("1. NIT Admission", "Can I get into an NIT?", "NIT_ADMISSION"),
    ("2. Colleges Available", "Which colleges can I get?", "COLLEGES_AVAILABLE"),
    ("3. Safest Options", "Which are my safest options?", "SAFEST_OPTIONS"),
    ("4. Best for AI", "Which programme is best for AI?", "AI_CURRICULUM"),
    ("5. Better Placements", "Which has better placements?", "PLACEMENTS_COMPARE"),
    ("6. Fees Inquiry", "What are the fees?", "FEES_INQUIRY"),
    ("7. Hostel Inquiry", "Is hostel available?", "HOSTEL_INQUIRY"),
    ("8. Why Ranked First", "Why did you rank this programme first?", "WHY_FIRST_RANK"),
    ("9. CSE Branch", "Can I get CSE?", "BRANCH_CSE"),
]

def run_tests():
    print("=" * 70)
    print("  RUNNING MULTI-INTENT FOLLOW-UP QUERY TEST SUITE")
    print("=" * 70)

    distinct_titles = set()
    distinct_intents = set()

    for label, question, expected_intent in QUESTIONS_TO_TEST:
        print(f"\nTesting {label}: '{question}'...")
        payload = {
            "message": question,
            "history": [],
            "current_profile": BASE_STUDENT
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200, f"Failed on {label}: {res.text}"
        data = res.json()

        intent = data.get("intent")
        structured = data.get("structured_data")
        reply = data.get("reply", "")

        assert intent == expected_intent, f"Expected intent {expected_intent}, got {intent}"
        assert structured is not None, f"Expected structured_data for {label}, got None"
        assert len(structured["rows"]) > 0, f"Expected non-empty rows for {label}"
        assert len(structured["columns"]) > 0, f"Expected non-empty columns for {label}"
        assert len(reply) > 20, f"Expected detailed explanation for {label}"

        # Ensure no placeholder or generic repeat
        assert "Your personalized, tier-classified preference list is ready on your dashboard" not in reply, \
            f"Failed: {label} repeated generic intake message!"

        print(f"  Intent: {intent}")
        print(f"  Title: {structured['title']}")
        print(f"  Columns: {', '.join(structured['columns'][:4])}...")
        print(f"  Rows Returned: {len(structured['rows'])}")
        print(f"  Explanation Snippet: {reply[:90]}...")

        distinct_titles.add(structured["title"])
        distinct_intents.add(intent)

    # Verify that all 9 questions produced 9 DISTINCT data-driven outcomes
    assert len(distinct_intents) == 9, f"Expected 9 distinct intents, got {len(distinct_intents)}"
    assert len(distinct_titles) == 9, f"Expected 9 distinct structured tables, got {len(distinct_titles)}"

    print("\n" + "=" * 70)
    print(" ALL 9 FOLLOW-UP QUERY TYPES PASSED WITH DISTINCT DATA-DRIVEN RESULTS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
