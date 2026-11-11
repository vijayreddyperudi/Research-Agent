from unittest.mock import patch, MagicMock
from app.tools.web_search import search_web
import pytest


def test_search_web_empty_query():
    with pytest.raises(ValueError):
        search_web("")


def test_search_web_invalid_max_results():
    with pytest.raises(ValueError):
        search_web("query", max_results=0)


def test_search_web_mocked():
    with patch("app.tools.web_search.DDGS") as mock_ddgs_cls:
        mock_instance = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_instance
        mock_instance.text.return_value = [
            {"title": "Result 1", "href": "https://example.com/1", "body": "Snippet 1", "date": "2026-01-01"}
        ]

        results = search_web("AI Agents", max_results=1)
        assert len(results) == 1
        assert results[0]["title"] == "Result 1"
        assert results[0]["url"] == "https://example.com/1"
