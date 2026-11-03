"""CodeTrack: a LeetCode-style UI backed by the Team 28 PostgreSQL schema."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from psycopg2 import Error

import db

st.set_page_config(page_title="CodeTrack", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """<style>
    /* Contrast-safe light application surface */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background: #f8fafc !important;
        color: #0f172a !important;
    }
    .main .block-container { max-width: 1380px; padding-top: 2.2rem; }
    .main h1, .main h2, .main h3, .main p, .main label,
    .main [data-testid="stMarkdownContainer"], .main [data-testid="stCaptionContainer"] {
        color: #0f172a !important;
    }
    .main [data-testid="stCaptionContainer"] { color: #475569 !important; }

    /* Forms and tables remain readable in every browser theme */
    .main input, .main textarea, .main [data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }
    .main input::placeholder, .main textarea::placeholder { color: #64748b !important; }
    [data-testid="stDataFrame"], [data-testid="stDataFrame"] * { color: #0f172a !important; }

    /* Dark navigation with targeted, readable text - no broad wildcard rule */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1e293b 100%) !important;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stCaption {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] label { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] button {
        background: #334155 !important; color: #f8fafc !important;
        border-color: #475569 !important;
    }

    /* Cards and actions */
    [data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
        padding: 16px; box-shadow: 0 3px 10px rgba(15,23,42,.05);
    }
    .stButton > button[kind="primary"] {
        background: #f59e0b !important; border: 1px solid #f59e0b !important;
        color: #111827 !important; font-weight: 750;
    }
    .stButton > button[kind="primary"]:hover {
        background: #fbbf24 !important; border-color: #fbbf24 !important;
    }
    div[data-testid="stExpander"] {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(15,23,42,.035);
    }
    </style>""",
    unsafe_allow_html=True,
)


def safe(call, fallback=None):
    try:
        return call()
    except Error as error:
        st.error("Database error: " + str(error))
        return fallback


def data_table(rows: list[dict], hide: list[str] | None = None):
    if not rows:
        st.info("Nothing to show yet.")
        return
    frame = pd.DataFrame(rows)
    if hide:
        frame = frame.drop(columns=[name for name in hide if name in frame], errors="ignore")
    st.dataframe(frame, use_container_width=True, hide_index=True)


def login_page():
    left, middle, right = st.columns([1, 1.3, 1])
    with middle:
        st.markdown("# ⚡ CodeTrack")
        st.caption("Practice. Compete. Improve.")
        sign_in, sign_up = st.tabs(["Sign in", "Create account"])
        with sign_in:
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                sent = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if sent:
                user = safe(lambda: db.authenticate(username, password))
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Incorrect username/password, or the account is inactive.")
        with sign_up:
            with st.form("signup", clear_on_submit=True):
                first, last = st.columns(2)
                first_name = first.text_input("First name")
                last_name = last.text_input("Last name")
                new_username = st.text_input("Username")
                email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                created = st.form_submit_button("Create secure account", use_container_width=True)
            if created:
                if not all([first_name.strip(), last_name.strip(), new_username.strip(), email.strip(), new_password]):
                    st.error("Complete every field.")
                elif len(new_password) < 6:
                    st.error("Use at least 6 characters for the password.")
                else:
                    try:
                        db.create_account(new_username, email, new_password, first_name, last_name)
                        st.success("Account created. You can sign in now.")
                    except Error as error:
                        st.error("Could not create account: " + str(error))
        st.divider()
        st.caption("Database-backed demo for Team 28's LeetCode-Style Practice Management System.")


def header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def home(user: dict):
    header("Welcome back, " + user["first_name"] + " 👋", "Your coding workspace at a glance")
    stats = safe(lambda: db.dashboard_stats(user["username"]), {}) or {}
    a, b, c, d = st.columns(4)
    a.metric("Problems solved", stats.get("solved", 0))
    b.metric("Attempts", stats.get("attempted", 0))
    c.metric("Submissions", stats.get("submissions", 0))
    d.metric("Practice score", stats.get("score", 0))
    st.subheader("Recent submissions")
    data_table(safe(lambda: db.recent_submissions(user["username"]), []) or [])
    st.subheader("Continue practicing")
    problems = safe(lambda: db.problem_list(user["username"], state="Unsolved"), []) or []
    data_table(problems[:5], ["author"])


def problems_page(user: dict):
    header("Problemset", "Find the right challenge using topic, difficulty, status, and title filters.")
    all_topics = safe(db.topics, []) or []
    c1, c2, c3, c4 = st.columns([2, 1.3, 1.3, 1.5])
    search = c1.text_input("Search", placeholder="Search problems")
    selected_difficulties = c2.multiselect("Difficulty", ["Easy", "Medium", "Hard"])
    topic_names = {"All topics": None}
    topic_names.update({item["topic_name"]: item["topic_id"] for item in all_topics})
    topic_name = c3.selectbox("Topic", list(topic_names))
    state = c4.selectbox("Status", ["All", "Solved", "Attempted", "Unsolved"])
    rows = safe(lambda: db.problem_list(user["username"], search, selected_difficulties, topic_names[topic_name], state), []) or []
    st.caption(str(len(rows)) + " problem(s) found")
    data_table(rows)
    if rows:
        choices = {"#" + str(item["problem_id"]) + " - " + item["title"]: item["problem_id"] for item in rows}
        selected = st.selectbox("Open a problem", list(choices))
        if st.button("Go to Solve", type="primary"):
            st.session_state.selected_problem = choices[selected]
            st.session_state.page = "Solve"
            st.rerun()


def solve_page(user: dict):
    header("Solve", "Read the problem, write a solution, and record a submission.")
    all_problems = safe(lambda: db.problem_list(user["username"]), []) or []
    if not all_problems:
        st.info("No problems exist yet. Ask an admin to create one in Admin Studio.")
        return
    by_id = {item["problem_id"]: item for item in all_problems}
    preferred = st.session_state.get("selected_problem", next(iter(by_id)))
    if preferred not in by_id:
        preferred = next(iter(by_id))
    problem_id = st.selectbox("Choose a problem", list(by_id), index=list(by_id).index(preferred),
                              format_func=lambda value: "#" + str(value) + " - " + by_id[value]["title"])
    problem = safe(lambda: db.problem_detail(problem_id))
    if not problem:
        return
    st.markdown("## " + problem["title"] + " · " + problem["difficulty_name"])
    st.caption("Topics: " + problem["topics"] + " · Created by " + problem["username"])
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown(problem["description"])
        if problem["constraints"]:
            st.markdown("#### Constraints")
            for item in problem["constraints"]:
                st.write("- " + item["constraint_description"])
        if problem["test_cases"]:
            st.markdown("#### Examples")
            for item in problem["test_cases"]:
                if item["is_sample"]:
                    st.code("Input: " + item["input_data"] + "\nOutput: " + item["expected_output"], language="text")
    with right:
        st.markdown("#### Code editor")
        language_rows = safe(db.languages, []) or []
        if not language_rows:
            st.warning("No programming languages have been seeded yet.")
            return
        language_by_name = {(item["language_name"] + " " + (item["version"] or "")).strip(): item["language_id"] for item in language_rows}
        language = st.selectbox("Language", list(language_by_name))
        code = st.text_area("Your solution", height=300, placeholder="# Write your solution here")
        st.caption("Demo judge: the schema stores submissions but has no sandboxed compiler. Select the outcome to simulate a judge result.")
        verdict = st.selectbox("Demo verdict", ["Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"])
        if st.button("Submit solution", type="primary", use_container_width=True):
            if not code.strip():
                st.error("Write code before submitting.")
            else:
                submission_id = safe(lambda: db.submit_solution(user["username"], problem_id, language_by_name[language], code, verdict))
                if submission_id:
                    st.success("Submission #" + str(submission_id) + ": " + verdict)


def contests_page(user: dict):
    header("Contests", "Register for contests and see the included problems.")
    rows = safe(lambda: db.contests(user["username"]), []) or []
    if not rows:
        st.info("No contests have been published yet.")
        return
    for contest in rows:
        title = contest["contest_name"] + " · " + contest["contest_status"] + " · " + str(contest["problem_count"]) + " problem(s)"
        with st.expander(title):
            st.write(contest["description"] or "No description provided.")
            st.caption(str(contest["start_time"]) + " → " + str(contest["end_time"]) + " · " + contest["scoring_rule"])
            if contest["registered"]:
                st.success("Registered · " + str(contest["completion_status"]))
            elif st.button("Register", key="contest-" + str(contest["contest_id"])):
                if safe(lambda: db.register_for_contest(user["username"], contest["contest_id"]), False):
                    st.success("Registered successfully. Refresh the page to see the updated status.")
                else:
                    st.info("You are already registered.")
            data_table(safe(lambda: db.contest_problems(contest["contest_id"]), []) or [])


def leaderboard_page():
    header("Global Leaderboard", "Ranked using solved-problem and contest scores.")
    rows = safe(db.leaderboard, []) or []
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    data_table(rows, ["username"])


def discuss_page(user: dict):
    header("Discuss", "Ask questions, share approaches, and comment on a problem.")
    problem_rows = safe(lambda: db.problem_list(user["username"]), []) or []
    if not problem_rows:
        st.info("Create a problem first.")
        return
    titles = {"#" + str(p["problem_id"]) + " - " + p["title"]: p["problem_id"] for p in problem_rows}
    with st.expander("Start a discussion"):
        with st.form("discussion", clear_on_submit=True):
            problem_title = st.selectbox("Problem", list(titles))
            title = st.text_input("Discussion title")
            content = st.text_area("Post")
            submitted = st.form_submit_button("Publish")
        if submitted:
            if not title.strip() or not content.strip():
                st.error("Title and post are required.")
            else:
                discussion_id = safe(lambda: db.create_discussion(user["username"], titles[problem_title], title, content))
                if discussion_id:
                    st.success("Discussion #" + str(discussion_id) + " published.")
    for discussion in safe(db.discussions, []) or []:
        label = discussion["discussion_title"] + " · " + discussion["problem_title"] + " · " + str(discussion["comments"]) + " comment(s)"
        with st.expander(label):
            st.caption("Posted by " + discussion["username"])
            st.write(discussion["content"])
            for comment in safe(lambda: db.comments(discussion["discussion_id"]), []) or []:
                st.write("**" + comment["username"] + "**: " + comment["comment_text"])
            with st.form("comment-" + str(discussion["discussion_id"]), clear_on_submit=True):
                message = st.text_input("Add a comment", key="text-" + str(discussion["discussion_id"]))
                replied = st.form_submit_button("Reply")
            if replied and message.strip():
                safe(lambda: db.create_comment(user["username"], discussion["discussion_id"], message))
                st.rerun()


def profile_page(user: dict):
    profile = safe(lambda: db.get_profile(user["username"]))
    if not profile:
        return
    header(profile["first_name"] + " " + profile["last_name"], "@" + profile["username"])
    stats = safe(lambda: db.dashboard_stats(user["username"]), {}) or {}
    one, two, three = st.columns(3)
    one.metric("Solved", stats.get("solved", 0))
    two.metric("Submissions", stats.get("submissions", 0))
    three.metric("Score", stats.get("score", 0))
    st.write(profile["profile_bio"] or "No bio yet.")
    st.subheader("Solved by difficulty")
    breakdown = safe(lambda: db.difficulty_breakdown(user["username"]), []) or []
    if breakdown:
        st.bar_chart(pd.DataFrame(breakdown).set_index("difficulty_name"))
    st.subheader("Badges")
    data_table(safe(lambda: db.badges_for(user["username"]), []) or [])
    st.subheader("Edit profile")
    language_rows = safe(db.languages, []) or []
    options = {"No preference": None}
    options.update({item["language_name"]: item["language_id"] for item in language_rows})
    with st.form("profile"):
        email = st.text_input("Email", value=profile["email"])
        bio = st.text_area("Bio", value=profile["profile_bio"] or "")
        preferred = st.selectbox("Preferred language", list(options))
        saved = st.form_submit_button("Save profile")
    if saved:
        safe(lambda: db.update_profile(user["username"], email, bio, options[preferred]))
        st.success("Profile updated.")


def admin_page(user: dict):
    header("Admin Studio", "Create, update, or delete problems.")
    if not safe(lambda: db.user_is_admin(user["username"]), False):
        st.warning("Admin Studio is available to users with the Admin or Problem Setter role.")
        return
    
    tab_create, tab_manage = st.tabs(["Create New Problem", "Update / Delete Problem"])
    
    with tab_create:
        topic_rows = safe(db.topics, []) or []
        topic_by_name = {item["topic_name"]: item["topic_id"] for item in topic_rows}
        with st.form("create-problem", clear_on_submit=True):
            title = st.text_input("Title")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            selected_topics = st.multiselect("Topics", list(topic_by_name))
            description = st.text_area("Problem statement", height=180)
            constraints = st.text_area("Constraints (one per line)", placeholder="1 <= n <= 10^5\nValues are integers")
            st.markdown("**Sample test case 1**")
            inp, out = st.columns(2)
            sample_input = inp.text_area("Input", key="sample-in")
            sample_output = out.text_area("Expected output", key="sample-out")
            created = st.form_submit_button("Publish problem", type="primary")
        if created:
            if not title.strip() or not description.strip():
                st.error("Title and statement are required.")
            else:
                new_id = safe(lambda: db.create_problem(title, description, difficulty, user["username"],
                    [topic_by_name[name] for name in selected_topics], constraints.splitlines(), [(sample_input, sample_output)]))
                if new_id:
                    st.success("Problem #" + str(new_id) + " published.")

    with tab_manage:
        st.subheader("Select a problem to manage")
        problems = safe(lambda: db.problem_list(user["username"]), []) or []
        if not problems:
            st.info("No problems exist yet.")
            return
        
        by_id = {p["problem_id"]: p for p in problems}
        selected_id = st.selectbox("Problem", list(by_id), format_func=lambda x: f"#{x} - {by_id[x]['title']}")
        
        detail = safe(lambda: db.problem_detail(selected_id))
        if detail:
            with st.form("update-form"):
                new_title = st.text_input("Title", value=detail["title"])
                new_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(detail["difficulty_name"]))
                new_description = st.text_area("Description", value=detail["description"], height=200)
                
                submitted = st.form_submit_button("Update Problem", type="primary")
                
            if submitted:
                affected = safe(lambda: db.update_problem(selected_id, new_title, new_description, new_difficulty))
                if affected:
                    st.success(f"Problem #{selected_id} updated successfully.")
                    
            st.divider()
            st.warning("Deletion is permanent.")
            confirm_delete = st.checkbox(f"Confirm deletion of Problem #{selected_id}")
            if st.button("Delete Problem", type="secondary", disabled=not confirm_delete):
                affected = safe(lambda: db.delete_problem(selected_id))
                if affected:
                    st.success(f"Problem #{selected_id} deleted.")
                    st.rerun()


def app_shell(user: dict):
    with st.sidebar:
        st.markdown("# ⚡ CodeTrack")
        st.caption("Signed in as **" + user["username"] + "**")
        pages = ["Home", "Problems", "Solve", "Contests", "Leaderboard", "Discuss", "Profile", "Admin Studio"]
        default = st.session_state.get("page", "Home")
        page = st.radio("Navigate", pages, index=pages.index(default) if default in pages else 0)
        st.session_state.page = page
        st.divider()
        if st.button("Test database connection", use_container_width=True):
            version = safe(db.test_connection)
            if version:
                st.success("Connected")
                st.caption(version.split(",")[0])
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    routes = {
        "Home": home, "Problems": problems_page, "Solve": solve_page, "Contests": contests_page,
        "Leaderboard": lambda _: leaderboard_page(), "Discuss": discuss_page, "Profile": profile_page,
        "Admin Studio": admin_page,
    }
    routes[st.session_state.page](user)


if st.session_state.get("user"):
    app_shell(st.session_state.user)
else:
    login_page()
