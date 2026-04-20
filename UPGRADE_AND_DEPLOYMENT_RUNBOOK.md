# AcroConnect Upgrade and Deployment Runbook

This runbook executes the agreed five-point upgrade plan:
1) SQLite to PostgreSQL readiness
2) Production hardening
3) UI/UX upgrades
4) Test coverage upgrade
5) Deployment sequence

## 1) SQLite to PostgreSQL

- Django now supports both:
  - local fallback: SQLite
  - production: `DATABASE_URL` (PostgreSQL)
- Dependencies already included for production DB:
  - `dj-database-url`
  - `psycopg2-binary`

Validation commands:

```powershell
cd backend
python manage.py check
python manage.py migrate --noinput
```

## 2) Production hardening

Set these env vars in production:

- `DEBUG=False`
- `DJANGO_SECRET_KEY=<strong-random-secret>`
- `ALLOWED_HOSTS=<backend-domain>`
- `CORS_ALLOWED_ORIGINS=<frontend-domain>`
- `CSRF_TRUSTED_ORIGINS=<backend-domain>`
- `DATABASE_URL=<postgres-url>`
- `GEMINI_API_KEY=<valid-key>`

Security behavior:

- App fails startup if `DEBUG=False` and `DJANGO_SECRET_KEY` is default.
- HTTPS-focused settings are enabled automatically when `DEBUG=False`.

## 3) UI/UX upgrades included

- Frontend now shows configured API endpoint in the UI for easier debugging.
- HTTP error messages are standardized and more readable.
- Student deletion in TPO dashboard now requires explicit confirmation.
- API response errors are surfaced consistently across profile, roadmap, jobs, and auth flows.

## 4) Automated tests added

New backend tests cover:

- login via username and email
- user registration cannot self-assign TPO role
- profile ownership restrictions
- student blocked from creating job postings
- TPO allowed to create job postings
- student skill assignment cannot target another profile
- roadmap endpoint behavior when Gemini is unavailable

Run tests:

```powershell
cd backend
python manage.py test
```

## 5) Deployment sequence (Render)

1. Create PostgreSQL service on Render, copy `DATABASE_URL`.
2. Deploy backend (`backend/Dockerfile`) with production env vars listed above.
3. Run migrations on backend service:
   - `python manage.py migrate --noinput`
4. Deploy frontend (`frontend/Dockerfile`) with:
   - `API_URL=https://<backend-service>.onrender.com`
5. Smoke test:
   - register/login
   - profile update
   - skill add/remove
   - roadmap generation
   - TPO job posting + dashboard

## What is still required from the project owner

- Render account actions (service creation + env var entry)
- New Gemini key value
- Final production domain names for frontend/backend
- Optional: a secure secret value for `DJANGO_SECRET_KEY`
- Final acceptance smoke test in browser
