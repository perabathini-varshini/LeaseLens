
import math

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

        # Generate and validate embeddings before replacing
        # the existing index.

        expected_dimension = None

        for chunk in chunks:
            embedding = self.embedding_client.embed(
                chunk["text"]
            )

            if (
                not isinstance(embedding, (list, tuple))
                or not embedding
            ):
                raise ValueError(
                    f"Invalid embedding for {chunk['chunk_id']}."
                )

            try:
                valid_embedding = all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    for value in embedding
                )
            except OverflowError:
                valid_embedding = False

            if not valid_embedding:
                raise ValueError(
                    f"Invalid embedding values for "
                    f"{chunk['chunk_id']}."
                )

            if expected_dimension is None:
                expected_dimension = len(embedding)
            elif len(embedding) != expected_dimension:
                raise ValueError(
                    "Embedding dimensions must be consistent "
                    "across all chunks."
                )

            new_records.append({
                "chunk": chunk,
                "embedding": [
                    float(value) for value in embedding
                ]
            })

        # Replace the previous index only after all
        # embeddings have been generated and validated.
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
