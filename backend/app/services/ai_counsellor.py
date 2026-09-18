import re
import json
import requests
from typing import Dict, Any, List, Tuple, Optional
from app.config import settings
from app.models.student import StudentProfile, ChatMessage, ChatResponse, StructuredQueryResult
from app.models.program import RecommendationItem, CollegeProgram
from app.services.ranker import load_college_programs
from app.services.query_service import process_counselling_query, classify_intent

def extract_profile_from_text(text: str, current: StudentProfile) -> Tuple[StudentProfile, List[str]]:
    """
    Robust rule-based extractor to parse and update student details from free-form text.
    Preserves all existing attributes unless explicitly updated.
    """
    updated = current.model_copy()
    lower_text = text.lower()

    # 1. Entrance exam extraction
    if "jee advanced" in lower_text or "jee adv" in lower_text:
        updated.entrance_exam = "JEE Advanced"
    elif "jee main" in lower_text or "jee mains" in lower_text:
        updated.entrance_exam = "JEE Main"
    elif "wbjee" in lower_text:
        updated.entrance_exam = "WBJEE"
    elif "kcet" in lower_text:
        updated.entrance_exam = "KCET"
    elif "met" in lower_text:
        updated.entrance_exam = "MET"
    elif "cet" in lower_text and not updated.entrance_exam:
        updated.entrance_exam = "State CET"

    # 2. Rank extraction
    rank_match = re.search(r'(?:rank\s*(?:is|:)?\s*|air\s*[:\s]?\s*)(\d{1,7})', lower_text)
    if not rank_match:
        rank_match = re.search(r'(\d{1,7})\s*(?:rank|air)', lower_text)
    if rank_match:
        try:
            updated.rank = int(rank_match.group(1))
        except ValueError:
            pass

    # 3. Category extraction
    if any(k in lower_text for k in ["obc-ncl", "obc ncl", "obc"]):
        updated.category = "OBC-NCL"
    elif "ews" in lower_text:
        updated.category = "EWS"
    elif re.search(r'\bsc\b', lower_text):
        updated.category = "SC"
    elif re.search(r'\bst\b', lower_text):
        updated.category = "ST"
    elif any(k in lower_text for k in ["general", "gen", "open"]):
        updated.category = "General"

    # 4. Academic strengths
    potential_strengths = ["math", "mathematics", "physics", "chemistry", "coding", "programming", "logic", "algorithms"]
    for s in potential_strengths:
        if s in lower_text:
            cleaned = "Mathematics" if s in ("math", "mathematics") else s.title()
            if cleaned not in updated.academic_strengths:
                updated.academic_strengths.append(cleaned)

    # 5. Interests
    interest_keywords = {
        "artificial intelligence": "Artificial Intelligence",
        "machine learning": "Machine Learning",
        "ai": "Artificial Intelligence",
        "ml": "Machine Learning",
        "data science": "Data Science",
        "robotics": "Robotics & Automation",
        "cybersecurity": "Cybersecurity",
        "cloud": "Cloud Computing",
        "web": "Web Development",
        "software": "Software Engineering",
        "electronics": "Core Electronics",
        "hardware": "Hardware / VLSI",
        "mechanical": "Mechanical Engineering"
    }
    for k, label in interest_keywords.items():
        if re.search(r'\b' + re.escape(k) + r'\b', lower_text):
            if label not in updated.interests:
                updated.interests.append(label)

    # 6. Career goals
    career_map = {
        "software engineer": "Software Engineering",
        "developer": "Software Engineering",
        "research": "Academic / Industrial Research",
        "quant": "Quantitative Finance",
        "finance": "Quantitative Finance",
        "product manager": "Product Management",
        "startup": "Entrepreneurship / Startups",
        "robotics engineer": "Robotics Engineering"
    }
    for k, goal in career_map.items():
        if k in lower_text:
            if goal not in updated.career_goals:
                updated.career_goals.append(goal)

    # 7. Higher study interest
    if any(k in lower_text for k in ["ms abroad", "masters", "phd", "higher studies", "higher study"]):
        updated.higher_study_interest = "Interested in MS/PhD graduate research"

    # 8. Entrepreneurship interest
    if any(k in lower_text for k in ["startup", "entrepreneurship", "incubator", "own company", "ventures"]):
        updated.entrepreneurship_interest = "Interested in tech startups & incubation"

    # 9. Placement priorities
    if any(k in lower_text for k in ["high package", "high ctc", "top placement", "good placement"]):
        if "High Placement CTC" not in updated.placement_priorities:
            updated.placement_priorities.append("High Placement CTC")

    # Missing fields for initial intake
    missing = []
    if updated.rank is None:
        missing.append("rank")
    if not updated.interests:
        missing.append("interests")
    if not updated.career_goals:
        missing.append("career_goals")
    if not updated.academic_strengths:
        missing.append("academic_strengths")

    return updated, missing

