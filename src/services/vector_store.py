import chromadb
import structlog
from chromadb.api import ClientAPI as ChromaClient
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from src.config.settings import settings

logger = structlog.get_logger()

_vector_store: Chroma | None = None
_client: ChromaClient | None = None


def init_vector_store() -> None:
    """Initialize the Chroma vector store with Ollama embeddings."""
    global _vector_store, _client
    _client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    embeddings = OllamaEmbeddings(
        model=settings.embedding_model,
    )
    _vector_store = Chroma(
        client=_client,
        collection_name="cooking_science",
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )
    logger.info("vector_store_initialized", path=settings.chroma_persist_dir)


def get_vector_store() -> Chroma:
    """Get the Chroma vector store, initializing if needed."""
    if _vector_store is None:
        init_vector_store()

    store = _vector_store
    if store is None:
        raise RuntimeError("Vector store failed to initialize")
    return store


def add_documents(documents: list[dict]) -> list[str]:
    """Add documents to vector store. Each doc: {content, metadata}."""
    vs = get_vector_store()
    texts = [d["content"] for d in documents]
    metadatas = [d.get("metadata", {}) for d in documents]
    ids = vs.add_texts(texts=texts, metadatas=metadatas)
    logger.info("documents_added", count=len(ids))
    return ids


def similarity_search(
    query: str, k: int = 5, filter: dict | None = None
) -> list[dict]:
    """Search for similar documents."""
    vs = get_vector_store()
    results = vs.similarity_search_with_score(query=query, k=k, filter=filter)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": score,
        }
        for doc, score in results
    ]


def get_collection_stats() -> dict:
    """Get stats about the vector store."""
    if _client is None:
        return {"collections": 0, "total_documents": 0}
    collections = _client.list_collections()
    total = sum(c.count() for c in collections)
    return {
        "collections": len(collections),
        "total_documents": total,
        "collection_names": [c.name for c in collections],
    }
