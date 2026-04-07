import json
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.config import settings

def extract_requirements(file_diff: str, code_full: str):

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.1,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    prompt = PromptTemplate(
        input_variables=["diff", "code"],
        template=
    )

    chain = prompt | llm
    response = chain.invoke({"diff": file_diff, "code": code_full})

    try:
        return json.loads(response.content)
    except Exception:

        return {
            "feature": "Code Update",
            "intent": "Manual code changes detected",
            "affected_components": ["Unknown"],
            "risk_level": "Medium",
            "expected_behavior": "Functional alignment with existing patterns"
        }
