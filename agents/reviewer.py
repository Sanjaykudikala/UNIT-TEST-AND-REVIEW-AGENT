import json
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import ReviewState
from core.config import settings

def reviewer_node(state: ReviewState):
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    # We add requirements into the prompt for explicit validation
    prompt = PromptTemplate(
        input_variables=["code", "context", "file_path", "requirements"],
        template="""You are a Principal AI Security and Code Architecture Reviewer. 
Your goal is to perform a senior-level Pull Request review on the following **Git Diff** while ensuring it aligns with the **New Requirements**.

Core Assignment Capabilities:
1. **Functional Correctness**: Identify logic errors and VALIDATE alignment with the requirements below.
2. **Code Quality**: Check for readability, maintainability, and naming conventions.
3. **Architectural Awareness**: Respect existing patterns, dependency management, and layer violations.
4. **Performance Analysis**: Inefficient loops, memory misuse, and unnecessary object creation.
5. **Security (CRITICAL)**: Identify Injection (SQL, Command), Unsafe Deserialization, Hardcoded Secrets, Auth flaws, and OWASP Top 10 risks.
6. **Regression Awareness**: Highlight potential side effects on the surrounding project context.
7. **Diff-Awareness**: Focus on the changes while considering the project's global state.

INPUTS:
Modified Code (Git Diff):
{code}

Global Project Context (Related classes found via RAG):
{context}

New Feature Requirements (The target for alignment):
{requirements}

Target Analysis Area: {file_path}

INSTRUCTIONS FOR OUTPUT:
- You MUST output ONLY a pure JSON object.
- Calculation: Start `overall_score` at 100. Deduct 25 for Critical, 15 for High, 5 for Medium, and 2 for Low issues found in the diff.

SCHEMA:
{{
  "summary": "Detailed assessment of how the changes align with requirements and their security impact",
  "issues": [
    {{
      "type": "Security | Bug | Performance | Style",
      "severity": "Critical | High | Medium | Low",
      "file": "filename.java",
      "line": 123,
      "description": "Issue explanation with reference to requirements or RAG context",
      "impact": "Real-world risk / What an attacker could exactly do",
      "suggestion": "Actionable code-level fix snippet"
    }}
  ],
  "overall_score": 58,
  "approval_status": "Approved | Changes required"
}}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "code": state["code_input"], 
        "context": state["context"],
        "file_path": state.get("file_path", "Local Git Changes"),
        "requirements": state.get("requirements", "No specific requirements provided.")
    })
    
    try:
        parsed_json = json.loads(response.content)
    except json.JSONDecodeError:
        cleaned = response.content.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(cleaned)

    return {"review_output": parsed_json}
