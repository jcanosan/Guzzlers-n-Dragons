#!/usr/bin/env python3
"""Ingest cooking science documents (/data/cooking_science) into ChromaDB vector
store to use them as RAG knowledge base."""

from pathlib import Path

from src.services.vector_store import vector_store


def chunk_text(
    text: str, chunk_size: int = 1000, overlap: int = 200
) -> list[str]:
    """Split text into overlapping chunks.

    Raises:
        ValueError: If overlap >= chunk_size (would loop forever).
    """
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be < chunk_size ({chunk_size})"
        )

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def load_markdown_files(directory: str) -> list[dict]:
    """Load all .md files from directory.
    return
        list of {content, metadata}
    """

    docs = []
    path = Path(directory)
    for md_file in path.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # Split by major sections (## headings)
        sections = content.split("\n## ")
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            # Add heading back if not first section
            if i > 0:
                section = "## " + section
            # Chunk large sections
            if len(section) > 1500:
                for j, chunk in enumerate(chunk_text(section)):
                    docs.append(
                        {
                            "content": chunk,
                            "metadata": {
                                "source": md_file.name,
                                "section": i,
                                "chunk": j,
                                "topic": md_file.stem,
                            },
                        }
                    )
            else:
                docs.append(
                    {
                        "content": section,
                        "metadata": {
                            "source": md_file.name,
                            "section": i,
                            "topic": md_file.stem,
                        },
                    }
                )
    return docs


if __name__ == "__main__":
    data_dir = "data/cooking_science"
    print(f"Loading documents from {data_dir}...")
    documents = load_markdown_files(data_dir)
    print(f"Prepared {len(documents)} document chunks")

    print("Initializing vector store...")
    vector_store.init()

    print("Adding documents to vector store...")
    ids = vector_store.add_documents(documents)
    print(f"Added {len(ids)} documents to vector store")
    print(f"Collection has {len(documents)} document chunks")
