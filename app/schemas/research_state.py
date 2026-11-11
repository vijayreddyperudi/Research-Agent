from typing import TypedDict, Any, Optional


class ResearchState(TypedDict, total=False):
    # Original question from the user
    user_query: str

    # Topics and plan objectives identified by the planner
    research_plan: list[str]

    # Information collected by the researcher (web search + internal docs)
    search_results: list[dict[str, Any]]

    # Sources evaluated and classified
    evaluated_sources: list[dict[str, Any]]

    # Sources rejected during evaluation
    rejected_sources: list[dict[str, Any]]

    # Failed objectives/search queries during research
    failed_objectives: list[str]

    # Research iteration tracking
    research_round: int
    max_research_rounds: int

    # Tracks whether each research topic has sufficient coverage
    coverage_status: dict[str, bool]

    # Evaluator's sufficiency decision
    is_sufficient: bool

    # Final generated report and execution metadata
    final_report: str
    metadata: dict[str, Any]
