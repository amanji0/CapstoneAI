# CapstoneAI

AI-powered platform that helps final-year students generate project ideas based on their interests and skills.

## Project Structure

```
├── frontend/     # Next.js 16 + Tailwind CSS
└── backend/      # FastAPI + Python
```

## Local Development

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Deployment

- **Frontend**: Deploy to [Vercel](https://vercel.com) — connect your GitHub repo and set root directory to `frontend`
- **Backend**: Deploy to [Render](https://render.com) — connect your GitHub repo and set root directory to `backend`

### Environment Variables

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL` = Your Render backend URL (e.g. `https://capstoneai-api.onrender.com`)

**Backend (Render):**
- `FRONTEND_URL` = Your Vercel frontend URL (e.g. `https://capstoneai.vercel.app`)
