from langgraph.graph import StateGraph, END
from core.state import ReviewState, TestState
from agents.reviewer import reviewer_node
from agents.tester import tester_node
from ingestion.vector_store import query_context

# --- Shared Context Retrieval ---
def fetch_review_context_node(state: ReviewState):
    code = state["code_input"]
    context = query_context(code)
    return {"context": context}

def fetch_test_context_node(state: TestState):
    code = state["code_input"]
    context = query_context(code)
    return {"context": context}

# --- Review Graph ---
review_graph = StateGraph(ReviewState)
review_graph.add_node("fetch_context", fetch_review_context_node)
review_graph.add_node("reviewer", reviewer_node)

review_graph.set_entry_point("fetch_context")
review_graph.add_edge("fetch_context", "reviewer")
review_graph.add_edge("reviewer", END)

app_review = review_graph.compile()


# --- Test Graph ---
test_graph = StateGraph(TestState)
test_graph.add_node("fetch_context", fetch_test_context_node)
test_graph.add_node("tester", tester_node)

test_graph.set_entry_point("fetch_context")
test_graph.add_edge("fetch_context", "tester")
test_graph.add_edge("tester", END)

app_test = test_graph.compile()
