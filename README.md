# 🚀 CapstoneAI - AI-Powered Project Mentor

![CapstoneAI Logo](frontend/public/window.svg)

## 📌 Problem Statement
Every year, millions of computer science students face a critical roadblock: selecting a final-year Capstone project. The current approach is deeply flawed:
1. **Skill Mismatch:** Students choose projects that are either too trivial (failing to impress recruiters) or far too complex (leading to failure to graduate).
2. **Lack of Personalization:** Generic Google searches yield the same 10 overused ideas (e.g., "Library Management System").
3. **No Objective Baseline:** Students often misjudge their own technical proficiency.

## 💡 Our Solution
**CapstoneAI** is an enterprise-grade, AI-driven platform that eliminates the guesswork. Instead of relying on self-reporting, our system directly integrates with the **GitHub API** to objectively analyze a student's public repositories, languages, and commit history. 

By calculating a true proficiency baseline and combining it with the student's academic field, interests, and time constraints, CapstoneAI generates **highly personalized, mathematically tailored project blueprints** guaranteed to align with their actual capabilities and career goals.

## 🏗️ Architecture & Tech Stack
We prioritized **Security, Efficiency, and Code Quality** to build a production-ready system:

- **Frontend:** Next.js 16 (React 19), Tailwind CSS v4, strictly typed TypeScript.
- **Backend:** FastAPI (Python), utilizing Pydantic for rigorous payload validation.
- **Security:** Strict CORS policies, enterprise-grade Security Headers (HSTS, CSP, XSS Protection, No-Sniff), and input sanitization.
- **Efficiency:** Implemented `@lru_cache` on the backend to prevent API rate-limiting and ensure O(1) response times for recurring GitHub profile scans.
- **Accessibility:** 100% WCAG compliant. Full ARIA labeling, semantic HTML (`<main>`, `<article>`, `<nav>`), keyboard navigation focus rings, and high-contrast Light/Dark mode themes.
- **Testing:** Comprehensive unit testing using `pytest` for the backend and `Jest` + `React Testing Library` for the frontend to ensure rock-solid stability.

## 🚀 Getting Started

### 1. Backend Setup (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest test_main.py  # Run automated test suite
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run test:coverage  # Run automated test suite
npm run dev
```

## 🔒 Security Posture
- All inputs are validated via Pydantic models with strict `min_length`, `max_length`, and regex boundaries.
- The Next.js configuration enforces a strict Content-Security-Policy (CSP).
- No sensitive keys are exposed to the client.

## ♿ Accessibility Standards
- "Skip to main content" pathways via semantic structure.
- `aria-live="polite"` tags to ensure screen readers announce asynchronous loading states.
- Explicit `<label htmlFor="...">` bindings for all form elements.

---
*Built with passion to help the next generation of engineers build things that matter.*
