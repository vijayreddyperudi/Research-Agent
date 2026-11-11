import sys
import os
from pathlib import Path

# Ensure project root is in sys.path regardless of where streamlit is launched
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import time
from app.workflow import run_research
from app.config import settings

st.set_page_config(
    page_title="Enterprise AI Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔍 Enterprise AI Research Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Autonomous, Source-Grounded Multi-Step Research Assistant powered by LangGraph</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Agent Configuration")

    model_option = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )
    max_rounds = st.slider("Max Search Iterations", min_value=1, max_value=5, value=settings.max_research_rounds)
    min_sources = st.slider("Min Sources Target", min_value=3, max_value=10, value=settings.min_useful_sources)
    
    st.markdown("---")
    st.markdown("### 📋 Agent Workflow")
    st.markdown("""
    1. **Planner**: Query breakdown into 4 objectives.
    2. **Researcher**: Multi-source web search & internal doc retrieval.
    3. **Evaluator**: Credibility, relevance, and coverage scoring.
    4. **Loop/Router**: Iterate if evidence is insufficient.
    5. **Report Generator**: Synthesis with citations & limitations.
    """)

# Main Input Section
query = st.text_area(
    "What would you like the agent to research?",
    placeholder="e.g., Explain the advancements in Small Language Models (SLMs) and on-device AI inference",
    height=90
)

col_run, col_clear = st.columns([1, 6])
with col_run:
    start_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)

if start_btn:
    if not query.strip():
        st.warning("Please enter a research topic or question.")
    else:
        status_box = st.status("Executing Research Workflow...", expanded=True)
        start_time = time.time()
        
        try:
            status_box.write("🧠 **Planner**: Decomposing research query into structured objectives...")
            result = run_research(query=query.strip(), max_rounds=max_rounds)
            duration = round(time.time() - start_time, 2)
            status_box.update(label=f"✅ Research Completed in {duration}s!", state="complete", expanded=False)

            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Rounds Executed", f"{result.get('research_round', 1)} / {max_rounds}")
            with m2:
                st.metric("Total Sources Analyzed", len(result.get('search_results', [])))
            with m3:
                st.metric("Verified Sources", len(result.get('evaluated_sources', [])))
            with m4:
                is_suff = result.get('is_sufficient', False)
                st.metric("Evidence Sufficiency", "Sufficient ✅" if is_suff else "Partial ⚠️")

            tab1, tab2, tab3 = st.tabs(["📄 Final Research Report", "🔎 Evaluated Sources", "🗺️ Research Plan & Coverage"])

            with tab1:
                st.markdown(result.get("final_report", "No report generated."))
                st.download_button(
                    label="📥 Download Markdown Report",
                    data=result.get("final_report", ""),
                    file_name=f"research_report_{int(time.time())}.md",
                    mime="text/markdown"
                )

            with tab2:
                sources = result.get("evaluated_sources", [])
                if sources:
                    for i, s in enumerate(sources, 1):
                        with st.expander(f"[{i}] {s.get('title', 'Source')} (Quality: {s.get('quality_label')})"):
                            st.write(f"**URL:** [{s.get('url')}]({s.get('url')})")
                            st.write(f"**Objective:** {s.get('research_objective')}")
                            st.write(f"**Relevance Score:** {s.get('relevance_score')} | **Credibility:** {s.get('credibility_score')} ({s.get('credibility_label')})")
                            st.write(f"**Content Snippet:** {s.get('content')}")
                else:
                    st.info("No sources were validated.")

            with tab3:
                st.subheader("Research Objectives:")
                for idx, obj in enumerate(result.get("research_plan", []), 1):
                    cov = result.get("coverage_status", {}).get(obj, False)
                    status_icon = "✅ Covered" if cov else "⚠️ Gaps Identified"
                    st.write(f"{idx}. **{obj}** — {status_icon}")

        except Exception as e:
            status_box.update(label="❌ Error occurred during execution", state="error")
            st.error(f"Execution Error: {e}")

