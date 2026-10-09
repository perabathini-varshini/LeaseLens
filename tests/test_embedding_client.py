from unittest.mock import MagicMock

import pytest

from src.embedding_client import GeminiEmbeddingClient


def create_client():
    mock_client = MagicMock()

    mock_response = MagicMock()

    mock_embedding = MagicMock()

    mock_embedding.values = [
        0.1,
        0.2,
        0.3,
        0.4
    ]

    mock_response.embeddings = [
        mock_embedding
    ]

    mock_client.models.embed_content = MagicMock(
        return_value=mock_response
    )

    return (
        GeminiEmbeddingClient(
            client=mock_client
        ),
        mock_client
    )


def test_embedding_generation():
    client, mock_client = create_client()

    embedding = client.embed(
        "The monthly rent is INR 50000."
    )

    assert embedding == [
        0.1,
        0.2,
        0.3,
        0.4
    ]

    mock_client.models.embed_content.assert_called_once_with(
        model="gemini-embedding-001",
        contents="The monthly rent is INR 50000."
    )


def test_empty_text():
    client, _ = create_client()

    with pytest.raises(
        ValueError,
        match="Embedding text cannot be empty"
    ):
        client.embed("")


def test_whitespace_text():
    client, _ = create_client()

    with pytest.raises(
        ValueError,
        match="Embedding text cannot be empty"
    ):
        client.embed("   ")


def test_missing_embeddings():
    client, mock_client = create_client()

    mock_response = MagicMock()
    mock_response.embeddings = []

    mock_client.models.embed_content.return_value = (
        mock_response
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini returned no embedding"
    ):
        client.embed(
            "The tenant shall pay rent."
        )


def test_empty_embedding():
    client, mock_client = create_client()

    mock_response = MagicMock()

    mock_embedding = MagicMock()
    mock_embedding.values = []

    mock_response.embeddings = [
        mock_embedding
    ]

    mock_client.models.embed_content.return_value = (
        mock_response
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini returned an empty embedding"
    ):
        client.embed(
            "The tenant shall pay rent."
        )