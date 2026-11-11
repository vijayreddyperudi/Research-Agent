from app.schemas.research_state import ResearchState
from app.tools.web_search import search_web
from app.tools.internal_retrieval import search_internal_docs


def conduct_research(state: ResearchState) -> dict:
    """
    Execute web searches and internal document retrieval for research objectives.
    """
    research_plan = state.get("research_plan", [])
    if not research_plan:
        raise ValueError("Research plan cannot be empty.")

    current_round = state.get("research_round", 0) + 1
    existing_results = list(state.get("search_results", []))
    seen_urls = {res.get("url") for res in existing_results if res.get("url")}
    
    new_results = []
    failed_objectives = []
    coverage_status = state.get("coverage_status", {})

    # In round > 1, focus specifically on uncovered objectives
    objectives_to_search = [
        obj for obj in research_plan
        if not coverage_status.get(obj, False)
    ] or research_plan

    for objective in objectives_to_search:
        print(f"\n[Round {current_round}] Researching: {objective}")

        # 1. Retrieve from internal docs first if available
        try:
            internal_docs = search_internal_docs(query=objective, max_results=2)
            for doc in internal_docs:
                url = doc.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    doc["research_objective"] = objective
                    new_results.append(doc)
        except Exception as err:
            print(f"Internal retrieval error: {err}")

        # 2. Search web sources
        try:
            results = search_web(query=objective, max_results=5)
            if not results:
                print(f"No web results found for: {objective}")
                failed_objectives.append(objective)
                continue

            for result in results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    result["research_objective"] = objective
                    new_results.append(result)

        except Exception as error:
            print(f"Web search error for '{objective}': {error}")
            failed_objectives.append(objective)

    combined_results = existing_results + new_results

    print(f"\nRound {current_round} Complete:")
    print(f"New sources collected: {len(new_results)}")
    print(f"Total cumulative sources: {len(combined_results)}")

    return {
        "search_results": combined_results,
        "failed_objectives": failed_objectives,
        "research_round": current_round
    }
