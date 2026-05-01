import requests
import streamlit as st

def fetch_repo_files(owner, repo):

    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {
        "Authorization": f"token {token}"
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return []

    files_data = res.json()
    all_files = []

    for file in files_data:

        if file["type"] == "file" and file["name"].endswith(".py"):

            file_url = file["download_url"]

            content_res = requests.get(file_url)

            if content_res.status_code == 200:

                all_files.append({
                    "name": file["name"],
                    "content": content_res.text
                })

    return all_files