def call_gemini_api(prompt: str) -> str:
    """
    Calls Gemini REST API if GEMINI_API_KEY is configured.
    """
    if not settings.GEMINI_API_KEY:
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 700
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[AI Counsellor] Gemini API call error: {e}")
    return ""


def classify_question_with_gemini(message: str, student: StudentProfile) -> str:
    """
    Uses Gemini to intelligently classify whether a question is admission-related
    or a general question. Returns 'ADMISSION' or 'GENERAL'.
    """
    if not settings.GEMINI_API_KEY:
        # Fallback to keyword-based classification if no API key
        msg_lower = message.lower()
        admission_keywords = [
            "rank", "cutoff", "college", "nit", "iit", "iiit", "eapcet", "jee",
            "admission", "eligibility", "can i get", "placement", "fee", "hostel",
            "branch", "safe", "likely", "aspirational"
        ]
        if any(kw in msg_lower for kw in admission_keywords):
            return "ADMISSION"
        return "GENERAL"

    prompt = f"""You are an intelligent router for an AI admission counseling system for engineering colleges.

User Question: "{message}"

Student Context: Rank={student.rank}, Exam={student.entrance_exam}, Category={student.category}

Classify this question as:

**ADMISSION** - Questions about:
- College admissions, eligibility, "can I get X college?"
- Specific college rankings, cutoffs, comparisons
- Placement statistics, fees, hostels at specific colleges
- Branch/program questions: "What is CSE/ECE/Mechanical?" (students want admission context)
- JEE/EAPCET exam counseling and seat allocation
- Career prospects of branches in the context of college admission
- Curriculum, placements, or opportunities for specific branches
- Any engineering branch or field (CSE, ECE, AI, Mechanical, etc.)

**GENERAL** - Questions about:
- Pure programming concepts: "Explain recursion/OOP/algorithms"
- Non-engineering topics: "Who invented Python?" "Tell me a joke"
- General technology NOT related to college admission: "What is blockchain?"
- Topics unrelated to admission counseling

CRITICAL RULES:
- "What is CSE?" = ADMISSION (student wants to know about CSE for admission)
- "What is ECE?" = ADMISSION (student wants to know about ECE for admission)
- "Explain recursion" = GENERAL (pure programming concept)
- "What is JEE Main?" = ADMISSION (exam for college admission)
- "Who invented Python?" = GENERAL (not related to admission)
- "Tell me about AI" = ADMISSION (AI as a branch for college)
- "Explain binary search" = GENERAL (pure computer science concept)

Output ONLY: "ADMISSION" or "GENERAL"
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                result = candidates[0]["content"]["parts"][0]["text"].strip().upper()
                if "GENERAL" in result:
                    return "GENERAL"
                elif "ADMISSION" in result:
                    return "ADMISSION"
    except Exception as e:
        print(f"[AI Counsellor] Gemini classification error: {e}")
    
    # Default fallback logic if Gemini fails
    msg_lower = message.lower()
    
    # Engineering branches should be ADMISSION (students want admission context)
    branch_keywords = ["cse", "ece", "mechanical", "civil", "eee", "electrical", 
                      "chemical", "aerospace", "biotechnology", "ai", "ml", 
                      "data science", "computer science", "electronics"]
    
    # Pure conceptual programming topics are GENERAL
    pure_concepts = ["recursion", "algorithm", "binary search", "sorting", 
                    "data structure", "time complexity", "oop concepts"]
    
    # Check if asking about branches
    if any(f"what is {branch}" in msg_lower or f"tell me about {branch}" in msg_lower 
           for branch in branch_keywords):
        return "ADMISSION"
    
    # Check if pure programming concepts
    if any(concept in msg_lower for concept in pure_concepts):
        return "GENERAL"
    
    # Generic "what is" questions in admission context default to ADMISSION
    if "what is" in msg_lower or "tell me about" in msg_lower:
        return "ADMISSION"
    
    return "ADMISSION"


def answer_general_question_with_gemini(
    message: str,
    history: List[ChatMessage],
    student: StudentProfile
) -> str:
    """
    Uses Gemini to answer general non-admission questions naturally.
    Maintains conversation context and personality.
    """
    if not settings.GEMINI_API_KEY:
        return "I need Gemini API access to answer general questions. For admission-related queries, I can help with verified college data."

    # Build conversation history
    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg.role == "user" else "Counsellor"
        history_text += f"{role}: {msg.content}\n"

    prompt = f"""You are a helpful, friendly AI assistant with expertise in education and technology.

