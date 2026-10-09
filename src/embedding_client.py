from google import genai


class GeminiEmbeddingClient:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
            return

        from src.gemini_client import GeminiClient

        gemini_client = GeminiClient()
        self.client = gemini_client.client

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError(
                "Embedding text cannot be empty."
            )

        try:
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned no embedding."
                )

            values = response.embeddings[0].values

            if not values:
                raise RuntimeError(
                    "Gemini returned an empty embedding."
                )

            return list(values)

        except Exception as exc:
            raise RuntimeError(
                f"Gemini embedding request failed: {exc}"
            ) from exc