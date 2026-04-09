from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.reviewer import reviewer_node
from agents.tester import tester_node
from ingestion.vector_store import query_context
from requirement_extractor import extract_requirements

def requirement_node(state: AgentState):
    print("🧠 Extracting intent and requirements from code changes...")
    reqs = extract_requirements(state["file_diff"], state["code_input"])
    print(f"Extracted feature: {reqs.get('feature', 'Unknown')}")
    return {"requirements": reqs}

def fetch_context_node(state: AgentState):
    print("🔍 Searching for relevant codebase context...")
    query = state["requirements"].get("feature", state["file_diff"])
    context = query_context(query)
    return {"context": context}

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("requirement_extractor", requirement_node)
    workflow.add_node("fetch_context", fetch_context_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("tester", tester_node)

    workflow.set_entry_point("requirement_extractor")
    workflow.add_edge("requirement_extractor", "fetch_context")

    workflow.add_edge("fetch_context", "reviewer")
    workflow.add_edge("fetch_context", "tester")

    workflow.add_edge("reviewer", END)
    workflow.add_edge("tester", END)

    return workflow.compile()

app = build_graph()
