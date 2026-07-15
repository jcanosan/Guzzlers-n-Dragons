"""Cooking science RAG tools for the agent system."""

from src.services.vector_store import vector_store


def find_technique_substitution(
    technique: str, context: str = ""
) -> list[dict]:
    """Find alternative techniques for a given cooking technique."""
    query = f"substitute for {technique} {context}"
    return vector_store.hybrid_search(query=query, num_results=5, alpha=0.6)


def find_flavor_pairing(ingredient: str) -> list[dict]:
    """Find flavor pairings and substitution options for an ingredient."""
    query = f"flavor pairing substitution for {ingredient}"
    return vector_store.hybrid_search(query=query, num_results=5, alpha=0.6)


def find_texture_modification(
    target_texture: str, starting_texture: str = ""
) -> list[dict]:
    """Find techniques to modify texture from one state to another."""
    query = f"make {starting_texture} {target_texture} texture modification"
    return vector_store.hybrid_search(query=query, num_results=5, alpha=0.6)


def get_cooking_science(query: str, num_results: int = 3) -> list[dict]:
    """General cooking science query."""
    return vector_store.hybrid_search(query, num_results)
