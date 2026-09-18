# AI Admission Counselling Agent

An intelligent, ethical admission counselling assistant that pairs **deterministic admission calculation algorithms** with **generative AI conversation and explanation**.

Built for hackathons with simplicity, modularity, and beginner-friendliness in mind.

---

## Key Highlights

1. **Deterministic Eligibility & Likelihood Engine (Pure Python)**:
   - Evaluates entrance ranks against historical closing cutoffs across **General, OBC-NCL, SC, ST, and EWS** categories.
   - Computes realistic **admission likelihood ranges** (e.g. `80% - 95%`, `50% - 75%`, `20% - 40%`).
   - Categorizes programs into **Safe**, **Likely**, and **Aspirational** tiers without leaving mathematics to LLM hallucination.
2. **Curriculum & Career Outcome Matching**:
   - Matches student technical interests and strengths against college branch curriculum and placement metrics (median salary, top recruiters, and domains).
3. **Strategic Choice-Filling Preference Sheet**:
   - Generates a balanced choice sequence following real-world counselling best practices (Aspirational reach on top, high-probability Likely in the middle, and foolproof Safe safety cushions at the bottom).
4. **AI-Powered Rationale & Ethical Guardrails**:
   - Generates personalized explanations of *why* each program is recommended.
   - Explicitly communicates uncertainty (cutoffs fluctuate across rounds; historical trends do not guarantee admission or placement).
5. **Zero-Setup Mock Mode & Live Gemini Mode**:
   - Works immediately out of the box with built-in heuristic intelligence.
   - Simply drop in a Google Gemini API key in `.env` to enable live LLM chat!

---

## Folder Structure

```text
admission_counselling/
├── backend/
│   ├── app/
│   │   ├── config.py             # Settings & Gemini API key configuration
│   │   ├── main.py               # FastAPI application with CORS & routes
│   │   ├── models/
│   │   │   ├── student.py        # StudentProfile, ChatMessage schemas
│   │   │   └── program.py        # CollegeProgram, RecommendationItem schemas
│   │   ├── services/
│   │   │   ├── evaluator.py      # Deterministic cutoff math & likelihood ranges
│   │   │   ├── matcher.py        # Curriculum & placement matching logic
│   │   │   ├── ranker.py         # Balanced preference sheet builder
│   │   │   └── ai_counsellor.py  # AI conversational agent & explanation generator
│   │   └── data/
│   │       └── sample_colleges.json # Mock dataset (IITs, NITs, IIITs, DTU, etc.)
│   ├── tests/
│   │   └── test_counsellor.py    # Automated test suite
│   ├── requirements.txt          # Python dependencies
│   ├── run.py                    # Backend server runner
│   └── .env.example              # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main split-panel container
│   │   ├── index.css             # Design system styling
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx    # Conversational chat UI with live profile badges
│   │   │   ├── PreferenceList.jsx# Filterable preference sheet with tier tabs
│   │   │   ├── ProgramCard.jsx   # Program card with metrics, badges & AI rationale
│   │   │   └── DisclaimerBanner.jsx # Persistent uncertainty & advisory banner
│   │   └── services/
│   │       └── api.js            # REST API client
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
└── README.md
```

---

## Quick Start Guide

### Step 1: Run Backend (FastAPI)

1. Open a terminal in the project root:
   ```powershell
   cd backend
   ```
2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
3. Run the backend server:
   ```powershell
   python run.py
   ```
   The backend will be running at `http://https://admissionai-1.onrender.com`.
   Interactive API documentation is available at `http://https://admissionai-1.onrender.com/docs`.

### Step 2: Run Frontend (React + Vite)

1. Open a second terminal in the project root:
   ```powershell
   cd frontend
   ```
2. Install dependencies (using the included portable Node in `tools/node` or your system Node):
   ```powershell
   ..\tools\node\npm.cmd install
   ..\tools\node\npm.cmd run dev
   ```
   *(Or simply `npm install` and `npm run dev` if Node is in your PATH)*
3. Open your browser at `http://localhost:5173`.

---

## Testing & Verification

To run the automated backend test suite:
```powershell
.\backend\venv\Scripts\python.exe backend\tests\test_counsellor.py
```

---

## (Optional) Configuring Google Gemini API

To enable live generative conversation with Gemini:
1. Copy `backend/.env.example` to `backend/.env`:
   ```powershell
   copy backend\.env.example backend\.env
   ```
2. Add your Gemini API key in `backend/.env`:
   ```text
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
3. Restart the backend server.
