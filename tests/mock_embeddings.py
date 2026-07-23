"""Mock embedding function for tests — avoids Ollama dependency in CI."""

from langchain_core.embeddings import Embeddings

VECTOR_SIZE = 768


class MockEmbeddings(Embeddings):
    """Returns all-zero vectors. Good enough for testing retrieval logic.

    Accepts any kwargs to replace OllamaEmbeddings — model name,
    configuration, etc. are all silently ignored.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * VECTOR_SIZE for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.0] * VECTOR_SIZE
