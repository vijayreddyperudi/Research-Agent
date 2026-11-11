from app.workflow import create_research_graph, should_continue
from app.schemas.research_state import ResearchState


def test_should_continue_sufficient():
    state: ResearchState = {
        "is_sufficient": True,
        "research_round": 1,
        "max_research_rounds": 3
    }
    decision = should_continue(state)
    assert decision == "report_generator"


def test_should_continue_retry():
    state: ResearchState = {
        "is_sufficient": False,
        "research_round": 1,
        "max_research_rounds": 3
    }
    decision = should_continue(state)
    assert decision == "researcher"


def test_should_continue_max_rounds():
    state: ResearchState = {
        "is_sufficient": False,
        "research_round": 3,
        "max_research_rounds": 3
    }
    decision = should_continue(state)
    assert decision == "report_generator"


def test_graph_creation():
    graph = create_research_graph()
    assert graph is not None

