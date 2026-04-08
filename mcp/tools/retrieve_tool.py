def retrieve(query: str, k: int = 5) -> list[str]:
    """Placeholder hybrid retrieval tool."""
    return [f"retrieved_chunk_{i}:{query}" for i in range(1, k + 1)]
