# AcroConnect

AcroConnect is a university placement & career guidance platform built for the Major Project.

**Important (submission view): this project runs as ONE website.**
- **User-facing website**: Streamlit portal (single login + role-based dashboards)
- **Backend service**: Django REST API (data + authentication)
- **Django admin** (`/admin`) is **developer-only** (used to create Faculty/TPO accounts and manage data), not a separate “dashboard website”.

## Quick Links
- Backend: `backend/`
- Frontend: `frontend/`
- Docker Compose: `docker-compose.yml`

## Local development (recommended)
### Easiest launch (recommended for demo/submission)

From the repo root, run:

```powershell
.\RUN_LOCAL.ps1
```

Then open the **single website** at `http://127.0.0.1:8501`.

### Docker Compose (optional)
1. Create a Python virtualenv and install dependencies for both backend and frontend.
2. Start services with Docker Compose:

```bash
# from repo root
export GEMINI_API_KEY="<your_key>"
docker-compose up --build
```

- Backend will be available at `http://127.0.0.1:8000`
- User-facing website (Streamlit portal) will be available at `http://127.0.0.1:8501`

## Deployment (Render + Postgres)
1. Create two Render Services (Docker): backend and frontend.
2. Add environment variables on Render:
   - `DATABASE_URL` (Postgres URL)
   - `GEMINI_API_KEY` (Gemini/Google API key)
   - `DJANGO_SECRET_KEY` (Django secret key)
   - `API_URL` (frontend service -> backend service URL)
3. Connect the repo and deploy. See `render.yaml` for sample config.

## Postgres in production
Switch the Django `DATABASES` to a proper Postgres URL via `DATABASE_URL` environment variable.

## Project structure
- `backend/` - Django project
- `frontend/` - Streamlit portal (single website UI)

## Team
- Varun Purohit (0827CI221148)
- Varun Bhaisare (0827CI221147)
- Mohd. Ayan Mansuri (0827CI221093)

## License
MIT — see `LICENSE` file.
