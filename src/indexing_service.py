from src.chunker import create_chunks
from src.embedding_client import GeminiEmbeddingClient


class IndexingService:
    def __init__(
        self,
        vector_store,
        embedding_client=None
    ):
        self.vector_store = vector_store
        self.embedding_client = (
            embedding_client
            if embedding_client is not None
            else GeminiEmbeddingClient()
        )

    def index_clauses(
        self,
        clauses: list[dict],
        max_words: int = 120
    ) -> dict:
        if not isinstance(clauses, list):
            raise ValueError(
                "Clauses must be provided as a list."
            )

        chunks = create_chunks(
            clauses,
            max_words=max_words
        )

        new_records = []

        # Generate embeddings before replacing the
        # existing index. This preserves the old index
        # if an embedding request fails.
        for chunk in chunks:
            embedding = self.embedding_client.embed(
                chunk["text"]
            )

            if not embedding:
                raise ValueError(
                    f"Empty embedding for {chunk['chunk_id']}."
                )

            new_records.append({
                "chunk": chunk,
                "embedding": embedding
            })

        # Replace the previous index only after all
        # embeddings have been generated successfully.
        previous_records = self.vector_store.records

        try:
            self.vector_store.records = new_records
            self.vector_store.save()
        except Exception:
            self.vector_store.records = previous_records
            raise

        return {
            "chunks_indexed": len(new_records),
            "chunk_ids": [
                record["chunk"]["chunk_id"]
                for record in new_records
            ]
        }