from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import hashlib
import json
import os

app = FastAPI(title="CapstoneAI API", description="Backend for CapstoneAI")

# Dynamic CORS: allow localhost for dev + production frontend URL
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL from env if set
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Idea Database (keyed by domain + skill combos) ────────────────────────

IDEA_POOL = {
    "Healthcare": [
        {"title": "AI-Powered Symptom Triage System", "tagline": "An intelligent chatbot that pre-screens patient symptoms using NLP, prioritizes urgency levels, and routes patients to the right specialist — reducing ER wait times by up to 40%.", "domain": "Healthcare AI"},
        {"title": "MedScan — Prescription Digitizer", "tagline": "Uses OCR and computer vision to digitize handwritten prescriptions, cross-references drug interactions, and sends structured data to pharmacies.", "domain": "Healthcare"},
        {"title": "Mental Health Journal with Sentiment Tracking", "tagline": "A private journaling app that uses NLP sentiment analysis to track emotional patterns over time and gently suggests professional help when needed.", "domain": "Mental Health"},
        {"title": "Hospital Bed Occupancy Predictor", "tagline": "Uses historical admission data and ML time-series forecasting to predict bed availability 48 hours in advance, helping hospital admins plan resources.", "domain": "Healthcare Analytics"},
    ],
    "Education": [
        {"title": "CapstoneAI — AI Project Mentor", "tagline": "An AI platform that generates complete, university-ready project blueprints based on a student's skills and interests — including architecture diagrams and roadmaps.", "domain": "EdTech AI"},
        {"title": "Adaptive Quiz Engine", "tagline": "A testing platform that dynamically adjusts question difficulty in real-time based on student performance using Item Response Theory (IRT) algorithms.", "domain": "EdTech"},
        {"title": "Plagiarism-Proof Assignment System", "tagline": "Generates unique assignment variants per student using LLMs, making copy-paste plagiarism structurally impossible while testing the same learning outcomes.", "domain": "EdTech"},
        {"title": "Study Group Matchmaker", "tagline": "Analyzes student schedules, learning styles, and weak topics to automatically form optimal study groups using graph-based clustering algorithms.", "domain": "Education"},
    ],
    "Finance": [
        {"title": "Expense Anomaly Detector", "tagline": "Uses unsupervised ML (Isolation Forest) to detect unusual spending patterns in personal finance data and alerts users to potential fraud or budget overruns.", "domain": "FinTech AI"},
        {"title": "AI Tax Filing Assistant", "tagline": "Reads uploaded financial documents using OCR, auto-fills tax forms, and uses rule-based AI to suggest deductions the user might have missed.", "domain": "FinTech"},
        {"title": "Micro-Investment Robo-Advisor", "tagline": "Rounds up daily purchases and invests spare change into diversified portfolios selected by a risk-assessment ML model.", "domain": "FinTech"},
        {"title": "Invoice Fraud Detection System", "tagline": "Scans B2B invoices for duplicate entries, inflated amounts, and phantom vendors using pattern matching and anomaly detection.", "domain": "Finance AI"},
    ],
    "Agriculture": [
        {"title": "CropDoc — Plant Disease Identifier", "tagline": "Upload a photo of a diseased leaf and get an instant diagnosis using a CNN trained on the PlantVillage dataset, plus treatment recommendations.", "domain": "AgriTech AI"},
        {"title": "Smart Irrigation Scheduler", "tagline": "Uses soil moisture sensors + weather API data + ML prediction to automatically schedule optimal irrigation, reducing water waste by 30%.", "domain": "AgriTech IoT"},
        {"title": "Farmer's Market Price Predictor", "tagline": "Forecasts crop prices using LSTM networks trained on historical market data, helping farmers decide the best time to sell.", "domain": "AgriTech"},
        {"title": "Drone-Based Field Health Monitor", "tagline": "Processes aerial drone imagery using NDVI analysis and computer vision to map crop health across large fields.", "domain": "AgriTech AI"},
    ],
    "E-Commerce": [
        {"title": "Visual Search Shopping Engine", "tagline": "Upload a photo of any product and find visually similar items across multiple stores using a Siamese neural network for image embeddings.", "domain": "E-Commerce AI"},
        {"title": "Dynamic Pricing Optimizer", "tagline": "Uses reinforcement learning to automatically adjust product prices based on demand signals, competitor pricing, and inventory levels.", "domain": "E-Commerce"},
        {"title": "AI Review Summarizer", "tagline": "Condenses thousands of product reviews into a structured pros/cons summary using extractive and abstractive NLP summarization.", "domain": "E-Commerce AI"},
        {"title": "Return Probability Predictor", "tagline": "Predicts the likelihood of a product being returned before purchase using customer history and product attributes, helping reduce return rates.", "domain": "E-Commerce Analytics"},
    ],
    "Cybersecurity": [
        {"title": "Phishing URL Detector", "tagline": "A browser extension that uses an ML classifier trained on URL features (length, entropy, subdomain count) to warn users about phishing links in real-time.", "domain": "Cybersecurity AI"},
        {"title": "Network Intrusion Detection Dashboard", "tagline": "Monitors live network traffic and flags anomalies using autoencoders, displayed on a real-time dashboard with severity levels.", "domain": "Cybersecurity"},
        {"title": "Password Strength Analyzer with Breach Check", "tagline": "Evaluates password strength using entropy calculation and checks against the HaveIBeenPwned API — without sending the full password over the network (k-anonymity).", "domain": "Cybersecurity"},
        {"title": "Malware Classification System", "tagline": "Classifies malware families from PE file headers and API call sequences using Random Forest and XGBoost ensemble models.", "domain": "Cybersecurity AI"},
    ],
    "Social Media": [
        {"title": "Fake News Detector", "tagline": "A browser extension that scores news articles for credibility using NLP stance detection, source reputation analysis, and cross-referencing with fact-check databases.", "domain": "Social Media AI"},
        {"title": "Toxic Comment Filter", "tagline": "A real-time content moderation API that classifies comments as toxic, threatening, or obscene using fine-tuned BERT, with explainability on why each comment was flagged.", "domain": "Social Media"},
        {"title": "Social Media Detox Tracker", "tagline": "Tracks daily screen time per app, visualizes addiction patterns, and uses nudge theory to gently reduce usage through smart notifications.", "domain": "Digital Wellbeing"},
    ],
    "Climate & Environment": [
        {"title": "Carbon Footprint Calculator with AI Tips", "tagline": "Calculates personal carbon footprint from lifestyle inputs and uses an LLM to generate personalized, actionable reduction tips ranked by impact.", "domain": "Climate Tech"},
        {"title": "Wildfire Risk Predictor", "tagline": "Combines satellite imagery, weather data, and vegetation indices to predict wildfire risk zones using gradient boosting models.", "domain": "Climate AI"},
        {"title": "Smart Waste Sorter", "tagline": "A camera-based system that classifies waste items into recyclable categories using a MobileNet CNN, designed to run on edge devices like Raspberry Pi.", "domain": "Environment AI"},
    ],
    "Gaming": [
        {"title": "AI Dungeon Master", "tagline": "A text-based RPG where the storyline is dynamically generated by an LLM that adapts to player choices, maintaining narrative coherence using memory chains.", "domain": "Gaming AI"},
        {"title": "Player Behavior Analytics Dashboard", "tagline": "Tracks in-game player actions and uses clustering to identify player archetypes (explorer, achiever, socializer), helping game designers optimize engagement.", "domain": "Game Analytics"},
    ],
    "Transportation": [
        {"title": "Smart Parking Finder", "tagline": "Uses real-time camera feeds and YOLO object detection to identify vacant parking spots and guides drivers via a mobile app with turn-by-turn navigation.", "domain": "Smart City AI"},
        {"title": "Public Transit Delay Predictor", "tagline": "Predicts bus/train delays using historical and real-time data with gradient boosting, giving commuters accurate arrival estimates.", "domain": "Transportation AI"},
    ],
    "Food & Nutrition": [
        {"title": "NutriSnap — Food Calorie Estimator", "tagline": "Take a photo of your meal and get instant calorie and macronutrient estimates using a food recognition CNN trained on the Food-101 dataset.", "domain": "Health Tech AI"},
        {"title": "AI Recipe Generator from Fridge Contents", "tagline": "Upload a photo of your fridge or type available ingredients, and an LLM generates healthy recipes with nutritional breakdowns.", "domain": "Food Tech AI"},
    ],
    "Mental Health": [
        {"title": "AI Therapy Companion", "tagline": "A CBT-based conversational AI that guides users through structured cognitive behavioral therapy exercises, with mood tracking and progress visualization.", "domain": "Mental Health AI"},
        {"title": "Stress Detection from Typing Patterns", "tagline": "Analyzes keystroke dynamics (typing speed, error rate, pause patterns) to passively detect stress levels without any wearable devices.", "domain": "Mental Health AI"},
    ],
    "Music & Art": [
        {"title": "AI Music Mood Curator", "tagline": "Detects your mood from facial expressions or text input and generates a personalized playlist using Spotify API + emotion classification models.", "domain": "Music AI"},
        {"title": "Style Transfer Art Generator", "tagline": "Apply the artistic style of famous painters to your photos using neural style transfer, with real-time preview and high-res export.", "domain": "Creative AI"},
    ],
    "Legal Tech": [
        {"title": "Contract Risk Highlighter", "tagline": "Upload a legal contract and the AI highlights risky clauses, unfair terms, and missing protections using fine-tuned legal NLP models.", "domain": "Legal AI"},
        {"title": "Case Law Research Assistant", "tagline": "An RAG-powered search engine over legal case databases that finds relevant precedents and summarizes key rulings in plain language.", "domain": "Legal Tech AI"},
    ],
    "Real Estate": [
        {"title": "Property Price Predictor", "tagline": "Predicts real estate prices using location, amenities, and market trends with an ensemble of XGBoost and neural network models.", "domain": "PropTech AI"},
        {"title": "Virtual Home Staging with AI", "tagline": "Transforms photos of empty rooms into beautifully furnished spaces using generative AI, helping sellers market properties faster.", "domain": "Real Estate AI"},
    ],
    "Sports & Fitness": [
        {"title": "AI Personal Trainer", "tagline": "Uses pose estimation (MediaPipe) to analyze exercise form in real-time via webcam, counting reps and correcting posture with visual feedback.", "domain": "Fitness AI"},
        {"title": "Match Outcome Predictor", "tagline": "Predicts sports match outcomes using historical stats, player form, and venue data with gradient boosting — includes a confidence interval for each prediction.", "domain": "Sports Analytics"},
    ],
    "Accessibility": [
        {"title": "Sign Language to Text Translator", "tagline": "Real-time sign language recognition using MediaPipe hand tracking and an LSTM classifier, displayed as live captions on screen.", "domain": "Accessibility AI"},
        {"title": "Screen Reader for Handwritten Notes", "tagline": "Converts handwritten text in photos to digital text using OCR, then reads it aloud with text-to-speech — designed for visually impaired students.", "domain": "Accessibility"},
    ],
}

