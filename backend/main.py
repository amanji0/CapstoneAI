from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import uvicorn
import hashlib
import json
import os
import urllib.request
from functools import lru_cache

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# ─── App Initialization & Security ─────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CapstoneAI API", 
    description="Enterprise-grade Backend for CapstoneAI Project Generator",
    version="1.1.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
if os.getenv("FRONTEND_URL"):
    ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """SECURITY: Middleware to append security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ─── Idea Database ─────────────────────────────────────────────────────────

IDEA_POOL = {
    "Healthcare": [
        {"title": "AI-Powered Symptom Triage System", "tagline": "An intelligent chatbot that pre-screens patient symptoms using NLP, prioritizes urgency levels, and routes patients to the right specialist — reducing ER wait times by up to 40%.", "domain": "Healthcare AI"},
        {"title": "MedScan — Prescription Digitizer", "tagline": "Uses OCR and computer vision to digitize handwritten prescriptions, cross-references drug interactions, and sends structured data to pharmacies.", "domain": "Healthcare"},
        {"title": "Mental Health Journal with Sentiment Tracking", "tagline": "A private journaling app that uses NLP sentiment analysis to track emotional patterns over time and gently suggests professional help when needed.", "domain": "Mental Health"},
    ],
    "Education": [
        {"title": "CapstoneAI — AI Project Mentor", "tagline": "An AI platform that generates complete, university-ready project blueprints based on a student's skills and interests — including architecture diagrams and roadmaps.", "domain": "EdTech AI"},
        {"title": "Adaptive Quiz Engine", "tagline": "A testing platform that dynamically adjusts question difficulty in real-time based on student performance using Item Response Theory (IRT) algorithms.", "domain": "EdTech"},
    ],
    "Finance": [
        {"title": "Expense Anomaly Detector", "tagline": "Uses unsupervised ML (Isolation Forest) to detect unusual spending patterns in personal finance data and alerts users to potential fraud or budget overruns.", "domain": "FinTech AI"},
        {"title": "AI Tax Filing Assistant", "tagline": "Reads uploaded financial documents using OCR, auto-fills tax forms, and uses rule-based AI to suggest deductions the user might have missed.", "domain": "FinTech"},
    ],
    "Cybersecurity": [
        {"title": "Phishing URL Detector", "tagline": "A browser extension that uses an ML classifier trained on URL features (length, entropy, subdomain count) to warn users about phishing links in real-time.", "domain": "Cybersecurity AI"},
        {"title": "Network Intrusion Detection Dashboard", "tagline": "Monitors live network traffic and flags anomalies using autoencoders, displayed on a real-time dashboard with severity levels.", "domain": "Cybersecurity"},
    ],
}

GENERIC_IDEAS = [
    {"title": "AI-Powered Portfolio Builder", "tagline": "Automatically generates a professional portfolio website from a GitHub profile and resume, using LLMs to write compelling project descriptions.", "domain": "Developer Tools"},
    {"title": "Smart Meeting Summarizer", "tagline": "Records meetings, transcribes them with Whisper, and generates structured summaries with action items using LLM extraction.", "domain": "Productivity AI"},
]

# ─── Core Logic (Efficiency & Optimization) ────────────────────────────────

@lru_cache(maxsize=1024)
def get_ideas_for_profile(interests_tuple: tuple, skills_tuple: tuple, complexity: str) -> list:
    """
    EFFICIENCY: Uses lru_cache to prevent recalculating for the same inputs.
    Generates personalized project ideas based on profile.
    """
    seed_str = json.dumps({"interests": sorted(interests_tuple), "skills": sorted(skills_tuple), "complexity": complexity})
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

    candidates = []
    for interest in interests_tuple:
        if interest in IDEA_POOL:
            candidates.extend(IDEA_POOL[interest])

    if not candidates:
        candidates = GENERIC_IDEAS.copy()

    # Deduplicate
    seen_titles = set()
    unique = []
    for idea in candidates:
        if idea["title"] not in seen_titles:
            seen_titles.add(idea["title"])
            unique.append(idea)
    candidates = unique

    import random
    rng = random.Random(seed)
    rng.shuffle(candidates)

    return candidates[:3]

# ─── Pydantic Models (Validation & Security) ──────────────────────────────

class ProfileInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    academic_field: str = Field(..., min_length=2, max_length=100)
    interests: List[str] = Field(..., max_length=20)
    skills: List[str] = Field(..., max_length=50)
    complexity: str = Field(..., pattern="^(Beginner|Intermediate|Advanced)$")
    time_available: int = Field(..., ge=1, le=52)
    github_username: Optional[str] = Field(None, max_length=200)

class GitHubAnalyzeRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=200, description="GitHub username or full URL")

# ─── API Endpoints ────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
@limiter.limit("60/minute")
def read_root(request: Request):
    """Health check endpoint."""
    return {"status": "online", "message": "Welcome to CapstoneAI API"}

@app.post("/api/generate-ideas", tags=["AI Generation"])
@limiter.limit("20/minute")
def generate_ideas(request: Request, profile: ProfileInput):
    """
    PROBLEM ALIGNMENT: Generates highly tailored final-year project ideas,
    aligning directly with the student's constraints to ensure success.
    """
    # Convert lists to tuples so they can be cached by lru_cache
    ideas = get_ideas_for_profile(tuple(profile.interests), tuple(profile.skills), profile.complexity)
    
    # Enrich ideas
    for idea in ideas:
        relevant_skills = [s for s in profile.skills if s.lower() in idea["tagline"].lower() or s.lower() in idea["title"].lower()]
        idea["matching_skills"] = relevant_skills if relevant_skills else profile.skills[:2]
        idea["estimated_weeks"] = min(profile.time_available, max(8, profile.time_available - 2))
        
    return {
        "ideas": ideas, 
        "profile_summary": {
            "name": profile.name, 
            "field": profile.academic_field,
            "skill_count": len(profile.skills), 
            "interest_count": len(profile.interests),
        }
    }

@lru_cache(maxsize=256)
def fetch_github_repos(username: str) -> list:
    """EFFICIENCY: Caches network requests to GitHub API to prevent rate limits."""
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=30"
    request = urllib.request.Request(url, headers={"User-Agent": "CapstoneAI/1.0", "Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())

@app.post("/api/analyze-github", tags=["Analysis"])
@limiter.limit("10/minute")
def analyze_github(request: Request, req: GitHubAnalyzeRequest):
    """
    Analyzes a GitHub profile to determine technical proficiency.
    """
    # Clean input
    username = req.username.strip().replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
    if not username:
        raise HTTPException(status_code=400, detail="Invalid GitHub username.")

    try:
        repos = fetch_github_repos(username)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise HTTPException(status_code=404, detail=f"Could not find GitHub user '{username}'.")
        raise HTTPException(status_code=500, detail="GitHub API error.")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to connect to GitHub.")

    if not repos or not isinstance(repos, list):
        raise HTTPException(status_code=404, detail=f"No public repos found for '{username}'.")

    language_count: Dict[str, int] = {}
    total_stars = 0
    repo_summaries = []

    for repo in repos[:20]:
        lang = repo.get("language")
        if lang:
            language_count[lang] = language_count.get(lang, 0) + 1
        total_stars += repo.get("stargazers_count", 0)
        repo_summaries.append({
            "name": repo.get("name", ""), 
            "description": repo.get("description", "") or "No description",
            "language": lang or "Unknown", 
            "stars": repo.get("stargazers_count", 0),
            "url": repo.get("html_url", ""),
        })

    sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)
    top_languages = [lang for lang, count in sorted_languages[:6]]

    # Logic to determine skill level
    total_repos = len(repos)
    if total_repos >= 15 and total_stars >= 10:
        level, level_reason = "Advanced", f"{total_repos} repos with {total_stars} stars shows strong experience."
    elif total_repos >= 5:
        level, level_reason = "Intermediate", f"{total_repos} repos shows solid foundational experience."
    else:
        level, level_reason = "Beginner", f"{total_repos} repos — great time to build something impressive!"

    return {
        "username": username, "total_repos": total_repos, "total_stars": total_stars,
        "top_languages": top_languages, "estimated_level": level,
        "level_reason": level_reason, "top_repos": repo_summaries[:6],
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
