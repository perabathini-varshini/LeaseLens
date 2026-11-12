
import math

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
        if (
            not isinstance(text, str)
            or not text.strip()
        ):
            raise ValueError(
                "Embedding text must be a non-empty string."
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

            try:
                valid_values = all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in values
            )
            except OverflowError:
                valid_values = False

            if not valid_values:
                raise RuntimeError(
                    "Gemini returned invalid embedding values."
        )

            return [float(value) for value in values]

        except Exception as exc:
            if (
                isinstance(exc, RuntimeError)
                and str(exc).startswith("Gemini returned")
            ):
                raise

            raise RuntimeError(
                f"Gemini embedding request failed: {exc}"
            ) from exc
