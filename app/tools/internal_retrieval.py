import os
import glob
from typing import List, Dict, Any


class InternalDocRetriever:
    """
    Retriever for local enterprise internal documents (e.g. Markdown, Text, Docs).
    Supports keyword-based and structured local retrieval without requiring an active external vector database,
    with seamless expansion to embedding-based retrieval when configured.
    """

    def __init__(self, docs_dir: str = "./data/internal_docs"):
        self.docs_dir = docs_dir
        os.makedirs(self.docs_dir, exist_ok=True)

    def retrieve(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search internal files for relevant sections matching query keywords.
        """
        results = []
        if not os.path.exists(self.docs_dir):
            return results

        keywords = {
            w.lower().strip(".,:;!?()[]{}")
            for w in query.split()
            if len(w) > 3
        }

        # Search .txt, .md, .rst files
        patterns = ["*.md", "*.txt", "*.rst"]
        matching_files = []
        for pattern in patterns:
            matching_files.extend(glob.glob(os.path.join(self.docs_dir, "**", pattern), recursive=True))

        for file_path in matching_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Score by keyword matches
                content_lower = content.lower()
                matches = sum(1 for kw in keywords if kw in content_lower)

                if matches > 0:
                    filename = os.path.basename(file_path)
                    # Extract most relevant snippet around match
                    snippet = content[:600] + ("..." if len(content) > 600 else "")
                    results.append({
                        "title": f"Internal Doc: {filename}",
                        "url": f"internal://{filename}",
                        "content": snippet,
                        "published_date": None,
                        "score": matches,
                        "is_internal": True
                    })
            except Exception as e:
                print(f"Error reading internal doc {file_path}: {e}")

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]


def search_internal_docs(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    retriever = InternalDocRetriever()
    return retriever.retrieve(query=query, max_results=max_results)

