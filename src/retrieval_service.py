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
        top_k: int = 5
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        query_embedding = (
            self.embedding_client.embed(
                query
            )
        )

        return self.retriever.search(
            query_embedding,
            top_k=top_k
        )