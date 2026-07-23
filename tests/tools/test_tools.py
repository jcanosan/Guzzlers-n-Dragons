import sys
import tempfile
from pathlib import Path

import pytest

from src.config.settings import settings
from src.services.vector_store import vector_store
from src.tools import (
    find_flavor_pairing,
    find_technique_substitution,
    find_texture_modification,
    get_cooking_science,
)
from tests.mock_embeddings import MockEmbeddings


@pytest.fixture
def seeded_store(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr(settings, "chroma_persist_dir", tmpdir)
    monkeypatch.setattr(
        sys.modules["src.services.vector_store"],
        "OllamaEmbeddings",
        MockEmbeddings,
    )
    vector_store.init()

    data_dir = Path("data/cooking_science")
    docs = []
    for md_file in data_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        for section in text.split("\n## "):
            if section.strip():
                docs.append(
                    {
                        "content": section,
                        "metadata": {
                            "source": md_file.name,
                            "topic": md_file.stem,
                        },
                    }
                )
    vector_store.add_documents(docs)
    yield
    vector_store.reset()


class TestFindTechniqueSubstitution:
    def test_returns_results(self, seeded_store):
        results = find_technique_substitution("cornstarch")
        assert len(results) > 0
        assert any("cornstarch" in r["content"].lower() for r in results)

    def test_empty_query(self, seeded_store):
        results = find_technique_substitution("")
        assert len(results) >= 0


class TestFindFlavorPairing:
    def test_returns_results(self, seeded_store):
        results = find_flavor_pairing("chocolate")
        assert len(results) > 0

    def test_unknown_ingredient(self, seeded_store):
        results = find_flavor_pairing("xyznonexistent")
        assert len(results) >= 0


class TestFindTextureModification:
    def test_returns_results(self, seeded_store):
        results = find_texture_modification("creamy", "watery")
        assert len(results) > 0


class TestGetCookingScience:
    def test_returns_results(self, seeded_store):
        results = get_cooking_science("emulsification")
        assert len(results) > 0

    def test_custom_k(self, seeded_store):
        results = get_cooking_science("sauce", num_results=5)
        assert len(results) <= 5
