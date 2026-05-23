# Franz

A JARVIS-like personal assistant running on localhost.

## Stack
- Python 3.12 — FastAPI backend
- React + Vite + TypeScript — frontend
- LangGraph + OpenAI — agent layer (wiring TBD)

## Dev

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```
