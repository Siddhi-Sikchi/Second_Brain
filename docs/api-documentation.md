# REST API Reference & Specification

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new student or researcher account.
- **Request Body:**
  ```json
  {
    "email": "student@university.edu",
    "password": "SecurePassword123!",
    "full_name": "Alex Student"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "student@university.edu",
      "full_name": "Alex Student",
      "role": "student",
      "is_active": true
    }
  }
  ```

### `POST /auth/login`
Authenticates user and returns JWT token.
- **Request Body:**
  ```json
  {
    "email": "student@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK):** Returns `access_token` and `user` object.

### `POST /auth/logout`
Terminates active session (Requires Bearer Token).

---

## 2. Document Ingestion & Processing

### `POST /documents/upload`
Uploads a document for background text extraction, categorization, and RAG chunk indexing.
- **Headers:** `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
- **Form Data:**
  - `file`: (Binary file - PDF, PNG, JPG, TXT, MD)
  - `title`: Optional custom document title
  - `category`: Optional subject classification
  - `tags`: Optional comma-separated tags
- **Response (201 Created):**
  ```json
  {
    "id": 1,
    "title": "Operating Systems Virtual Memory",
    "original_filename": "os_memory.pdf",
    "file_type": "pdf",
    "file_size": 1048576,
    "processing_status": "completed",
    "page_count": 12,
    "word_count": 3450,
    "summary": "This document examines virtual memory techniques including paging...",
    "key_takeaways": ["Paging maps virtual to physical addresses.", "TLB speeds up translations."],
    "category": "Computer Science",
    "tags": [{"id": 1, "name": "OperatingSystems"}]
  }
  ```

### `GET /documents`
List user documents with optional query filters:
- `category`: string
- `file_type`: string
- `status`: string
- `tag`: string

### `DELETE /documents/{id}`
Deletes document record, disk file, and associated vector chunks.

---

## 3. Notes Management

### `POST /notes`
Create a study note with automatic word count and RAG vector chunking.
- **Request Body:**
  ```json
  {
    "title": "Backpropagation Algorithm",
    "content": "Backpropagation computes the gradient of the loss function with respect to weights...",
    "category": "Artificial Intelligence",
    "tags": ["NeuralNetworks", "DeepLearning"],
    "is_pinned": true
  }
  ```

### `GET /notes`
Returns user notes sorted by pinned status and update time.

---

## 4. Search & RAG Q&A Engine

### `POST /search`
Hybrid keyword and cosine similarity search across documents and notes.
- **Request Body:**
  ```json
  {
    "query": "virtual memory page tables",
    "limit": 10
  }
  ```
- **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "title": "Operating Systems Virtual Memory",
      "type": "document",
      "snippet": "Paging maps virtual addresses onto physical memory using page tables...",
      "relevance_score": 0.84,
      "category": "Computer Science"
    }
  ]
  ```

### `POST /search/rag`
Retrieval-Augmented Generation answering questions with verified source citations.
- **Request Body:**
  ```json
  {
    "question": "How does multi-head attention improve representation learning?"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "question": "How does multi-head attention improve representation learning?",
    "answer": "According to your knowledge base, multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.",
    "is_grounded": true,
    "confidence_score": 0.88,
    "citations": [
      {
        "source_title": "Transformer Architectures & Attention",
        "source_type": "document",
        "source_id": 1,
        "page": 1,
        "excerpt": "In multi-head attention, the model jointly attends to information from different representation subspaces...",
        "relevance": 0.88
      }
    ]
  }
  ```

---

## 5. Knowledge Graph

### `GET /graph`
Returns nodes and evidence-based edges for interactive visualization.
- **Response (200 OK):**
  ```json
  {
    "nodes": [
      {"id": "doc_1", "label": "Operating Systems", "group": "document", "val": 5.0},
      {"id": "tag_1", "label": "#Systems", "group": "tag", "val": 3.0}
    ],
    "links": [
      {"source": "doc_1", "target": "tag_1", "relation": "tagged_with", "weight": 1.5}
    ],
    "total_nodes": 2,
    "total_edges": 1
  }
  ```

---

## 6. AI Quizzes & Spaced Repetition

### `POST /quizzes/generate`
Generates an MCQ quiz from selected documents or notes.
- **Request Body:**
  ```json
  {
    "title": "Midterm Review Quiz",
    "source_type": "all",
    "question_count": 5
  }
  ```

### `POST /quizzes/{id}/submit`
Submits user answers, calculates percentage score, provides detailed feedback, and enrolls missed items into the revision schedule.

### `GET /revision/due`
Returns flashcards and concepts due for review today according to the SuperMemo SM-2 algorithm.

### `POST /revision/{id}/review`
Accepts review rating (`again`, `hard`, `good`, `easy`) and calculates the next spaced interval.

---

## 7. Learning Analytics Dashboard

### `GET /analytics/dashboard`
Returns 100% genuine database metrics:
- `total_documents`, `total_notes`, `total_words`
- `average_quiz_score`, `total_quizzes_taken`
- `storage_used_bytes`
- `active_streak_days`
- `categories`: breakdown count per subject
- `top_tags`: most frequent tags
- `recent_activity`: log of recent user events
