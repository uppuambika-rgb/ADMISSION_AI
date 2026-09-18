import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print(" /api/health passed!")

def test_api_programs():
    res = client.get("/api/programs")
    assert res.status_code == 200
    programs = res.json()
    assert len(programs) >= 12
    assert "id" in programs[0]
    assert "college_name" in programs[0]
    assert "placement_stats" in programs[0]
    print(f" /api/programs passed! Total programs: {len(programs)}")

def test_api_chat():
    # Turn 1: Introduce rank and category
    req1 = {
        "message": "Hello, my rank is 4500 and category is General.",
        "history": [],
        "current_profile": None
    }
    res1 = client.post("/api/chat", json=req1)
    assert res1.status_code == 200
    data1 = res1.json()
    profile1 = data1["extracted_profile"]
    assert profile1["rank"] == 4500
    assert profile1["category"] == "General"
    print(" /api/chat Turn 1 passed! Extracted rank:", profile1["rank"])

    # Turn 2: Provide interests and career goals
    req2 = {
        "message": "I love Artificial Intelligence and Machine Learning, and want to be a software engineer.",
        "history": [
            {"role": "user", "content": req1["message"]},
            {"role": "assistant", "content": data1["reply"]}
        ],
        "current_profile": profile1
    }
    res2 = client.post("/api/chat", json=req2)
    assert res2.status_code == 200
    data2 = res2.json()
    profile2 = data2["extracted_profile"]
    assert "Artificial Intelligence" in profile2["interests"]
    assert "Software Engineering" in profile2["career_goals"]
    assert data2["is_profile_complete"] is True
    print(" /api/chat Turn 2 passed! Profile complete:", data2["is_profile_complete"])

def test_api_recommend():
    student_payload = {
        "rank": 5200,
        "category": "General",
        "academic_strengths": ["Mathematics", "Programming"],
        "interests": ["Artificial Intelligence", "Machine Learning", "Software Engineering"],
        "career_goals": ["Software Engineering"],
        "preferred_locations": []
    }
    res = client.post("/api/recommend", json=student_payload)
    assert res.status_code == 200
    data = res.json()
    assert "preferences" in data
    assert len(data["preferences"]) > 0
    assert "tier_summary" in data
    assert "disclaimer" in data
    
    # Check top recommendation structure
    first_pref = data["preferences"][0]
    assert "tier" in first_pref
    assert "likelihood_range" in first_pref
    assert "composite_score" in first_pref
    assert "ai_explanation" in first_pref
    assert "uncertainty_note" in first_pref
    
    print(f" /api/recommend passed! Generated {len(data['preferences'])} choices.")
    print("   Sample choice #1:", first_pref["program"]["college_name"], "-", first_pref["program"]["branch_name"], f"[{first_pref['tier']}]")

def test_frontend_mount():
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Admission Counsellor" in res.text or "<html" in res.text
    print(" Frontend static mount passed!")

if __name__ == "__main__":
    test_api_health()
    test_api_programs()
    test_api_chat()
    test_api_recommend()
    test_frontend_mount()
    print("\nALL END-TO-END API TESTS PASSED SUCCESSFULLY!")
