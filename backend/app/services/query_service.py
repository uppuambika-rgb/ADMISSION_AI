import re
from typing import Dict, Any, List, Optional, Tuple
from app.models.student import StudentProfile, StructuredQueryResult
from app.models.program import CollegeProgram
from app.services.evaluator import filter_and_evaluate_admission
from app.services.matcher import find_programmes_matching_interests, detect_curriculum_mismatch
from app.services.college_info_service import (
    get_fees_information,
    get_scholarships_information,
    get_hostel_information,
    get_location_information
)
from app.services.placement_service import (
    get_placement_comparison,
    get_job_roles_information,
    get_higher_studies_information,
    get_entrepreneurship_information
)
from app.services.ranker import generate_recommendations

DISCLAIMER_TEXT = (
    "Historical Trend Notice: Admission probabilities, cutoff margins, and placement records are derived from historical 2024 benchmarks. "
    "They represent estimated probabilistic ranges and do not guarantee future seat allotment or job placement."
)

# ── Intent Classification ────────────────────────────────────────────────────

def classify_intent(message: str) -> str:
    """
    Classifies student question into a normalized intent category.
    Improved to handle a wider range of natural phrasings and follow-up questions.
    """
    msg = message.lower().strip()

    # 1. Why ranked first / ranking rationale
    if any(k in msg for k in ["why did you rank", "why is this ranked first", "why ranked #1",
                               "why rank this first", "why first", "why is it first", "why top"]):
        return "WHY_FIRST_RANK"

    # 2. Preference list inquiry
    if any(k in msg for k in ["preference list", "choice filling", "my choices", "show preference",
                               "show choices", "choice sheet", "preference sheet"]):
        return "PREFERENCE_LIST"

    # 3. College type queries — order matters: check Advanced before Main
    if any(k in msg for k in ["ap eapcet", "eapcet", "ap counselling", "ap engineering"]):
        return "AP_EAPCET"

    if any(k in msg for k in ["jee advanced", "iit", "iits", "top iit", "iit bombay", "iit delhi",
                               "iit madras", "iit kharagpur", "iit roorkee", "iit kanpur",
                               "iit hyderabad", "iit guwahati", "iit bhu"]):
        return "IIT_ADMISSION"

    if any(k in msg for k in ["nit", "nits", "nit trichy", "nit warangal", "nit surathkal",
                               "nit calicut", "nit rourkela", "nit allahabad", "nit kurukshetra",
                               "national institute"]):
        return "NIT_ADMISSION"

    if any(k in msg for k in ["iiit", "iiits", "iiit hyderabad", "iiit bangalore", "iiit delhi",
                               "international institute of information"]):
        return "IIIT_ADMISSION"

    if any(k in msg for k in ["gfti", "government funded", "central university"]):
        return "GFTI_ADMISSION"    # 4. Branch queries — expanded to include "what is" questions
    if any(k in msg for k in ["can i get cse", "get cse", "computer science", "cse options",
                               "cs options", "btech cs", "b.tech cs", "what is cse", 
                               "tell me about cse", "about cse", "cse branch"]):
        return "BRANCH_CSE"

    if any(k in msg for k in ["ece", "electronics and communication", "electronics branch",
                               "get ece", "can i get ece", "what is ece", "tell me about ece",
                               "about ece", "ece branch"]):
        return "BRANCH_ECE"

    if any(k in msg for k in ["mechanical", "mech branch", "get mechanical",
                               "can i get mechanical", "what is mechanical", 
                               "tell me about mechanical", "about mechanical"]):
        return "BRANCH_MECH"

    if any(k in msg for k in ["civil", "civil branch", "get civil", "what is civil",
                               "tell me about civil", "about civil engineering"]):
        return "BRANCH_CIVIL"

    if any(k in msg for k in ["electrical", "eee", "get electrical", "what is electrical",
                               "what is eee", "tell me about electrical"]):
        return "BRANCH_EE"

    if any(k in msg for k in ["data science", "ds branch", "ai branch",
                               "artificial intelligence branch", "get data science",
                               "what is data science", "what is ai branch", 
                               "tell me about ai", "about artificial intelligence"]):
        return "BRANCH_DS_AI"

    # 5. Tier-specific queries
    if any(k in msg for k in ["safest", "safe options", "safe colleges", "my safe", "safety"]):
        return "SAFEST_OPTIONS"
    if any(k in msg for k in ["aspirational", "reach options", "dream colleges", "dream options",
                               "ambitious", "stretch goals"]):
        return "ASPIRATIONAL_OPTIONS"
    if any(k in msg for k in ["likely options", "likely colleges", "moderate options",
                               "realistic options", "realistic"]):
        return "LIKELY_OPTIONS"

    # 6. General college availability
    if any(k in msg for k in ["which colleges can i get", "what colleges can i get",
                               "colleges for my rank", "where can i get", "what can i get",
                               "which college", "available colleges", "eligible for"]):
        return "COLLEGES_AVAILABLE"

    # 7. College comparison
    if any(k in msg for k in ["compare", "vs", "versus", "better between", "which is better",
                               "difference between", "compare nit", "compare iit", "iit vs nit",
                               "nit vs iiit", "which one is better"]):
        return "COLLEGE_COMPARE"

    # 8. AI and Curriculum matching
    if any(k in msg for k in ["best for ai", "best for machine learning", "programme for ai",
                               "teach ai", "matches my interests", "match my interests",
                               "ai curriculum", "ml curriculum", "good for ai", "ai program",
                               "best ai college"]):
        return "AI_CURRICULUM"

    # 9. Placements & Job roles
    if any(k in msg for k in ["better placement", "best placement", "compare placement",
                               "highest ctc", "placement rate", "placements", "salary",
                               "package", "lpa", "ctc", "top package"]):
        return "PLACEMENTS_COMPARE"
    if any(k in msg for k in ["job roles", "typical roles", "what jobs", "career roles",
                               "job profiles", "what kind of jobs", "after graduation"]):
        return "JOB_ROLES"

    # 10. Fees, Scholarships, Hostels, Location
    if any(k in msg for k in ["fee", "fees", "tuition", "cost of study", "how expensive",
                               "fee structure", "how much does it cost", "total cost"]):
        return "FEES_INQUIRY"
    if any(k in msg for k in ["scholarship", "scholarships", "fee waiver", "financial aid",
                               "concession", "merit scholarship", "need based"]):
        return "SCHOLARSHIPS"
    if any(k in msg for k in ["hostel", "hostels", "accommodation", "dorm", "hostel fee",
                               "room", "campus stay", "boarding"]):
        return "HOSTEL_INQUIRY"
    if any(k in msg for k in ["located", "location", "locations", "which city", "which state",
                               "where is", "where are", "campus location"]):
        return "LOCATION_INQUIRY"

    # 11. Higher studies & Entrepreneurship
    if any(k in msg for k in ["higher study", "higher studies", "ms abroad", "masters",
                               "phd", "research", "graduate school", "foreign university",
                               "ms program", "phd program"]):
        return "HIGHER_STUDIES"
    if any(k in msg for k in ["entrepreneurship", "startup", "startups", "incubator",
                               "incubation", "ventures", "own company", "found a company"]):
        return "ENTREPRENEURSHIP"

    # 12. Admission chances for specific college (e.g. "can I get IIIT Hyderabad?")
    if any(k in msg for k in ["can i get", "my chances", "will i get", "chance at",
                               "chances at", "chance of getting", "probability of"]):
        return "COLLEGES_AVAILABLE"

    # 13. State quota / home state queries
    if any(k in msg for k in ["state quota", "home state", "hs quota", "other state quota",
                               "os quota", "domicile"]):
        return "STATE_QUOTA"

    # 14. Cutoff queries
    if any(k in msg for k in ["cutoff", "cutoffs", "closing rank", "opening rank",
                               "last rank", "last year cutoff", "2024 cutoff", "2023 cutoff"]):
        return "CUTOFF_INQUIRY"

    return "GENERAL_CONVERSATION"


