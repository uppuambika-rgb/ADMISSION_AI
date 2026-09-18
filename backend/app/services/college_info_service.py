from typing import List, Dict, Any, Optional
from app.models.program import CollegeProgram

def get_fees_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns factual fee details (tuition and hostel) without fabrication.
    """
    rows = []
    for p in programs:
        tuition_str = f"₹{p.annual_tuition_fee_inr:,} / year" if p.annual_tuition_fee_inr is not None else "Not available"
        hostel_str = f"₹{p.annual_hostel_fee_inr:,} / year" if p.annual_hostel_fee_inr is not None else "Not available"
        hostel_avail_str = "Yes" if p.hostel_available else "No"
        
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "type": p.college_type,
            "annual_tuition_fee": tuition_str,
            "hostel_available": hostel_avail_str,
            "annual_hostel_fee": hostel_str,
            "location": p.location
        })
    return rows

def get_scholarships_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns verified scholarship and fee-waiver policies.
    """
    rows = []
    for p in programs:
        rows.append({
            "college": p.college_name,
            "branch": p.branch_name,
            "type": p.college_type,
            "scholarships": p.scholarships or "Not available",
            "annual_tuition_fee": f"₹{p.annual_tuition_fee_inr:,} / year" if p.annual_tuition_fee_inr is not None else "Not available"
        })
    return rows

def get_hostel_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns hostel availability and mess/room fees.
    """
    rows = []
    for p in programs:
        hostel_str = f"₹{p.annual_hostel_fee_inr:,} / year" if p.annual_hostel_fee_inr is not None else "Not available"
        rows.append({
            "college": p.college_name,
            "location": p.location,
            "hostel_available": "Yes (On-campus)" if p.hostel_available else "No / Not available",
            "hostel_fee": hostel_str
        })
    return rows

def get_location_information(programs: List[CollegeProgram]) -> List[Dict[str, Any]]:
    """
    Returns location and campus context.
    """
    rows = []
    for p in programs:
        rows.append({
            "college": p.college_name,
            "location": p.location,
            "type": p.college_type
        })
    return rows
