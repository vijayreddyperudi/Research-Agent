from unittest.mock import patch
from app.schemas.research_state import ResearchState
from app.agents.researcher import conduct_research


def test_conduct_research_mocked():
    state: ResearchState = {
        "user_query": "Test Query",
        "research_plan": ["Objective 1", "Objective 2"],
        "search_results": [],
        "evaluated_sources": [],
        "research_round": 0,
        "max_research_rounds": 3,
        "coverage_status": {},
        "is_sufficient": False,
        "final_report": ""
    }

    mock_results = [
        {"title": "Test Title 1", "url": "https://example.com/1", "content": "Sample content 1", "published_date": "2026-01-01"},
        {"title": "Test Title 2", "url": "https://example.com/2", "content": "Sample content 2", "published_date": "2026-01-02"}
    ]

    with patch("app.agents.researcher.search_web", return_value=mock_results):
        result = conduct_research(state)
        assert len(result["search_results"]) >= 2
        assert result["research_round"] == 1
