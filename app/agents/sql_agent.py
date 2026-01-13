from langgraph.prebuilt import create_react_agent
from ..llm import make_llm
from ..tools import build_tools
from ..state import AgentState
from ..text import content_to_text

SQL_SYSTEM = """You are the SQL agent.
Goal: produce exactly ONE BigQuery Standard SQL query for the user question.

Rules:
- Only SELECT/WITH (read-only)
- Use dataset `bigquery-public-data.thelook_ecommerce` with backticks
- Use only the following tables from the big query dataset: {orders, order_items, products, users}
- Use tools to check schema if unsure: bq_table_schema
- Prefer aggregation + time filter
- IMPORTANT: For TIMESTAMP arithmetic use TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL <N> DAY) or use DATE_SUB(CURRENT_DATE(), INTERVAL <N> WEEK).
  Do NOT use "INTERVAL <N> WEEK" with TIMESTAMP_SUB.
- Output ONLY the final SQL in your last message. No markdown fences.
"""


def run_sql_agent(state: AgentState) -> AgentState:
    sql_react = create_react_agent(
        model=make_llm(),
        tools=build_tools(),
    )

    result = sql_react.invoke(
        {
            "messages": [
                {"role": "system", "content": SQL_SYSTEM},
                {"role": "user", "content": state["question"]},
            ]
        }
    )

    final_msg = result["messages"][-1]
    state["sql"] = content_to_text(final_msg.content).strip()

    # capture tool calls + intermediate reasoning/messages
    state.setdefault("trace", {})["sql_agent_messages"] = [
        (m.model_dump() if hasattr(m, "model_dump") else (m.dict() if hasattr(m, "dict") else str(m)))
        for m in result["messages"]
    ]
    return state