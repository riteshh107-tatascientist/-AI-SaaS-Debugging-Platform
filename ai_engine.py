import requests
import streamlit as st

def ai_fix_code(error, code=""):

    api_key = st.secrets["GEMINI_API_KEY"]

    prompt = f"""
You are a senior software engineer.

Error:
{error}

Code:
{code}

Give:
1. Explanation
2. Step-by-step fix
3. Fixed code
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        res = requests.post(url, json=payload, timeout=10)

        if res.status_code != 200:
            return f"API Error: {res.text}"

        data = res.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"AI Error: {str(e)}"