from app.schemas.research_state import ResearchState
from app.agents.planner import create_research_plan


def test_create_research_plan():
    state: ResearchState = {
        "user_query": "Research the latest developments in Generative AI",
        "research_plan": [],
        "search_results": [],
        "evaluated_sources": [],
        "research_round": 0,
        "max_research_rounds": 3,
        "coverage_status": {},
        "is_sufficient": False,
        "final_report": ""
    }

    result = create_research_plan(state)
    assert len(result["research_plan"]) >= 3
    assert all(isinstance(topic, str) for topic in result["research_plan"])
    assert all(topic.strip() for topic in result["research_plan"])
