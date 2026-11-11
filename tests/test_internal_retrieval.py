from app.tools.internal_retrieval import search_internal_docs, InternalDocRetriever
import os


def test_internal_retriever_empty(tmp_path):
    retriever = InternalDocRetriever(docs_dir=str(tmp_path))
    res = retriever.retrieve("artificial intelligence")
    assert res == []


def test_internal_retriever_matches(tmp_path):
    doc_path = tmp_path / "test_doc.md"
    doc_path.write_text("Artificial intelligence and machine learning models are advancing rapidly.", encoding="utf-8")

    retriever = InternalDocRetriever(docs_dir=str(tmp_path))
    res = retriever.retrieve("intelligence models")
    assert len(res) == 1
    assert res[0]["url"] == "internal://test_doc.md"
    assert res[0]["is_internal"] is True
    assert "artificial intelligence" in res[0]["content"].lower()

