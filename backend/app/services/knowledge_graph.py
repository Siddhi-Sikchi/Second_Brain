from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from app.models import Document, Note, Tag, GraphNode, GraphEdge
from app.schemas import GraphDataResponse, GraphNodeSchema, GraphEdgeSchema
from app.services.search_engine import compute_tf_vector, cosine_similarity


def build_user_knowledge_graph(db: Session, user_id: int) -> GraphDataResponse:
    """
    Constructs an evidence-based knowledge graph for the authenticated user.
    Nodes: Documents, Notes, Tags, and Topics.
    Edges:
      1. Tagged relations (Doc/Note <-> Tag)
      2. Conceptual and semantic similarity (Doc <-> Doc, Doc <-> Note, Note <-> Note)
    """
    nodes_map: Dict[str, GraphNodeSchema] = {}
    edges_set: Set[str] = set()
    edges_list: List[GraphEdgeSchema] = []

    # Fetch user data
    docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.processing_status == "completed"
    ).all()

    notes = db.query(Note).filter(
        Note.user_id == user_id,
        Note.is_archived == False
    ).all()

    tags = db.query(Tag).filter(Tag.user_id == user_id).all()

    # 1. Add Tag Nodes
    for tag in tags:
        tag_id = f"tag_{tag.id}"
        nodes_map[tag_id] = GraphNodeSchema(
            id=tag_id,
            label=f"#{tag.name}",
            group="tag",
            val=3.0,
            source_id=tag.id,
            meta={"color": tag.color, "type": "tag"}
        )

    # 2. Add Document Nodes and Tag Edges
    doc_vectors: Dict[str, Dict[str, float]] = {}
    for doc in docs:
        doc_id = f"doc_{doc.id}"
        nodes_map[doc_id] = GraphNodeSchema(
            id=doc_id,
            label=doc.title,
            group="document",
            val=5.0,
            source_id=doc.id,
            meta={
                "type": "document",
                "file_type": doc.file_type,
                "category": doc.category,
                "summary": doc.summary or "",
                "created_at": doc.created_at.isoformat()
            }
        )
        doc_vectors[doc_id] = compute_tf_vector(doc.extracted_text or doc.title)

        # Connect to tags
        for t in doc.tags:
            tag_id = f"tag_{t.id}"
            if tag_id in nodes_map:
                edge_key = f"{doc_id}->{tag_id}"
                if edge_key not in edges_set:
                    edges_set.add(edge_key)
                    edges_list.append(GraphEdgeSchema(
                        source=doc_id,
                        target=tag_id,
                        relation="tagged_with",
                        weight=1.5
                    ))

    # 3. Add Note Nodes and Tag Edges
    note_vectors: Dict[str, Dict[str, float]] = {}
    for note in notes:
        note_id = f"note_{note.id}"
        nodes_map[note_id] = GraphNodeSchema(
            id=note_id,
            label=note.title,
            group="note",
            val=4.0,
            source_id=note.id,
            meta={
                "type": "note",
                "category": note.category,
                "summary": note.summary or note.content[:150],
                "created_at": note.created_at.isoformat()
            }
        )
        note_vectors[note_id] = compute_tf_vector(note.content)

        # Connect to tags
        for t in note.tags:
            tag_id = f"tag_{t.id}"
            if tag_id in nodes_map:
                edge_key = f"{note_id}->{tag_id}"
                if edge_key not in edges_set:
                    edges_set.add(edge_key)
                    edges_list.append(GraphEdgeSchema(
                        source=note_id,
                        target=tag_id,
                        relation="tagged_with",
                        weight=1.5
                    ))

    # 4. Generate Semantic Similarity Edges (Threshold > 0.20 for strong semantic relevance)
    all_items = list(doc_vectors.items()) + list(note_vectors.items())
    for i in range(len(all_items)):
        for j in range(i + 1, len(all_items)):
            id_a, vec_a = all_items[i]
            id_b, vec_b = all_items[j]

            sim = cosine_similarity(vec_a, vec_b)
            if sim >= 0.22:
                edge_key = f"{id_a}->{id_b}"
                if edge_key not in edges_set:
                    edges_set.add(edge_key)
                    edges_list.append(GraphEdgeSchema(
                        source=id_a,
                        target=id_b,
                        relation="semantic_similarity",
                        weight=round(sim * 2.0, 2)
                    ))

    node_list = list(nodes_map.values())
    return GraphDataResponse(
        nodes=node_list,
        links=edges_list,
        total_nodes=len(node_list),
        total_edges=len(edges_list)
    )
