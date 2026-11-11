
import time

from ddgs import DDGS
from ddgs.exceptions import DDGSException


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web with retry handling.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    for attempt in range(1, 4):

        try:
            search_results = []

            with DDGS() as ddgs:
                results = ddgs.text(
                    query,
                    max_results=max_results
                )

                for result in results:
                    search_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "content": result.get("body", ""),
                        "published_date": result.get("date")
                    })

            return search_results

        except DDGSException as error:

            print(
                f"Search attempt {attempt} failed: {error}"
            )

            if attempt < 3:
                time.sleep(2)

    print(f"Search failed after 3 attempts: {query}")

    return []
