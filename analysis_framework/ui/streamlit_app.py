import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:9000")

st.set_page_config(page_title="3-Agent Skill Governance Lab", page_icon=":lock:")
st.title(":lock: 3-Agent Skill Governance Lab")

uploaded = st.file_uploader("Upload skill files (multiple allowed)", accept_multiple_files=True)

if st.button("Analyze"):
    files = {}
    for f in uploaded:
        files[f.name] = f.getvalue().decode("utf-8", errors="ignore")
    resp = requests.post(f"{API_URL}/analyze", json={"files": files})
    st.json(resp.json())

st.markdown("---")
st.markdown("Use the API endpoints to integrate in CI/CD pipelines: POST /analyze")