GENERIC_IDEAS = [
    {"title": "AI-Powered Portfolio Builder", "tagline": "Automatically generates a professional portfolio website from a GitHub profile and resume, using LLMs to write compelling project descriptions.", "domain": "Developer Tools"},
    {"title": "Smart Meeting Summarizer", "tagline": "Records meetings, transcribes them with Whisper, and generates structured summaries with action items using LLM extraction.", "domain": "Productivity AI"},
    {"title": "Code Review Bot", "tagline": "A GitHub bot that automatically reviews pull requests, flags potential bugs, suggests improvements, and checks for security vulnerabilities using LLMs.", "domain": "Developer Tools"},
    {"title": "AI Resume Screener", "tagline": "Ranks job applicants by parsing resumes with NLP, extracting skills, and scoring them against job requirements using semantic similarity.", "domain": "HR Tech AI"},
]


def get_ideas_for_profile(interests: List[str], skills: List[str], complexity: str) -> list:
    seed_str = json.dumps({"interests": sorted(interests), "skills": sorted(skills), "complexity": complexity})
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

    candidates = []
    for interest in interests:
        if interest in IDEA_POOL:
            candidates.extend(IDEA_POOL[interest])

    if not candidates:
        candidates = GENERIC_IDEAS.copy()

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

    if complexity == "Beginner" and len(candidates) > 3:
        beginner_friendly = [c for c in candidates if "AI" not in c["domain"]]
        others = [c for c in candidates if "AI" in c["domain"]]
        candidates = beginner_friendly + others

    return candidates[:3]


