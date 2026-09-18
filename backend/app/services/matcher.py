from typing import List, Tuple, Dict, Any, Optional
from app.models.student import StudentProfile
from app.models.program import CollegeProgram

# Synonyms and related terms map for smart matching without heavy NLP libraries
SYNONYM_MAP = {
    "ai": ["artificial intelligence", "machine learning", "deep learning", "neural", "nlp", "computer vision", "generative ai"],
    "ml": ["machine learning", "deep learning", "data science", "analytics", "statistics", "reinforcement learning"],
    "data science": ["data analytics", "machine learning", "statistics", "big data", "python"],
    "software": ["programming", "algorithms", "data structures", "web", "full stack", "cloud", "devops"],
    "coding": ["algorithms", "data structures", "competitive programming", "software", "python", "c++"],
    "web": ["web technologies", "full stack", "frontend", "backend", "cloud", "web applications"],
    "robotics": ["control systems", "embedded systems", "sensors", "mechatronics", "iot", "automation"],
    "hardware": ["vlsi", "microprocessors", "embedded systems", "semiconductors", "circuits"],
    "finance": ["financial engineering", "quantitative finance", "stochastic", "fintech", "trading"],
    "cybersecurity": ["information security", "network security", "cryptography"]
}

def calculate_curriculum_match(
    student: StudentProfile,
    program: CollegeProgram
) -> Tuple[float, List[str]]:
    """
    Matches student interests and strengths against curriculum keywords & branch name.
    Returns:
        (interest_score_0_to_100, matched_keywords)
    """
    user_queries = [s.lower().strip() for s in (student.interests + student.academic_strengths + student.career_goals)]
    if not user_queries:
        return 50.0, ["General Engineering Foundation"]

    curriculum_keywords_lower = [kw.lower() for kw in program.curriculum_keywords]
    branch_lower = program.branch_name.lower()
    matched_tags = set()

    raw_matches = 0
    for query in user_queries:
        if not query:
            continue
        
        # Direct match in branch name
        if query in branch_lower or branch_lower in query:
            raw_matches += 2.0
            matched_tags.add(program.branch_name)

        # Direct match in curriculum keywords
        for kw in program.curriculum_keywords:
            if query in kw.lower() or kw.lower() in query:
                raw_matches += 1.5
                matched_tags.add(kw)

        # Synonym expansion match
        for key, synonyms in SYNONYM_MAP.items():
            if query == key or query in synonyms:
                for kw in program.curriculum_keywords:
                    kw_low = kw.lower()
                    if any(syn in kw_low for syn in synonyms):
                        raw_matches += 1.0
                        matched_tags.add(kw)

    base_score = 35.0
    scaled_score = min(98.0, base_score + (raw_matches * 12.0))

    matched_list = sorted(list(matched_tags))[:5]
    if not matched_list:
        matched_list = [program.branch_name]

    return round(scaled_score, 1), matched_list

def calculate_ai_ml_relevance(program: CollegeProgram) -> Tuple[str, float]:
    """
    Evaluates how strongly the curriculum focuses on AI, ML, and Data Science.
    Returns: (relevance_label, relevance_score_0_to_100)
    """
    ai_keywords = ["artificial intelligence", "machine learning", "deep learning", "natural language processing", "computer vision", "generative ai", "reinforcement learning"]
    matched = [kw for kw in program.curriculum_keywords if any(ak in kw.lower() for ak in ai_keywords)]
    
    # Check branch name
    if "artificial intelligence" in program.branch_name.lower() or "data" in program.branch_name.lower():
        return "High (Specialized AI/DS Degree)", 95.0
    elif len(matched) >= 2:
        return f"Moderate-to-High ({len(matched)} core AI courses)", 80.0
    elif len(matched) == 1:
        return "Elective / Foundational AI", 60.0
    else:
        return "Minimal / Peripheral", 25.0

def detect_curriculum_mismatch(student: StudentProfile, program: CollegeProgram) -> Optional[str]:
    """
    Honestly identifies mismatches: if a program is prestigious but does NOT
    strongly support the student's stated career goal, explicitly warns the student.
    """
    goals_lower = [g.lower() for g in student.career_goals]
    interests_lower = [i.lower() for i in student.interests]
    
    wants_software_or_ai = any(
        k in g or k in i
        for k in ["software", "coding", "developer", "artificial intelligence", "ai", "machine learning", "data"]
        for g in goals_lower
        for i in interests_lower
    )

    is_mechanical_or_civil = any(
        core in program.branch_name.lower()
        for core in ["mechanical", "civil", "chemical", "metallurgy"]
    )

    if wants_software_or_ai and is_mechanical_or_civil:
        return (
            f"Advisory Warning: While {program.college_name} has high brand prestige, its curriculum in "
            f"{program.branch_name} focuses on core engineering topics ({', '.join(program.curriculum_keywords[:3])}). "
            "If your primary goal is Software Development or AI, you will need significant self-study alongside a demanding core lab schedule."
        )

    return None

def find_programmes_matching_interests(
    student: StudentProfile,
    programs: List[CollegeProgram],
    focus_keyword: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Ranks programmes primarily by curriculum fit, AI/ML focus, and what the course actually teaches.
    """
    results = []
    
    # If explicit focus keyword provided (e.g. "AI"), temporarily inject
    student_for_eval = student.model_copy()
    if focus_keyword and focus_keyword not in student_for_eval.interests:
        student_for_eval.interests = [focus_keyword] + student_for_eval.interests

    for p in programs:
        match_score, matched_topics = calculate_curriculum_match(student_for_eval, p)
        ai_label, ai_score = calculate_ai_ml_relevance(p)
        mismatch = detect_curriculum_mismatch(student, p)

        # Composite interest score
        composite = match_score * 0.7 + ai_score * 0.3 if focus_keyword and "ai" in focus_keyword.lower() else match_score

        results.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "type": p.college_type,
            "curriculum_focus": ", ".join(p.curriculum_keywords[:4]),
            "curriculum_fit_score": f"{match_score} / 100",
            "ai_ml_relevance": ai_label,
            "median_ctc": f"₹{p.placement_stats.median_salary_lpa} LPA",
            "mismatch_warning": mismatch,
            "_sort_score": composite
        })

    results.sort(key=lambda x: x["_sort_score"], reverse=True)
    for r in results:
        del r["_sort_score"]
    return results

def calculate_placement_score(program: CollegeProgram, student: StudentProfile) -> float:
    p_stats = program.placement_stats
    lpa_score = max(0.0, min(100.0, ((p_stats.median_salary_lpa - 6.0) / (32.0 - 6.0)) * 100.0))
    rate_score = max(0.0, min(100.0, ((p_stats.placement_percentage - 75.0) / 25.0) * 100.0))

    bonus = 0.0
    student_goals = [g.lower() for g in student.career_goals]
    if student_goals:
        for domain in p_stats.key_career_domains:
            if any(goal in domain.lower() for goal in student_goals):
                bonus += 10.0
                break

    composite_placement = (lpa_score * 0.55) + (rate_score * 0.35) + bonus
    return round(min(100.0, composite_placement), 1)
