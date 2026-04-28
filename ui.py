import streamlit as st
import requests
import pandas as pd

# Configuration
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="FinAI - Document Intelligence", layout="wide")

# --- SESSION STATE FOR AUTH ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None

# --- SIDEBAR: AUTHENTICATION ---
with st.sidebar:
    st.title("🔐 Access Control")
    if not st.session_state.token:
        auth_choice = st.radio("Choose Action", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if auth_choice == "Register":
            role = st.selectbox("Role", ["Admin", "Financial Analyst", "Auditor", "Client"])
            if st.button("Register"):
                resp = requests.post(f"{BASE_URL}/auth/register", params={"username": username, "password": password, "role": role})
                if resp.status_code == 200: st.success("Registered! Please Login.")
                else: st.error("Registration failed.")
        
        else:
            if st.button("Login"):
                resp = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
                if resp.status_code == 200:
                    st.session_state.token = resp.json()["access_token"]
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    else:
        st.write(f"Logged in as: **{username if 'username' in locals() else 'User'}**")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

# --- MAIN UI ---
st.title("🏦 Financial Document Intelligence")
st.markdown("---")

if not st.session_state.token:
    st.warning("Please login from the sidebar to access the system.")
else:
    tab1, tab2 = st.tabs(["📄 Document Management", "🔍 Semantic Search"])

    # TAB 1: UPLOAD
    with tab1:
        st.header("Upload Financial Documents")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Document Title")
            company = st.text_input("Company Name")
        with col2:
            doc_type = st.selectbox("Type", ["report", "invoice", "contract"])
            uploaded_file = st.file_uploader("Choose a text file", type=['txt'])

        if st.button("Index Document"):
            if uploaded_file and title and company:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
                data = {"title": title, "company": company, "doc_type": doc_type}
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                
                with st.spinner("Processing AI Embeddings..."):
                    resp = requests.post(f"{BASE_URL}/documents/upload", data=data, files=files, headers=headers)
                    if resp.status_code == 200:
                        st.success(f"Successfully indexed: {title}")
                    else:
                        st.error(f"Error: {resp.json().get('detail')}")
            else:
                st.warning("Please fill all fields.")

    # TAB 2: SEARCH
    with tab2:
        st.header("AI-Powered Semantic Search")
        query = st.text_input("Enter your financial query (e.g., 'What are the liquidity risks?')")
        
        if st.button("Analyze Documents"):
            if query:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                with st.spinner("Searching & Reranking..."):
                    resp = requests.post(f"{BASE_URL}/rag/search", params={"query": query}, headers=headers)
                    
                    if resp.status_code == 200:
                        results = resp.json()["top_5_results"]
                        if not results:
                            st.info("No matching context found.")
                        else:
                            st.subheader("Top AI Insights")
                            for idx, res in enumerate(results):
                                with st.expander(f"Result {idx+1} - Relevance Score: {res['score']:.4f}"):
                                    st.write(f"**Context:** {res['text']}")
                                    st.caption(f"Source: {res['meta']['title']} | Doc ID: {res['meta']['doc_id']}")
                    else:
                        st.error("Search failed. Check your permissions.")