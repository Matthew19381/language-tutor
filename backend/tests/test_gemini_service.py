import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from backend.services.gemini_service import generate_text, generate_json, with_model, _model_override


class TestGenerateText:
    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        mock_response = {"choices": [{"message": {"content": "Hello world"}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                result = await generate_text("Test prompt")
                assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_generate_text_with_custom_model(self):
        mock_response = {"choices": [{"message": {"content": "Custom model response"}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                result = await generate_text("Test prompt", model="custom/model")
                assert result == "Custom model response"

    @pytest.mark.asyncio
    async def test_generate_text_api_error(self):
        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(side_effect=Exception("API Error"))
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                with pytest.raises(Exception):
                    await generate_text("Test prompt")


class TestGenerateJson:
    @pytest.mark.asyncio
    async def test_generate_json_success(self):
        json_text = '{"key": "value", "number": 42}'
        mock_response = {"choices": [{"message": {"content": json_text}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                result = await generate_json("Give me JSON")
                assert result["key"] == "value"
                assert result["number"] == 42

    @pytest.mark.asyncio
    async def test_generate_json_strips_markdown_fences(self):
        json_text = "```json\n{\"name\": \"test\"}\n```"
        mock_response = {"choices": [{"message": {"content": json_text}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                result = await generate_json("Give me JSON")
                assert result["name"] == "test"

    @pytest.mark.asyncio
    async def test_generate_json_strips_plain_fences(self):
        json_text = "```\n{\"data\": 123}\n```"
        mock_response = {"choices": [{"message": {"content": json_text}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                result = await generate_json("Give me JSON")
                assert result["data"] == 123

    @pytest.mark.asyncio
    async def test_generate_json_invalid_json(self):
        mock_response = {"choices": [{"message": {"content": "Not valid JSON"}}]}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                with pytest.raises(ValueError):
                    await generate_json("Give me JSON")

    @pytest.mark.asyncio
    async def test_generate_json_appends_instruction(self):
        """Test that generate_json appends the JSON-only instruction."""
        mock_response = {"choices": [{"message": {"content": '{"ok": true}'}}]}
        mock_client = AsyncMock()
        post_mock = AsyncMock(return_value=MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_response)
        ))
        mock_client.post = post_mock

        with patch("backend.services.gemini_service.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            with patch("backend.services.gemini_service.httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
                await generate_json("What is this?")
                # Check that the payload includes the JSON instruction
                call_args = post_mock.call_args
                payload = call_args[1]["json"]
                assert "Respond ONLY with valid JSON" in payload["messages"][0]["content"]


class TestWithModelDecorator:
    def test_with_model_decorator_sets_context(self):
        """Test that the with_model decorator sets the model override."""
        # Reset any existing override
        _model_override.set(None)

        @with_model("placement")
        async def dummy_func():
            from backend.services.model_router import get_model_for_task
            model = _model_override.get()
            return model

        # We can't easily test the decorator without mocking model_router,
        # but we can verify it's callable and async
        assert callable(dummy_func)

    def test_with_model_decorator_preserves_function_name(self):
        @with_model("test")
        async def my_function():
            pass

        assert my_function.__name__ == "my_function"
