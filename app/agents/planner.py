from langchain_core.prompts import ChatPromptTemplate
from app.schemas.research_state import ResearchState
from app.services.llm_service import get_llm
from pydantic import BaseModel, Field


class PlanOutput(BaseModel):
    research_plan: list[str] = Field(
        description="A list of 3-5 distinct, targeted research subtopics or questions to comprehensively answer the user query."
    )


PLANNER_SYSTEM_PROMPT = """You are an expert Enterprise Research Planner.
Your role is to analyze a user's research question, decompose it into 3 to 5 clear, objective, and search-ready subtopics.
Each subtopic should target:
1. Core background, technical concepts, and architecture/scope.
2. Latest advancements, state-of-the-art developments, or industry updates.
3. Practical real-world applications, case studies, or production trade-offs.
4. Key challenges, risks, compliance, performance, or limitations.

Ensure queries are concise, highly search-friendly, and avoid unnecessary jargon."""


def create_research_plan(state: ResearchState) -> dict:
    """
    Generate research objectives using the configured OpenAI LLM.
    Falls back gracefully to structured heuristic breakdown if API is unavailable during tests or offline modes.
    """
    user_query = state.get("user_query", "").strip()

    if not user_query:
        raise ValueError("Research question cannot be empty.")

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(PlanOutput)
        prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
            ("user", "User Research Query: {query}")
        ])
        chain = prompt | structured_llm
        result: PlanOutput = chain.invoke({"query": user_query})
        plan = [topic.strip() for topic in result.research_plan if topic.strip()]
        if not plan:
            raise ValueError("LLM returned empty plan")
        return {"research_plan": plan}

    except Exception as e:
        print(f"LLM planner unavailable or failed ({e}); utilizing rule-based decomposition.")
        # Fallback to deterministic high-quality objectives
        fallback_plan = [
            f"Background, architecture and scope of {user_query}",
            f"Latest technical developments and state of the art in {user_query}",
            f"Real-world enterprise applications and case studies of {user_query}",
            f"Benefits, limitations, risks and challenges of {user_query}",
        ]
        return {"research_plan": fallback_plan}
