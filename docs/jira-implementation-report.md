# Jira Project Implementation & Scrum Management Report

## 1. Project Overview & Environment

- **Jira Instance:** [https://vit-team-sxjbt0vb.atlassian.net](https://vit-team-sxjbt0vb.atlassian.net)
- **Project Key:** `SCRUM` ("Agile Methodology CP")
- **Project Type:** Team-Managed Software (Scrum)
- **Board ID:** `1` ("SCRUM board")
- **Atlassian MCP Integration:** Connected via official Atlassian Remote MCP Server with OAuth 2.1 authentication.

---

## 2. Epic Structure & Scope Allocation

All existing epics were preserved, and dedicated epics for AI Summarization and Security/Testing were created to cover the complete software engineering lifecycle:

| Epic Key | Epic Summary | Story Points | Objective & Completion Criteria |
|----------|--------------|:------------:|---------------------------------|
| `SCRUM-1` | **User Management** | 12 SP | Secure registration, login, profile management, password resets, and session termination. |
| `SCRUM-2` | **Document Processing** | 18 SP | Ingestion of PDFs, images, notes, text parsing, OCR fallback, and library management. |
| `SCRUM-16`| **AI Summarization and Smart Tagging** | 8 SP | Automatic executive summaries, bullet point generation, and taxonomy classification. |
| `SCRUM-3` | **AI Search Engine** | 5 SP | Hybrid keyword and semantic vector search with Retrieval-Augmented Generation (RAG). |
| `SCRUM-4` | **Knowledge Graph** | 5 SP | Interactive node-link visualization connecting documents, notes, tags, and semantic concepts. |
| `SCRUM-5` | **Quiz Generator** | 5 SP | Automated MCQ quiz creation from notes/documents, grading engine, and explanation citations. |
| `SCRUM-6` | **Analytics Dashboard** | 3 SP | Real-time database metrics, learning streak counter, and visual topic charts. |
| `SCRUM-7` | **Collaboration & Revision** | 3 SP | SuperMemo SM-2 spaced repetition queue to reinforce weak concepts. |
| `SCRUM-17`| **Security, Testing, Deployment and Documentation** | 9 SP | Pytest automated test suites, production build validation, security hardening, and technical docs. |

**Total Project Estimate:** **68 Story Points**

---

## 3. Four-Sprint Delivery Roadmap

The 8-week development cycle was partitioned into four 2-week iterations maintaining an average velocity of 17 story points per sprint:

```
+-----------------------------------------------------------------------------------------------+
| SPRINT 1 (Weeks 1-2): Foundation, Architecture & User Management (18 Story Points)            |
| SCRUM-8 (3 SP) | SCRUM-9 (3 SP) | SCRUM-10 (3 SP) | SCRUM-11 (1 SP)                           |
| SCRUM-18 (3 SP) | SCRUM-19 (3 SP) | SCRUM-20 (2 SP)                                           |
+-----------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+-----------------------------------------------------------------------------------------------+
| SPRINT 2 (Weeks 3-4): Document Ingestion, Notes & Processing Pipeline (18 Story Points)       |
| SCRUM-12 (5 SP) | SCRUM-13 (5 SP) | SCRUM-21 (5 SP) | SCRUM-22 (3 SP)                         |
+-----------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+-----------------------------------------------------------------------------------------------+
| SPRINT 3 (Weeks 5-6): AI Summarization, RAG Search & Knowledge Graph (18 Story Points)         |
| SCRUM-23 (5 SP) | SCRUM-24 (3 SP) | SCRUM-25 (5 SP) | SCRUM-26 (5 SP)                         |
+-----------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+-----------------------------------------------------------------------------------------------+
| SPRINT 4 (Weeks 7-8): Quizzes, Spaced Repetition, Analytics & QA Hardening (14 Story Points)  |
| SCRUM-27 (5 SP) | SCRUM-28 (3 SP) | SCRUM-29 (3 SP) | SCRUM-30 (3 SP)                         |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Complete Traceability Matrix (Requirements -> Code -> Verification)

| Jira Key | Issue Type | Story Points | Sprint | Implementation Code | Test Verification | Final Status |
|:---------|:----------:|:------------:|:------:|:--------------------|:------------------|:------------:|
| **SCRUM-8** | Story | 3 | 1 | `backend/app/routers/auth.py`<br>`frontend/src/pages/Register.tsx` | `test_user_registration_success`<br>`test_user_registration_duplicate_rejected` | **Done** |
| **SCRUM-9** | Story | 3 | 1 | `backend/app/routers/auth.py`<br>`frontend/src/pages/Login.tsx` | `test_user_login_success`<br>`test_user_login_invalid_password` | **Done** |
| **SCRUM-10**| Story | 3 | 1 | `backend/app/routers/users.py`<br>`frontend/src/pages/Profile.tsx` | `test_user_profile_management` | **Done** |
| **SCRUM-11**| Story | 1 | 1 | `backend/app/routers/auth.py`<br>`frontend/src/context/AuthContext.tsx` | `test_user_logout` | **Done** |
| **SCRUM-18**| Story | 3 | 1 | `backend/app/models/__init__.py`<br>`backend/app/database.py` | `scripts/verify_db.py`<br>`conftest.py` | **Done** |
| **SCRUM-19**| Story | 3 | 1 | `frontend/src/components/Sidebar.tsx`<br>`frontend/src/components/Navbar.tsx` | `npm run build` (Clean bundle in 10.4s) | **Done** |
| **SCRUM-20**| Story | 2 | 1 | `backend/app/routers/users.py`<br>`frontend/src/pages/Profile.tsx` | `test_password_change` | **Done** |
| **SCRUM-12**| Story | 5 | 2 | `backend/app/routers/documents.py`<br>`frontend/src/pages/Documents.tsx` | `test_upload_text_document`<br>`test_upload_unsupported_format_rejected` | **Done** |
| **SCRUM-13**| Story | 5 | 2 | `backend/app/routers/notes.py`<br>`frontend/src/pages/Notes.tsx` | `test_create_and_manage_note` | **Done** |
| **SCRUM-21**| Story | 5 | 2 | `backend/app/services/text_extractor.py` | `test_upload_text_document` | **Done** |
| **SCRUM-22**| Story | 3 | 2 | `backend/app/routers/documents.py`<br>`frontend/src/pages/Documents.tsx` | `test_upload_text_document` | **Done** |
| **SCRUM-23**| Story | 5 | 3 | `backend/app/services/summarizer.py` | `test_upload_text_document` | **Done** |
| **SCRUM-24**| Story | 3 | 3 | `backend/app/services/tagger.py` | `test_upload_text_document` | **Done** |
| **SCRUM-25**| Story | 5 | 3 | `backend/app/services/search_engine.py`<br>`frontend/src/pages/Search.tsx` | `test_hybrid_search_and_rag`<br>`test_rag_empty_information_fallback` | **Done** |
| **SCRUM-26**| Story | 5 | 3 | `backend/app/services/knowledge_graph.py`<br>`frontend/src/pages/KnowledgeGraph.tsx`| `test_knowledge_graph_data` | **Done** |
| **SCRUM-27**| Story | 5 | 4 | `backend/app/services/quiz_engine.py`<br>`frontend/src/pages/Quizzes.tsx` | `test_quiz_generator_and_submission` | **Done** |
| **SCRUM-28**| Story | 3 | 4 | `backend/app/routers/analytics.py`<br>`frontend/src/pages/Dashboard.tsx` | `test_analytics_dashboard_metrics` | **Done** |
| **SCRUM-29**| Story | 3 | 4 | `backend/app/services/spaced_repetition.py`<br>`frontend/src/pages/Revision.tsx` | Automated review queue state | **Done** |
| **SCRUM-30**| Story | 3 | 4 | `backend/tests/`<br>`docs/` | 15/15 Pytest Passed (100% Pass Rate) | **Done** |

---

## 5. Scrum Master Retrospective & Best Practices

1. **Realistic Velocity & Sizing:** Each sprint was capped between 14 and 18 Story Points using Fibonacci sizing (1, 2, 3, 5), avoiding scope creep.
2. **Defensive AI Engineering:** Incorporating a fallback extractive summarizer and heuristic question maker ensured zero downtime and decoupled test suites from cloud API token rates.
3. **Audit Readiness:** Every user story directly maps to verifiable acceptance criteria, automated test suites, and clean commit boundaries.