# ─── Models ─────────────────────────────────────────────────────────────────

class ProfileInput(BaseModel):
    name: str
    academic_field: str
    interests: List[str]
    skills: List[str]
    complexity: str
    time_available: int
    github_username: Optional[str] = None


class GitHubAnalyzeRequest(BaseModel):
    username: str


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to CapstoneAI API"}


@app.post("/api/generate-ideas")
def generate_ideas(profile: ProfileInput):
    ideas = get_ideas_for_profile(profile.interests, profile.skills, profile.complexity)
    for idea in ideas:
        relevant_skills = [s for s in profile.skills if s.lower() in idea["tagline"].lower() or s.lower() in idea["title"].lower()]
        idea["matching_skills"] = relevant_skills if relevant_skills else profile.skills[:2]
        idea["estimated_weeks"] = min(profile.time_available, max(8, profile.time_available - 2))
    return {"ideas": ideas, "profile_summary": {
        "name": profile.name, "field": profile.academic_field,
        "skill_count": len(profile.skills), "interest_count": len(profile.interests),
    }}


@app.post("/api/analyze-github")
def analyze_github(req: GitHubAnalyzeRequest):
    import urllib.request
    import json as json_module

    username = req.username.strip().replace("https://github.com/", "").replace("http://github.com/", "").strip("/")

    try:
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=30"
        request = urllib.request.Request(url, headers={"User-Agent": "CapstoneAI/1.0", "Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            repos = json_module.loads(response.read().decode())
    except Exception:
        raise HTTPException(status_code=404, detail=f"Could not fetch repos for '{username}'. Make sure the username is correct and has public repos.")

    if not repos or not isinstance(repos, list):
        raise HTTPException(status_code=404, detail=f"No public repos found for '{username}'.")

    language_count: dict[str, int] = {}
    total_stars = 0
    total_repos = len(repos)
    repo_summaries = []

    for repo in repos[:20]:
        lang = repo.get("language")
        if lang:
            language_count[lang] = language_count.get(lang, 0) + 1
        total_stars += repo.get("stargazers_count", 0)
        repo_summaries.append({
            "name": repo.get("name", ""), "description": repo.get("description", "") or "No description",
            "language": lang or "Unknown", "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0), "updated_at": repo.get("updated_at", ""),
            "url": repo.get("html_url", ""),
        })

    sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)
    top_languages = [lang for lang, count in sorted_languages[:6]]

    if total_repos >= 15 and total_stars >= 10:
        level = "Advanced"
        level_reason = f"{total_repos} repos with {total_stars} stars shows strong development experience."
    elif total_repos >= 5:
        level = "Intermediate"
        level_reason = f"{total_repos} repos shows solid foundational experience."
    else:
        level = "Beginner"
        level_reason = f"{total_repos} repos — just getting started. Great time to build something impressive!"

    return {
        "username": username, "total_repos": total_repos, "total_stars": total_stars,
        "top_languages": top_languages, "estimated_level": level,
        "level_reason": level_reason, "top_repos": repo_summaries[:6],
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
