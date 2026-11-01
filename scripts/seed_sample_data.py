"""
Seed Sample Data Script
Initializes the database with a pre-configured student demo account,
sample documents, notes, tags, chunks, a generated quiz, and revision queue items.
"""

import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.database import engine, Base, SessionLocal
from app.models import User, Document, Note, Tag, Chunk, Quiz, QuizQuestion, QuizAttempt, RevisionItem
from app.utils.security import hash_password
from app.services.text_extractor import process_document_file
from app.services.summarizer import extractive_summary
from app.services.tagger import extract_smart_tags, classify_category
from app.services.search_engine import index_document_chunks, index_note_chunks


def seed():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Create Demo Student User
    demo_email = "student@university.edu"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        print("Creating demo student user...")
        user = User(
            email=demo_email,
            hashed_password=hash_password("SecurePassword123!"),
            full_name="Alex Student",
            bio="Junior Undergraduate in Computer Science & Artificial Intelligence.",
            role="student",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print("Demo user already exists.")

    # 2. Create Tags
    tag_names = ["ArtificialIntelligence", "DistributedSystems", "OperatingSystems", "Databases", "Algorithms"]
    tags_map = {}
    for tname in tag_names:
        tag = db.query(Tag).filter(Tag.user_id == user.id, Tag.name == tname).first()
        if not tag:
            tag = Tag(user_id=user.id, name=tname)
            db.add(tag)
            db.flush()
        tags_map[tname] = tag

    # 3. Seed Sample Document 1: Deep Learning & Transformers
    doc1 = db.query(Document).filter(Document.user_id == user.id, Document.title == "Transformer Architectures & Attention").first()
    if not doc1:
        print("Seeding sample document: Transformer Architectures...")
        doc1_text = (
            "The Transformer architecture relies entirely on self-attention mechanisms to compute representations of its "
            "input and output without using sequence-aligned RNNs or convolution. Attention mechanisms allow modeling of "
            "dependencies regardless of their distance in the input or output sequences. In multi-head attention, the model "
            "jointly attends to information from different representation subspaces at different positions. Positional encodings "
            "are injected into the input embeddings to account for the order of tokens in the sequence. Transformers form the "
            "backbone of modern Large Language Models (LLMs) and enable retrieval-augmented generation (RAG) by embedding text "
            "chunks into continuous vector spaces."
        )
        summary, takeaways = extractive_summary(doc1_text, max_sentences=3)
        doc1 = Document(
            user_id=user.id,
            title="Transformer Architectures & Attention",
            original_filename="transformers_overview.txt",
            stored_filename="seed_transformers_overview.txt",
            file_path=str(backend_path / "uploads" / "seed_transformers.txt"),
            file_type="text",
            file_size=len(doc1_text.encode("utf-8")),
            mime_type="text/plain",
            processing_status="completed",
            extracted_text=doc1_text,
            page_count=1,
            word_count=len(doc1_text.split()),
            char_count=len(doc1_text),
            summary=summary,
            key_takeaways=takeaways,
            category="Artificial Intelligence"
        )
        doc1.tags.append(tags_map["ArtificialIntelligence"])
        db.add(doc1)
        db.commit()
        db.refresh(doc1)
        index_document_chunks(db, user.id, doc1.id, doc1_text)

    # 4. Seed Sample Document 2: Distributed Consensus & Raft
    doc2 = db.query(Document).filter(Document.user_id == user.id, Document.title == "Raft Consensus Algorithm Guide").first()
    if not doc2:
        print("Seeding sample document: Raft Consensus...")
        doc2_text = (
            "Raft is a consensus algorithm designed to be understandable and easy to implement. It is equivalent to Paxos in "
            "fault tolerance and performance. Raft decomposes consensus into three relatively independent subproblems: "
            "Leader election, Log replication, and Safety. A leader must be elected when an existing leader fails. The leader "
            "accepts log entries from clients, replicates them across other servers, and tells servers when it is safe to apply "
            "log entries to their state machines. Once a leader has been elected, state changes are driven strictly by the leader. "
            "Heartbeat messages prevent election timeouts in follower nodes."
        )
        summary2, takeaways2 = extractive_summary(doc2_text, max_sentences=3)
        doc2 = Document(
            user_id=user.id,
            title="Raft Consensus Algorithm Guide",
            original_filename="raft_consensus.txt",
            stored_filename="seed_raft_consensus.txt",
            file_path=str(backend_path / "uploads" / "seed_raft.txt"),
            file_type="text",
            file_size=len(doc2_text.encode("utf-8")),
            mime_type="text/plain",
            processing_status="completed",
            extracted_text=doc2_text,
            page_count=1,
            word_count=len(doc2_text.split()),
            char_count=len(doc2_text),
            summary=summary2,
            key_takeaways=takeaways2,
            category="Computer Science"
        )
        doc2.tags.append(tags_map["DistributedSystems"])
        db.add(doc2)
        db.commit()
        db.refresh(doc2)
        index_document_chunks(db, user.id, doc2.id, doc2_text)

    # 5. Seed Sample Study Note
    note1 = db.query(Note).filter(Note.user_id == user.id, Note.title == "Lecture Notes: Operating Systems Virtual Memory").first()
    if not note1:
        print("Seeding sample note: Operating Systems...")
        note_content = (
            "Virtual memory is a memory management capability of an operating system that uses hardware and software to "
            "allow a computer to compensate for physical memory shortages by temporarily transferring data from random access "
            "memory (RAM) to disk storage. Paging maps virtual addresses used by an application onto physical addresses in computer "
            "memory. Page tables maintain the mapping, and translation lookaside buffers (TLBs) cache recent translations."
        )
        note1 = Note(
            user_id=user.id,
            title="Lecture Notes: Operating Systems Virtual Memory",
            content=note_content,
            summary="Virtual memory compensates for physical memory shortages using paging, page tables, and TLBs.",
            category="Computer Science",
            word_count=len(note_content.split()),
            is_pinned=True
        )
        note1.tags.append(tags_map["OperatingSystems"])
        db.add(note1)
        db.commit()
        db.refresh(note1)
        index_note_chunks(db, user.id, note1.id, note_content)

    # 6. Seed Sample Quiz & Attempt
    quiz1 = db.query(Quiz).filter(Quiz.user_id == user.id, Quiz.title == "Foundations of AI & Systems Quiz").first()
    if not quiz1:
        print("Seeding sample quiz...")
        quiz1 = Quiz(
            user_id=user.id,
            title="Foundations of AI & Systems Quiz",
            description="Self-assessment on Transformers and Raft consensus.",
            source_type="all",
            question_count=2
        )
        db.add(quiz1)
        db.commit()
        db.refresh(quiz1)

        q1 = QuizQuestion(
            quiz_id=quiz1.id,
            question_text="What mechanism does the Transformer architecture rely on to model sequence dependencies?",
            question_type="mcq",
            options=["Self-attention mechanisms", "Recurrent neural loops", "Convolutional pooling", "K-means clustering"],
            correct_answer="Self-attention mechanisms",
            explanation="The Transformer architecture relies entirely on self-attention mechanisms to compute representations without RNNs.",
            order_index=0
        )
        q2 = QuizQuestion(
            quiz_id=quiz1.id,
            question_text="What are the three core subproblems that the Raft consensus algorithm decomposes consensus into?",
            question_type="mcq",
            options=[
                "Leader election, Log replication, and Safety",
                "Hashing, Encryption, and Decryption",
                "Indexing, Querying, and Sharding",
                "Paging, Segmentation, and Swapping"
            ],
            correct_answer="Leader election, Log replication, and Safety",
            explanation="Raft decomposes consensus into three subproblems: Leader election, Log replication, and Safety.",
            order_index=1
        )
        db.add(q1)
        db.add(q2)
        db.commit()

        # Seed an attempt
        attempt = QuizAttempt(
            quiz_id=quiz1.id,
            user_id=user.id,
            score=100.0,
            total_questions=2,
            correct_count=2,
            answers_data=[{"q": q1.id, "ans": q1.correct_answer}, {"q": q2.id, "ans": q2.correct_answer}],
            time_taken_seconds=45,
            completed_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()

    # 7. Seed Revision Items
    rev_item = db.query(RevisionItem).filter(RevisionItem.user_id == user.id).first()
    if not rev_item:
        print("Seeding revision items...")
        item = RevisionItem(
            user_id=user.id,
            item_type="concept",
            title="Concept: Multi-Head Attention Subspaces",
            content_preview="Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.",
            repetition_level=1,
            interval_days=1,
            ease_factor=2.5,
            next_review_date=datetime.utcnow() - timedelta(hours=1),  # Due now
            review_count=1
        )
        db.add(item)
        db.commit()

    db.close()
    print("Seed data successfully populated!")


if __name__ == "__main__":
    seed()
