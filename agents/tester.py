from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState
from core.config import settings

def tester_node(state: AgentState):
    print("🧪 Tester Agent is generating unit tests...")
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
        template="""
        You are a Test Automation Expert specializing in Java, JUnit 5, and Mockito.
        
        GOAL: Generate a comprehensive unit test for the changes in the provided code.
        
        FULL SOURCE CODE:
        {code}
        
        CODE DIFF (CURRENT CHANGES):
        {diff}
        
        REPOSITORY CONTEXT (Patterns/Utils):
        {context}
        
        INTENTED REQUIREMENTS:
        {requirements}
        
        REVIEW FEEDBACK TO ADDRESS:
        Summary: {review_summary}
        Issues: {review_issues}
        
        Instructions:
        1. Use JUnit 5 and Mockito.
        2. Mock all external dependencies.
        3. Aim for 100% branch coverage of the NEW logic.
        4. Follow the coding style found in the context.
        5. Output ONLY the code for the test class. No markdown, no explanations.
        """
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
