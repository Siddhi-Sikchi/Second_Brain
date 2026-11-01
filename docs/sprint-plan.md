# Agile Scrum Sprint Plan & Execution Roadmap

This document outlines the four 2-week sprints established in Jira project **`SCRUM`** on board **1**.

---

## Sprint 1: Project Foundation, Core Architecture & User Management
- **Duration:** Weeks 1–2
- **Sprint Goal:** Establish project architecture, database models, secure authentication, and user profile management.
- **Sprint State:** Planned / Delivered
- **Story Points:** 18 SP

### Included Backlog Items:
1. `SCRUM-8`: **User Registration** (3 Story Points)
   - Email format validation, duplicate address prevention, password hashing with bcrypt, initial account creation.
2. `SCRUM-9`: **User Login** (3 Story Points)
   - Secure credential verification, JWT token issuance, session maintenance, masked input.
3. `SCRUM-10`: **User Profile Management** (3 Story Points)
   - Profile information viewing, display name and bio editing, avatar management.
4. `SCRUM-11`: **User Logout** (1 Story Point)
   - Explicit session termination and secure token invalidation.
5. `SCRUM-18`: **Backend Architecture & Database Schema Initialization** (3 Story Points)
   - FastAPI structure, SQLAlchemy ORM models, SQLite WAL configuration, error handlers.
6. `SCRUM-19`: **Frontend Shell, Theme & Responsive Navigation** (3 Story Points)
   - React 18, Vite, TypeScript, Tailwind layout, collapsible sidebar, route guards.
7. `SCRUM-20`: **Password Reset & Account Security Settings** (2 Story Points)
   - Secure password update verifying old password and enforcing strength rules.

---

## Sprint 2: Document Ingestion, Note Taking & Document Processing
- **Duration:** Weeks 3–4
- **Sprint Goal:** Document ingestion, note taking, text extraction, OCR, and document processing.
- **Sprint State:** Planned / Delivered
- **Story Points:** 18 SP

### Included Backlog Items:
1. `SCRUM-12`: **Upload PDF and Documents** (5 Story Points)
   - Multi-format file uploader (PDF, text, code), 25MB file size limit, UUID file storage.
2. `SCRUM-13`: **Upload Images and Create Notes** (5 Story Points)
   - Image ingestion, rich text note creation, edit/delete capabilities, note pinning.
3. `SCRUM-21`: **Document Text Extraction and OCR Engine** (5 Story Points)
   - PyPDF page parser, image metadata/OCR fallback, word and character counts.
4. `SCRUM-22`: **Document Metadata Management and Knowledge Library View** (3 Story Points)
   - Library view, sorting, category/type filtering, file inspection modal, secure deletion.

---

## Sprint 3: AI Summarization, Smart Tagging, RAG Search & Knowledge Graph
- **Duration:** Weeks 5–6
- **Sprint Goal:** AI summarization, auto-tagging, RAG semantic search, and interactive knowledge graph.
- **Sprint State:** Planned / Delivered
- **Story Points:** 18 SP

### Included Backlog Items:
1. `SCRUM-23`: **AI-Powered Document Summarization** (5 Story Points)
   - Executive summaries, bullet point takeaways, dual-engine (Gemini + extractive fallback).
2. `SCRUM-24`: **Automated Smart Tagging & Taxonomy Engine** (3 Story Points)
   - Keyword density analysis, domain classification (AI, CS, Math, Science, Business), tag management.
3. `SCRUM-25`: **Hybrid Keyword & Semantic RAG Search Engine** (5 Story Points)
   - 500-char sliding chunking, TF-IDF vector storage, cosine similarity, grounded Q&A with citations.
4. `SCRUM-26`: **Interactive Knowledge Graph Visualization** (5 Story Points)
   - 2D Canvas force layout, node taxonomy, evidence-based similarity edges, node inspection drawer.

---

## Sprint 4: AI Quiz Generator, Spaced Repetition, Analytics & QA Hardening
- **Duration:** Weeks 7–8
- **Sprint Goal:** AI quiz generation, analytics dashboard, revision scheduling, testing, security, and deployment.
- **Sprint State:** Planned / Delivered
- **Story Points:** 14 SP

### Included Backlog Items:
1. `SCRUM-27`: **AI Quiz Generator and Interactive Assessment Engine** (5 Story Points)
   - MCQ quiz generation from user materials, timed test mode, instant grading, explanation review.
2. `SCRUM-28`: **Learning Analytics & Activity Dashboard** (3 Story Points)
   - Real database KPI cards, Recharts visualizations, active study streak counter, recent event feed.
3. `SCRUM-29`: **Spaced Repetition & Revision Scheduling System** (3 Story Points)
   - SuperMemo SM-2 flashcard scheduler, daily revision queue, automatic enrollment of failed quiz questions.
4. `SCRUM-30`: **Automated Test Suite, Security Hardening & Deployment Guides** (3 Story Points)
   - 15 pytest unit/integration tests, production bundle verification, complete documentation.
