import json
from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import make_llm
from ..state import AgentState


def run_analyst(state: AgentState) -> AgentState:
    llm = make_llm()

    if state.get("error"):
        system = SystemMessage(content=(
            "You are the ANALYST agent. Execution failed.\n"
            "Explain the likely cause and propose a corrected, smaller query approach."
        ))
        human = HumanMessage(content=f"Question:\n{state['question']}\n\nSQL:\n{state.get('sql','')}\n\nError:\n{state['error']}")
        from ..text import content_to_text
        state["answer"] = content_to_text(llm.invoke([system, human]).content).strip()
        return state

    system = SystemMessage(content=(
        "You are the ANALYST agent.\n"
        "Turn the query results into actionable business insights:\n"
        "- Findings (bullets)\n"
        "- So what (why it matters)\n"
        "- Actions (recommendations)\n"
        "- Data notes (timeframe/definitions)\n"
        "- SQL used (include the SQL)\n"
        "Be concise."
    ))
    human = HumanMessage(content=(
        f"Question:\n{state['question']}\n\n"
        f"Plan:\n{state.get('plan','')}\n\n"
        f"Result JSON:\n{json.dumps(state.get('result', {}), indent=2)}\n"
    ))
    from ..text import content_to_text
    state["answer"] = content_to_text(llm.invoke([system, human]).content).strip()
    return state