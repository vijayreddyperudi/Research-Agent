"""
LangGraph Workflow Orchestrator for Enterprise AI Research Agent
Implements state transitions between Planner -> Researcher -> Evaluator -> (Loop or Report Generator) -> END
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from app.schemas.research_state import ResearchState
from app.agents.planner import create_research_plan
from app.agents.researcher import conduct_research
from app.agents.evaluator import evaluate_research
from app.agents.report_generator import generate_report


def should_continue(state: ResearchState) -> Literal["researcher", "report_generator"]:
    """
    Conditional routing function:
    - If evidence is sufficient -> generate report.
    - If evidence is insufficient and research_round < max_research_rounds -> repeat research.
    - Otherwise (rounds exhausted) -> proceed to report generation with disclosed limitations.
    """
    is_sufficient = state.get("is_sufficient", False)
    current_round = state.get("research_round", 1)
    max_rounds = state.get("max_research_rounds", 3)

    if is_sufficient:
        print("[Workflow] Evidence sufficiency achieved. Routing to report generator.")
        return "report_generator"

    if current_round < max_rounds:
        print(f"[Workflow] Round {current_round}/{max_rounds}: Insufficient evidence. Routing to researcher for additional search.")
        return "researcher"

    print(f"[Workflow] Max research rounds ({max_rounds}) reached. Routing to report generator with limitations.")
    return "report_generator"


def create_research_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(ResearchState)

    # Add agent nodes
    workflow.add_node("planner", create_research_plan)
    workflow.add_node("researcher", conduct_research)
    workflow.add_node("evaluator", evaluate_research)
    workflow.add_node("report_generator", generate_report)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Connect nodes
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "evaluator")

    # Conditional routing after evaluation
    workflow.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "researcher": "researcher",
            "report_generator": "report_generator"
        }
    )

    workflow.add_edge("report_generator", END)

    return workflow.compile()


# Pre-compiled graph instance
research_graph = create_research_graph()


def run_research(query: str, max_rounds: int = 3) -> dict:
    """
    Synchronous helper to execute the full research agent workflow.
    """
    initial_state: ResearchState = {
        "user_query": query,
        "research_plan": [],
        "search_results": [],
        "evaluated_sources": [],
        "rejected_sources": [],
        "failed_objectives": [],
        "research_round": 0,
        "max_research_rounds": max_rounds,
        "coverage_status": {},
        "is_sufficient": False,
        "final_report": "",
        "metadata": {}
    }

    final_state = research_graph.invoke(initial_state)
    return final_state

