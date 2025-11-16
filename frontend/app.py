import streamlit as st

import pandas as pd
import requests



# API base URL

API_URL = "http://127.0.0.1:8000"



DEFAULT_SESSION_STATE = {

    "logged_in": False,

    "token": None,

    "is_tpo": False,

    "user_email": None,

    "user_id": None,

    "nav_option": None,

}





def init_session_state() -> None:

    for key, default in DEFAULT_SESSION_STATE.items():

        st.session_state.setdefault(key, default)





def reset_session_state() -> None:

    for key, default in DEFAULT_SESSION_STATE.items():

        st.session_state[key] = default





def show_login_page() -> None:

    st.title("Welcome to AcroConnect")

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

                        data=payload,

                        timeout=10,

                    )

                    if response.status_code != 200:

                        # If login fails, show the error

                        try:

                            error_data = response.json()

                            error_message = (

                                error_data.get("detail")

                                or error_data.get("message")

                                or str(error_data)

                            )

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
                        # Fallback to token response data if /me/ fails
                        st.session_state.user_email = data.get("email") or data.get("username") or (login_identifier if "@" in login_identifier else None)
                        st.session_state.user_id = data.get("user_id") or data.get("id")
                        st.session_state.is_tpo = bool(data.get("is_tpo", False))

                    st.success("Login successful!")

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(f"Login failed: {exc}")



    with register_tab:

        st.subheader("Register as a New Student")

        with st.form("register_form", clear_on_submit=True):

            name = st.text_input("Full Name")

            username = st.text_input("Username", key="register_username")

            reg_email = st.text_input("Email", key="register_email")

            phone = st.text_input("Phone Number")

            reg_password = st.text_input("Password", type="password", key="register_password")

            register_submit = st.form_submit_button("Create Account")



        if register_submit:

            if not all([name, username, reg_email, phone, reg_password]):

                st.error("All fields are required for registration.")

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

                            st.success(f"Registration successful! You can now log in.")

                            st.info(f"Registered with Username: **{created_username}** | Email: **{created_email}**")

                        except ValueError:

                            st.success("Registration successful! You can now log in.")

                    else:

                        try:

                            error_data = response.json()

                            error_message = (

                                error_data.get("detail")

                                or error_data.get("message")

                                or str(error_data)

                            )

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

    st.subheader("My Profile")

    # Profile Update Form
    with st.form("profile_form", clear_on_submit=False):
        name = st.text_input("Full Name", value=profile_data.get("full_name", ""))
        phone = st.text_input("Phone", value=profile_data.get("phone", ""))

        cgpa_value = profile_data.get("cgpa")
        if cgpa_value is None:
            cgpa_value = 0.0
        else:
            try:
                cgpa_value = float(cgpa_value)
            except (ValueError, TypeError):
                cgpa_value = 0.0

        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=cgpa_value, step=0.01)
        career_goal = st.text_area("Career Goal", value=profile_data.get("career_goal", ""))
        st.caption("💡 Describe your career aspirations (this helps generate better AI roadmaps)")
        update_button = st.form_submit_button("Update Profile")

    if update_button:
        update_payload = {
            "full_name": name,
            "phone": phone,
            "cgpa": cgpa,
            "career_goal": career_goal,
        }
        try:
            update_response = requests.patch(
                f"{API_URL}/api/v1/student-profiles/{profile_id}/",
                json=update_payload,
                headers=headers,
                timeout=10,
            )
            if update_response.status_code in (200, 204):
                st.success("Profile updated successfully!")
                st.rerun()
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
                st.error(f"Update failed: {error_message}")
        except requests.RequestException as e:
            st.error(f"Error updating profile: {e}")

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
                            st.success(f"Removed {skill_name}")
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
        if skills_response.status_code == 200:
            all_skills = skills_response.json()
            existing_skill_ids = [a.get("skill", {}).get("id") for a in skill_assignments if a.get("skill")]
            available_skills = [s for s in all_skills if s.get("id") not in existing_skill_ids]
            
            if available_skills:
                with st.form("add_skill_form", clear_on_submit=True):
                    skill_options = {f"{s.get('skill_name')} ({s.get('category', 'N/A')})": s.get("id") for s in available_skills}
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
                            st.success("Skill added successfully!")
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
        else:
            st.error(f"Failed to fetch roadmaps: {response.status_code}")
            user_roadmaps = []
    except requests.RequestException as e:
        st.error(f"Error fetching roadmaps: {e}")
        user_roadmaps = []

    st.subheader("AI Roadmap")

    # Display existing roadmaps
    if user_roadmaps:
        st.write("### Your Generated Roadmaps")
        for roadmap in user_roadmaps:
            generated_on = roadmap.get("generated_on", "")
            roadmap_text = roadmap.get("roadmap_text", "")
            with st.expander(f"Roadmap generated on {generated_on[:10] if generated_on else 'Unknown date'}"):
                st.markdown(roadmap_text)
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

    st.subheader("Job Board")

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

    st.subheader("TPO Dashboard")

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

    # Prepare data for analytics
    all_skills = []
    skill_counts = {}
    total_skills = 0

    for profile in profiles:
        skill_assignments = profile.get("skill_assignments", [])
        for assignment in skill_assignments:
            skill = assignment.get("skill", {})
            skill_name = skill.get("skill_name", "")
            if skill_name:
                all_skills.append(skill_name)
                skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
                total_skills += 1

    # Analytics Charts
    st.write("### Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Skill Distribution**")
        if skill_counts:
            skill_df = pd.DataFrame(
                list(skill_counts.items()),
                columns=["Skill", "Count"]
            ).sort_values("Count", ascending=False)
            st.bar_chart(skill_df.set_index("Skill"))
        else:
            st.info("No skills data available.")

    with col2:
        st.write("**Average Skills per Student**")
        if profiles:
            avg_skills = total_skills / len(profiles) if len(profiles) > 0 else 0
            st.metric("Average Skills", f"{avg_skills:.2f}")
            st.metric("Total Students", len(profiles))
        else:
            st.info("No student data available.")

    # Student Data Table
    st.write("### All Students")
    
    # Prepare DataFrame
    student_data = []
    for profile in profiles:
        user = profile.get("user", {})
        skill_assignments = profile.get("skill_assignments", [])
        skills_list = [
            assignment.get("skill", {}).get("skill_name", "")
            for assignment in skill_assignments
            if assignment.get("skill")
        ]
        
        student_data.append({
            "ID": profile.get("id"),
            "User ID": user.get("id"),
            "Full Name": profile.get("full_name", ""),
            "Email": user.get("email", ""),
            "Phone": profile.get("phone", ""),
            "CGPA": profile.get("cgpa", 0.0),
            "Skills": ", ".join(skills_list) if skills_list else "None",
            "Skill Count": len(skills_list),
        })

    if student_data:
        df = pd.DataFrame(student_data)
        st.dataframe(df, use_container_width=True)

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
                        st.success(f"Student with User ID {user_id_to_delete} deleted successfully!")
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

    st.subheader("Job Management")

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
                        st.success("Job posted successfully!")
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
                                skill_names = [
                                    skill.get("skill", {}).get("skill_name", "Unknown")
                                    for skill in required_skills
                                    if skill.get("skill")
                                ]
                                st.write(", ".join(skill_names) if skill_names else "None specified")
                            
                            # Delete button for each job
                            if st.button(f"Delete Job", key=f"delete_job_{job_id}"):
                                try:
                                    delete_response = requests.delete(
                                        f"{API_URL}/api/v1/job-postings/{job_id}/",
                                        headers=headers,
                                        timeout=10,
                                    )
                                    if delete_response.status_code in (200, 204):
                                        st.success(f"Job '{title}' deleted successfully!")
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



def show_main_app() -> None:

    st.title(f"Welcome, {st.session_state.user_email or 'User'}")

    if st.sidebar.button("Logout"):

        reset_session_state()

        st.rerun()



    if st.session_state.is_tpo:

        nav_options = ["TPO Dashboard", "Job Management"]

    else:

        nav_options = ["My Profile", "AI Roadmap", "Job Board"]



    selected_option = st.sidebar.radio(

        "Navigate to:",

        nav_options,

        key="nav_option",

    )



    # Route to appropriate page based on selection
    if st.session_state.is_tpo:
        if selected_option == "TPO Dashboard":
            show_tpo_dashboard_page()
        elif selected_option == "Job Management":
            show_job_management_page()
    else:
        if selected_option == "My Profile":
            show_profile_page()
        elif selected_option == "AI Roadmap":
            show_roadmap_page()
        elif selected_option == "Job Board":
            show_job_board_page()





def main() -> None:

    init_session_state()

    if not st.session_state.logged_in:

        show_login_page()

    else:

        show_main_app()





if __name__ == "__main__":

    main()