CONVERSATION HISTORY:
{history_text}
Student (latest): {message}

Context: You're primarily an admission counselor, but the student asked a general question.

Instructions:
1. Answer the question naturally and helpfully
2. Keep responses concise (2-4 sentences for simple questions, more for complex ones)
3. Be friendly and conversational
4. After answering, you can gently remind them you're available for admission counseling if relevant
5. Maintain conversation context from history

Answer the student's question:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[AI Counsellor] Gemini general answer error: {e}")
    
    return "I apologize, but I'm having trouble processing that question right now. Feel free to ask admission-related questions, and I'll use verified college data to help you."


def call_gemini_with_history(
    message: str,
    history: List[ChatMessage],
    student: StudentProfile,
    factual_context: str,
    table_sample: str
) -> str:
    """
    Calls Gemini with full conversation history so follow-up questions
    are answered in context. Grounded strictly in factual_context.
    """
    if not settings.GEMINI_API_KEY:
        return ""

    # Build a compact history string (last 6 turns to stay within token limits)
    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg.role == "user" else "Counsellor"
        history_text += f"{role}: {msg.content}\n"

    prompt = (
        "You are an expert, empathetic AI Admission Counsellor for Indian engineering admissions.\n\n"
        "CONVERSATION SO FAR:\n"
        f"{history_text}\n"
        f"Student (latest): {message}\n\n"
        f"Student Profile: Rank={student.rank}, Category={student.category}, "
        f"Interests={student.interests}, Goals={student.career_goals}\n\n"
        f"FACTUAL DATA FROM DATABASE:\n{factual_context}\n"
        f"SAMPLE ROWS: {table_sample}\n\n"
        "STRICT RULES:\n"
        "1. Answer the student's LATEST question using the factual data above.\n"
        "2. Use conversation history ONLY to understand context (e.g. which college they referred to).\n"
        "3. NEVER invent cutoffs, fees, placement figures or hostel facts not in the data.\n"
        "4. If data is unavailable for something, clearly say so.\n"
        "5. Keep the reply concise (3-5 sentences). Mention the table below for details.\n"
        "6. Always include the standard disclaimer: historical cutoffs fluctuate and are not a guarantee.\n"
        "7. For JEE Main → NITs/IIITs/GFTIs. For JEE Advanced → IITs."
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview"
        f":generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.15, "maxOutputTokens": 700}
    }
    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[AI Counsellor] Gemini history call error: {e}")
    return ""


