from unittest.mock import MagicMock, patch

import pytest

from llm.client import LLMClientError, generate_text


def test_generate_text_raises_error_when_api_key_missing():
    with (
        patch("llm.client.settings.llm_api_key", ""),
        pytest.raises(LLMClientError, match="LLM_API_KEY"),
    ):
        generate_text("prompt")


def test_generate_text_raises_error_when_model_missing():
    with (
        patch("llm.client.settings.llm_api_key", "test-key"),
        patch("llm.client.settings.llm_model", ""),
        pytest.raises(LLMClientError, match="LLM_MODEL"),
    ):
        generate_text("prompt")


def test_generate_text_returns_llm_content():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "  Generated answer  "

    with (
        patch("llm.client.settings.llm_api_key", "test-key"),
        patch("llm.client.settings.llm_model", "test-model"),
        patch("llm.client.OpenAI") as mock_openai,
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        result = generate_text("prompt", system_prompt="system")

    assert result == "Generated answer"
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["temperature"] == 0
    messages = call_kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
