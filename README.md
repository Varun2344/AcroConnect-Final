# AcroConnect

AcroConnect is a university placement & career guidance platform (Django backend + Streamlit frontend) built for the Major Project. It includes student profiles, job postings, and an AI-powered "Learning Roadmap" generator that uses Google Generative AI (Gemini).

## Quick Links
- Backend: `backend/`
- Frontend: `frontend/`
- Docker Compose: `docker-compose.yml`

## Local development (recommended)
1. Create a Python virtualenv and install dependencies for both backend and frontend.
2. Start services with Docker Compose (recommended):

```bash
# from repo root
export GEMINI_API_KEY="<your_key>"
docker-compose up --build
```

- Backend will be available at `http://127.0.0.1:8000`
- Frontend (Streamlit) will be available at `http://127.0.0.1:8501`

## Deployment (Render + Postgres)
1. Create two Render Services (Docker): backend and frontend.
2. Add environment variables on Render:
   - `DATABASE_URL` (Postgres URL)
   - `GEMINI_API_KEY` (Gemini/Google API key)
   - `SECRET_KEY` (Django secret key)
3. Connect the repo and deploy. See `render.yaml` for sample config.

## Postgres in production
Switch the Django `DATABASES` to a proper Postgres URL via `DATABASE_URL` environment variable.

## Project structure
- `backend/` - Django project
- `frontend/` - Streamlit frontend app

## Team
- Varun Purohit (0827CI221148)
- Varun Bhaisare (0827CI221147)
- Mohd. Ayan Mansuri (0827CI221093)

## License
MIT — see `LICENSE` file.
