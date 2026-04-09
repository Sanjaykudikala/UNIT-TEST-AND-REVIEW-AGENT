import os
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.config import settings

def inject_code_change(file_path: str):

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.7 
    )

    prompt = PromptTemplate(
        input_variables=["code"],
        template="""
        You are a simulator that performs meaningful, realistic code modifications to Java source files.
        
        YOUR TASK: Modify the code below to simulate a real developer task (e.g., adding a feature, fixing a bug, refactoring).
        - Ensure the change is functionally consistent.
        - Add logic that is easy to unit test.
        - Keep the overall class structure valid.
        
        ORIGINAL CODE:
        {code}
        
        Output ONLY the complete modified Java file. No markdown, no explanations.
        """
    )

    chain = prompt | llm
    response = chain.invoke({"code": original_code})

    modified_code = response.content

    if "```java" in modified_code:
        modified_code = modified_code.split("```java")[1].split("```")[0].strip()
    elif "```" in modified_code:
        modified_code = modified_code.split("```")[1].strip()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(modified_code)

    return True
