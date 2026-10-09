import math


class VectorRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float]
    ) -> float:

        if not vector_a or not vector_b:
            raise ValueError(
                "Vectors cannot be empty."
            )

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Vectors must have the same dimensions."
            )

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = math.sqrt(
            sum(
                value * value
                for value in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                value * value
                for value in vector_b
            )
        )

        if magnitude_a == 0 or magnitude_b == 0:
            raise ValueError(
                "Vectors cannot have zero magnitude."
            )

        return dot_product / (
            magnitude_a * magnitude_b
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5
    ) -> list[dict]:

        if not query_embedding:
            raise ValueError(
                "Query embedding cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        scored_results = []

        for record in self.vector_store.records:
            embedding = record.get(
                "embedding",
                []
            )

            similarity = self.cosine_similarity(
                query_embedding,
                embedding
            )

            scored_results.append({
                "chunk": record["chunk"],
                "score": similarity
            })

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_results[:top_k]