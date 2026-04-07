from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState
from core.config import settings

def tester_node(state: AgentState):
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.1
    )

    context_str = ""
    for item in state["context"]:
        context_str += f"\nFile: {item['file']}\n{item['text']}\n"

    prompt = PromptTemplate(
        input_variables=["code", "diff", "context", "requirements", "review_summary", "review_issues"],
        template=
    )

    review_summary = state.get("review_output", {}).get("summary", "No review summary.")
    review_issues = "\n".join([f"- {i['description']}" for i in state.get("review_output", {}).get("issues", [])])

    chain = prompt | llm
    response = chain.invoke({
        "code": state["code_input"],
        "diff": state["file_diff"],
        "context": context_str,
        "requirements": str(state["requirements"]),
        "review_summary": review_summary,
        "review_issues": review_issues if review_issues else "No specific issues identified."
    })

    code = response.content.replace("```java", "").replace("```", "").strip()
    return {"test_output": code}
