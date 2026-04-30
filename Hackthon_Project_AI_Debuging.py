import streamlit as st
import pandas as pd
import re
import time
from auth import ensure_admin

from analytics import get_login_stats
from mailer import send_alert
from pdf_report import generate_pdf
from chat_ui import render_chat

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
# ---------------- AUTO REFRESH ----------------
st.query_params["refresh"] = str(time.time())

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- ULTRA STYLE ----------------
st.markdown("""
<style>

/* BACKGROUND */
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

/* 🔥 PREMIUM TOP BAR */
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
<span>🚀 DebugAI Pro | AI SaaS Debugging Platform | Real-Time Monitoring | Built by Ritesh</span>
</div>
<div class="space"></div>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if not st.session_state.login:
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
    m.train(r"D:\AI_Debbuing_system\data\error_logs_dataset.csv")
    return m

model = load_model()

def extract_errors(text):
    return list(set(re.findall(r".*Error.*|.*Exception.*", text)))

# =====================================================
# 🏠 DASHBOARD (FULL FILLED)
# =====================================================
# =====================================================
# 🏠 DASHBOARD (STARTUP LANDING PAGE)
# =====================================================
if page == "🏠 Dashboard":

    users = get_all_users()
    activity = get_activity()

    total_users = len(users)
    banned = sum(1 for u in users if u[1] == 1)
    deleted = sum(1 for u in users if u[2] == 1)

    # 🔥 HERO SECTION
    st.markdown("""
    <div class='card' style='padding:40px'>
        <h1 style='font-size:40px'>🚀 DebugAI Pro</h1>
        <p style='font-size:18px'>
        AI-powered debugging SaaS platform to analyze logs, monitor users,
        and solve errors in real-time like a professional system.
        </p>
        <hr>
        <b>⚡ Fast | 🤖 Smart | 📊 Real-time | 🔐 Secure</b>
    </div>
    """, unsafe_allow_html=True)

    # 🔥 STATS
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='card'>👥 Total Users<br><h2>{total_users}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>🚫 Banned Users<br><h2>{banned}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>🗑 Deleted Users<br><h2>{deleted}</h2></div>", unsafe_allow_html=True)

    # 🔥 FEATURES SECTION
    st.subheader("🔥 Platform Features")

    f1, f2, f3 = st.columns(3)

    f1.markdown("""
    <div class='card'>
    🤖 AI Log Analyzer<br><br>
    Detect errors automatically and get instant fixes.
    </div>
    """, unsafe_allow_html=True)

    f2.markdown("""
    <div class='card'>
    💬 Smart AI Assistant<br><br>
    Ask questions and get step-by-step solutions.
    </div>
    """, unsafe_allow_html=True)

    f3.markdown("""
    <div class='card'>
    👑 Admin Control System<br><br>
    Ban, delete, restore users like Instagram.
    </div>
    """, unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)

    f4.markdown("""
    <div class='card'>
    📊 Real-Time Analytics<br><br>
    Track user activity and login trends live.
    </div>
    """, unsafe_allow_html=True)

    f5.markdown("""
    <div class='card'>
    📄 PDF Reports<br><br>
    Export debugging reports instantly.
    </div>
    """, unsafe_allow_html=True)

    f6.markdown("""
    <div class='card'>
    🚨 Email Alerts<br><br>
    Get alerts when critical errors occur.
    </div>
    """, unsafe_allow_html=True)

    # 🔥 ANALYTICS PREVIEW
    st.subheader("📈 Live System Analytics")
    st.line_chart(get_login_stats())

    # 🔥 RECENT ACTIVITY
    st.subheader("⚡ Recent Activity Feed")
    df = pd.DataFrame(activity, columns=["User","Action","Time"])
    st.dataframe(df.tail(10))

    # 🔥 FINAL CTA SECTION
    st.markdown("""
    <div class='card' style='padding:30px'>
    <h3>🚀 Ready to Debug Smarter?</h3>
    Use the Log Analyzer or AI Assistant to start solving issues now.
    </div>
    """, unsafe_allow_html=True)
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
# 💬 AI ASSISTANT
# =====================================================
elif page == "💬 AI Assistant":

    q = st.text_input("Ask issue")

    if st.button("Ask"):
        ans = rule_fix(q)[1]
        render_chat(q, ans)
        log_activity(st.session_state.user, "CHAT_USED")

# =====================================================
# 📊 ANALYTICS
# =====================================================
elif page == "📊 Analytics":

    st.subheader("📈 Login Stats")
    st.line_chart(get_login_stats())

    st.subheader("📊 Activity Logs")
    st.dataframe(pd.DataFrame(get_activity(),
                              columns=["User","Action","Time"]))

# =====================================================
# 👑 ADMIN PANEL
# =====================================================
elif page == "👑 Admin Panel":

    if st.session_state.user != "admin":
        st.error("Access Denied")
        st.stop()

    st.subheader("👑 Admin Control Center")

    users = pd.DataFrame(get_all_users(),
                         columns=["User","Banned","Deleted","Created"])

    st.dataframe(users)

    u = st.text_input("Target User")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Ban"):
            ban_user(u)

    with col2:
        if st.button("Unban"):
            unban_user(u)

    with col3:
        if st.button("Delete"):
            delete_user(u)

    with col4:
        if st.button("Restore"):
            restore_user(u)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
<span>🚀 DebugAI Pro | SaaS AI Platform | Built by Ritesh</span>
</div>
""", unsafe_allow_html=True)