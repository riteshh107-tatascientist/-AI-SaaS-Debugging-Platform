import requests
import streamlit as st
import base64

def fetch_repo_files(owner, repo):

    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {
        "Authorization": f"token {token}"
    }

    files_data = []

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return []

        files = res.json()

        for f in files:
            if f["type"] == "file":

                file_url = f["download_url"]
                file_res = requests.get(file_url, timeout=10)

                if file_res.status_code == 200:
                    files_data.append({
                        "name": f["name"],
                        "content": file_res.text[:2000]   # limit for AI
                    })

        return files_data

    except Exception as e:
        return [{"error": str(e)}]