def handle_general_with_gemini(
    message: str,
    history: List[ChatMessage],
    student: StudentProfile,
    programs: List
) -> str:
    """
    Uses Gemini to answer general admission questions not covered by
    structured intents, grounded in the available college data summary.
    """
    if not settings.GEMINI_API_KEY:
        return ""

    # Build a brief data summary so Gemini has factual grounding
    data_summary = "Available colleges in database:\n"
    for p in programs[:12]:
        cutoff_gen = p.category_cutoffs.get("General", p.category_cutoffs.get(
            list(p.category_cutoffs.keys())[0]
        ))
        data_summary += (
            f"- {p.college_name} | {p.branch_name} | {p.college_type} | "
            f"Closing rank (General): {cutoff_gen.closing_rank} | "
            f"Median CTC: ₹{p.placement_stats.median_salary_lpa} LPA\n"
        )

    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg.role == "user" else "Counsellor"
        history_text += f"{role}: {msg.content}\n"

    prompt = (
        "You are a knowledgeable AI Admission Counsellor for Indian engineering admissions (JEE Main / JEE Advanced).\n\n"
        "CONVERSATION:\n"
        f"{history_text}"
        f"Student (latest): {message}\n\n"
        f"Student Profile: Rank={student.rank}, Category={student.category}, "
        f"Interests={student.interests}, Goals={student.career_goals}\n\n"
        f"COLLEGE DATA AVAILABLE:\n{data_summary}\n\n"
        "RULES:\n"
        "1. Answer the student's question accurately.\n"
        "2. Only use facts from the data above. Do NOT invent cutoffs or statistics.\n"
        "3. For anything not in the data, say: 'Verified data for this is not in our current database. "
        "Please check the official JoSAA/CSAB portal.'\n"
        "4. JEE Main → NITs, IIITs, GFTIs via JoSAA. JEE Advanced → IITs via JoSAA.\n"
        "5. Keep reply to 3-5 sentences. Be helpful and honest.\n"
        "6. Always add: 'These are historical estimates; actual cutoffs vary each year.'"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash"
        f":generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600}
    }
    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[AI Counsellor] General Gemini call error: {e}")
    return ""

