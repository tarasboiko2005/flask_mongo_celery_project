from flask import Blueprint, request, jsonify
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vector_store import get_vectorstore

rag_bp = Blueprint("rag", __name__)

@rag_bp.route("/add_document", methods=["POST"])
def add_document():
    """
    Add a document to FAISS
    ---
    tags:
      - RAG
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            text:
              type: string
            metadata:
              type: object
    responses:
      200:
        description: Document added successfully
    """
    data = request.get_json()
    text = data.get("text")
    metadata = data.get("metadata", {})

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents([Document(page_content=text, metadata=metadata)])

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    return jsonify({
        "message": f"Added {len(chunks)} chunks to vectorstore",
        "metadata": metadata
    }), 200