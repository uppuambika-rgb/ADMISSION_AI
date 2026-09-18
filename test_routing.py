"""Quick test to verify exam routing works correctly"""
import requests

BASE = "http://localhost:8000/api"

tests = [
    {"rank": 5000, "category": "General", "entrance_exam": "JEE Main", "expected": "NIT"},
    {"rank": 2000, "category": "General", "entrance_exam": "JEE Advanced", "expected": "IIT"},
    {"rank": 10000, "category": "OC", "entrance_exam": "AP EAPCET", "expected": "AP EAPCET"},
]

print("Testing Exam Routing...")
print("=" * 80)

for test in tests:
    resp = requests.post(f"{BASE}/recommend", json=test)
    data = resp.json()
    
    total = data["total_evaluated"]
    prefs = data.get("preferences", [])
    if not prefs:
        print(f"  ⚠️ No recommendations returned!")
        continue
    
    top_3 = [p.get("college_name", p.get("program", {}).get("college_name", "Unknown")) for p in prefs[:3]]
    types = set(p.get("college_type", p.get("program", {}).get("college_type", "Unknown")) for p in prefs)
    
    print(f"\n✓ {test['entrance_exam']} | Rank {test['rank']}")
    print(f"  Total Evaluated: {total}")
    print(f"  College Types: {', '.join(types)}")
    print(f"  Top 3:")
    for i, name in enumerate(top_3, 1):
        print(f"    {i}. {name}")
    
    # Verify routing
    assert test["expected"] in types, f"Expected {test['expected']} colleges!"
    assert len(types) == 1, f"Should only show {test['expected']} colleges!"
    print(f"  ✅ Routing correct: Only {test['expected']} colleges returned")

print("\n" + "=" * 80)
print("✅ All routing tests passed!")
