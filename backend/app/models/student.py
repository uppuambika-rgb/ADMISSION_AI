from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StudentProfile(BaseModel):
    entrance_exam: Optional[str] = Field(default=None, description="Entrance exam (e.g. JEE Main, JEE Advanced, CET)")
    rank: Optional[int] = Field(default=None, description="All-India or Entrance Exam Rank")
    category: str = Field(default="General", description="Counselling category: General, OBC-NCL, SC, ST, EWS")
    home_state: Optional[str] = Field(default=None, description="State of domicile for quota consideration")
    academic_strengths: List[str] = Field(default_factory=list, description="Subjects or skills student excels at")
    interests: List[str] = Field(default_factory=list, description="Academic domains, technologies, or subjects of interest")
    career_goals: List[str] = Field(default_factory=list, description="Desired roles, industries, or future aspirations")
    placement_priorities: List[str] = Field(default_factory=list, description="Placement priorities e.g. High CTC, Tech roles, Product firms")
    higher_study_interest: Optional[str] = Field(default=None, description="Interest in MS / M.Tech / PhD research")
    entrepreneurship_interest: Optional[str] = Field(default=None, description="Interest in startups, incubation, ventures")
    preferred_locations: List[str] = Field(default_factory=list, description="Target states or cities")

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text")
    structured_data: Optional[Dict[str, Any]] = Field(default=None, description="Structured table/cards data for in-chat display")

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    current_profile: Optional[StudentProfile] = None

class StructuredQueryResult(BaseModel):
    query_type: str = Field(..., description="Normalized intent type e.g. ADMISSION_EVAL, FEES, PLACEMENT")
    title: str = Field(..., description="Display title for the table / comparison card")
    columns: List[str] = Field(default_factory=list, description="Column headers for tabular presentation")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="Rows of structured factual data")
    disclaimer: str = Field(default="", description="Advisory disclaimer regarding historical cutoffs & facts")
    mismatch_warning: Optional[str] = Field(default=None, description="Honest warning if program does not fit career goal")

class ChatResponse(BaseModel):
    reply: str
    extracted_profile: StudentProfile
    is_profile_complete: bool
    missing_fields: List[str] = Field(default_factory=list)
    intent: Optional[str] = Field(default=None, description="Recognized user intent")
    structured_data: Optional[StructuredQueryResult] = Field(default=None, description="Structured factual result for UI display")
