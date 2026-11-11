from datetime import datetime
from urllib.parse import urlparse

from app.schemas.research_state import ResearchState
from app.config import settings

# Trusted domains: official organizations and established research publishers
TRUSTED_DOMAINS = {
    "arxiv.org",
    "nature.com",
    "science.org",
    "springer.com",
    "sciencedirect.com",
    "acm.org",
    "ieee.org",
    "openai.com",
    "microsoft.com",
    "google.com",
    "ibm.com",
    "nvidia.com",
    "aws.amazon.com",
    "ai.google",
    "deepmind.google",
    "huggingface.co",
}

# Established educational and technology publishers
ESTABLISHED_DOMAINS = {
    "coursera.org",
    "geeksforgeeks.org",
    "masterofcode.com",
    "crn.com",
    "nextmsc.com",
    "upgrad.com",
    "wiley.com",
    "oxjournal.org",
    "github.com",
    "stackoverflow.com",
    "medium.com",
    "techcrunch.com",
    "theverge.com",
    "venturebeat.com",
    "mit.edu",
    "stanford.edu"
}

LOW_CONFIDENCE_DOMAINS = {
    "wikipedia.org",
    "researchgate.net",
}


def get_domain(url: str) -> str:
    """Extract a normalized hostname."""
    try:
        if url.startswith("internal://"):
            return "internal.enterprise"
        hostname = urlparse(url).hostname or ""
        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except ValueError:
        return ""


def get_domain_credibility(url: str) -> tuple[float, str]:
    """Estimate credibility from the source domain."""
    if url.startswith("internal://"):
        return 0.95, "Internal Verified Enterprise Document"

    domain = get_domain(url)

    if not domain:
        return 0.0, "Invalid domain"

    for trusted in TRUSTED_DOMAINS:
        if domain == trusted or domain.endswith("." + trusted):
            return 0.90, "Trusted publisher or official source"

    for established in ESTABLISHED_DOMAINS:
        if domain == established or domain.endswith("." + established):
            return 0.70, "Established publisher"

    for low_confidence in LOW_CONFIDENCE_DOMAINS:
        if domain == low_confidence or domain.endswith("." + low_confidence):
            return 0.35, "Low-confidence reference source"

    if domain.endswith(".edu") or domain.endswith(".gov"):
        return 0.90, "Academic or government source"

    return 0.50, "General web source"


def extract_keywords(text: str) -> set[str]:
    """Extract basic keywords for relevance scoring."""
    stop_words = {
        "the", "and", "for", "with", "from", "what",
        "this", "that", "into", "about", "related",
        "identify", "understand", "evaluate", "find",
        "latest", "recent", "developments", "real",
        "world", "examples", "information", "scope",
        "background", "overview"
    }

    return {
        word.lower().strip(".,:;!?()[]{}")
        for word in text.split()
        if len(word) > 2 and word.lower() not in stop_words
    }


def calculate_relevance(objective: str, title: str, content: str) -> float:
    """Calculate keyword overlap between objective and evidence."""
    objective_keywords = extract_keywords(objective)
    if not objective_keywords:
        return 0.0

    source_keywords = extract_keywords(f"{title} {content}")
    matched = objective_keywords.intersection(source_keywords)
    return round(len(matched) / len(objective_keywords), 2)


def calculate_content_quality(title: str, content: str, warning: bool = False) -> float:
    """Estimate evidence quality from title and snippet."""
    score = 1.0

    if not title:
        return 0.0

    if len(content) < 50:
        score -= 0.40
    elif len(content) < 150:
        score -= 0.15

    if len(title) > 180:
        score -= 0.30

    if warning:
        score -= 0.20

    return round(max(0.0, min(1.0, score)), 2)


def calculate_freshness(published_date) -> tuple[float, str]:
    """Estimate freshness using publication date."""
    if not published_date:
        return 0.60, "Date unavailable (Standard)"

    try:
        published = datetime.strptime(
            str(published_date)[:10],
            "%Y-%m-%d"
        ).date()

        today = datetime.now().date()
        age_days = (today - published).days

        if age_days < 0:
            return 0.0, "Future publication date"
        if age_days <= 365:
            return 1.0, "Fresh source (within 1 year)"
        if age_days <= 730:
            return 0.75, "Moderately recent source (1-2 years)"
        if age_days <= 1095:
            return 0.50, "Older source (2-3 years)"
        return 0.30, "Archival source (>3 years)"

    except (ValueError, TypeError):
        return 0.50, "Unparsed publication date"


def evaluate_research(state: ResearchState) -> dict:
    """Evaluate source relevance, credibility, freshness and quality."""
    research_plan = state.get("research_plan", [])
    search_results = state.get("search_results", [])

    if not research_plan:
        raise ValueError("Research plan cannot be empty.")

    evaluated_sources = []
    rejected_sources = []
    seen_urls = set()

    coverage_counts = {
        objective: 0 for objective in research_plan
    }

    for source in search_results:
        url = source.get("url", "").strip()
        title = source.get("title", "").strip()
        content = source.get("content", "").strip()
        objective = source.get("research_objective", "")

        reasons = []

        is_internal = url.startswith("internal://")
        parsed_url = urlparse(url)

        if not is_internal and (
            not url
            or parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
        ):
            reasons.append("Invalid URL")
        elif url in seen_urls:
            reasons.append("Duplicate URL")

        if not title:
            reasons.append("Missing title")
        if len(content) < 30:
            reasons.append("Insufficient content")

        if reasons:
            rejected_sources.append({
                **source,
                "evaluation_status": "rejected",
                "rejection_reasons": reasons
            })
            continue

        seen_urls.add(url)

        credibility_score, credibility_label = get_domain_credibility(url)
        relevance_score = calculate_relevance(objective, title, content)
        content_quality_score = calculate_content_quality(
            title, content, source.get("title_warning", False)
        )
        freshness_score, freshness_label = calculate_freshness(
            source.get("published_date")
        )

        quality_score = round(
            credibility_score * 0.30
            + relevance_score * 0.30
            + content_quality_score * 0.20
            + freshness_score * 0.20,
            2
        )

        if quality_score >= 0.70:
            quality_label = "High"
        elif quality_score >= 0.45:
            quality_label = "Medium"
        else:
            quality_label = "Low"

        evaluated_source = source.copy()
        evaluated_source.update({
            "is_relevant": relevance_score >= 0.10,
            "relevance_score": relevance_score,
            "credibility_score": credibility_score,
            "credibility_label": credibility_label,
            "content_quality_score": content_quality_score,
            "freshness_score": freshness_score,
            "freshness_label": freshness_label,
            "quality_score": quality_score,
            "quality_label": quality_label,
            "evaluation_status": "accepted"
        })

        evaluated_sources.append(evaluated_source)
        if objective in coverage_counts:
            coverage_counts[objective] += 1

    # Require at least 1 reliable source per objective
    coverage_status = {
        objective: count >= 1
        for objective, count in coverage_counts.items()
    }

    min_sources = settings.min_useful_sources
    is_sufficient = (
        len(evaluated_sources) >= min_sources
        and all(coverage_status.values())
    )

    return {
        "evaluated_sources": evaluated_sources,
        "rejected_sources": rejected_sources,
        "coverage_status": coverage_status,
        "is_sufficient": is_sufficient
    }
