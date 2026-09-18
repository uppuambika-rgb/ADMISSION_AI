from typing import List, Dict, Any
from app.models.program import CollegeProgram

def get_placement_comparison(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Sorts and formats placement outcomes across programmes.
    """
    # Sort by median salary descending
    sorted_progs = sorted(programs, key=lambda p: p.placement_stats.median_salary_lpa, reverse=True)
    rows = []
    for p in sorted_progs:
        stats = p.placement_stats
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "median_ctc": f"₹{stats.median_salary_lpa} LPA",
            "placement_rate": f"{stats.placement_percentage}%",
            "top_recruiters": ", ".join(stats.top_recruiters[:4]),
            "career_domains": ", ".join(stats.key_career_domains[:3])
        })
    return rows

def get_job_roles_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns verified typical job profiles for each programme.
    """
    rows = []
    for p in programs:
        roles_str = ", ".join(p.typical_roles) if p.typical_roles else "Not available"
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "typical_roles": roles_str,
            "median_ctc": f"₹{p.placement_stats.median_salary_lpa} LPA",
            "key_recruiters": ", ".join(p.placement_stats.top_recruiters[:3])
        })
    return rows

def get_higher_studies_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns graduate research and master's degree admission records.
    """
    rows = []
    for p in programs:
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "higher_studies": p.higher_study_opportunities or "Not available",
            "tier": p.tier_rating
        })
    return rows

def get_entrepreneurship_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns campus startup incubation, funding, and entrepreneurship support.
    """
    rows = []
    for p in programs:
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "entrepreneurship_support": p.entrepreneurship_opportunities or "Not available"
        })
    return rows
