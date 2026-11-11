from app.agents.evaluator import evaluate_research, get_domain_credibility
from app.schemas.research_state import ResearchState


def test_get_domain_credibility():
    score, label = get_domain_credibility("https://openai.com/research")
    assert score == 0.90
    assert "Trusted" in label

    score_internal, label_internal = get_domain_credibility("internal://guide.md")
    assert score_internal == 0.95
    assert "Internal" in label_internal


def test_evaluate_research():
    state: ResearchState = {
        "user_query": "Test Topic",
        "research_plan": ["Objective 1", "Objective 2"],
        "search_results": [
            {
                "title": "Objective 1 Comprehensive Research",
                "url": "https://nature.com/articles/s41586",
                "content": "This is a detailed analysis covering Objective 1 comprehensive research content with extensive data and evaluation.",
                "research_objective": "Objective 1"
            },
            {
                "title": "Objective 2 In-Depth Analysis",
                "url": "https://openai.com/blog/sample",
                "content": "This is another thorough text regarding Objective 2 in-depth analysis and findings across modern machine learning benchmarks.",
                "research_objective": "Objective 2"
            }
        ],
        "evaluated_sources": [],
        "rejected_sources": [],
        "failed_objectives": [],
        "research_round": 1,
        "max_research_rounds": 3,
        "coverage_status": {},
        "is_sufficient": False,
        "final_report": "",
        "metadata": {}
    }

    result = evaluate_research(state)
    assert len(result["evaluated_sources"]) == 2
    assert result["coverage_status"]["Objective 1"] is True
    assert result["coverage_status"]["Objective 2"] is True

