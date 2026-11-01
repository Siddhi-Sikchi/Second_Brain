# System Architecture & Technical Specification

## 1. Executive Summary
The **AI-Powered Personal Knowledge Management System (Second Brain)** is a full-stack, local-first web application designed to help students, researchers, and professionals ingest, organize, search, summarize, and retain multi-format knowledge assets. 

The architecture follows a decoupled Client-Server architecture utilizing a **FastAPI (Python 3.11+)** backend, a **React 18 + Vite + TypeScript + Tailwind CSS** frontend, and an embedded **SQLite database with Write-Ahead Logging (WAL)** for seamless, zero-configuration local persistence that easily scales to PostgreSQL.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 USER BROWSER                                      |
|                                                                                   |
|  [ React 18 + Vite SPA | TypeScript | Tailwind CSS | Recharts | Canvas Force Graph ]  |
+-----------------------------------------------------------------------------------+
                                         │
                               HTTP / REST APIs (JWT Bearer Token)
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND SERVICE                              |
|                                                                                   |
|  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────────┐  |
|  │  Authentication   │  │ Document Ingest   │  │ AI Search & RAG Q&A Engine    │  |
|  │  (Bcrypt + JWT)   │  │ (PDF / Image OCR) │  │ (TF-IDF + Vector Cosine Sim)  │  |
|  └───────────────────┘  └───────────────────┘  └───────────────────────────────┘  |
|  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────────┐  |
|  │  Knowledge Graph  │  │ AI Quiz Generator │  │ Spaced Repetition (SM-2)      │  |
|  │  (Evidence Links) │  │ (MCQs & Grading)  │  │ & Learning Analytics Feed     │  |
|  └───────────────────┘  └───────────────────┘  └───────────────────────────────┘  |
+-----------------------------------------------------------------------------------+
                      │                                       │
                      ▼                                       ▼
+────────────────────────────────────────+   +──────────────────────────────────────+
|          SQLITE LOCAL DATABASE         |   |           AI INFERENCE ENGINE        |
|                                        |   |                                      |
|  • WAL Mode Enabled                    |   |  • Dual-Engine Design:               |
|  • 11 Normalized Tables                |   |    - Google Gemini 1.5 Flash (Online)|
|  • Foreign Key Constraints Enforced    |   |    - Deterministic NLP (Offline Local|
|  • In-DB Dense TF-IDF Embeddings       |   |      Extractive & Heuristics)        |
+────────────────────────────────────────+   +──────────────────────────────────────+
```

---

## 3. Core Architectural Modules

### Module 1: User Management & Authentication
- **Security Protocols:** Passwords hashed with `bcrypt` (12 rounds of work factor).
- **Session Tokens:** Stateless RFC 7519 JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`) and configurable expiration window (1440 minutes default).
- **Access Control:** FastAPI dependency injection (`get_current_user`) verifies token signature, checks user active status, and isolates all queries by `user_id`.

### Module 2: Multi-Format Document Processing
- **Format Ingestion:** Supports `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`, `.md`, `.json`, `.csv`, `.py`.
- **PDF Parser:** Native page-by-page extraction with `pypdf`, tracking character counts, page counts, and word counts.
- **Image Fallback:** Image metadata parser (format, dimensions, color mode) with automated fallback to `pytesseract` OCR where system binaries are present.
- **Storage Safety:** Unique UUID file renaming prevents filename collision and directory traversal exploits. 25MB file-size guardrails enforced during stream buffering.

### Module 3: Hybrid Search & Retrieval-Augmented Generation (RAG)
- **Chunking Pipeline:** Overlapping sliding window (500-character target, 100-character overlap) preserves context across chunk boundaries.
- **Vector Representations:** L2-normalized sparse Term-Frequency (TF) vectors stored directly in the `chunks` table as JSON, enabling zero-install, zero-C-extension vector similarity search on any platform.
- **Hybrid Scoring:**
  $$\text{Final Score} = (\text{Cosine Similarity} \times 0.7) + \min(\text{Keyword Match Boost}, 0.3)$$
- **Grounded Q&A Generation:** Top-k passages are assembled into a synthesized answer. Citations explicitly state document title, chunk page index, relevance score, and source excerpt. If top relevance $< 0.12$, the system reports insufficient evidence.

### Module 4: Knowledge Graph Engine
- **Node Taxonomy:** Document nodes, Study Note nodes, and Tag/Concept nodes.
- **Evidence-Based Edges:**
  1. *Taxonomy Edges:* Links documents and notes to their respective user-assigned or smart auto-tags.
  2. *Semantic Edges:* Evaluates cross-document cosine similarity and forms an edge when similarity threshold exceeds $0.22$.
- **Visualization:** High-performance HTML5 Canvas force layout with dynamic pan, zoom, hover tooltips, and click-to-inspect drawer.

### Module 5: AI Quiz Generator & Assessment
- **Question Generation:** Analyzes high-density factual declarative statements from user documents or notes. Formulates MCQs with plausible distractors selected from surrounding text.
- **Evaluation:** Real-time scoring with instant answer breakdown, correct answer citations, and explanations.
- **Automated Feedback Loop:** Questions missed by the student are automatically converted into flashcards and inserted into the Spaced Repetition queue.

### Module 6: Spaced Repetition (SuperMemo SM-2)
- Implements the validated SuperMemo SM-2 spaced repetition algorithm:
  - Rating options: `Again` (interval resets to 1 day, ease factor penalized), `Hard` (1.2x interval), `Good` (standard ease factor multiplier), `Easy` (ease factor bonus, 1.3x multiplier).
- Next review date calculated dynamically and queried daily.

### Module 7: Learning Analytics Engine
- Computes 100% authentic database metrics:
  - Total documents, notes, words, quizzes taken, average score, storage bytes.
  - Category distribution visual charts (Recharts).
  - Learning streak tracking active study days over the past 30 days.
  - Recent activity event log.
