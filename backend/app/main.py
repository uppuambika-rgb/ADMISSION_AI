import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from app.config import settings
from app.models.student import StudentProfile, ChatRequest, ChatResponse
from app.models.program import CollegeProgram, RecommendationResponse
from app.services.ranker import load_college_programs, generate_recommendations
from app.services.ai_counsellor import generate_chat_reply, enrich_explanations_with_ai
from app.services.auth_service import register_user, login_user, get_user_from_token, logout_user

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Admission Counselling Agent with deterministic eligibility engine and conversational guidance."
)

frontend_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
configured_frontend_url = os.getenv("FRONTEND_URL", "")
frontend_origins.extend(
    origin.strip()
    for origin in configured_frontend_url.split(",")
    if origin.strip()
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Frontend dist — works both locally and on Render
# The dist folder sits at: <repo_root>/frontend/dist
# main.py is at:           <repo_root>/backend/app/main.py
# So we go: main.py → app/ → backend/ → repo_root/ → frontend/dist
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "gemini_configured": bool(settings.GEMINI_API_KEY)}


# ── Auth models ────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


# ── Auth endpoints ─────────────────────────────────────────────
@app.post("/api/auth/register")
def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required.")
    try:
        user = register_user(req.name, req.email, req.password)
        return {"message": "Account created successfully.", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        result = login_user(req.email, req.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
def me(authorization: Optional[str] = Header(default=None)):
    token = _extract_token(authorization)
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return user


@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    token = _extract_token(authorization)
    logout_user(token)
    return {"message": "Logged out successfully."}


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed.")
    return authorization.split(" ", 1)[1]


@app.get("/api/programs", response_model=List[CollegeProgram])
def get_programs():
    """Returns all college programs (IITs, NITs, and AP EAPCET colleges)."""
    from app.services.ranker import load_college_programs, load_ap_eapcet_programs
    
    # Load both datasets
    jee_programs = load_college_programs()  # IITs and NITs
    ap_programs = load_ap_eapcet_programs()  # AP EAPCET colleges
    
    # Combine and return
    return jee_programs + ap_programs

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Conversational admission counsellor endpoint.
    Extracts student profile attributes and returns guided dialogue.
    """
    profile = request.current_profile or StudentProfile()
    return generate_chat_reply(
        message=request.message,
        history=request.history,
        current_profile=profile
    )

@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend_endpoint(student: StudentProfile):
    """
    Generates deterministic recommendations, tiers (Safe/Likely/Aspirational),
    curriculum matches, and AI-enriched explanations.
    """
    if student.rank is None:
        raise HTTPException(status_code=400, detail="Student rank is required to generate recommendations.")

    # 1. Deterministic evaluation & preference ranking
    response = generate_recommendations(student)

    # 2. Enrich top recommendations with conversational explanations
    response.preferences = enrich_explanations_with_ai(response.preferences, student)

    return response

# ── Serve built frontend (production / Render deployment) ─────────────────
if DIST_DIR.exists():
    # Mount the assets folder so /assets/xxx.js and /assets/xxx.css are served
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    def serve_root():
        """Serve the React SPA index.html at the root."""
        return FileResponse(str(DIST_DIR / "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        """
        SPA fallback — serve index.html for all non-API routes
        so React Router can handle client-side navigation.
        """
        # If the path points to a real file in dist, serve it directly
        file_path = DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise fall back to index.html (React Router takes over)
        return FileResponse(str(DIST_DIR / "index.html"))

else:
    @app.get("/")
    def read_root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online — frontend not built yet",
            "docs_url": "/docs"
        }
