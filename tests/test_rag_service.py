from src.rag_service import RAGService


class FakeEmbeddingClient:

    def embed(self, text: str) -> list[float]:
        if "security deposit" in text.lower():
            return [0.0, 0.0, 1.0]

        return [1.0, 0.0, 0.0]


class FakeGeminiClient:

    def __init__(self):
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt

        return (
            "The security deposit is ₹40,000 "
            "[CHUNK-002]."
        )


class FakeVectorStore:

    def __init__(self):
        self.records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-001",
                    "clause_id": "CLAUSE-002",
                    "section_title": "RENT",
                    "clause_type": "RENT",
                    "text": "Monthly rent is ₹25,000.",
                },
                "embedding": [1.0, 0.0, 0.0]
            },
            {
                "chunk": {
                    "chunk_id": "CHUNK-002",
                    "clause_id": "CLAUSE-003",
                    "section_title": "SECURITY DEPOSIT",
                    "clause_type": "SECURITY_DEPOSIT",
                    "text": "The security deposit is ₹40,000.",
                },
                "embedding": [0.0, 0.0, 1.0]
            }
        ]


def create_service():
    return RAGService(
        vector_store=FakeVectorStore(),
        embedding_client=FakeEmbeddingClient(),
        gemini_client=FakeGeminiClient()
    )


def test_rag_returns_answer_and_sources():

    service = create_service()

    result = service.answer(
        "What is the security deposit?"
    )

    assert "answer" in result
    assert "sources" in result

    assert (
        "₹40,000"
        in result["answer"]
    )

    assert len(result["sources"]) > 0

    assert (
        result["sources"][0]["chunk_id"]
        == "CHUNK-002"
    )


def test_rag_uses_retrieved_context():

    service = create_service()

    service.answer(
        "What is the security deposit?"
    )

    prompt = (
        service.gemini_client.last_prompt
    )

    assert (
        "CHUNK-002"
        in prompt
    )

    assert (
        "The security deposit is ₹40,000."
        in prompt
    )


def test_rag_prompt_is_grounded():

    service = create_service()

    service.answer(
        "What is the security deposit?"
    )

    prompt = (
        service.gemini_client.last_prompt
    )

    assert (
        "ONLY the lease evidence"
        in prompt
    )

    assert (
        "Do not use outside knowledge."
        in prompt
    )

    assert (
        "Do not invent facts."
        in prompt
    )


def test_empty_question_is_rejected():

    service = create_service()

    try:
        service.answer("")
        assert False
    except ValueError as exc:
        assert (
            str(exc)
            == "Question cannot be empty."
        )


def test_whitespace_question_is_rejected():

    service = create_service()

    try:
        service.answer("   ")
        assert False
    except ValueError as exc:
        assert (
            str(exc)
            == "Question cannot be empty."
        )

    def test_invalid_top_k_is_rejected():

        service = create_service()

    try:
        service.answer(
            "What is the rent?",
            top_k=0
        )
        assert False
    except ValueError as exc:
        assert (
            str(exc)
            == "top_k must be greater than zero."
        )


def test_negative_top_k_is_rejected():

    service = create_service()

    try:
        service.answer(
            "What is the rent?",
            top_k=-1
        )
        assert False
    except ValueError as exc:
        assert (
            str(exc)
            == "top_k must be greater than zero."
        )


class EmptyVectorStore:

    def __init__(self):
        self.records = []


def test_no_retrieved_chunks_returns_grounded_message():

    service = RAGService(
        vector_store=EmptyVectorStore(),
        embedding_client=FakeEmbeddingClient(),
        gemini_client=FakeGeminiClient()
    )

    result = service.answer(
        "What is the rent?"
    )

    assert (
        result["answer"]
        == "I could not find relevant information in the lease."
    )

    assert result["sources"] == []


class FailingGeminiClient:

    def generate(self, prompt: str) -> str:
        raise RuntimeError(
            "Gemini unavailable"
        )


def test_gemini_failure_is_reported():

    service = RAGService(
        vector_store=FakeVectorStore(),
        embedding_client=FakeEmbeddingClient(),
        gemini_client=FailingGeminiClient()
    )

    try:
        service.answer(
            "What is the security deposit?"
        )
        assert False
    except RuntimeError as exc:
        assert (
            str(exc)
            == "RAG generation failed: Gemini unavailable"
        )


class FailingRetrievalService:

    def search(self, query, top_k=5):
        raise RuntimeError(
            "Vector retrieval unavailable"
        )


def test_retrieval_failure_is_reported():

    service = create_service()

    service.retrieval_service = (
        FailingRetrievalService()
    )

    try:
        service.answer(
            "What is the security deposit?"
        )
        assert False
    except RuntimeError as exc:
        assert (
            str(exc)
            == (
                "RAG retrieval failed: "
                "Vector retrieval unavailable"
            )
        )


class MalformedVectorStore:

    def __init__(self):
        self.records = [
            {
                "chunk": {
                    "section_title": "RENT",
                    "clause_type": "RENT",
                    "text": "Monthly rent is ₹25,000."
                },
                "embedding": [1.0, 0.0, 0.0]
            }
        ]


def test_malformed_chunks_are_not_used_as_sources():

    service = RAGService(
        vector_store=MalformedVectorStore(),
        embedding_client=FakeEmbeddingClient(),
        gemini_client=FakeGeminiClient()
    )

    result = service.answer(
        "What is the rent?"
    )

    assert (
        result["answer"]
        == (
            "I could not find usable "
            "lease evidence for this question."
        )
    )

    assert result["sources"] == []