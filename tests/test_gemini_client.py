from unittest.mock import MagicMock

import pytest

from src.gemini_client import GeminiClient


def test_gemini_api_key_exists():
    client = GeminiClient()

    assert client.client is not None


def test_gemini_generate():
    client = GeminiClient()

    mock_response = MagicMock()
    mock_response.text = (
        "LeaseLens API test successful."
    )

    client.client.models.generate_content = MagicMock(
        return_value=mock_response
    )

    response = client.generate(
        "Reply with exactly: LeaseLens API test successful."
    )

    assert response == (
        "LeaseLens API test successful."
    )

    client.client.models.generate_content.assert_called_once_with(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: LeaseLens API test successful."
    )


def test_empty_prompt():
    client = GeminiClient()

    with pytest.raises(
        ValueError,
        match="Gemini prompt cannot be empty"
    ):
        client.generate("")


def test_whitespace_prompt():
    client = GeminiClient()

    with pytest.raises(
        ValueError,
        match="Gemini prompt cannot be empty"
    ):
        client.generate("   ")

def test_gemini_empty_response():
    client = GeminiClient()

    mock_response = MagicMock()
    mock_response.text = None

    client.client.models.generate_content = MagicMock(
        return_value=mock_response
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini API request failed"
    ):
        client.generate("Test prompt")


def test_gemini_non_string_response():
    client = GeminiClient()

    mock_response = MagicMock()
    mock_response.text = 12345

    client.client.models.generate_content = MagicMock(
        return_value=mock_response
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini API request failed"
    ):
        client.generate("Test prompt")


def test_gemini_api_failure():
    client = GeminiClient()

    client.client.models.generate_content = MagicMock(
        side_effect=Exception("API unavailable")
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini API request failed"
    ):
        client.generate("Test prompt")