import streamlit as st

import pandas as pd
import requests
import re
import plotly.express as px
import os
import time
from datetime import datetime
from streamlit_cookies_controller import CookieController

# Global controller
controller = CookieController()



# API base URL

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="AcroConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_global_styles() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

  /* Global Typography & Theme */
  html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
  }
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600;
  }

  /* Base Streamlit Overrides */
  .stApp {
    background: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.08), transparent 25%),
                #0f172a; /* Slate 900 */
    color: #f8fafc;
  }

  /* Hide Streamlit Header */
  header[data-testid="stHeader"] {
    display: none !important;
  }
  
  /* Sidebar Styling */
  [data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.05);
  }
  
  /* Inputs & Buttons Styling */
  .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
    background-color: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
    transition: all 0.3s ease;
  }
  .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stNumberInput>div>div>input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
  }

  /* Primary Button Styling */
  .stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3), 0 2px 4px -1px rgba(99, 102, 241, 0.2) !important;
  }
  .stButton>button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 8px -1px rgba(99, 102, 241, 0.4), 0 4px 6px -1px rgba(99, 102, 241, 0.3) !important;
  }
  
  /* Secondary Button Styling */
  .stButton>button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.7) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
  }
  .stButton>button[kind="secondary"]:hover {
    background: rgba(51, 65, 85, 0.9) !important;
    border-color: rgba(255,255,255,0.2) !important;
  }

  /* Expanders Styling */
  .streamlit-expanderHeader {
    background-color: rgba(30, 41, 59, 0.5) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    transition: background-color 0.2s ease !important;
  }
  .streamlit-expanderHeader:hover {
    background-color: rgba(30, 41, 59, 0.8) !important;
  }

  /* Metric Cards Styling */
  [data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
  }
  [data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.3);
  }

  /* Dataframe Styling */
  [data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
  }

  /* Custom Classes */
  .acro-hero {
    padding: 40px 32px;
    border-radius: 24px;
    background: radial-gradient(1200px 600px at 10% 0%,
      rgba(99, 102, 241, 0.15) 0%,
      rgba(16, 185, 129, 0.05) 45%,
      rgba(15, 23, 42, 0) 75%),
      linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(2, 6, 23, 0.6));
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }
  .acro-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  }
  .acro-hero h1 { 
    margin: 0 0 12px 0; 
    font-size: 48px; 
    line-height: 1.1; 
    background: linear-gradient(to right, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
  }
  .acro-hero p { 
    margin: 0; 
    font-size: 18px; 
    color: rgba(226, 232, 240, 0.8); 
    line-height: 1.6;
    max-width: 600px;
  }
  .acro-pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    color: #818cf8;
    font-size: 13px;
    font-weight: 500;
    margin-right: 8px;
    margin-bottom: 16px;
    letter-spacing: 0.02em;
    backdrop-filter: blur(8px);
  }
  .acro-card {
    padding: 24px;
    border-radius: 20px;
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    height: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
  }
  .acro-card:hover {
    transform: translateY(-4px);
    background: rgba(30, 41, 59, 0.6);
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }
  .acro-card h3 { 
    margin-top: 0; 
    color: #f8fafc;
    font-size: 1.25rem;
    margin-bottom: 12px;
  }
  .acro-muted { 
    color: #94a3b8; 
    line-height: 1.5;
    font-size: 0.95rem;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def show_public_landing() -> None:
    _inject_global_styles()

    st.markdown(
        """
<div class="acro-hero">
  <div class="acro-pill">Placement & Career Guidance</div>
  <div class="acro-pill">AI Roadmaps (Gemini)</div>
  <div class="acro-pill">Student Profiles</div>
  <div class="acro-pill">Job Board</div>
  <h1>AcroConnect</h1>
  <p>One portal for students and faculty/TPO — sign in once and get the right dashboard automatically.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
<div class="acro-card">
  <h3>For Students</h3>
  <div class="acro-muted">Build your profile, manage skills, and generate an AI learning roadmap aligned to your career goal.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="acro-card">
  <h3>For Faculty / TPO</h3>
  <div class="acro-muted">View student analytics, manage job postings, and help guide placements — all inside this same portal.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
<div class="acro-card">
  <h3>Single Website</h3>
  <div class="acro-muted">The Django backend runs as an API service; the full user-facing website is this portal.</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    a1, a2, a3 = st.columns([1, 1, 1])
    with a1:
        if st.button("Log in", type="primary", use_container_width=True):
            st.session_state.public_page = "login"
            st.rerun()
    with a2:
        if st.button("Register (New Student)", use_container_width=True):
            st.session_state.public_page = "register"
            st.rerun()
    with a3:
        if st.button("About", use_container_width=True):
            st.session_state.public_page = "about"
            st.rerun()


def show_about_page() -> None:
    _inject_global_styles()
    st.markdown(
        """
<div class="acro-hero">
  <h1>About AcroConnect</h1>
  <p>A university placement & career guidance platform: student profiles, job postings, and AI-generated learning roadmaps.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.subheader("How it works")
    st.markdown(
        """
- **One Login**: same login screen for everyone.
- **Role-based Routing**: faculty/TPO accounts open the **TPO Dashboard**; students open the **Student Dashboard**.
- **Registration**: creates **student accounts only** by default.
- **Faculty/TPO Accounts**: created by the developer (superuser) in the backend.
        """
    )
    st.subheader("What you can demo quickly")
    st.markdown(
        """
- Student: register → log in → update profile/skills → generate AI roadmap → view job board.
- Faculty/TPO: log in → analytics of students → post & manage job postings.
        """
    )



DEFAULT_SESSION_STATE = {

    "logged_in": False,

    "token": None,

    "is_tpo": False,

    "user_email": None,

    "user_id": None,

    "nav_option": None,
    "public_page": "home",

}





def init_session_state() -> None:
    # Handle the 1-tick delay of JS cookie loading
    if "cookie_checked" not in st.session_state:
        st.session_state["cookie_checked"] = False

    cookie_token = None
    try:
        cookie_token = controller.get('acro_token')
    except TypeError:
        # Handle streamlit_cookies_controller returning None for internal cookie cache.
        cookie_token = None
    except Exception:
        cookie_token = None
    
    if cookie_token and not st.session_state.get('logged_in'):
        st.session_state['logged_in'] = True
        st.session_state['token'] = cookie_token
        try:
            headers = {"Authorization": f"Bearer {cookie_token}"}
            res = requests.get(f"{API_URL}/api/v1/users/me/", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                st.session_state['is_tpo'] = bool(data.get("is_tpo", False))
                st.session_state['user_email'] = data.get("email") or data.get("username")
                st.session_state['user_id'] = data.get("id")
            else:
                st.session_state['logged_in'] = False
                st.session_state['token'] = None
        except Exception:
            pass
            
    elif cookie_token is None and not st.session_state.get('logged_in') and not st.session_state["cookie_checked"]:
        # Give JS a fraction of a second to send cookies to Python, then force a rerun
        st.session_state["cookie_checked"] = True
        time.sleep(0.3)
        st.rerun()

    for key, default in DEFAULT_SESSION_STATE.items():
        st.session_state.setdefault(key, default)





def reset_session_state() -> None:
    for key, default in DEFAULT_SESSION_STATE.items():
        st.session_state[key] = default
    try:
        controller.remove('acro_token')
    except Exception:
        pass





def handle_auth_failure(response) -> bool:
    """
    Detect JWT auth failures, reset session, and redirect to login.
    Returns True when auth failure was handled.
    """
    if response is None or response.status_code != 401:
        return False

    message = "Session expired or invalid token. Please log in again."
    try:
        data = response.json()
        if isinstance(data, dict):
            detail = data.get("detail") or data.get("message")
            if detail:
                message = f"{message} ({detail})"
    except ValueError:
        pass

    reset_session_state()
    st.error(message)
    st.rerun()
    return True


def show_login_page() -> None:

    _inject_global_styles()

    st.markdown(
        """
<div class="acro-hero">
  <h1>Sign in to AcroConnect</h1>
  <p>Enter your credentials. Faculty/TPO users will be routed to the TPO dashboard automatically.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    login_tab, register_tab = st.tabs(["Login", "Register (New Student)"])



    with login_tab:

        st.subheader("Login")

        with st.form("login_form", clear_on_submit=False):

            login_identifier = st.text_input("Username or Email", key="login_identifier")

            password = st.text_input("Password", type="password", key="login_password")

            submitted = st.form_submit_button("Log In")



        if submitted:

            if not login_identifier or not password:

                st.error("Please enter both username/email and password.")

            else:

                try:

                    # Django token endpoint requires 'username' field

                    # Send the identifier as username (works for both username and email)

                    payload = {"username": login_identifier, "password": password}

                    response = requests.post(

                        f"{API_URL}/api/token/",

                        # SimpleJWT expects JSON; form-encoded can fail validation.
                        json=payload,

                        timeout=10,

                    )

                    if response.status_code != 200:

                        # If login fails, show the error

                        try:
                            error_data = response.json()
                            if isinstance(error_data, dict):
                                if "detail" in error_data:
                                    error_message = error_data.get("detail")
                                elif "message" in error_data:
                                    error_message = error_data.get("message")
                                else:
                                    msgs = []
                                    for k, v in error_data.items():
                                        val = v[0] if isinstance(v, list) else v
                                        msgs.append(f"{k.capitalize()}: {val}")
                                    error_message = " | ".join(msgs) if msgs else str(error_data)
                            else:
                                error_message = str(error_data)
                        except ValueError:

                            error_message = response.text or "Unable to log in."

                        st.error(f"Login failed: {error_message}")

                        return

                    # If we reach here, status code is 200
                    data = response.json()

                    token = data.get("access") or data.get("token")

                    if not token:

                        st.error("Login failed: token missing in response.")

                        return

                    st.session_state.token = token

                    st.session_state.logged_in = True

                    # Fetch user details from /api/v1/users/me/
                    headers = {"Authorization": f"Bearer {token}"}
                    try:
                        user_response = requests.get(
                            f"{API_URL}/api/v1/users/me/",
                            headers=headers,
                            timeout=10,
                        )
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            st.session_state.user_id = user_data.get("id")
                            st.session_state.user_email = user_data.get("email") or user_data.get("username")
                            st.session_state.is_tpo = bool(user_data.get("is_tpo", False))
                        else:
                            # Fallback to token response data if /me/ fails
                            st.session_state.user_email = data.get("email") or data.get("username") or (login_identifier if "@" in login_identifier else None)
                            st.session_state.user_id = data.get("user_id") or data.get("id")
                            st.session_state.is_tpo = bool(data.get("is_tpo", False))
                    except requests.RequestException:
                        st.session_state.user_email = data.get("email") or data.get("username") or (login_identifier if "@" in login_identifier else None)
                        st.session_state.user_id = data.get("user_id") or data.get("id")
                        st.session_state.is_tpo = bool(data.get("is_tpo", False))

                    try:
                        controller.set('acro_token', str(st.session_state.token))
                    except Exception:
                        pass

                    st.toast("Login successful!", icon="🔓")

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(f"Login failed: {exc}")



    with register_tab:

        st.subheader("Register as a New Student")
        st.caption("New registrations are students by default. For Faculty/TPO access, contact the developer.")

        with st.form("register_form", clear_on_submit=True):

            name = st.text_input("Full Name")

            username = st.text_input("Username", key="register_username")

            reg_email = st.text_input("Email", key="register_email")

            phone = st.text_input("Phone Number")

            reg_password = st.text_input("Password", type="password", key="register_password")

            register_submit = st.form_submit_button("Create Account")



        if register_submit:

            if not all([name, username, reg_email, phone, reg_password]):

                st.error("❌ All fields are required for registration.")
            elif len(reg_password) < 8:
                st.error("❌ Password must be at least 8 characters long.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                st.error("❌ Please enter a valid email address.")
            else:

                payload = {

                    "name": name,

                    "username": username,

                    "email": reg_email,

                    "phone": phone,

                    "password": reg_password,

                }

                try:

                    response = requests.post(

                        f"{API_URL}/api/v1/users/",

                        json=payload,

                        timeout=10,

                    )

                    if response.status_code in (200, 201):

                        try:

                            response_data = response.json()

                            created_username = response_data.get("username", username)

                            created_email = response_data.get("email", reg_email)

                            st.toast(f"Registration successful! You can now log in.", icon="🎉")

                            st.info(f"Registered with Username: **{created_username}** | Email: **{created_email}**")

                        except ValueError:

                            st.toast("Registration successful! You can now log in.", icon="🎉")

                    else:

                        try:
                            error_data = response.json()
                            if isinstance(error_data, dict):
                                if "detail" in error_data:
                                    error_message = error_data.get("detail")
                                elif "message" in error_data:
                                    error_message = error_data.get("message")
                                else:
                                    msgs = []
                                    for k, v in error_data.items():
                                        val = v[0] if isinstance(v, list) else v
                                        msgs.append(f"{k.capitalize()}: {val}")
                                    error_message = " | ".join(msgs) if msgs else str(error_data)
                            else:
                                error_message = str(error_data)
                        except ValueError:

                            error_message = response.text or "Unable to register."

                        st.error(f"Registration failed: {error_message}")

                except requests.RequestException as exc:

                    st.error(f"Registration failed: {exc}")





def show_profile_page() -> None:
    """Display and update student profile."""
    token = st.session_state.token
    user_id = st.session_state.user_id

    if not token:
        st.error("Authentication token not found. Please log in again.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Fetch current profile data using /me/ endpoint
    try:
        response = requests.get(
            f"{API_URL}/api/v1/student-profiles/me/",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            profile_data = response.json()
            profile_id = profile_data.get("id")
        else:
            st.error(f"Failed to fetch profile: {response.status_code}")
            profile_data = {}
            profile_id = None
    except requests.RequestException as e:
        st.error(f"Error fetching profile: {e}")
        profile_data = {}
        profile_id = None

    if not profile_id:
        st.error("Profile not found. Please try logging in again.")
        return

    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(16, 185, 129, 0.1)); 
                    padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;'>
            <h2 style='margin:0; font-family: "Outfit", sans-serif; color: #f8fafc;'>👤 Complete Your Profile for AI Matching</h2>
            <p style='margin: 8px 0 0 0; color: #e2e8f0; font-size: 1.05rem; line-height: 1.5;'>
                Welcome to your AcroConnect hub! 🚀 Keeping your profile updated is critical. 
                Our underlying <strong>Gemini AI Engine</strong> uses this exact data—your CGPA, skills, and career goals—to 
                generate highly accurate, dynamic learning roadmaps and match you with the best job opportunities from your TPO.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- Autosave helpers ---
    def _normalize_text(v):
        return (v or "").strip()

    def _normalize_url(v):
        value = _normalize_text(v)
        if not value:
            return ""
        if value.startswith("http://") or value.startswith("https://"):
            return value
        # Accept user-entered domains/usernames by defaulting to https scheme.
        return f"https://{value}"

    def _snapshot_from_widgets():
        return {
            "full_name": _normalize_text(st.session_state.get("profile_full_name")),
            "phone": _normalize_text(st.session_state.get("profile_phone")),
            "cgpa": float(st.session_state.get("profile_cgpa") or 0.0),
            "semester": int(st.session_state.get("profile_semester") or 1),
            "section": _normalize_text(st.session_state.get("profile_section")),
            "tech_stack": _normalize_text(st.session_state.get("profile_tech_stack")),
            "resume_url": _normalize_url(st.session_state.get("profile_resume_url")),
            "github_url": _normalize_url(st.session_state.get("profile_github_url")),
            "linkedin_url": _normalize_url(st.session_state.get("profile_linkedin_url")),
            "portfolio_url": _normalize_url(st.session_state.get("profile_portfolio_url")),
            "career_goal": _normalize_text(st.session_state.get("profile_career_goal")),
            "achievements": _normalize_text(st.session_state.get("profile_achievements")),
            "projects": _normalize_text(st.session_state.get("profile_projects")),
        }

    def _snapshot_from_server(d):
        def _num(x, default=0.0):
            try:
                return float(x)
            except (TypeError, ValueError):
                return default

        def _int(x, default=1):
            try:
                return int(x)
            except (TypeError, ValueError):
                return default

        return {
            "full_name": _normalize_text(d.get("full_name")),
            "phone": _normalize_text(d.get("phone")),
            "cgpa": _num(d.get("cgpa"), 0.0),
            "semester": _int(d.get("semester"), 1),
            "section": _normalize_text(d.get("section")),
            "tech_stack": _normalize_text(d.get("tech_stack")),
            "resume_url": _normalize_text(d.get("resume_url")),
            "github_url": _normalize_text(d.get("github_url")),
            "linkedin_url": _normalize_text(d.get("linkedin_url")),
            "portfolio_url": _normalize_text(d.get("portfolio_url")),
            "career_goal": _normalize_text(d.get("career_goal")),
            "achievements": _normalize_text(d.get("achievements")),
            "projects": _normalize_text(d.get("projects")),
        }

    def _diff_payload(current, last_saved):
        payload = {}
        for k, v in current.items():
            if last_saved.get(k) != v:
                payload[k] = v
        return payload

    # Initialize autosave session state once per profile id
    autosave_key = f"profile_autosave_init_{profile_id}"
    last_saved_key = f"profile_last_saved_{profile_id}"
    last_save_ts_key = f"profile_last_save_ts_{profile_id}"
    server_snapshot = _snapshot_from_server(profile_data)
    if not st.session_state.get(autosave_key):
        st.session_state[last_saved_key] = server_snapshot
        st.session_state[last_save_ts_key] = 0.0
        st.session_state[autosave_key] = True

    # Always ensure widgets are rehydrated when returning from another page.
    # Streamlit can drop widget-bound keys if a widget is not rendered in a run.
    field_keys = [
        ("profile_full_name", "full_name"),
        ("profile_phone", "phone"),
        ("profile_cgpa", "cgpa"),
        ("profile_semester", "semester"),
        ("profile_section", "section"),
        ("profile_tech_stack", "tech_stack"),
        ("profile_resume_url", "resume_url"),
        ("profile_github_url", "github_url"),
        ("profile_linkedin_url", "linkedin_url"),
        ("profile_portfolio_url", "portfolio_url"),
        ("profile_career_goal", "career_goal"),
        ("profile_achievements", "achievements"),
        ("profile_projects", "projects"),
    ]
    source_snapshot = st.session_state.get(last_saved_key) or server_snapshot
    for widget_key, data_key in field_keys:
        if widget_key not in st.session_state:
            st.session_state[widget_key] = source_snapshot.get(data_key, "")

    colA, colB = st.columns([3, 2])
    with colB:
        autosave_enabled = st.toggle("Autosave", value=True, help="Automatically saves changes as you edit.")
        st.caption("Autosave keeps your data retained even if you refresh.")

    with colA:
        st.write("")

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("Full Name", key="profile_full_name")
            st.text_input("Phone", key="profile_phone")
            st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.01, key="profile_cgpa")
        with c2:
            st.number_input("Semester", min_value=1, max_value=10, step=1, key="profile_semester")
            st.text_input("Class/Section", key="profile_section", help="Example: CSE-A, IT-B, etc.")
            st.text_input("Tech Stack (comma-separated)", key="profile_tech_stack", help="Example: Python, Django, React")
        with c3:
            st.text_input("Resume URL", key="profile_resume_url")
            st.text_input("GitHub URL", key="profile_github_url")
            st.text_input("LinkedIn URL", key="profile_linkedin_url")
            st.text_input("Portfolio URL", key="profile_portfolio_url")

    st.write("")
    st.text_area("Career Goal", key="profile_career_goal")
    st.caption("Describe your career aspirations (this helps generate better AI roadmaps).")
    st.text_area("Achievements", key="profile_achievements", help="Awards, certifications, hackathons, etc.")
    st.text_area("Projects (one per line)", key="profile_projects")

    current_snapshot = _snapshot_from_widgets()
    last_saved_snapshot = st.session_state.get(last_saved_key, {})
    payload = _diff_payload(current_snapshot, last_saved_snapshot)

    save_col1, save_col2, save_col3 = st.columns([1, 1, 2])
    with save_col1:
        save_now = st.button("Save now", type="primary", disabled=not bool(payload), use_container_width=True)
    with save_col2:
        discard = st.button("Discard changes", disabled=not bool(payload), use_container_width=True)
    with save_col3:
        if payload:
            st.warning("Unsaved changes", icon="⚠️")
        else:
            st.success("All changes saved", icon="✅")

    if discard:
        # reset widgets to last saved values
        for k, v in last_saved_snapshot.items():
            st.session_state[f"profile_{k}"] = v
        st.rerun()

    should_autosave = autosave_enabled and bool(payload)
    throttled = (time.time() - float(st.session_state.get(last_save_ts_key, 0.0))) < 1.2

    if (save_now or (should_autosave and not throttled)) and payload:
        try:
            update_response = requests.patch(
                f"{API_URL}/api/v1/student-profiles/{profile_id}/",
                json=payload,
                headers=headers,
                timeout=10,
            )
            if update_response.status_code in (200, 204):
                # Update last saved snapshot locally
                merged = dict(last_saved_snapshot)
                merged.update(payload)
                st.session_state[last_saved_key] = merged
                st.session_state[last_save_ts_key] = time.time()
                if save_now:
                    st.toast("Saved")
            else:
                try:
                    error_data = update_response.json()
                    error_message = (
                        error_data.get("detail")
                        or error_data.get("message")
                        or str(error_data)
                    )
                except ValueError:
                    error_message = update_response.text or "Unable to update profile."
                st.error(f"Save failed: {error_message}")
        except requests.RequestException as e:
            st.error(f"Save failed: {e}")

    # Display existing skills
    st.write("### Your Skills")
    skill_assignments = profile_data.get("skill_assignments", [])
    if skill_assignments:
        for assignment in skill_assignments:
            skill = assignment.get("skill", {})
            skill_name = skill.get("skill_name", "Unknown")
            skill_level = assignment.get("skill_level", 0)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{skill_name}**")
            with col2:
                if st.button("Remove", key=f"remove_skill_{assignment.get('id')}"):
                    try:
                        delete_response = requests.delete(
                            f"{API_URL}/api/v1/student-skill-sets/{assignment.get('id')}/",
                            headers=headers,
                            timeout=10,
                        )
                        if delete_response.status_code in (200, 204):
                            st.toast(f"Removed {skill_name}", icon="🗑️")
                            st.rerun()
                        else:
                            st.error("Failed to remove skill.")
                    except requests.RequestException as e:
                        st.error(f"Error removing skill: {e}")
            st.progress(skill_level / 5.0 if skill_level <= 5 else 1.0)
            st.caption(f"Level: {skill_level}/5")
    else:
        st.info("No skills added yet. Add a skill below!")

    # Add Skill Form
    st.write("### Add New Skill")
    try:
        skills_response = requests.get(
            f"{API_URL}/api/v1/skills/",
            headers=headers,
            timeout=10,
        )
        # Also fetch job postings to see which skills are in demand
        job_demand = {}
        try:
            jobs_res = requests.get(f"{API_URL}/api/v1/job-postings/", headers=headers, timeout=10)
            if jobs_res.status_code == 200:
                for job in jobs_res.json():
                    comp = job.get("company") or "Unknown Company"
                    for req in job.get("required_skills", []):
                        s_id = req.get("skill", {}).get("id")
                        if s_id:
                            if s_id not in job_demand:
                                job_demand[s_id] = set()
                            job_demand[s_id].add(comp)
        except Exception:
            pass

        if skills_response.status_code == 200:
            all_skills = skills_response.json()
            existing_skill_ids = [a.get("skill", {}).get("id") for a in skill_assignments if a.get("skill")]
            available_skills = [s for s in all_skills if s.get("id") not in existing_skill_ids]
            
            if available_skills:
                with st.form("add_skill_form", clear_on_submit=True):
                    skill_options = {}
                    for s in available_skills:
                        s_id = s.get("id")
                        base_name = f"{s.get('skill_name')} ({s.get('category', 'N/A')})"
                        if s_id in job_demand:
                            comps = list(job_demand[s_id])
                            base_name += f" 🔥 Required by {', '.join(comps[:2])}" + ("..." if len(comps)>2 else "")
                        skill_options[base_name] = s_id
                        
                    selected_skill = st.selectbox("Select Skill", options=list(skill_options.keys()))
                    skill_level = st.slider("Skill Level", min_value=1, max_value=5, value=3, step=1)
                    add_skill_button = st.form_submit_button("Add Skill")

                if add_skill_button:
                    selected_skill_id = skill_options[selected_skill]
                    skill_payload = {
                        "student_profile_id": profile_id,
                        "skill_id": selected_skill_id,
                        "skill_level": skill_level,
                    }
                    try:
                        add_response = requests.post(
                            f"{API_URL}/api/v1/student-skill-sets/",
                            json=skill_payload,
                            headers=headers,
                            timeout=10,
                        )
                        if add_response.status_code in (200, 201):
                            st.toast("Skill added successfully!", icon="⭐")
                            st.rerun()
                        else:
                            try:
                                error_data = add_response.json()
                                error_message = (
                                    error_data.get("detail")
                                    or error_data.get("message")
                                    or str(error_data)
                                )
                            except ValueError:
                                error_message = add_response.text or "Unable to add skill."
                            st.error(f"Failed to add skill: {error_message}")
                    except requests.RequestException as e:
                        st.error(f"Error adding skill: {e}")
            else:
                st.info("All available skills have been added to your profile.")
        else:
            st.error(f"Failed to fetch skills: {skills_response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error fetching skills: {e}")

def show_roadmap_page() -> None:
    """Display and generate AI roadmaps for the student."""
    token = st.session_state.token
    user_id = st.session_state.user_id

    if not token:
        st.error("Authentication token not found. Please log in again.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Fetch all roadmaps
    try:
        response = requests.get(
            f"{API_URL}/api/v1/roadmaps/",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            all_roadmaps = response.json()
            # Filter roadmaps for current user
            user_roadmaps = [
                r for r in all_roadmaps
                if r.get("profile", {}).get("user", {}).get("id") == user_id
            ]
        elif handle_auth_failure(response):
            return
        else:
            st.error(f"Failed to fetch roadmaps: {response.status_code}")
            user_roadmaps = []
    except requests.RequestException as e:
        st.error(f"Error fetching roadmaps: {e}")
        user_roadmaps = []

    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1)); 
                    padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;'>
            <h2 style='margin:0; font-family: "Outfit", sans-serif; color: #f8fafc;'>🚀 AI Learning Roadmap</h2>
            <p style='margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;'>Generate and track your personalized career path using Gemini AI.</p>
        </div>
    """, unsafe_allow_html=True)

    # Display existing roadmaps
    if user_roadmaps:
        st.write("### Your Generated Roadmaps")
        for roadmap in user_roadmaps:
            generated_on = roadmap.get("generated_on", "")
            roadmap_text = roadmap.get("roadmap_text", "")
            roadmap_id = roadmap.get("id")

            generated_label = "Unknown time"
            if generated_on:
                try:
                    dt = datetime.fromisoformat(generated_on.replace("Z", "+00:00"))
                    generated_label = dt.strftime("%d %b %Y, %I:%M:%S %p")
                except ValueError:
                    generated_label = generated_on

            with st.expander(f"Roadmap generated on {generated_label}"):
                st.markdown(roadmap_text)
                if st.button("Delete this roadmap", key=f"delete_roadmap_{roadmap_id}", type="secondary"):
                    try:
                        delete_response = requests.delete(
                            f"{API_URL}/api/v1/roadmaps/{roadmap_id}/",
                            headers=headers,
                            timeout=10,
                        )
                        if delete_response.status_code in (200, 204):
                            st.toast("Roadmap deleted successfully.", icon="🗑️")
                            st.rerun()
                        elif handle_auth_failure(delete_response):
                            return
                        else:
                            try:
                                error_data = delete_response.json()
                                error_message = (
                                    error_data.get("detail")
                                    or error_data.get("message")
                                    or str(error_data)
                                )
                            except ValueError:
                                error_message = delete_response.text or "Unable to delete roadmap."
                            st.error(f"Delete failed: {error_message}")
                    except requests.RequestException as e:
                        st.error(f"Error deleting roadmap: {e}")
    else:
        st.info("No roadmaps generated yet. Click the button below to generate your first AI roadmap!")

    # Generate new roadmap button
    st.write("### Generate New Roadmap")
    st.write("**Note:** Your AI roadmap will be generated based on your current profile, skills, and career goal. Make sure to update your profile first!")
    
    if st.button("🚀 Generate New AI Roadmap", use_container_width=True):
        with st.spinner("✨ Generating your personalized AI roadmap using Google Gemini..."):
            try:
                generate_response = requests.post(
                    f"{API_URL}/api/v1/generate-roadmap/",
                    headers=headers,
                    timeout=60,
                )
                if generate_response.status_code == 201:
                    new_roadmap = generate_response.json()
                    st.success("✅ Roadmap generated successfully!")
                    st.rerun()
                elif handle_auth_failure(generate_response):
                    return
                else:
                    try:
                        error_data = generate_response.json()
                        error_message = (
                            error_data.get("detail")
                            or error_data.get("message")
                            or str(error_data)
                        )
                    except ValueError:
                        error_message = generate_response.text or "Unable to generate roadmap."
                    st.error(f"❌ Failed to generate roadmap: {error_message}")
            except requests.RequestException as e:
                st.error(f"❌ Error generating roadmap: {e}")


def show_job_board_page() -> None:
    """Display all available job postings."""
    token = st.session_state.token

    if not token:
        st.error("Authentication token not found. Please log in again.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1)); 
                    padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;'>
            <h2 style='margin:0; font-family: "Outfit", sans-serif; color: #f8fafc;'>💼 Exclusive Campus Opportunities</h2>
            <p style='margin: 8px 0 0 0; color: #e2e8f0; font-size: 1.05rem; line-height: 1.5;'>
                Discover top-tier roles curated specifically for you by the Training and Placement Office. Ensure your profile and AI Roadmap are up to date before applying to stand out to recruiters! ✨
            </p>
        </div>
    """, unsafe_allow_html=True)

    try:
        response = requests.get(
            f"{API_URL}/api/v1/job-postings/",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                for job in jobs:
                    job_id = job.get("id")
                    title = job.get("title", "Untitled")
                    company = job.get("company", "")
                    description = job.get("description", "No description available.")
                    posted_on = job.get("posted_on", "")
                    required_skills = job.get("required_skills", [])
                    tpo_user = job.get("tpo_user", {})

                    expander_title = f"**{title}**"
                    if company:
                        expander_title += f" - {company}"
                    expander_title += f" - Posted on {posted_on[:10] if posted_on else 'Unknown date'}"

                    with st.expander(expander_title):
                        if company:
                            st.write(f"**Company:** {company}")
                        st.write("**Description:**")
                        st.write(description)
                        
                        if required_skills:
                            st.write("**Required Skills:**")
                            skill_names = [
                                skill.get("skill", {}).get("skill_name", "Unknown")
                                for skill in required_skills
                                if skill.get("skill")
                            ]
                            st.write(", ".join(skill_names) if skill_names else "None specified")
                        
                        if tpo_user:
                            tpo_name = tpo_user.get("first_name") or tpo_user.get("username", "Unknown")
                            st.write(f"**Posted by:** {tpo_name}")
            else:
                st.info("No job postings available at the moment. Check back later!")
        else:
            st.error(f"Failed to fetch job postings: {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error fetching job postings: {e}")


def show_tpo_dashboard_page() -> None:
    """TPO Dashboard with analytics and student management."""
    token = st.session_state.token

    if not token:
        st.error("Authentication token not found. Please log in again.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1)); 
                        padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>
                <h2 style='margin:0; font-family: "Outfit", sans-serif; color: #f8fafc;'>📊 Advanced TPO Analytics Engine</h2>
                <p style='margin: 8px 0 0 0; color: #e2e8f0; font-size: 1.05rem; line-height: 1.5;'>
                    Welcome to the central command center for student success. 🎯 Use these real-time analytics to track student readiness, filter by specific tech stacks, and make data-driven decisions to drastically increase campus placement rates.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.write("") # Spacing to align button vertically
        st.write("")
        if st.button("🔄 Refresh Data", use_container_width=True, help="Fetch the latest student data"):
            st.rerun()

    # Fetch all student profiles
    try:
        response = requests.get(
            f"{API_URL}/api/v1/student-profiles/",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            profiles = response.json()
        else:
            st.error(f"Failed to fetch student profiles: {response.status_code}")
            profiles = []
    except requests.RequestException as e:
        st.error(f"Error fetching student profiles: {e}")
        profiles = []

    if not profiles:
        st.info("No student profiles found.")
        return

    # Normalize student profiles into a DataFrame for filtering/analytics
    rows = []
    for p in profiles:
        user = p.get("user") or {}
        skills_assignments = p.get("skill_assignments") or []
        skills_list = [
            (a.get("skill") or {}).get("skill_name", "").strip()
            for a in skills_assignments
            if a.get("skill")
        ]
        tech_stack_raw = (p.get("tech_stack") or "").strip()
        tech_stack_tokens = [t.strip() for t in tech_stack_raw.split(",") if t.strip()]

        rows.append(
            {
                "profile_id": p.get("id"),
                "user_id": (user.get("id") if isinstance(user, dict) else None),
                "name": p.get("full_name") or "",
                "email": user.get("email") or "",
                "phone": p.get("phone") or "",
                "cgpa": float(p.get("cgpa") or 0.0),
                "semester": int(p.get("semester") or 1),
                "section": p.get("section") or "",
                "tech_stack_raw": tech_stack_raw,
                "tech_stack": ", ".join(tech_stack_tokens) if tech_stack_tokens else "",
                "resume_url": p.get("resume_url") or "",
                "github_url": p.get("github_url") or "",
                "linkedin_url": p.get("linkedin_url") or "",
                "portfolio_url": p.get("portfolio_url") or "",
                "career_goal": p.get("career_goal") or "",
                "achievements": p.get("achievements") or "",
                "projects": p.get("projects") or "",
                "skill_count": len([s for s in skills_list if s]),
                "skills": ", ".join([s for s in skills_list if s]),
                "updated_at": p.get("updated_at") or "",
                "_tech_stack_tokens": tech_stack_tokens,
                "_skills_list": [s for s in skills_list if s],
            }
        )

    df = pd.DataFrame(rows)

    # --- Filters / grouping ---
    st.write("### Filters & Groups")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        semesters = sorted([int(x) for x in df["semester"].dropna().unique().tolist()])
        selected_semesters = st.multiselect("Semester", options=semesters, default=semesters)
    with f2:
        sections = sorted([s for s in df["section"].dropna().unique().tolist() if str(s).strip()])
        selected_sections = st.multiselect("Class/Section", options=sections, default=sections)
    with f3:
        min_cgpa = float(df["cgpa"].min()) if not df.empty else 0.0
        max_cgpa = float(df["cgpa"].max()) if not df.empty else 10.0
        cgpa_range = st.slider("CGPA range", min_value=0.0, max_value=10.0, value=(min_cgpa, max_cgpa), step=0.1)
    with f4:
        tech_query = st.text_input("Tech stack contains", placeholder="e.g. Django / React / Java")

    # Optional skill filter
    all_skills = sorted({s for sub in df["_skills_list"].tolist() for s in (sub or [])})
    selected_skill = st.selectbox("Must have skill (optional)", options=["(Any)"] + all_skills, index=0)

    filtered = df.copy()
    if selected_semesters:
        filtered = filtered[filtered["semester"].isin(selected_semesters)]
    if selected_sections:
        filtered = filtered[filtered["section"].isin(selected_sections)]
    filtered = filtered[(filtered["cgpa"] >= cgpa_range[0]) & (filtered["cgpa"] <= cgpa_range[1])]
    if tech_query.strip():
        tq = tech_query.strip().lower()
        filtered = filtered[filtered["tech_stack_raw"].fillna("").str.lower().str.contains(tq)]
    if selected_skill != "(Any)":
        filtered = filtered[filtered["_skills_list"].apply(lambda xs: selected_skill in (xs or []))]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Students (filtered)", int(filtered.shape[0]))
    k2.metric("Avg CGPA", f"{(filtered['cgpa'].mean() if not filtered.empty else 0.0):.2f}")
    k3.metric("Avg skills / student", f"{(filtered['skill_count'].mean() if not filtered.empty else 0.0):.2f}")
    k4.metric("Unique tech stacks", int(filtered["tech_stack"].nunique()))

    # --- Analytics ---
    st.write("### Analytics")
    a1, a2 = st.columns(2)
    with a1:
        st.write("**Students by Semester**")
        if not filtered.empty:
            sem_counts = filtered.groupby("semester")["profile_id"].count().reset_index()
            sem_counts.columns = ["Semester", "Count"]
            fig1 = px.bar(sem_counts, x="Semester", y="Count", color="Semester", color_continuous_scale="Viridis", text="Count", labels={"Count": "Number of Students"})
            fig1.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            fig1.update_xaxes(dtick=1)
            fig1.update_yaxes(dtick=1)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data for selected filters.")

        st.write("**Students by Section**")
        if not filtered.empty:
            sec_counts = filtered.groupby("section")["profile_id"].count().sort_values(ascending=False).head(12).reset_index()
            sec_counts.columns = ["Section", "Count"]
            if sec_counts.empty:
                st.info("No section data available.")
            else:
                fig2 = px.pie(sec_counts, names="Section", values="Count", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig2.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig2, use_container_width=True)

    with a2:
        st.write("**CGPA Distribution (Filtered)**")
        if not filtered.empty:
            cgpa_counts = filtered["cgpa"].round(1).value_counts().sort_index().reset_index()
            cgpa_counts.columns = ["CGPA", "Count"]
            fig3 = px.bar(cgpa_counts, x="CGPA", y="Count", color="CGPA", color_continuous_scale="Plasma", labels={"Count": "Number of Students"})
            fig3.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            fig3.update_xaxes(range=[0, 10])
            fig3.update_yaxes(dtick=1)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data for selected filters.")

        st.write("**Top Skills (Filtered)**")
        if not filtered.empty:
            skill_counts = {}
            for xs in filtered["_skills_list"].tolist():
                for s in xs or []:
                    skill_counts[s] = skill_counts.get(s, 0) + 1
            if skill_counts:
                skill_df = (
                    pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
                    .sort_values("Count", ascending=True)
                    .tail(15)
                )
                fig4 = px.bar(skill_df, x="Count", y="Skill", orientation='h', color="Count", color_continuous_scale="Tealgrn", text="Count", labels={"Count": "Number of Students"})
                fig4.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                fig4.update_xaxes(dtick=1)
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No skills data available.")

    st.write("**Top Tech Stack Keywords (Filtered)**")
    if not filtered.empty:
        tech_counts = {}
        for tokens in filtered["_tech_stack_tokens"].tolist():
            for t in tokens or []:
                key = t.strip()
                if key:
                    tech_counts[key] = tech_counts.get(key, 0) + 1
        if tech_counts:
            tech_df = (
                pd.DataFrame(list(tech_counts.items()), columns=["Tech", "Count"])
                .sort_values("Count", ascending=True)
                .tail(15)
            )
            fig5 = px.bar(tech_df, x="Count", y="Tech", orientation='h', color="Count", color_continuous_scale="Sunset", text="Count", labels={"Count": "Number of Students", "Tech": "Technology"})
            fig5.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            fig5.update_xaxes(dtick=1)
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No tech stack data available.")

    # Student Data Table
    st.write("### Student Directory")
    if not filtered.empty:
        
        # CSV Export Functionality
        csv_data = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="?? Download Analytics Data as CSV",
            data=csv_data,
            file_name=f"tpo_student_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        display_cols = [
            "profile_id",
            "user_id",
            "name",
            "email",
            "phone",
            "semester",
            "section",
            "cgpa",
            "tech_stack",
            "skill_count",
            "skills",
            "achievements",
            "projects",
            "updated_at",
        ]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

        with st.expander("Quick view (selected student)", expanded=False):
            picked = st.selectbox(
                "Select student",
                options=filtered["profile_id"].tolist(),
                format_func=lambda pid: f"{int(pid)} - {filtered.loc[filtered['profile_id']==pid,'name'].values[0]}",
            )
            row = filtered.loc[filtered["profile_id"] == picked].iloc[0].to_dict()
            cL, cR = st.columns(2)
            with cL:
                st.write(f"**Name:** {row.get('name','')}")
                st.write(f"**Email:** {row.get('email','')}")
                st.write(f"**Semester/Section:** {row.get('semester','')} / {row.get('section','')}")
                st.write(f"**CGPA:** {row.get('cgpa','')}")
                st.write(f"**Tech Stack:** {row.get('tech_stack','') or '—'}")
                st.write(f"**Skills:** {row.get('skills','') or '—'}")
            with cR:
                if row.get("resume_url"):
                    st.link_button("Resume", row["resume_url"])
                if row.get("github_url"):
                    st.link_button("GitHub", row["github_url"])
                if row.get("linkedin_url"):
                    st.link_button("LinkedIn", row["linkedin_url"])
                if row.get("portfolio_url"):
                    st.link_button("Portfolio", row["portfolio_url"])
                st.write("**Achievements**")
                st.write(row.get("achievements") or "—")
                st.write("**Projects**")
                st.write(row.get("projects") or "—")

        # Delete Student Function
        st.write("### Delete Student")
        with st.form("delete_student_form", clear_on_submit=True):
            user_id_to_delete = st.number_input(
                "Enter User ID to delete",
                min_value=1,
                step=1,
                key="delete_user_id"
            )
            delete_submit = st.form_submit_button("Delete Student", type="primary")

            if delete_submit:
                try:
                    delete_response = requests.delete(
                        f"{API_URL}/api/v1/student-profiles/{user_id_to_delete}/",
                        headers=headers,
                        timeout=10,
                    )
                    if delete_response.status_code in (200, 204):
                        st.toast(f"Student with User ID {user_id_to_delete} deleted successfully!", icon="🗑️")
                        st.rerun()
                    else:
                        try:
                            error_data = delete_response.json()
                            error_message = (
                                error_data.get("detail")
                                or error_data.get("message")
                                or str(error_data)
                            )
                        except ValueError:
                            error_message = delete_response.text or "Unable to delete student."
                        st.error(f"Delete failed: {error_message}")
                except requests.RequestException as e:
                    st.error(f"Error deleting student: {e}")


def show_job_management_page() -> None:
    """TPO page to post and manage job postings."""
    token = st.session_state.token

    if not token:
        st.error("Authentication token not found. Please log in again.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.1)); 
                    padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;'>
            <h2 style='margin:0; font-family: "Outfit", sans-serif; color: #f8fafc;'>🏢 Job Management</h2>
            <p style='margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;'>Create, manage, and delete job postings for students.</p>
        </div>
    """, unsafe_allow_html=True)

    # Master Skill Database
    st.write("### 🛠️ Master Skill Database")
    with st.expander("Add New Skill to Global Database"):
        st.write("If a specific skill is missing from the global list, add it here so students can select it and you can require it for jobs.")
        with st.form("tpo_add_skill_form", clear_on_submit=True):
            new_skill_name = st.text_input("Skill Name (e.g. FastAPI, MongoDB)")
            new_skill_category = st.text_input("Category (e.g. Backend, Database) [Optional]")
            if st.form_submit_button("Add to Database"):
                if new_skill_name:
                    try:
                        res = requests.post(f"{API_URL}/api/v1/skills/", json={"skill_name": new_skill_name, "category": new_skill_category}, headers=headers, timeout=10)
                        if res.status_code in (200, 201):
                            st.toast(f"Skill '{new_skill_name}' added to global database!", icon="✅")
                            st.rerun()
                        else:
                            st.error(f"Failed to add skill. It might already exist.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Skill name is required.")

    # Fetch all global skills once for job assignment
    all_global_skills = []
    try:
        sk_res = requests.get(f"{API_URL}/api/v1/skills/", headers=headers, timeout=10)
        if sk_res.status_code == 200:
            all_global_skills = sk_res.json()
    except:
        pass

    # Form to post new job
    st.write("### Post a New Job")
    with st.form("post_job_form", clear_on_submit=True):
        job_title = st.text_input("Title", key="job_title")
        job_company = st.text_input("Company", key="job_company")
        job_description = st.text_area("Description", key="job_description", height=150)
        post_submit = st.form_submit_button("Post Job", type="primary")

        if post_submit:
            if not job_title or not job_description:
                st.error("Title and Description are required.")
            else:
                payload = {
                    "title": job_title,
                    "company": job_company,
                    "description": job_description,
                }
                try:
                    response = requests.post(
                        f"{API_URL}/api/v1/job-postings/",
                        json=payload,
                        headers=headers,
                        timeout=10,
                    )
                    if response.status_code in (200, 201):
                        st.toast("Job posted successfully!", icon="💼")
                        st.rerun()
                    else:
                        try:
                            error_data = response.json()
                            error_message = (
                                error_data.get("detail")
                                or error_data.get("message")
                                or str(error_data)
                            )
                        except ValueError:
                            error_message = response.text or "Unable to post job."
                        st.error(f"Failed to post job: {error_message}")
                except requests.RequestException as e:
                    st.error(f"Error posting job: {e}")

    # Display existing jobs
    st.write("### Existing Job Postings")
    try:
        response = requests.get(
            f"{API_URL}/api/v1/job-postings/",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                # Filter jobs posted by current TPO user
                tpo_jobs = [job for job in jobs if job.get("tpo_user", {}).get("id") == st.session_state.user_id]
                
                if tpo_jobs:
                    for job in tpo_jobs:
                        job_id = job.get("id")
                        title = job.get("title", "Untitled")
                        company = job.get("company", "")
                        description = job.get("description", "No description available.")
                        posted_on = job.get("posted_on", "")
                        required_skills = job.get("required_skills", [])

                        expander_title = f"**{title}**"
                        if company:
                            expander_title += f" - {company}"
                        expander_title += f" - Posted on {posted_on[:10] if posted_on else 'Unknown date'}"

                        with st.expander(expander_title):
                            if company:
                                st.write(f"**Company:** {company}")
                            st.write("**Description:**")
                            st.write(description)
                            
                            if required_skills:
                                st.write("**Required Skills:**")
                                for req_skill in required_skills:
                                    s_info = req_skill.get("skill", {})
                                    s_name = s_info.get("skill_name", "Unknown")
                                    r_level = req_skill.get("required_level", 0)
                                    req_id = req_skill.get("id")
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"- {s_name} (Level {r_level}/5)")
                                    with col2:
                                        if st.button("Remove", key=f"del_req_{req_id}", help="Remove this requirement"):
                                            try:
                                                requests.delete(f"{API_URL}/api/v1/required-skills/{req_id}/", headers=headers, timeout=10)
                                                st.rerun()
                                            except:
                                                pass
                            else:
                                st.write("**Required Skills:** None specified")
                            
                            st.write("---")
                            # Form to add a new requirement to this job
                            existing_req_ids = [rs.get("skill", {}).get("id") for rs in required_skills if rs.get("skill")]
                            avail_skills = [s for s in all_global_skills if s.get("id") not in existing_req_ids]
                            
                            if avail_skills:
                                with st.form(f"add_req_form_{job_id}", clear_on_submit=True):
                                    st.write("**Add Required Skill**")
                                    skill_opts = {f"{s.get('skill_name')}": s.get("id") for s in avail_skills}
                                    sel_sk = st.selectbox("Select Skill", options=list(skill_opts.keys()), key=f"sel_{job_id}")
                                    sel_lvl = st.slider("Required Level", 1, 5, 3, key=f"lvl_{job_id}")
                                    if st.form_submit_button("Add Requirement"):
                                        if sel_sk:
                                            try:
                                                req_response = requests.post(
                                                    f"{API_URL}/api/v1/required-skills/", 
                                                    json={"job_posting_id": job_id, "skill_id": skill_opts[sel_sk], "required_level": sel_lvl},
                                                    headers=headers, timeout=10
                                                )
                                                if req_response.status_code in (200, 201):
                                                    st.toast("Requirement added!")
                                                    st.rerun()
                                                else:
                                                    st.error(f"Failed to add: {req_response.text}")
                                            except Exception as e:
                                                st.error(f"Error: {e}")
                                        else:
                                            st.error("Please select a skill first.")
                            else:
                                st.info("All global skills have been assigned to this job.")
                            
                            # Delete button for each job
                            if st.button(f"Delete Job", key=f"delete_job_{job_id}"):
                                try:
                                    delete_response = requests.delete(
                                        f"{API_URL}/api/v1/job-postings/{job_id}/",
                                        headers=headers,
                                        timeout=10,
                                    )
                                    if delete_response.status_code in (200, 204):
                                        st.toast(f"Job '{title}' deleted successfully!", icon="🗑️")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete job.")
                                except requests.RequestException as e:
                                    st.error(f"Error deleting job: {e}")
                else:
                    st.info("You haven't posted any jobs yet.")
            else:
                st.info("No job postings available.")
        else:
            st.error(f"Failed to fetch job postings: {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error fetching job postings: {e}")

# Removed on_nav_change


def show_main_app() -> None:

    st.title(f"Welcome, {st.session_state.user_email or 'User'}")

    if st.sidebar.button("Logout"):

        reset_session_state()

        st.rerun()



    if st.session_state.is_tpo:
        pg_dash = st.Page(show_tpo_dashboard_page, title="TPO Dashboard", icon="📊")
        pg_job = st.Page(show_job_management_page, title="Job Management", icon="💼")
        pg = st.navigation([pg_dash, pg_job])
    else:
        pg_profile = st.Page(show_profile_page, title="My Profile", icon="👤")
        pg_roadmap = st.Page(show_roadmap_page, title="AI Roadmap", icon="🗺️")
        pg_board = st.Page(show_job_board_page, title="Job Board", icon="🏢")
        pg = st.navigation([pg_profile, pg_roadmap, pg_board])

    # Run the selected page
    pg.run()






def main() -> None:

    init_session_state()

    if not st.session_state.logged_in:
        st.sidebar.title("AcroConnect")
        st.sidebar.caption("Single portal (UI) + Django API backend")

        public_page = st.sidebar.radio(
            "Explore",
            options=["Home", "Login / Register", "About"],
            index=0 if st.session_state.public_page == "home" else (1 if st.session_state.public_page in ("login", "register") else 2),
        )

        if public_page == "Home":
            st.session_state.public_page = "home"
            show_public_landing()
        elif public_page == "About":
            st.session_state.public_page = "about"
            show_about_page()
        else:
            st.session_state.public_page = "login"
            show_login_page()

    else:

        show_main_app()





if __name__ == "__main__":

    main()
