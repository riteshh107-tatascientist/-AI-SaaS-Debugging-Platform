import streamlit as st
import pandas as pd
import re
import time
from ai_engine import ai_fix_code
from github_ai import fetch_repo_files

from auth import ensure_admin

from analytics import get_login_stats
from mailer import send_alert
from pdf_report import generate_pdf
from chat_ui import render_chat
from datetime import datetime

def get_greeting():
    hour = datetime.now().hour

    if hour < 12:
        return "🌅 Good Morning"
    elif hour < 18:
        return "☀️ Good Afternoon"
    else:
        return "🌙 Good Evening"

from auth import (
    create_table, signup, login,
    get_all_users, ban_user, unban_user,
    delete_user, restore_user,
    get_activity, log_activity
)

from model import DebugModel, rule_fix
from utils import format_out

# ---------------- INIT ----------------
st.set_page_config(page_title="DebugAI Pro", layout="wide")
create_table()
ensure_admin()
# ---------------- SESSION INIT ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- AUTO REFRESH ----------------
st.query_params["refresh"] = str(time.time())

# ---------------- SESSION ----------------
if "last_deleted" not in st.session_state:
    st.session_state.last_deleted = None

if "delete_time" not in st.session_state:
    st.session_state.delete_time = None

# ---------------- ULTRA STYLE ----------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg,#0f172a,#1e3a8a,#9333ea,#020617);
    background-size: 400% 400%;
    animation: bg 10s infinite;
    color: white;
}
@keyframes bg {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

/* TOP BAR */
.topbar {
    width: 100%;
    height: 70px;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 12px;
    margin-bottom: 20px;
}
.topbar span {
    white-space: nowrap;
    padding-left: 100%;
    font-size: 26px;
    font-weight: 900;
    background: linear-gradient(90deg,#00f5ff,#a855f7,#ff006e,#00f5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: moveText 12s linear infinite;
}
@keyframes moveText {
    0% {transform: translateX(100%);}
    100% {transform: translateX(-100%);}
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    margin: 10px 0;
    text-align:center;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(45deg,#00f5ff,#a855f7);
    color: black;
    font-weight: bold;
    width: 100%;
    border-radius: 10px;
}

/* FOOTER */
.footer {
    width: 100%;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    margin-top: 40px;
    padding: 12px 0;
    text-align: center;
    overflow: hidden;
}
.footer span {
    display: inline-block;
    padding-left: 100%;
    white-space: nowrap;
    font-size: 16px;
    font-weight: 700;
    background: linear-gradient(90deg,#00f5ff,#a855f7,#ff006e,#00f5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: moveText 15s linear infinite;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="topbar">
<span>🏆 TIT SRIJAN 2026 Hackathon Project | DebugAI Pro 🚀 | 24H Innovation → Real-Time AI Debugging System ⚡</span>
</div>
<div class="space"></div>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if not st.session_state.get("login", False):
    st.sidebar.title("🔐 Login System")

    mode = st.sidebar.selectbox("Select", ["Login", "Signup"])

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if mode == "Signup":
        if st.button("Create Account"):
            if signup(u, p):
                st.success("Account Created 🚀")
            else:
                st.error("User already exists")

    if mode == "Login":
        if st.button("Login"):
            res = login(u, p)

            if res == True:
                st.session_state.login = True
                st.session_state.user = u
                st.rerun()

            elif res == "BANNED":
                st.error("🚫 You are banned")

            elif res == "DELETED":
                st.error("❌ Your account is deleted")

            else:
                st.error("Wrong credentials")

    st.stop()

st.markdown(f"👤 Logged in as: **{st.session_state.user}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.session_state.user = None
    st.rerun()

admin_user = st.secrets["ADMIN_USERNAME"]

greet = get_greeting()

if st.session_state.user == admin_user:
    st.success(f"👑 {greet},Boss {st.session_state.user}! Full system access granted 🚀")
else:
    st.info(f"👤 {greet}, {st.session_state.user}! Ready to debug smarter? 🚀")
# ---------------- NAV ----------------
page = st.sidebar.radio("Navigation", [
    "🏠 Dashboard",
    "📄 Log Analyzer",
    "💬 AI Assistant",
    "📊 Analytics",
    "👑 Admin Panel"
])

# ---------------- MODEL ----------------
@st.cache_resource
def load_model():
    m = DebugModel()
    m.train("data/error_logs_dataset.csv")
    return m

model = load_model()

def extract_errors(text):
    return list(set(re.findall(r".*Error.*|.*Exception.*", text)))

# =====================================================
# 🏠 DASHBOARD
# =====================================================
if page == "🏠 Dashboard":

    users = get_all_users()
    activity = get_activity()

    total_users = len(users)
    banned = sum(1 for u in users if u[1] == 1)
    deleted = sum(1 for u in users if u[2] == 1)

    st.markdown("""
    <div class='card' style='padding:40px'>
        <h1>🚀 DebugAI Pro</h1>
        <p>AI debugging SaaS platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='card'>Users<br><h2>{total_users}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>Banned<br><h2>{banned}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>Deleted<br><h2>{deleted}</h2></div>", unsafe_allow_html=True)

    st.line_chart(get_login_stats())

    st.dataframe(pd.DataFrame(activity, columns=["User","Action","Time"]))

# =====================================================
# 📄 LOG ANALYZER
# =====================================================
elif page == "📄 Log Analyzer":

    uploaded = st.file_uploader("Upload log file")
    manual = st.text_area("Paste logs")

    log = ""
    if uploaded:
        log = uploaded.read().decode()
    if manual:
        log += manual

    if st.button("Analyze"):
        errors = extract_errors(log)

        for e in errors:
            cat, sol = rule_fix(e)

            send_alert("DebugAI Alert", f"{st.session_state.user}: {e}")
            log_activity(st.session_state.user, "LOG_ANALYZED")

            st.markdown(f"""
            <div class="card">
            ❌ {e}<br>
            📌 {cat}<br>
            🛠 {sol}
            </div>
            """, unsafe_allow_html=True)


# =====================================================
# 💬 AI ASSISTANT (UPGRADED)
# =====================================================
elif page == "💬 AI Assistant":

    st.title("🧠 Senior Developer AI System")

    mode = st.selectbox("Mode", [
        "Error Fix",
        "Code Fix",
        "GitHub Repo Scan"
    ])

    # ---------------- ERROR ----------------
    if mode == "Error Fix":

        error = st.text_area("Paste Error")

        if st.button("Analyze"):
            result = ai_fix_code(error)

            st.markdown("### 🧠 AI OUTPUT")
            st.write(result)

    # ---------------- CODE FIX ----------------
    elif mode == "Code Fix":

        code = st.text_area("Paste Code")
        error = st.text_area("Error")

        if st.button("Auto Fix"):
            result = ai_fix_code(error, code)

            st.markdown("### 🧾 FIXED RESULT")
            st.write(result)

    # ---------------- GITHUB ----------------
    elif mode == "GitHub Repo Scan":

        owner = st.text_input("GitHub Username")
        repo = st.text_input("Repo Name")

        if st.button("Scan Repo"):

            files = fetch_repo_files(owner, repo)

            if not files:
                st.error("❌ Repo not found or API error")

            else:
                st.success("✅ Repo Loaded Successfully")

                for f in files:

                    st.subheader(f"📂 {f['name']}")

                    # AI ANALYSIS
                    ai_result = ai_fix_code(
                        "Analyze this code and find issues",
                        f["content"]
                    )

                    st.markdown("### 🧠 AI Analysis")
                    st.write(ai_result)
# =====================================================
# 📊 ANALYTICS
# =====================================================
elif page == "📊 Analytics":

    st.line_chart(get_login_stats())

    st.dataframe(pd.DataFrame(get_activity(),
                              columns=["User","Action","Time"]))
# =====================================================
# 👑 ADMIN PANEL (FIXED + STABLE)
# =====================================================
elif page == "👑 Admin Panel":

    admin_user = st.secrets["ADMIN_USERNAME"]

    if st.session_state.user != admin_user:
        st.error("🚫 Access Denied")
        st.stop()

    st.subheader("👑 Admin Control Center")

    users = pd.DataFrame(get_all_users(),
                         columns=["User","Banned","Deleted","Created"])

    st.dataframe(users)

    u = st.text_input("Target User")

    col1, col2, col3, col4 = st.columns(4)

    # ---------------- BAN ----------------
    with col1:
        if st.button("Ban"):
            if u:
                ban_user(u)
                st.toast(f"✅ {u} banned")
            else:
                st.warning("⚠ Enter username")

    # ---------------- UNBAN ----------------
    with col2:
        if st.button("Unban"):
            if u:
                unban_user(u)
                st.toast(f"✅ {u} unbanned")
            else:
                st.warning("⚠ Enter username")

    # ---------------- DELETE ----------------
    with col3:
        confirm = st.checkbox("⚠ Confirm Delete", key="delete_confirm")

        if st.button("Delete"):
            if not confirm:
                st.warning("⚠ Please confirm delete")
            elif u:
                delete_user(u)

                # save for undo
                st.session_state.last_deleted = u
                st.session_state.delete_time = time.time()

                st.toast(f"🗑 {u} deleted (Undo available)")
            else:
                st.warning("⚠ Enter username")

    # ---------------- RESTORE ----------------
    with col4:
        if st.button("Restore"):
            if u:
                restore_user(u)
                st.toast(f"♻ {u} restored")
            else:
                st.warning("⚠ Enter username")

    # =====================================================
    # 🔁 UNDO DELETE SYSTEM (SAFE)
    # =====================================================
    if st.session_state.get("last_deleted"):

        elapsed = time.time() - st.session_state.get("delete_time", 0)

        if elapsed < 5:
            st.warning(f"⏳ Undo delete for {st.session_state.last_deleted}")

            if st.button("♻ Undo Delete"):
                restore_user(st.session_state.last_deleted)
                st.toast("♻ Restored successfully")

                st.session_state.last_deleted = None
                st.session_state.delete_time = None
                st.rerun()

        else:
            # auto clear after 5 sec
            st.session_state.last_deleted = None
            st.session_state.delete_time = None

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
<span>🚀 DebugAI Pro |Real-Time AI Debugging System | Built by Ritesh Kumar Singh & Krishna Chandra Gupta</span>
</div>
""", unsafe_allow_html=True)