def generate_chat_reply(
    message: str,
    history: List[ChatMessage],
    current_profile: StudentProfile
) -> ChatResponse:
    """
    Central admission counsellor dialogue handler with intelligent Gemini-based routing.
    
    Flow:
    1. Extract student profile from conversation
    2. Classify question: ADMISSION or GENERAL (using Gemini)
    3. ADMISSION → Use existing recommendation engine with verified data
    4. GENERAL → Let Gemini answer naturally
    5. Maintain conversation context for follow-ups
    """
    # Extract profile from the entire recent history as well as the current message
    # so follow-up questions inherit context from previous turns
    updated_profile = current_profile
    for msg in history[-4:]:
        if msg.role == "user":
            updated_profile, _ = extract_profile_from_text(msg.content, updated_profile)
    updated_profile, missing_fields = extract_profile_from_text(message, updated_profile)

    is_complete = (updated_profile.rank is not None and len(updated_profile.interests) > 0)
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: Intelligent Question Classification using Gemini
    # ═══════════════════════════════════════════════════════════════════════
    question_type = classify_question_with_gemini(message, updated_profile)
    
    print(f"[AI Counsellor] Question classified as: {question_type}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: Route to GENERAL answer (non-admission questions)
    # ═══════════════════════════════════════════════════════════════════════
    if question_type == "GENERAL":
        ai_reply = answer_general_question_with_gemini(message, history, updated_profile)
        return ChatResponse(
            reply=ai_reply,
            extracted_profile=updated_profile,
            is_profile_complete=is_complete,
            missing_fields=missing_fields,
            intent="GENERAL_CONVERSATION"
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: ADMISSION questions → Use existing verified data engine
    # ═══════════════════════════════════════════════════════════════════════
    
    # Load programs (IIT/NIT/AP EAPCET)
    from app.services.ranker import load_college_programs, load_ap_eapcet_programs
    programs = load_college_programs() + load_ap_eapcet_programs()
    
    # Classify specific admission intent using existing system
    intent = classify_intent(message)
    
    # Process with existing admission engine (uses verified cutoff data)
    factual_explanation, structured_res = process_counselling_query(
        message=message,
        student=updated_profile,
        programs=programs
    )

    # Use Gemini to present the verified data naturally
    if settings.GEMINI_API_KEY and not settings.MOCK_MODE and factual_explanation:
        table_sample = json.dumps(structured_res.rows[:4]) if structured_res else "{}"
        ai_text = call_gemini_with_history(
            message=message,
            history=history,
            student=updated_profile,
            factual_context=factual_explanation or "No structured data returned.",
            table_sample=table_sample
        )
        if ai_text:
            return ChatResponse(
                reply=ai_text,
                extracted_profile=updated_profile,
                is_profile_complete=is_complete,
                missing_fields=missing_fields,
                intent=intent,
                structured_data=structured_res
            )

    # Fallback: return factual explanation directly
    if factual_explanation:
        return ChatResponse(
            reply=factual_explanation,
            extracted_profile=updated_profile,
            is_profile_complete=is_complete,
            missing_fields=missing_fields,
            intent=intent,
            structured_data=structured_res
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: Profile intake flow (if no specific question detected)
    # ═══════════════════════════════════════════════════════════════════════
    reply_lines = []
    if updated_profile.rank is None:
        reply_lines.append(
            "Hello! I am your AI Admission Counsellor. To evaluate realistic options, "
            "please share your **entrance exam rank** (JEE Main / JEE Advanced / AP EAPCET) "
            "and your **category** (General, OBC-NCL, SC, ST, EWS)."
        )
    elif not updated_profile.interests:
        reply_lines.append(
            f"Got it! Rank **#{updated_profile.rank:,}** ({updated_profile.category}). "
            "Which fields excite you most? (e.g. Artificial Intelligence, Software Engineering, "
            "Robotics, Core Electronics, Data Science)"
        )
    elif not updated_profile.career_goals:
        reply_lines.append(
            f"Great! With interests in **{', '.join(updated_profile.interests)}**, "
            "what are your career goals? "
            "(e.g. Software Engineer at product firms, Research/MS abroad, Core Engineering)"
        )
    else:
        reply_lines.append(
            f"Profile set: Rank **#{updated_profile.rank:,}** ({updated_profile.category}), "
            f"interests in **{', '.join(updated_profile.interests)}**, "
            f"goals in **{', '.join(updated_profile.career_goals)}**. "
            "Your preference sheet is ready! Ask me: "
            "'*Can I get an NIT?*', '*Which IIT can I get?*', '*Best college for AI?*', "
            "'*Compare placements*', '*What are the fees?*', or '*Show my safe options*'. "
            "\n\nI can also answer general questions about engineering, technology, or anything else!"
        )

    return ChatResponse(
        reply=" ".join(reply_lines),
        extracted_profile=updated_profile,
        is_profile_complete=is_complete,
        missing_fields=missing_fields,
        intent="INTAKE"
    )

def enrich_explanations_with_ai(
    recommendations: List[RecommendationItem],
    student: StudentProfile
) -> List[RecommendationItem]:
    """
    Enriches recommendations with personalized rationales based on deterministic scores.
    """
    for item in recommendations[:5]:
        prog = item.program
        
        tier_phrasing = {
            "Safe": "provides a comfortable safety cushion against past closing cutoffs",
            "Likely": "sits right in your competitive sweet spot based on recent cutoffs",
            "Aspirational": "represents an ambitious reach where late round movement could work in your favor",
            "Reach": "is an ambitious moonshot choice"
        }
        
        curriculum_text = (
            f"Its curriculum covers {', '.join(item.interest_alignment_tags[:2])}, aligning directly with your goals."
            if item.interest_alignment_tags else "The program offers robust foundational engineering training."
        )

        item.ai_explanation = (
            f"{prog.college_name} ({prog.branch_name}) {tier_phrasing.get(item.tier.value, 'is recommended')}. "
            f"{curriculum_text} Graduates average ₹{prog.placement_stats.median_salary_lpa} LPA with top recruiters including "
            f"{', '.join(prog.placement_stats.top_recruiters[:3])}. *Historical cutoffs fluctuate annually; not a guarantee.*"
        )

    return recommendations
