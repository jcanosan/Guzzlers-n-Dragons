import tempfile

import pytest

from src.config.settings import settings
from src.services.vector_store import vector_store


@pytest.fixture
def test_store(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr(settings, "chroma_persist_dir", tmpdir)
    vector_store.init()
    yield
    vector_store.reset()


class TestInitVectorStore:
    def test_init(self, test_store):
        stats = vector_store.get_collection_stats()
        assert stats["collections"] >= 1


class TestAddDocuments:
    def test_add_single(self, test_store):
        docs = [{"content": "test content", "metadata": {"source": "test"}}]
        ids = vector_store.add_documents(docs)
        assert len(ids) == 1

    def test_add_multiple(self, test_store):
        docs = [
            {"content": "first doc", "metadata": {"idx": 0}},
            {"content": "second doc", "metadata": {"idx": 1}},
        ]
        ids = vector_store.add_documents(docs)
        assert len(ids) == 2


class TestSimilaritySearch:
    def test_basic_search(self, test_store):
        vector_store.add_documents(
            [
                {
                    "content": "How to thicken a sauce with cornstarch",
                    "metadata": {},
                },
                {"content": "Making beurre blanc emulsion", "metadata": {}},
                {
                    "content": "Grilling steak reverse sear method",
                    "metadata": {},
                },
            ]
        )
        results = vector_store.similarity_search("thickening sauce", k=2)
        assert len(results) >= 1
        assert "cornstarch" in results[0]["content"]

    def test_empty_store(self, test_store):
        results = vector_store.similarity_search("anything", k=2)
        assert results == []


class TestCollectionStats:
    def test_before_init(self):
        stats = vector_store.get_collection_stats()
        assert stats["collections"] >= 0

    def test_after_add(self, test_store):
        vector_store.add_documents(
            [
                {"content": "doc one", "metadata": {}},
                {"content": "doc two", "metadata": {}},
            ]
        )
        stats = vector_store.get_collection_stats()
        assert stats["collections"] >= 1
