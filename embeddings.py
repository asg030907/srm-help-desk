"""
embeddings.py
Thin wrapper around an embeddings provider, used for knowledge-base /
memory similarity search. Swap `_call_provider` for a real API call
(OpenAI, Voyage, Cohere, etc.) when you wire up retrieval.
"""

import hashlib
from typing import List

from src.utils.logger import get_logger

logger = get_logger(__name__)

EMBEDDING_DIM = 16  # placeholder dimensionality for the stub


def _call_provider(text: str) -> List[float]:
    """
    Placeholder embedding function — deterministic but NOT semantically
    meaningful. Replace with a real embeddings API call, e.g.:

        response = openai_client.embeddings.create(
            model="text-embedding-3-small", input=text
        )
        return response.data[0].embedding
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [b / 255.0 for b in digest[:EMBEDDING_DIM]]


def embed_text(text: str) -> List[float]:
    """Return an embedding vector for a single string."""
    if not text.strip():
        return [0.0] * EMBEDDING_DIM
    return _call_provider(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Return embedding vectors for a list of strings."""
    return [embed_text(t) for t in texts]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
