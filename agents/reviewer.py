import json
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState
from core.config import settings

def reviewer_node(state: AgentState):
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    context_str = ""
    for item in state["context"]:
        context_str += f"\nFile: {item['file']}\n{item['text']}\n"

    prompt = PromptTemplate(
        input_variables=["code", "context", "file_path", "requirements"],
        template=
    )

    chain = prompt | llm

    for attempt in range(2):
        response = chain.invoke({
            "code": state["file_diff"], 
            "context": context_str,
            "file_path": state["file_path"],
            "requirements": json.dumps(state["requirements"], indent=2)
        })

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()

            parsed_json = json.loads(content)
            return {"review_output": parsed_json}
        except (json.JSONDecodeError, IndexError):
            if attempt == 1:

                return {"review_output": {"summary": "Failed to generate valid JSON", "issues": [], "overall_score": 0, "approval_status": "Changes required"}}
            continue

    return {"review_output": {}}
