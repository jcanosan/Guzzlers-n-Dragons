import chromadb
import structlog
from chromadb.api import ClientAPI as ChromaClient
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from src.config.settings import settings

logger = structlog.get_logger()


class VectorStore:
    """Chroma vector store with hybrid (vector + keyword) search."""

    def __init__(self) -> None:
        self._vector_store: Chroma | None = None
        self._client: ChromaClient | None = None

    def init(self) -> None:
        """Initialize the Chroma vector store with Ollama embeddings."""
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        embeddings = OllamaEmbeddings(
            model=settings.embedding_model,
        )
        self._vector_store = Chroma(
            client=self._client,
            collection_name="cooking_science",
            embedding_function=embeddings,
            persist_directory=settings.chroma_persist_dir,
        )
        logger.info(
            "vector store initialized", path=settings.chroma_persist_dir
        )

    def _ensure_initialized(self) -> None:
        """Lazy-init the store if needed. Raise if init fails."""
        if self._vector_store is None:
            self.init()
        if self._vector_store is None:
            raise RuntimeError("Vector store failed to initialize")

    def get_store(self) -> Chroma:
        """Get the Chroma vector store. Initialize it if needed."""
        self._ensure_initialized()
        return self._vector_store  # type: ignore

    def add_documents(self, documents: list[dict]) -> list[str]:
        """Add documents to the vector store. Each doc: {content, metadata}."""
        self._ensure_initialized()
        texts = [d["content"] for d in documents]
        metadatas = [d.get("metadata", {}) for d in documents]
        ids = self._vector_store.add_texts(texts=texts, metadatas=metadatas)  # type: ignore
        logger.info("documents added to vector store", count=len(ids))
        return ids

    def similarity_search(
        self, query: str, k: int = 5, filter: dict | None = None
    ) -> list[dict]:
        """Search the vector store for similar documents."""
        self._ensure_initialized()
        results = self._vector_store.similarity_search_with_score(  # type: ignore
            query=query, k=k, filter=filter
        )
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for doc, score in results
        ]

    def hybrid_search(
        self,
        query: str,
        num_results: int = 5,
        filter: dict | None = None,
        alpha: float = 0.5,
    ) -> list[dict]:
        """
        Hybrid search combining vector similarity and keyword matching for
        better recall.

        Args:
            query: Search query
            num_results: Number of results
            filter: Metadata filter
            alpha: Weight for vector search
                  (0.0 = keyword only, 1.0 = vector only)
        """
        self._ensure_initialized()
        vector_results = self._vector_search(query, num_results * 2, filter)
        keyword_results = self._keyword_search(query, num_results * 2, filter)
        merged = self._deduplicate(vector_results, keyword_results)
        return self._rank_results(merged, alpha, num_results)

    def _vector_search(
        self, query: str, k: int, filter: dict | None
    ) -> list[tuple]:
        """Semantic search by embedding similarity."""
        return self._vector_store.similarity_search_with_score(  # type: ignore
            query=query, k=k, filter=filter
        )

    def _keyword_search(
        self, query: str, k: int, filter: dict | None
    ) -> list[tuple]:
        """Text-match search using Chroma's where_document filter."""
        if not query or self._vector_store is None:
            return []
        where_document: dict | None = {"$contains": query.lower()}
        return self._vector_store.similarity_search_with_score(
            query=query, k=k, filter=filter, where_document=where_document
        )

    def _deduplicate(
        self,
        vector_results: list[tuple],
        keyword_results: list[tuple],
    ) -> list[dict]:
        """Merge two result lists, dedup by content prefix hash."""
        seen = set()
        combined: list[dict] = []

        for doc, score in vector_results:
            key = self._content_key(doc.page_content)
            if key not in seen:
                seen.add(key)
                combined.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "vector_score": float(score),
                        "keyword_score": 0.0,
                    }
                )

        for doc, score in keyword_results:
            key = self._content_key(doc.page_content)
            if key not in seen:
                seen.add(key)
                combined.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "vector_score": 0.0,
                        "keyword_score": self._invert_distance(score),
                    }
                )
            else:
                for item in combined:
                    if self._content_key(item["content"]) == key:
                        item["keyword_score"] = self._invert_distance(score)
                        break

        return combined

    @staticmethod
    def _content_key(content: str) -> int:
        """Hash of first 100 chars, used for deduplication."""
        return hash(content[:100])

    @staticmethod
    def _invert_distance(score: float) -> float:
        """Convert Chroma distance to similarity (higher = more similar)."""
        return 1.0 / (1.0 + float(score))

    def _rank_results(
        self, combined: list[dict], alpha: float, k: int
    ) -> list[dict]:
        """Compute hybrid scores, sort, return top k formatted results."""
        for item in combined:
            vs_norm = (
                self._invert_distance(item["vector_score"])
                if float(item["vector_score"]) > 0
                else 0.0
            )
            kw_norm = float(item["keyword_score"])
            item["hybrid_score"] = alpha * vs_norm + (1 - alpha) * kw_norm

        combined.sort(key=lambda x: float(x["hybrid_score"]), reverse=True)
        return [
            {
                "content": item["content"],
                "metadata": item["metadata"],
                "score": float(item["hybrid_score"]),
            }
            for item in combined[:k]
        ]

    def get_collection_stats(self) -> dict:
        """Get stats about the vector store."""
        if self._client is None:
            return {"collections": 0, "total_documents": 0}
        collections = self._client.list_collections()
        total = sum(c.count() for c in collections)
        return {
            "collections": len(collections),
            "total_documents": total,
            "collection_names": [c.name for c in collections],
        }

    def reset(self) -> None:
        """Reset store and client. Useful for tests."""
        self._vector_store = None
        self._client = None


vector_store = VectorStore()
