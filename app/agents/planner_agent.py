from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import make_llm
from ..state import AgentState
from ..text import content_to_text  # (move this import to the top if you want)


def run_planner(state: AgentState) -> AgentState:
    llm = make_llm()
    system = SystemMessage(content=(
        "You are the PLANNER agent for e-commerce analysis.\n"
        "Given the user question, produce a short plan:\n"
        "1) goal, 2) metrics, 3) tables, 4) time window guidance, 5) expected output.\n"
        "Do NOT write SQL."
    ))
    human = HumanMessage(
        content=f"User question:\n{state['question']}\n"
                "Available tables: orders, order_items, products, users"
    )

    state["plan"] = content_to_text(llm.invoke([system, human]).content).strip()

    # ✅ add this line here
    state.setdefault("trace", {})["plan"] = state["plan"]

    return state