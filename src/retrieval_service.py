import math

from src.embedding_client import GeminiEmbeddingClient
from src.retriever import VectorRetriever


class RetrievalService:
    def __init__(
        self,
        vector_store,
        embedding_client=None
    ):
        self.embedding_client = (
            embedding_client
            or GeminiEmbeddingClient()
        )

        self.retriever = VectorRetriever(
            vector_store
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = -1.0
    ) -> list[dict]:

        if (
            not isinstance(query, str)
            or not query.strip()
        ):
            raise ValueError(
                "Search query must be a non-empty string."
            )

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError(
                "top_k must be a positive integer."
            )

        try:
            valid_similarity = (
                isinstance(min_similarity, (int, float))
                and not isinstance(min_similarity, bool)
                and math.isfinite(min_similarity)
                and -1.0 <= min_similarity <= 1.0
            )
        except OverflowError:
            valid_similarity = False

        if not valid_similarity:
            raise ValueError(
                "min_similarity must be a finite number "
                "between -1.0 and 1.0."
            )

        query_embedding = (
            self.embedding_client.embed(
                query
            )
        )

        return self.retriever.search(
            query_embedding,
            top_k=top_k,
            min_similarity=min_similarity
        )
