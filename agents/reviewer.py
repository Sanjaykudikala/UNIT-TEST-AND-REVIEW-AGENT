import json
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState
from core.config import settings

def reviewer_node(state: AgentState):
    print("🛡️ Reviewer Agent is auditing the changes...")
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
        template="""
        You are a Senior Principal Engineer performing a high-stakes code review.
        
        FILE PATH: {file_path}
        
        INTENT/REQUIREMENTS:
        {requirements}
        
        CODE DIFF (CURRENT CHANGES):
        {code}
        
        ADDITIONAL REPOSITORY CONTEXT:
        {context}
        
        Your task:
        1. Evaluate logic correctness and potential bugs.
        2. Check for security vulnerabilities (injection, auth, etc. especially since this is Java).
        3. Ensure alignment with established repository patterns found in the context.
        4. Provide an overall score (0-100).
        5. State clear 'Approval Status' (Approved, Minor changes, or Changes required).

        RESPONSE MUST BE ONLY A VALID JSON OBJECT:
        {{
            "summary": "High level summary",
            "overall_score": 85,
            "approval_status": "Approved/Minor changes/Changes required",
            "issues": [
                {{"severity": "Critical/Major/Minor", "description": "...", "line_hint": 0}}
            ],
            "best_practices": ["..."]
        }}
        """
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
