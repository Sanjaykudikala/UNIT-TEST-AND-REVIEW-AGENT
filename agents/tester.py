from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from core.state import TestState
from core.config import settings

def tester_node(state: TestState):
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.1 # Low temperature for accurate code generation
    )
    
    # We use the "Contextual Test Package" structure
    prompt = PromptTemplate(
        input_variables=["code", "diff", "context"],
        template="""--- SYSTEM PROMPT ---
You are a Senior Java QA Engineer. Your goal is to generate a complete, high-quality JUnit 5 test file for the provided Java class.

STRICT RULES:
1. **Frameworks**: Use JUnit 5 and Mockito (MockitoExtension).
2. **Design Pattern**: Strictly follow the **Arrange-Act-Assert (AAA)** structure for every test.
3. **Coverage**: Target 100% coverage. Include:
   - Happy paths
   - Edge cases (Null inputs, empty strings, boundaries)
   - Failure scenarios (Exceptions, invalid states)
4. **Mocking**: Use the provided 'DEPENDENCY CONTEXT' to write accurate Mockito code.
5. **Regression**: Specifically ensure the changes in 'MODIFIED CODE (DIFF)' are covered by new or updated tests.
6. **Readability**: Use clear, descriptive test names (e.g., shouldReturnUserWhenIdIsValid).

--- TARGET FILE CODE ---
{code}

--- MODIFIED CODE (DIFF) ---
{diff}

--- DEPENDENCY CONTEXT (FROM VECTOR DB) ---
{context}

--- TASK ---
Generate the full [ClassName]Test.java file. Output ONLY the code.
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "code": state["code_input"], # Full class code
        "diff": state.get("diff_content", "No changes detected (Full file test)"), 
        "context": state.get("context", "No external dependency signatures found.")
    })
    
    # Clean up markdown if present
    code = response.content.replace("```java", "").replace("```", "").strip()
    return {"test_output": code}