# ── Query Processor ──────────────────────────────────────────────────────────

def process_counselling_query(
    message: str,
    student: StudentProfile,
    programs: List[CollegeProgram]
) -> Tuple[str, Optional[StructuredQueryResult]]:
    """
    Executes intent-based processing across reusable backend services.
    Returns (natural_text_explanation, structured_query_result).
    """
    intent = classify_intent(message)
    rank = student.rank if student.rank is not None else 8000
    category = student.category or "General"
    exam = student.entrance_exam or ""

    # ── AP EAPCET — explicit unavailable, never substitute NITs/IITs ────────
    if intent == "AP_EAPCET":
        return (
            "**AP EAPCET Data Unavailable.**\n\n"
            "Verified AP EAPCET participating-college cutoff data is not yet in our database. "
            "We cannot recommend colleges for AP EAPCET without verified, official data. "
            "We will **never** substitute JEE Main (NIT) or JEE Advanced (IIT) data for AP EAPCET — "
            "those are completely separate admission systems with different rank scales.\n\n"
            "📌 For AP EAPCET counselling, please visit the official portal: "
            "**https://cets.apsche.ap.gov.in**",
            None
        )

    # ── NIT Admission ────────────────────────────────────────────────────────
    if intent == "NIT_ADMISSION":
        # Validate: NITs need JEE Main. Warn if user has JEE Advanced.
        if exam and "advanced" in exam.lower():
            return (
                "NITs admit students via **JEE Main** scores through JoSAA counselling. "
                "You have mentioned **JEE Advanced** — with a JEE Advanced rank you are eligible for **IITs**, "
                "not NITs directly. You may still apply to NITs using your JEE Main score if you appeared for both exams. "
                "Please share your JEE Main rank for NIT eligibility.",
                None
            )
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             college_type="NIT", entrance_exam=exam or "JEE Main")
        if not rows:
            return (
                f"No NIT programmes found for rank #{rank:,} ({category}). "
                "NITs typically accept JEE Main scores. If your rank is very high (>50,000), consider State-level counselling options.",
                None
            )
        columns = ["College", "Branch", "Candidate Rank", "Historical Cutoff",
                   "Rank Difference", "Likelihood Range", "Tier", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Candidate Rank": r["candidate_rank"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"], "Median CTC": r["median_ctc"]
        } for r in rows]

        safe_count   = sum(1 for r in rows if r["tier"] == "Safe")
        likely_count = sum(1 for r in rows if r["tier"] == "Likely")
        asp_count    = sum(1 for r in rows if r["tier"] == "Aspirational")

        explanation = (
            f"Based on your rank of **#{rank:,}** ({category} category), here are the National Institutes of Technology (NITs) in our database. "
            f"You have **{safe_count} Safe**, **{likely_count} Likely**, and **{asp_count} Aspirational** options. "
            "NITs accept JEE Main scores via JoSAA counselling. Review the table below."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"NIT Admission Possibilities — Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── IIT Admission ────────────────────────────────────────────────────────
    elif intent == "IIT_ADMISSION":
        # Validate: IITs need JEE Advanced. Warn if user only has JEE Main.
        if exam and "advanced" not in exam.lower() and "jee" in exam.lower():
            return (
                "IITs admit students through **JEE Advanced** scores via JoSAA counselling. "
                "You have mentioned **JEE Main** — a JEE Main rank makes you eligible for **NITs, IIITs, and GFTIs**, "
                "but NOT for IITs. To get into an IIT, you must first qualify JEE Advanced by scoring in the top ~2.5 lakh in JEE Main, "
                "then appear for JEE Advanced and secure a rank there. "
                "Would you like to see NIT/IIIT options for your JEE Main rank instead?",
                None
            )
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             college_type="IIT", entrance_exam=exam or "JEE Advanced")
        if not rows:
            return (
                f"No IIT programmes found for rank #{rank:,} ({category}) in our database. "
                "IITs admit students through JEE Advanced. If you appeared for JEE Main only, "
                "you need to first qualify JEE Advanced to be eligible for IIT counselling. "
                "Consider NIT/IIIT options for JEE Main rank.",
                None
            )
        columns = ["College", "Branch", "Candidate Rank", "Historical Cutoff",
                   "Rank Difference", "Likelihood Range", "Tier", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Candidate Rank": r["candidate_rank"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"], "Median CTC": r["median_ctc"]
        } for r in rows]

        safe_count   = sum(1 for r in rows if r["tier"] == "Safe")
        likely_count = sum(1 for r in rows if r["tier"] == "Likely")
        asp_count    = sum(1 for r in rows if r["tier"] == "Aspirational")

        explanation = (
            f"IIT evaluation for JEE Advanced rank **#{rank:,}** ({category}). "
            f"You have **{safe_count} Safe**, **{likely_count} Likely**, and **{asp_count} Aspirational** IIT options. "
            "IITs are admitted through JoSAA counselling using JEE Advanced scores."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"IIT Admission Possibilities — Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── IIIT Admission ───────────────────────────────────────────────────────
    elif intent == "IIIT_ADMISSION":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             college_type="IIIT", entrance_exam=exam or "JEE Main")
        if not rows:
            return (
                f"No IIIT programmes found for rank #{rank:,} ({category}) in our database. "
                "IIITs specialise in IT and Computing. Top IIITs (like IIIT Hyderabad) have very competitive cutoffs.",
                None
            )
        columns = ["College", "Branch", "Candidate Rank", "Historical Cutoff",
                   "Rank Difference", "Likelihood Range", "Tier", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Candidate Rank": r["candidate_rank"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"], "Median CTC": r["median_ctc"]
        } for r in rows]

        explanation = (
            f"IIIT evaluation for rank **#{rank:,}** ({category}). "
            "IIITs focus on IT/Computer Science and are excellent for software and AI careers. "
            "They are admitted via JoSAA (JEE Main) counselling."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"IIIT Admission Possibilities — Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── GFTI Admission ───────────────────────────────────────────────────────
    elif intent == "GFTI_ADMISSION":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             college_type="GFTI", entrance_exam=exam or "JEE Main")
        if not rows:
            return (
                "No GFTI programmes found in our current database. "
                "Government Funded Technical Institutes (GFTIs) are admitted via JoSAA using JEE Main scores.",
                None
            )
        columns = ["College", "Branch", "Historical Cutoff", "Rank Difference",
                   "Likelihood Range", "Tier", "Location"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"], "Location": r["location"]
        } for r in rows]
        explanation = f"GFTI options for rank **#{rank:,}** ({category})."
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"GFTI Admission Options — Rank #{rank:,}",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── College comparison ───────────────────────────────────────────────────
    elif intent == "COLLEGE_COMPARE":
        rows = get_placement_comparison(programs)
        # Also attach admission info
        all_eval = filter_and_evaluate_admission(rank, category, programs)
        eval_map = {r["college"] + "|" + r["branch"]: r for r in all_eval}

        columns = ["College", "Branch", "Type", "Tier", "Likelihood Range",
                   "Median CTC", "Placement Rate", "Top Recruiters"]
        table_rows = []
        for r in rows[:8]:
            key = r["college"] + "|" + r["branch"]
            ev  = eval_map.get(key, {})
            table_rows.append({
                "College": r["college"],
                "Branch": r["branch"],
                "Type": r.get("type", ""),
                "Tier": ev.get("tier", "—"),
                "Likelihood Range": ev.get("likelihood_range", "—"),
                "Median CTC": r["median_ctc"],
                "Placement Rate": r["placement_rate"],
                "Top Recruiters": r["top_recruiters"],
            })

        explanation = (
            f"Here is a comparison of colleges for rank **#{rank:,}** ({category}), "
            "showing both your admission likelihood and placement outcomes. "
            "Use this to weigh brand/placement value against your actual probability of admission."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="College Comparison — Admission Chances + Placements",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── Branch queries ───────────────────────────────────────────────────────
    elif intent in ("BRANCH_CSE", "BRANCH_ECE", "BRANCH_MECH",
                    "BRANCH_CIVIL", "BRANCH_EE", "BRANCH_DS_AI"):

        branch_map = {
            "BRANCH_CSE":   ("CSE", "Computer Science & Engineering (CSE / IT)", 
                            "CSE focuses on software development, AI/ML, algorithms, and computing. "
                            "Top career paths: Software Engineer, Data Scientist, AI Researcher. "
                            "Highest placement branches across IITs/NITs."),
            "BRANCH_ECE":   ("ECE", "Electronics & Communication Engineering (ECE)",
                            "ECE covers electronics, telecommunications, embedded systems, and VLSI. "
                            "Career paths: Hardware Engineer, Embedded Systems, Telecom, Chip Design."),
            "BRANCH_MECH":  ("Mech", "Mechanical Engineering",
                            "Mechanical Engineering covers design, manufacturing, robotics, and automotive. "
                            "Career paths: Core Manufacturing, Automotive, Robotics, Product Design."),
            "BRANCH_CIVIL": ("Civil", "Civil Engineering",
                            "Civil Engineering focuses on infrastructure, construction, and urban planning. "
                            "Career paths: Construction, Infrastructure, Government Projects, Urban Planning."),
            "BRANCH_EE":    ("Electrical", "Electrical Engineering",
                            "Electrical Engineering covers power systems, control systems, and electrical design. "
                            "Career paths: Power Sector, Renewable Energy, Control Systems, Automation."),
            "BRANCH_DS_AI": ("Data Science", "Data Science / Artificial Intelligence",
                            "Data Science & AI focuses on machine learning, analytics, and AI systems. "
                            "Career paths: Data Scientist, ML Engineer, AI Researcher, Analytics."),
        }
        bk, branch_label, branch_description = branch_map[intent]
        
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             branch_keyword=bk, entrance_exam=exam)
        if not rows:
            return (
                f"**{branch_label}**\n\n{branch_description}\n\n"
                f"Unfortunately, no {branch_label} programmes found for rank #{rank:,} ({category}) in our database. "
                "Try broadening your search or checking alternate branches.",
                None
            )

        columns = ["College", "Branch", "Historical Cutoff", "Rank Difference",
                   "Likelihood Range", "Tier", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"], "Median CTC": r["median_ctc"]
        } for r in rows]

        explanation = (
            f"**{branch_label}**\n\n{branch_description}\n\n"
            f"Based on your rank of **#{rank:,}** ({category}), here are your {branch_label} admission options:"
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"{branch_label} Options for Rank #{rank:,}",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── Cutoff inquiry ───────────────────────────────────────────────────────
    elif intent == "CUTOFF_INQUIRY":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             entrance_exam=exam)[:12]
        columns = ["College", "Branch", "Category", "Historical Cutoff (Closing)",
                   "Cutoff Year/Round", "Rank Difference", "Tier"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Category": r["category"],
            "Historical Cutoff (Closing)": r["historical_cutoff"],
            "Cutoff Year/Round": r["cutoff_year_round"],
            "Rank Difference": r["rank_difference"],
            "Tier": r["tier"]
        } for r in rows]
        explanation = (
            f"Historical closing cutoffs for rank **#{rank:,}** ({category}). "
            "All cutoffs are from 2024 Round 6 (final closing). "
            "Positive rank difference means you are ranked better than the cutoff — the larger the positive value, the safer the seat. "
            "Note: Cutoffs shift ±5-10% annually."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Historical Cutoffs vs Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── State quota ──────────────────────────────────────────────────────────
    elif intent == "STATE_QUOTA":
        explanation = (
            "**State Quota & Home State Seats:** \n\n"
            "• **NITs** — 50% of seats are Home State Quota (HS). These have significantly easier cutoffs than the Other State (OS) quota. "
            "If you are applying to your home state's NIT, your HS quota cutoffs can be 20-40% more relaxed than OS.\n\n"
            "• **IITs & IIITs** — No state quota; all seats are filled on All-India merit via JoSAA.\n\n"
            "• **State Government Colleges** — Conducted through state counselling (e.g. TS EAMCET, MHT-CET, KCET). "
            "These use separate rank lists and are NOT part of JoSAA.\n\n"
            "To get precise HS vs OS cutoffs for a specific NIT, please share the NIT name and I will look it up."
        )
        return explanation, None

    # ── Colleges available ───────────────────────────────────────────────────
    elif intent == "COLLEGES_AVAILABLE":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             entrance_exam=exam)
        relevant = [r for r in rows if r["tier"] in ("Safe", "Likely", "Aspirational")][:10]
        columns = ["College", "Branch", "Type", "Historical Cutoff",
                   "Rank Difference", "Likelihood Range", "Tier"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Type": r["type"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Tier": r["tier"]
        } for r in relevant]
        explanation = (
            f"For rank **#{rank:,}** ({category}), here are institutions where you have a realistic admission chance "
            "across Safe, Likely, and Aspirational tiers."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Colleges Available for Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── Tier-specific ────────────────────────────────────────────────────────
    elif intent == "SAFEST_OPTIONS":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             tier_filter="Safe", entrance_exam=exam)
        columns = ["College", "Branch", "Historical Cutoff", "Rank Difference",
                   "Likelihood Range", "Median CTC", "Location"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Median CTC": r["median_ctc"], "Location": r["location"]
        } for r in rows]
        explanation = (
            f"Your **Safe options** for rank **#{rank:,}** — these have a >12% positive margin over 2024 closing cutoffs, "
            "giving you a high probability of securing a seat."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Safest Options for Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    elif intent == "LIKELY_OPTIONS":
        rows = filter_and_evaluate_admission(rank, category, programs,
                                             tier_filter="Likely", entrance_exam=exam)
        columns = ["College", "Branch", "Historical Cutoff", "Rank Difference",
                   "Likelihood Range", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Median CTC": r["median_ctc"]
        } for r in rows]
        explanation = (
            f"Your **Likely options** (50-75% probability) for rank **#{rank:,}** ({category}). "
            "These are competitive targets within realistic striking range."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Likely Options for Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    elif intent == "ASPIRATIONAL_OPTIONS":
        rows = filter_and_evaluate_admission(rank, category, programs, tier_filter="Aspirational")
        columns = ["College", "Branch", "Historical Cutoff", "Rank Difference",
                   "Likelihood Range", "Median CTC"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Historical Cutoff": r["historical_cutoff"],
            "Rank Difference": r["rank_difference"],
            "Likelihood Range": r["likelihood_range"],
            "Median CTC": r["median_ctc"]
        } for r in rows]
        explanation = (
            f"Your **Aspirational reach options** (20-40% probability) for rank **#{rank:,}** ({category}). "
            "Worth including — late rounds and sliding can sometimes make these possible."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Aspirational Options for Rank #{rank:,} ({category})",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── AI Curriculum ────────────────────────────────────────────────────────
    elif intent == "AI_CURRICULUM":
        matches = find_programmes_matching_interests(student, programs,
                                                     focus_keyword="Artificial Intelligence")
        top_matches = matches[:6]
        columns = ["College", "Branch", "AI/ML Relevance", "Curriculum Focus",
                   "Curriculum Fit Score", "Median CTC"]
        table_rows = [{
            "College": m["college"], "Branch": m["branch"],
            "AI/ML Relevance": m["ai_ml_relevance"],
            "Curriculum Focus": m["curriculum_focus"],
            "Curriculum Fit Score": m["curriculum_fit_score"],
            "Median CTC": m["median_ctc"]
        } for m in top_matches]
        mismatch_note = next(
            (m["mismatch_warning"] for m in top_matches if m.get("mismatch_warning")), None
        )
        explanation = (
            "Programmes ranked by AI/ML curriculum strength. Specialised AI degrees (IIIT Hyderabad, PES University) "
            "and IITs with strong research labs top this list."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Top Programmes for Artificial Intelligence & Machine Learning",
            columns=columns, rows=table_rows,
            disclaimer=DISCLAIMER_TEXT, mismatch_warning=mismatch_note
        )

    # ── Placements ───────────────────────────────────────────────────────────
    elif intent == "PLACEMENTS_COMPARE":
        rows = get_placement_comparison(programs)[:8]
        columns = ["College", "Branch", "Median CTC", "Placement Rate",
                   "Top Recruiters", "Key Domains"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Median CTC": r["median_ctc"],
            "Placement Rate": r["placement_rate"],
            "Top Recruiters": r["top_recruiters"],
            "Key Domains": r["career_domains"]
        } for r in rows]
        explanation = (
            "Placement comparison sorted by median CTC, using verified data from our database. "
            "IIT Bombay CSE, IIIT Hyderabad CSE, and IIT Delhi M&C lead in compensation."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Placement Comparison — Median CTC & Placement Rates",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    elif intent == "JOB_ROLES":
        rows = get_job_roles_information(programs)[:7]
        columns = ["College", "Branch", "Typical Roles", "Median CTC", "Key Recruiters"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Typical Roles": r["typical_roles"],
            "Median CTC": r["median_ctc"],
            "Key Recruiters": r["key_recruiters"]
        } for r in rows]
        explanation = (
            "Graduate job profiles across programmes, spanning Software Engineering, "
            "AI/ML Research, Quantitative Finance, and Core Hardware."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Graduate Roles & Career Profiles",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── Fees / Scholarships / Hostel / Location ──────────────────────────────
    elif intent == "FEES_INQUIRY":
        rows = get_fees_information(programs)[:8]
        columns = ["College", "Branch", "Type", "Annual Tuition Fee",
                   "Hostel Available", "Annual Hostel Fee", "Location"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"], "Type": r["type"],
            "Annual Tuition Fee": r["annual_tuition_fee"],
            "Hostel Available": r["hostel_available"],
            "Annual Hostel Fee": r["annual_hostel_fee"],
            "Location": r["location"]
        } for r in rows]
        explanation = (
            "Fee comparison across institutions. NITs, IITs and IIITs are government-funded "
            "with heavily subsidised tuition (₹1.5-2.5 L/yr). Private universities charge significantly more."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Annual Tuition & Hostel Fee Comparison",
            columns=columns, rows=table_rows,
            disclaimer="Fee figures are based on 2024 academic year data and exclude caution deposits."
        )

    elif intent == "SCHOLARSHIPS":
        rows = get_scholarships_information(programs)[:7]
        columns = ["College", "Branch", "Type",
                   "Scholarship & Fee Remission Schemes", "Annual Tuition"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"], "Type": r["type"],
            "Scholarship & Fee Remission Schemes": r["scholarships"],
            "Annual Tuition": r["annual_tuition_fee"]
        } for r in rows]
        explanation = (
            "Scholarship schemes. All central NITs and IITs provide 100% tuition remission "
            "for SC/ST students and family income < ₹1 Lakh, and 66% remission for ₹1–5 Lakhs income."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Scholarship Schemes & Fee Remissions",
            columns=columns, rows=table_rows,
            disclaimer="Verify eligibility with the institute's financial aid office during document verification."
        )

    elif intent == "HOSTEL_INQUIRY":
        rows = get_hostel_information(programs)[:8]
        columns = ["College", "Location", "Hostel Available", "Annual Hostel & Mess Fee"]
        table_rows = [{
            "College": r["college"], "Location": r["location"],
            "Hostel Available": r["hostel_available"],
            "Annual Hostel & Mess Fee": r["hostel_fee"]
        } for r in rows]
        explanation = (
            "Hostel availability and accommodation costs. All IITs, NITs, and IIITs "
            "provide mandatory on-campus housing with mess facilities."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Hostel & Accommodation Details",
            columns=columns, rows=table_rows,
            disclaimer="Hostel allotment is confirmed on payment of semester seat acceptance fee."
        )

    elif intent == "LOCATION_INQUIRY":
        rows = get_location_information(programs)[:8]
        columns = ["College", "Type", "Location"]
        table_rows = [{
            "College": r["college"], "Type": r["type"], "Location": r["location"]
        } for r in rows]
        explanation = (
            "Campus locations. Proximity to tech hubs (Bengaluru, Delhi-NCR, Hyderabad, Mumbai) "
            "is advantageous for internships and local industry networking."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="College Campus Locations",
            columns=columns, rows=table_rows,
            disclaimer="Consider travel connectivity when ordering choices."
        )

    # ── Why first rank ───────────────────────────────────────────────────────
    elif intent == "WHY_FIRST_RANK":
        rec_res = generate_recommendations(student)
        top_pref = rec_res.preferences[0] if rec_res.preferences else None
        if not top_pref:
            return "No recommendation list has been generated yet. Please share your rank first.", None

        explanation = (
            f"**{top_pref.program.college_name} — {top_pref.program.branch_name}** is ranked #1 "
            f"because it maximises your composite score ({top_pref.composite_score}/100).\n\n"
            f"1. **Feasibility ({top_pref.tier.value})**: Rank #{rank:,} gives a "
            f"{top_pref.likelihood_range} admission likelihood.\n"
            f"2. **Curriculum Fit**: Matches your interests in "
            f"{', '.join(top_pref.interest_alignment_tags)}.\n"
            f"3. **Placements**: {top_pref.program.placement_stats.placement_percentage}% placement, "
            f"₹{top_pref.program.placement_stats.median_salary_lpa} LPA median, "
            f"recruiters: {', '.join(top_pref.program.placement_stats.top_recruiters[:3])}."
        )
        columns = ["Preference #", "College", "Branch", "Tier",
                   "Likelihood Range", "Strategy Score", "Median CTC"]
        table_rows = [{
            "Preference #": "#1",
            "College": top_pref.program.college_name,
            "Branch": top_pref.program.branch_name,
            "Tier": top_pref.tier.value,
            "Likelihood Range": top_pref.likelihood_range,
            "Strategy Score": f"{top_pref.composite_score} / 100",
            "Median CTC": f"₹{top_pref.program.placement_stats.median_salary_lpa} LPA"
        }]
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Reasoning for #1 Preference",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    # ── Higher studies & Entrepreneurship ────────────────────────────────────
    elif intent == "HIGHER_STUDIES":
        rows = get_higher_studies_information(programs)[:7]
        columns = ["College", "Branch", "Higher Study & Research Record", "Tier Rating"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Higher Study & Research Record": r["higher_studies"],
            "Tier Rating": r["tier"]
        } for r in rows]
        explanation = (
            "Graduate school and research track records. IIT Bombay, IIT Delhi, and IIIT Hyderabad "
            "lead in MS/PhD admits to top global universities (Stanford, MIT, CMU, ETH Zurich)."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Graduate Studies & Research Opportunities",
            columns=columns, rows=table_rows,
            disclaimer="Graduate outcomes depend on CGPA, research experience, and GRE/TOEFL scores."
        )

    elif intent == "ENTREPRENEURSHIP":
        rows = get_entrepreneurship_information(programs)[:7]
        columns = ["College", "Branch", "Campus Startup & Incubation Ecosystem"]
        table_rows = [{
            "College": r["college"], "Branch": r["branch"],
            "Campus Startup & Incubation Ecosystem": r["entrepreneurship_support"]
        } for r in rows]
        explanation = (
            "Entrepreneurship ecosystems. IIT Madras Research Park, SINE at IIT Bombay, "
            "and IIIT Hyderabad CIE lead in student startup creation and seed funding."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title="Campus Entrepreneurship & Incubation",
            columns=columns, rows=table_rows,
            disclaimer="Funding depends on annual faculty and investor committee decisions."
        )

    # ── Preference list ──────────────────────────────────────────────────────
    elif intent == "PREFERENCE_LIST":
        rec_res = generate_recommendations(student)
        columns = ["Preference #", "College", "Branch", "Tier",
                   "Likelihood Range", "Strategy Score", "Median CTC"]
        table_rows = [{
            "Preference #": f"#{idx}",
            "College": p.program.college_name,
            "Branch": p.program.branch_name,
            "Tier": p.tier.value,
            "Likelihood Range": p.likelihood_range,
            "Strategy Score": f"{p.composite_score} / 100",
            "Median CTC": f"₹{p.program.placement_stats.median_salary_lpa} LPA"
        } for idx, p in enumerate(rec_res.preferences, 1)]
        explanation = (
            f"Your balanced choice-filling sheet for rank **#{rank:,}** ({category}). "
            "Aspirational options come first, Likely in the middle, Safe at the base — "
            "exactly as recommended for JoSAA/CSAB strategy."
        )
        return explanation, StructuredQueryResult(
            query_type=intent,
            title=f"Strategic Preference Sheet — Rank #{rank:,}",
            columns=columns, rows=table_rows, disclaimer=DISCLAIMER_TEXT
        )

    return "", None
