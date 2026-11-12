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

        try:
            valid_vectors = all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for vector in (vector_a, vector_b)
                for value in vector
            )
        except (TypeError, OverflowError):
            valid_vectors = False

        if not valid_vectors:
            raise ValueError(
                "Vectors must contain only finite numeric values."
            )

        try:
            dot_product = math.fsum(
                a * b
                for a, b in zip(vector_a, vector_b)
            )

            magnitude_a = math.hypot(*vector_a)
            magnitude_b = math.hypot(*vector_b)

            if magnitude_a == 0 or magnitude_b == 0:
                raise ValueError(
                    "Vectors cannot have zero magnitude."
                )

            similarity = (
                dot_product / magnitude_a / magnitude_b
            )

        except OverflowError as exc:
            raise ValueError(
                "Vector values exceed supported numeric limits."
            ) from exc

        if not math.isfinite(similarity):
            raise ValueError(
                "Cosine similarity must be finite."
            )

        return max(-1.0, min(1.0, similarity))


    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_similarity: float = -1.0
    ) -> list[dict]:

        if not isinstance(query_embedding, (list, tuple)):
            raise ValueError(
                "Query embedding must be a list or tuple."
        )

        if not query_embedding:
            raise ValueError(
                "Query embedding cannot be empty."
            )

        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            for value in query_embedding
        ):
            raise ValueError(
                "Query embedding must contain only finite numeric values."
            )

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError(
                "top_k must be a positive integer."
            )


        if (
            not isinstance(min_similarity, (int, float))
            or isinstance(min_similarity, bool)
            or not math.isfinite(min_similarity)
            or not -1.0 <= min_similarity <= 1.0
        ):
            raise ValueError(
                "min_similarity must be a finite number "
                "between -1.0 and 1.0."
            )

        scored_results = []

        for record in self.vector_store.records:
            if not isinstance(record, dict):
                continue

            embedding = record.get("embedding")
            chunk = record.get("chunk")

            if not isinstance(embedding, (list, tuple)):
                continue

            if not isinstance(chunk, dict):
                continue

            try:
                similarity = self.cosine_similarity(
                    query_embedding,
                    embedding
                )
            except ValueError:
                continue

            if similarity < min_similarity:
                continue

            scored_results.append({
                "chunk": record["chunk"],
                "score": similarity
            })

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_results[:top_k]
