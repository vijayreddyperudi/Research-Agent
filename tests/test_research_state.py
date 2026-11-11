from app.schemas.research_state import ResearchState


def test_research_state_initialization():
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

    assert state["user_query"] != ""
    assert state["research_round"] == 0
    assert state["max_research_rounds"] == 3
