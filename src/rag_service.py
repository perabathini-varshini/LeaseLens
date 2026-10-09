from src.gemini_client import GeminiClient
from src.retrieval_service import RetrievalService


class RAGService:
    def __init__(
        self,
        vector_store,
        embedding_client=None,
        gemini_client=None
    ):
        self.retrieval_service = RetrievalService(
            vector_store,
            embedding_client=embedding_client
        )

        self.gemini_client = (
            gemini_client
            or GeminiClient()
        )

    def answer(
        self,
        query: str,
        top_k: int = 5
    ) -> dict:

        if not query or not query.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        try:
            retrieved_results = (
                self.retrieval_service.search(
                    query,
                    top_k=top_k
                )
            )
        except Exception as exc:
            raise RuntimeError(
                f"RAG retrieval failed: {exc}"
            ) from exc

        if not retrieved_results:
            return {
                "answer": (
                    "I could not find relevant "
                    "information in the lease."
                ),
                "sources": []
            }

        context_parts = []
        sources = []

        for result in retrieved_results:
            chunk = result.get("chunk", {})

            chunk_id = chunk.get("chunk_id")

            if not chunk_id:
                continue

            chunk_text = chunk.get("text", "").strip()

            if not chunk_text:
                continue

            context_parts.append(
                f"[{chunk_id}] "
                f"Section: "
                f"{chunk.get('section_title', '')}\n"
                f"Clause Type: "
                f"{chunk.get('clause_type', '')}\n"
                f"{chunk_text}"
            )

            sources.append({
                "chunk_id": chunk_id,
                "clause_id": chunk.get("clause_id"),
                "section_title": chunk.get(
                    "section_title"
                ),
                "clause_type": chunk.get(
                    "clause_type"
                ),
                "text": chunk_text,
                "score": result.get("score")
            })

        if not context_parts:
            return {
                "answer": (
                    "I could not find usable "
                    "lease evidence for this question."
                ),
                "sources": []
            }

        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
You are LeaseLens, a lease document analysis assistant.

Answer the user's question using ONLY the lease evidence
provided below.

Do not use outside knowledge.
Do not invent facts.
Do not make assumptions about information that is
not present in the retrieved evidence.

If the evidence does not contain enough information
to answer the question, clearly say that the lease
does not provide enough information.

Always keep the answer grounded in the provided
lease evidence.

User question:
{query}

Retrieved lease evidence:
{context}

Return a concise and clear answer.
When making a factual claim, reference the relevant
chunk ID, such as [CHUNK-001].
"""

        try:
            answer = self.gemini_client.generate(
                prompt
            )
        except Exception as exc:
            raise RuntimeError(
                f"RAG generation failed: {exc}"
            ) from exc

        return {
            "answer": answer,
            "sources": sources
        }