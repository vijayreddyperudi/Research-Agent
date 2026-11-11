import json
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.research_state import ResearchState
from app.services.llm_service import get_llm

REPORT_SYSTEM_PROMPT = """You are an Enterprise AI Research Synthesis Specialist.
Generate a structured, professional, authoritative, and source-grounded research report based strictly on the provided evidence.

CRITICAL CONSTRAINTS:
1. Never hallucinate facts, metrics, or citations. All findings must be directly grounded in the provided sources.
2. In-text citations should reference the sources by bracketed numbers like [1], [2].
3. If evidence is lacking or inconclusive for any topic, explicitly state the limitation in the Limitations section.

REPORT STRUCTURE:
# [Report Title]

## 1. Executive Summary
- High-level overview of core conclusions and strategic takeaways.

## 2. Research Methodology
- State the objective, search iterations executed, and evidence evaluation metrics applied.

## 3. Key Findings & Insights
- Bullet points summarizing the most critical points discovered.

## 4. In-Depth Analysis
- Break down each research objective with detailed analysis and inline citations [1], [2].

## 5. Evidence Limitations & Risk Analysis
- Explicitly state any gaps, unverified claims, or constraints observed.

## 6. Strategic Recommendations & Conclusion
- Actionable steps forward and summary conclusion.

## 7. References & Sources
- Complete list of evaluated sources: [Index] Title - URL (Credibility: Score/Label)
"""


def generate_fallback_report(state: ResearchState) -> str:
    """Generate structured markdown report when LLM is unavailable."""
    query = state.get("user_query", "Enterprise Research")
    evaluated_sources = state.get("evaluated_sources", [])
    coverage_status = state.get("coverage_status", {})
    plan = state.get("research_plan", [])

    lines = [
        f"# Enterprise Research Report: {query}\n",
        "## 1. Executive Summary",
        f"This report presents an objective evaluation of research into '{query}'. "
        f"A total of {len(evaluated_sources)} verified sources were analyzed across {len(plan)} target research dimensions.\n",
        "## 2. Research Methodology",
        f"- **Primary Query**: {query}",
        f"- **Rounds Executed**: {state.get('research_round', 1)} / {state.get('max_research_rounds', 3)}",
        f"- **Evaluated Sources**: {len(evaluated_sources)} accepted",
        f"- **Overall Sufficiency**: {'Sufficient' if state.get('is_sufficient') else 'Partial Coverage'}\n",
        "## 3. Key Findings",
    ]

    for i, src in enumerate(evaluated_sources[:5], 1):
        lines.append(f"- **{src.get('title', 'Finding')}** [{i}]: {src.get('content', '')[:200]}...")

    lines.append("\n## 4. Topic Analysis")
    for topic in plan:
        lines.append(f"### {topic}")
        matching = [s for s in evaluated_sources if s.get("research_objective") == topic]
        if matching:
            for m in matching:
                lines.append(f"- {m.get('title')}: {m.get('content', '')[:250]} (Source: {m.get('url')})")
        else:
            lines.append("- *No verified evidence gathered during this round.*")

    lines.append("\n## 5. Evidence Limitations")
    missing = [t for t, cov in coverage_status.items() if not cov]
    if missing:
        lines.append(f"- Incomplete coverage on the following topics: {', '.join(missing)}.")
    else:
        lines.append("- All planned research dimensions met minimum quality thresholds.")
    lines.append("- Public web summaries may be subject to changes or restricted access.")

    lines.append("\n## 6. Conclusion")
    lines.append(f"Research indicates substantial multi-dimensional interest in {query}. Ongoing tracking is recommended.\n")

    lines.append("## 7. References")
    for i, src in enumerate(evaluated_sources, 1):
        lines.append(f"[{i}] {src.get('title')} - {src.get('url')} (Quality: {src.get('quality_label', 'Medium')}, Credibility: {src.get('credibility_score', 0.5)})")

    return "\n".join(lines)


def generate_report(state: ResearchState) -> dict:
    """
    Generate the comprehensive final research report using LLM or structured synthesis.
    """
    user_query = state.get("user_query", "")
    evaluated_sources = state.get("evaluated_sources", [])

    sources_summary = []
    for idx, s in enumerate(evaluated_sources, 1):
        sources_summary.append({
            "index": idx,
            "title": s.get("title"),
            "url": s.get("url"),
            "objective": s.get("research_objective"),
            "content": s.get("content", "")[:350],
            "credibility": s.get("credibility_label"),
            "quality": s.get("quality_label")
        })

    prompt_data = {
        "query": user_query,
        "objectives": state.get("research_plan", []),
        "round": state.get("research_round", 1),
        "is_sufficient": state.get("is_sufficient", False),
        "coverage": state.get("coverage_status", {}),
        "sources": sources_summary
    }

    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", REPORT_SYSTEM_PROMPT),
            ("user", "Research Context and Data:\n```json\n{data}\n```\nSynthesize the final report now:")
        ])
        chain = prompt | llm
        response = chain.invoke({"data": json.dumps(prompt_data, indent=2)})
        final_report = response.content
        if not final_report or not final_report.strip():
            raise ValueError("Empty report returned by LLM")
    except Exception as e:
        print(f"LLM synthesis unavailable or failed ({e}); generating structured fallback report.")
        final_report = generate_fallback_report(state)

    return {
        "final_report": final_report,
        "metadata": {
            "total_sources": len(evaluated_sources),
            "research_rounds": state.get("research_round", 1),
            "sufficient": state.get("is_sufficient", False)
        }
    }

