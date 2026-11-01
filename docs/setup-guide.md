# Local Setup & Installation Guide

This guide explains how to install, configure, run, and test the **AI-Powered Personal Knowledge Management System (Second Brain)** on Windows, macOS, or Linux.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **Python:** 3.10+ (Tested on Python 3.13.14)
- **Node.js:** v18.0+ (Tested on Node v22.16.0)
- **Package Manager:** npm (v10+)
- **Disk Space:** ~500 MB for dependencies and virtual environments

---

## 2. Directory Structure

```
second-brain/
├── backend/                  # FastAPI Application
│   ├── app/                  # Application Source Code
│   │   ├── models/           # SQLAlchemy Data Models
│   │   ├── routers/          # REST API Endpoints
│   │   ├── schemas/          # Pydantic v2 Request/Response Schemas
│   │   ├── services/         # Text Extraction, RAG, Graph, Quizzes
│   │   ├── utils/            # JWT & Bcrypt Security Helpers
│   │   ├── config.py         # App Configuration
│   │   ├── database.py       # SQLite Engine & Session Configuration
│   │   └── main.py           # FastAPI Application Entrypoint
│   ├── tests/                # Automated Pytest Test Suite
│   ├── uploads/              # Local Storage for Uploaded Documents
│   ├── .env.example          # Environment Variable Template
│   └── requirements.txt      # Python Dependencies
├── frontend/                 # React 18 + Vite Frontend
│   ├── src/                  # Components, Pages, Context, Services
│   ├── package.json          # Node Dependencies & Scripts
│   ├── tailwind.config.js    # Tailwind CSS Styling Configuration
│   └── vite.config.ts        # Vite Server & API Reverse Proxy
├── docs/                     # Architectural & Academic Documentation
├── scripts/                  # Automated Startup & Seed Scripts
│   ├── start-backend.bat     # Windows Backend Launcher
│   ├── start-frontend.bat    # Windows Frontend Launcher
│   ├── run-tests.bat         # Automated Test Suite Launcher
│   └── seed_sample_data.py   # Database Initializer with Demo Data
└── README.md                 # Project Overview
```

---

## 3. Quick Start (Windows)

We provide pre-configured batch scripts for instant startup:

### Step 1: Initialize Database & Seed Demo Data
Open a terminal in the project root:
```powershell
# Create Python virtual environment if not already present
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install backend dependencies
pip install -r backend\requirements.txt

# Seed sample documents, notes, quizzes, and demo student user
python scripts\seed_sample_data.py
```

### Step 2: Install Frontend Dependencies
```powershell
cd frontend
npm.cmd install
cd ..
```

### Step 3: Run the Application
Open two separate terminal windows or double-click the scripts:

- **Terminal 1 (Backend):**
  ```powershell
  .\scripts\start-backend.bat
  ```
  The API will be live at: `http://127.0.0.1:8000`  
  Interactive Swagger UI documentation: `http://127.0.0.1:8000/docs`

- **Terminal 2 (Frontend):**
  ```powershell
  .\scripts\start-frontend.bat
  ```
  The web UI will be live at: `http://localhost:5173`

---

## 4. Default Demo Credentials

You can use the built-in "Fill Student Demo Account" button on the login screen, or enter:
- **Email:** `student@university.edu`
- **Password:** `SecurePassword123!`

---

## 5. Configuration (.env)

The backend configuration is managed via `backend/.env`. A template is provided in `backend/.env.example`:

| Environment Variable | Default Value | Description |
|----------------------|---------------|-------------|
| `APP_NAME` | `Second Brain AI` | Application title |
| `DATABASE_URL` | `sqlite:///./second_brain.db` | Database connection string |
| `SECRET_KEY` | *(Random 32-char key)* | Secret key for JWT HMAC signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token validity duration (24 hours) |
| `UPLOAD_DIR` | `./uploads` | Folder for storing uploaded PDFs/images |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum single file upload limit |
| `GEMINI_API_KEY` | *(Optional)* | Google Gemini API key for cloud LLM inference |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |

> **Note on AI Functionality:**  
> If `GEMINI_API_KEY` is not provided, Second Brain automatically operates in **Offline Deterministic Mode**, utilizing built-in extractive textrank summarization, heuristic MCQ quiz generation, and TF-IDF vector cosine similarity. No external API keys or cloud dependencies are required to achieve full functionality.

---

## 6. Running Automated Tests

Run the comprehensive pytest suite:
```powershell
.\scripts\run-tests.bat
```
Or directly via pytest:
```powershell
cd backend
..\venv\Scripts\python.exe -m pytest tests -v
```

All 15 test suites verify:
- User registration, duplicate checks, login, and profile modification
- Document upload, size limits, and format rejection
- Note creation, editing, and auto-tagging
- Semantic vector search and RAG Q&A grounding
- Quiz generation, assessment grading, and Spaced Repetition queue creation
- Real-time Analytics Dashboard calculations
