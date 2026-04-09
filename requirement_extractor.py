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
        template="""
        You are an expert requirement analyst. Your task is to analyze a git diff and provide a structured understanding of the code change.
        
        GIT DIFF:
        {diff}
        
        FULL FILE CODE:
        {code}
        
        Extract the following information in JSON format:
        {{
            "feature": "Name of the feature being modified",
            "intent": "What is the developer trying to achieve?",
            "affected_components": ["List of methods/classes affected"],
            "risk_level": "High/Medium/Low",
            "expected_behavior": "Description of what the code should now do"
        }}
        """
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
