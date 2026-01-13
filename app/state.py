from typing import TypedDict, Dict, Any

class AgentState(TypedDict, total=False):
    question: str
    plan: str
    sql: str
    result: Dict[str, Any]
    answer: str
    error: str
    trace: Dict[str, Any]   # NEW: store intermediate steps here