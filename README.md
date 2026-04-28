# 🏦 FinAI: Advanced Financial Document Intelligence Platform

## 🚀 Overview
FinAI is a production-ready, end-to-end **Agentic RAG (Retrieval-Augmented Generation)** platform. It allows financial analysts to upload unstructured reports and perform high-precision semantic queries. 

The system is built with a **Two-Stage Retrieval Architecture** to solve the accuracy challenges of complex financial data.

---

## 📸 Intelligence Dashboard (New UI Demo)

| Feature | Screenshot |
| :--- | :--- |
| **Main AI Dashboard** | ![Dashboard](screenshots/Dashboard.png) |
| **Registration & RBAC** | ![Register](screenshots/register_success.png) |
| **Document Indexing** | ![Index](screenshots/Sucess%20index%20document.png) |
| **Semantic Search Result** | ![Search](screenshots/Semantic%20search%20result.png) |

---

## 🧠 AI Architecture
Unlike basic vector search systems, this project implements a **Two-Stage Retrieval Architecture**:

1.  **Stage 1: Vector Retrieval (Bi-Encoder)**: Uses **FAISS** (Facebook AI Similarity Search) and `all-MiniLM-L6-v2` embeddings to perform a broad search across document chunks to find the top 20 candidates.

2.  **Stage 2: Semantic Reranking (Cross-Encoder)**: Uses **FlashRank** (`ms-marco-MiniLM-L-12-v2`) to re-score candidates. This ensures contextually and financially relevant results.

---

## 🛠️ Tech Stack
- **Backend**: FastAPI (Asynchronous, High Performance)
- **Frontend**: Streamlit (Intelligence Dashboard)
- **Vector Engine**: FAISS (High-speed Similarity Search)
- **Reranker**: FlashRank (State-of-the-art Cross-Encoder)
- **Database**: SQLite & SQLAlchemy (Metadata & RBAC Management)
- **Security**: JWT Authentication & **Role-Based Access Control (RBAC)**
- **DevOps**: Docker, Docker-Compose

---

## 🛡️ Security & Roles
Strict security is enforced via FastAPI dependencies to ensure data integrity:
- **Admin**: Full system access.
- **Financial Analyst**: Permission to upload, index, and analyze documents.
- **Auditor / Client**: Read-only access to search results.

---

## 🐳 Deployment (DevOps)

### Using Docker
docker build -t finance-ai-app .
docker-compose up
code
Code
### Local Development
1. Install Dependencies
pip install -r requirements.txt
2. Start Backend (FastAPI)
python main.py
3. Start Frontend (Streamlit)
streamlit run ui.py
code
Code
---

## 📍 API Endpoints Mapping

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| POST | /auth/register | Register new user | Public |
| POST | /auth/login | Get JWT Access Token | Public |
| POST | /documents/upload | Upload & Index Doc | Admin/Analyst |
| GET | /documents | List all metadata | All Auth |
| POST | /rag/search | Semantic Search + Rerank | All Auth |

---

## 🛠️ Performance Fixes Implemented
- **Bcrypt Conflict**: Switched to PBKDF2 for stable Windows/Linux cross-compatibility.
- **Numpy Serialization**: Handled custom float32 casting for standard JSON responses.
- **Vector ID Handling**: Integrated **UUID4** for robust indexing in local vector storage.

---

### **Selection Note for Recruiters:**
This project demonstrates the ability to build and package AI models into **secure, scalable, and user-friendly products**. It bridges the gap between AI Research, Software Engineering, and Cloud DevOps.
