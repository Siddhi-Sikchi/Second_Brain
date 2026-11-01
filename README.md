# Second Brain: AI-Powered Personal Knowledge Management System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite%20%7C%20TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20(WAL%20Mode)-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Pytest](https://img.shields.io/badge/Tests-15%2F15%20Passed%20(100%25)-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)
[![Jira](https://img.shields.io/badge/Agile%20Scrum-Jira%20(SCRUM)-0052CC.svg?logo=jira&logoColor=white)](https://vit-team-sxjbt0vb.atlassian.net)

---

## 1. Project Overview

Students and knowledge workers collect vast amounts of information across PDFs, research papers, images, lecture notes, and online articles. This information quickly becomes scattered and difficult to organize, retrieve, synthesize, and revise.

**Second Brain** is an intelligent, full-stack personal knowledge management system. It provides a centralized local-first workspace where users can upload study materials, write structured notes, perform hybrid semantic searches, ask natural-language questions grounded on their own documents (RAG), explore conceptual linkages through an interactive knowledge graph, generate self-assessment quizzes, and retain information using spaced repetition.

---

## 2. Key Modules & Features

### 👤 Module 1: User Management & Authentication
- Secure registration and login with `bcrypt` password hashing and signed JSON Web Tokens (`HS256`).
- Profile management (name, avatar, bio) and secure in-app password changes.
- Route guards and strict multi-tenant data isolation by `user_id`.

### 📄 Module 2: Multi-Format Document Processing & Notes
- Upload PDFs, text files, markdown, code, and images (up to 25MB per file).
- Native PDF text extraction (`pypdf`) with page, word, and character metrics.
- Image parser with OCR fallback for scanned diagrams and handwritten text.
- Markdown note-taking workspace with note pinning, categorization, and editing.

### 🧠 Module 3: AI Summarization & Smart Tagging
- Automatic executive summaries and key bullet points generated during file ingestion.
- Keyword density analysis and domain taxonomy classification (AI, Computer Science, Math, Business, Humanities).
- Extensible dual-engine: Google Gemini 1.5 Flash cloud API integration with seamless offline local extractive fallback.

### 🔍 Module 4: Hybrid Search & Retrieval-Augmented Generation (RAG)
- 500-character overlapping sliding window text chunking.
- In-database L2-normalized TF-IDF vector embeddings with cosine similarity matching.
- Natural-language Q&A assistant providing answers strictly grounded on personal documents with clickable source citations.
- Explicit detection when the knowledge base lacks sufficient information to prevent hallucinations.

### 🕸️ Module 5: Interactive Knowledge Graph
- 2D Canvas force-directed graph connecting notes, documents, and topical tags.
- Evidence-based edges reflecting shared tags and high semantic similarity ($>0.22$).
- Interactive zoom, pan, hover tooltips, and click-to-inspect drawer.

### 🎯 Module 6: AI Quiz Generator & Assessment
- Automatically generates multiple-choice (MCQ) self-assessment tests from study materials.
- Timed test mode with instant scoring and detailed answer explanations.
- Automatic learning loop: questions missed during quizzes are auto-enrolled into the spaced revision queue.

### 🔄 Module 7: Spaced Repetition (SuperMemo SM-2) & Analytics
- Implements the SuperMemo SM-2 spaced repetition curve (Again, Hard, Good, Easy ratings).
- Real-time Analytics Dashboard with Recharts category charts, word counts, storage metrics, and active study streak counter.

---

## 3. Technology Stack

- **Backend:** Python 3.11+ / 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Security:** PyJWT, Bcrypt, OAuth2 Password Bearer
- **NLP & Search:** PyPDF, Pillow, Scikit/Numpy Sparse Vector Cosine Similarity, Google Gemini API
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Recharts
- **Database:** SQLite 3 with Write-Ahead Logging (WAL) and enforced Foreign Keys
- **Testing:** Pytest, Pytest-Asyncio, HTTPX TestClient

---

## 4. Quick Start Guide

### Step 1: Clone and Set Up Python Virtual Environment
```powershell
# From the project root
python -m venv venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt
```

### Step 2: Seed Demo Data
Populates the database with demo student user, sample documents, notes, quizzes, and revision queue:
```powershell
python scripts\seed_sample_data.py
```

### Step 3: Install Frontend Dependencies
```powershell
cd frontend
npm.cmd install
cd ..
```

### Step 4: Run the Application
Open two terminal windows:

- **Backend Terminal:**
  ```powershell
  .\scripts\start-backend.bat
  ```
  API runs at `http://127.0.0.1:8000` (Docs at `/docs`)

- **Frontend Terminal:**
  ```powershell
  .\scripts\start-frontend.bat
  ```
  Web UI runs at `http://localhost:5173`

### Demo Credentials
- **Email:** `student@university.edu`
- **Password:** `SecurePassword123!`

---

## 5. Automated Test Suite

Run all automated pytest suites:
```powershell
.\scripts\run-tests.bat
```
**Results:** **15/15 tests passed** across Authentication, Document Ingestion, RAG Search, Quiz Generation, and Real-Time Analytics.

---

## 6. Jira Scrum Management

- **Jira Project URL:** [https://vit-team-sxjbt0vb.atlassian.net](https://vit-team-sxjbt0vb.atlassian.net)
- **Project Key:** `SCRUM` | **Board ID:** `1`
- **Total Backlog:** 18 User Stories across 9 Epics (68 Story Points)
- **Sprint Schedule:** Four 2-week sprints (Sprint 1: 18 SP, Sprint 2: 18 SP, Sprint 3: 18 SP, Sprint 4: 14 SP)
- **Traceability:** Detailed in `docs/jira-implementation-report.md`.
