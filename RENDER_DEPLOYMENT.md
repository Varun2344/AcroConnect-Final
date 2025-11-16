# Render Deployment Guide — AcroConnect

Complete step-by-step instructions to deploy AcroConnect on Render with Postgres database.

**Time estimate:** 15-20 minutes total
**Result:** Live public URLs for frontend and backend

---

## Step 1: Sign In to Render (2 min)

1. Go to `https://render.com`
2. Click **"Sign up"** or **"Log in"**
3. Use **GitHub login** (recommended) — authorize Render to access your GitHub account
4. You'll land on the Render dashboard

---

## Step 2: Create Postgres Database (3 min)

1. On Render dashboard, click **"New +"** button (top right)
2. Select **"PostgreSQL"**
3. Fill in:
   - **Name:** `acroconnect-db`
   - **Database:** `acroconnect`
   - **User:** `acrouser`
   - **Password:** `acropass` (or choose your own)
   - **Region:** `Ohio` (or closest to you)
   - **Plan:** `Free` (scroll down, select free tier)
4. Click **"Create Database"**
5. Wait 1-2 minutes for it to be created
6. Once ready, **copy the `DATABASE_URL`** from the dashboard (it looks like `postgres://acrouser:...@...`)
   - Save this in a notepad — you'll paste it into the backend service next

---

## Step 3: Create Backend Service (5 min)

1. On Render dashboard, click **"New +"** → **"Web Service"**
2. Select **"Deploy existing repository"** → pick `Varun2344/AcroConnect-Final`
3. Fill in:
   - **Name:** `acroconnect-backend`
   - **Environment:** `Docker`
   - **Region:** `Ohio` (same as database)
   - **Branch:** `main`
   - **Dockerfile Path:** `backend/Dockerfile`
   - **Port:** Leave default or set to `8000`
4. Scroll down and click **"Advanced"**
5. In **"Environment"** section, add these variables (click **"Add Environment Variable"** for each):
   ```
   Key: GEMINI_API_KEY
   Value: <paste-your-new-rotated-API-key-from-Google-Cloud>
   
   Key: SECRET_KEY
   Value: django-insecure-9q2w3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j8k9l0z1x2c3v4b5n6m7
   
   Key: DATABASE_URL
   Value: <paste-the-DATABASE_URL-from-Step-2>
   
   Key: ALLOWED_HOSTS
   Value: *
   ```
6. Click **"Create Web Service"**
7. Render will start building — this takes 5-10 minutes
8. Once deployment completes, you'll get a URL like `https://acroconnect-backend.onrender.com`
9. **Copy this backend URL** — you'll need it for the frontend

---

## Step 4: Run Database Migrations (2 min)

After backend is deployed, run migrations to initialize the database:

1. Go back to Render dashboard
2. Click on the `acroconnect-backend` service
3. Look for the **"Shell"** tab at the top (or use the dashboard logs)
4. If Shell is available, click it and run:
   ```bash
   python manage.py migrate --noinput
   ```
5. If Shell is not available, you can also:
   - SSH into the service via terminal (Render provides instructions)
   - Or add a build script to `backend/Dockerfile` (ask me if needed)

**If migrations fail:** Check logs (Logs tab) — usually means `DATABASE_URL` is incorrect.

---

## Step 5: Create Frontend Service (5 min)

1. On Render dashboard, click **"New +"** → **"Web Service"**
2. Select `Varun2344/AcroConnect-Final` again
3. Fill in:
   - **Name:** `acroconnect-frontend`
   - **Environment:** `Docker`
   - **Region:** `Ohio`
   - **Branch:** `main`
   - **Dockerfile Path:** `frontend/Dockerfile`
   - **Port:** Leave default or set to `8501`
4. Scroll down and click **"Advanced"**
5. Add environment variable:
   ```
   Key: BACKEND_URL
   Value: <paste-the-backend-URL-from-Step-3>
   ```
   Example: `https://acroconnect-backend.onrender.com`
6. Click **"Create Web Service"**
7. Render will build and deploy — takes 5-10 minutes
8. Once complete, you'll get a frontend URL like `https://acroconnect-frontend.onrender.com`

---

## Step 6: Verify Deployment ✅

1. Open the **frontend URL** in your browser: `https://acroconnect-frontend.onrender.com`
2. Test the app:
   - **Login page** — can you see the login form?
   - **Login** — try with a test account (or create one)
   - **Profile page** — fill in skills, CGPA, goal
   - **AI Roadmap** — click "Generate Roadmap" and wait (may take 10-20 sec)
   - Should see generated roadmap text

3. If roadmap generation works, your deployment is successful! 🎉

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend shows error connecting to backend | Check `BACKEND_URL` env var matches backend service URL exactly (including `https://` and no trailing `/`) |
| Roadmap generation fails | Verify `GEMINI_API_KEY` is set and valid (your new rotated key) |
| Database connection error | Verify `DATABASE_URL` is correct; check Postgres service is running |
| Build fails | Check Render logs (Logs tab) for error messages; common: missing dependencies in `requirements.txt` |
| 502 Bad Gateway | Service crashed; check logs and error output |

**Check Logs:**
- Click on service → **"Logs"** tab → scroll to see error messages

---

## Your Public Links (once deployed)

- **Frontend (what you demo to faculty):**
  ```
  https://acroconnect-frontend.onrender.com
  ```

- **Backend API (for reference, requires auth):**
  ```
  https://acroconnect-backend.onrender.com/api/v1/roadmaps/
  ```

---

## Demo Walkthrough (for your presentation)

Open only the **frontend link** in your browser and:

1. **Login** — show authentication
2. **Fill Profile** — CGPA, skills, career goal
3. **Generate Roadmap** — highlight the AI integration (Gemini)
4. **View Result** — show the personalized roadmap generated by AI
5. **Optional:** Show saved roadmaps list

---

## Notes

- Free tier on Render will spin down after 15 minutes of inactivity (takes 50 sec to wake up on next request)
- For production, upgrade to paid plan
- All secrets are encrypted in Render's environment variables
- Never commit API keys — use environment variables only

---

**Done! You now have a live, public AcroConnect deployment.** 🚀
