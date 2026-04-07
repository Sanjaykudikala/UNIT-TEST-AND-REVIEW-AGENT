from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):

    code_input: str  
    file_diff: str   
    file_path: str   
    context: List[Dict[str, Any]] 

    requirements: Dict[str, Any]

    review_output: Dict[str, Any]
    test_output: str
