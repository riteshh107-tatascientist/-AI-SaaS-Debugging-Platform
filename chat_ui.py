import streamlit as st

def render_chat(user_msg, ai_msg):
    st.markdown(f"""
    <div style='text-align:right; padding:10px;'>
        <span style='background:#4f46e5;color:white;padding:10px;border-radius:10px'>
        {user_msg}
        </span>
    </div>

    <div style='text-align:left; padding:10px;'>
        <span style='background:#10b981;color:white;padding:10px;border-radius:10px'>
        {ai_msg}
        </span>
    </div>
    """, unsafe_allow_html=True)