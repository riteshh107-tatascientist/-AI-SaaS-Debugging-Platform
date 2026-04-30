import requests
import streamlit as st

def fetch_repo(owner, repo):

    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {
        "Authorization": f"token {token}"
    }

    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        return res.json()
    else:
        return []