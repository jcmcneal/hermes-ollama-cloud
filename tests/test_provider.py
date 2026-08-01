"""Tests for the Ollama Cloud web search/extract provider plugin."""

from __future__ import annotations

import json
import os
from unittest.mock import patch, MagicMock

import pytest

from hermes_ollama_cloud.provider import (
    OllamaWebSearchProvider,
    _normalize_search_results,
    _normalize_fetch_result,
)


@pytest.fixture
def provider():
    return OllamaWebSearchProvider()


@pytest.fixture(autouse=True)
def clear_api_key():
    old = os.environ.pop("OLLAMA_API_KEY", None)
    yield
    if old is not None:
        os.environ["OLLAMA_API_KEY"] = old


class TestProviderBasics:
    """ABC contract — name, availability, capabilities."""

    def test_name(self, provider):
        assert provider.name == "ollama"

    def test_display_name(self, provider):
        assert provider.display_name == "Ollama Cloud"

    def test_is_available_without_key(self, provider):
        assert provider.is_available() is False

    def test_is_available_with_key(self, provider):
        os.environ["OLLAMA_API_KEY"] = "test-key"
        assert provider.is_available() is True

    def test_supports_search(self, provider):
        assert provider.supports_search() is True

    def test_supports_extract(self, provider):
        assert provider.supports_extract() is True

    def test_get_setup_schema(self, provider):
        schema = provider.get_setup_schema()
        assert schema["name"] == "Ollama Cloud"
        assert schema["web_backend"] == "ollama"
        env_vars = schema["env_vars"]
        assert len(env_vars) == 1
        assert env_vars[0]["key"] == "OLLAMA_API_KEY"


class TestSearchAPIKeyGating:
    """Search returns a clean error dict when no API key is set."""

    def test_search_without_key(self, provider):
        result = provider.search("test query")
        assert result["success"] is False
        assert "OLLAMA_API_KEY" in result["error"]

    def test_search_with_key_makes_request(self, provider):
        os.environ["OLLAMA_API_KEY"] = "test-key"
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        with patch("hermes_ollama_cloud.provider.httpx.post", return_value=mock_response):
            result = provider.search("test query")
        assert result["success"] is True
        assert "web" in result["data"]


class TestExtractAPIKeyGating:
    """Extract returns per-URL error entries when no API key is set."""

    def test_extract_without_key(self, provider):
        result = provider.extract(["https://example.com"])
        assert isinstance(result, list)
        assert len(result) == 1
        assert "error" in result[0]
        assert "OLLAMA_API_KEY" in result[0]["error"]

    def test_extract_with_key_makes_request(self, provider):
        os.environ["OLLAMA_API_KEY"] = "test-key"
        mock_response = MagicMock()
        mock_response.json.return_value = {"title": "Test", "content": "Hello"}
        mock_response.raise_for_status = MagicMock()
        with patch("hermes_ollama_cloud.provider.httpx.post", return_value=mock_response):
            result = provider.extract(["https://example.com"])
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Test"
        assert result[0]["content"] == "Hello"


class TestNormalizeSearchResults:
    """Normalization handles all Ollama response shapes."""

    def test_standard_results(self):
        raw = {
            "results": [
                {"title": "Example", "url": "https://example.com", "content": "Some content"},
            ]
        }
        out = _normalize_search_results(raw)
        assert out["success"] is True
        assert len(out["data"]["web"]) == 1
        assert out["data"]["web"][0]["title"] == "Example"
        assert out["data"]["web"][0]["url"] == "https://example.com"
        assert out["data"]["web"][0]["description"] == "Some content"
        assert out["data"]["web"][0]["position"] == 1

    def test_markdown_links_in_content(self):
        raw = {"content": "[Example](https://example.com)\n[Another](https://another.com)"}
        out = _normalize_search_results(raw)
        assert out["success"] is True
        assert len(out["data"]["web"]) == 2
        assert out["data"]["web"][0]["title"] == "Example"
        assert out["data"]["web"][1]["title"] == "Another"

    def test_json_string_content(self):
        raw = {"content": json.dumps({"results": [{"title": "X", "url": "https://x.com"}]})}
        out = _normalize_search_results(raw)
        assert out["success"] is True
        assert len(out["data"]["web"]) == 1
        assert out["data"]["web"][0]["title"] == "X"

    def test_results_cap_at_10(self):
        results = [{"title": f"R{i}", "url": f"https://r{i}.com"} for i in range(15)]
        out = _normalize_search_results({"results": results})
        assert len(out["data"]["web"]) == 10

    def test_non_dict_response(self):
        out = _normalize_search_results("not a dict")
        assert out["success"] is True
        assert out["data"]["web"] == []

    def test_string_result_items(self):
        raw = {"results": ["https://a.com", "https://b.com"]}
        out = _normalize_search_results(raw)
        assert len(out["data"]["web"]) == 2
        assert out["data"]["web"][0]["url"] == "https://a.com"


class TestNormalizeFetchResult:
    """Fetch normalization handles various response shapes."""

    def test_standard_fetch(self):
        raw = {"title": "Example", "content": "Page content"}
        out = _normalize_fetch_result(raw, fallback_url="https://example.com")
        assert out["url"] == "https://example.com"
        assert out["title"] == "Example"
        assert out["content"] == "Page content"
        assert out["raw_content"] == "Page content"
        assert out["metadata"]["sourceURL"] == "https://example.com"

    def test_text_key_fallback(self):
        raw = {"text": "Text content"}
        out = _normalize_fetch_result(raw, fallback_url="https://example.com")
        assert out["content"] == "Text content"

    def test_non_dict_response(self):
        out = _normalize_fetch_result("plain string", fallback_url="https://example.com")
        assert out["content"] == "plain string"
        assert out["url"] == "https://example.com"

    def test_metadata_source_url_injection(self):
        raw = {"title": "T", "content": "C", "metadata": {"other": "val"}}
        out = _normalize_fetch_result(raw, fallback_url="https://example.com")
        assert out["metadata"]["sourceURL"] == "https://example.com"
        assert out["metadata"]["other"] == "val"
