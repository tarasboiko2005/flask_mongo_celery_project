import faiss
import logging
from threading import Lock
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_vectorstore = None
_lock = Lock()

def _create_vectorstore() -> FAISS:
    embeddings = get_embeddings()
    test_vector = embeddings.embed_query("test")
    dimension = len(test_vector)

    index = faiss.IndexFlatL2(dimension)
    docstore = InMemoryDocstore({})

    logger.info(f"FAISS vectorstore initialized with dimension {dimension}")

    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id={}
    )

def get_vectorstore() -> FAISS:
    global _vectorstore

    if _vectorstore is None:
        with _lock:
            if _vectorstore is None:
                _vectorstore = _create_vectorstore()

    return _vectorstore

def add_metadata(vectorstore: FAISS, text: str, metadata: dict | None = None):
    if not metadata:
        metadata = {}

    logger.info("Adding metadata to vectorstore")

    vectorstore.add_texts(
        texts=[text],
        metadatas=[metadata]
    )