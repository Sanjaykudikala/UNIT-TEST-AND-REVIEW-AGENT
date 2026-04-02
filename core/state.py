from typing import TypedDict, List, Dict, Any

class ReviewState(TypedDict):
    code_input: str
    file_path: str
    context: str
    review_output: Dict[str, Any]

class TestState(TypedDict):
    code_input: str
    file_path: str
    test_output: str
