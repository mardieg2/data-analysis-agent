from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import AgentState
from .bq_client import BigQueryRunner
from .agents.planner_agent import run_planner
from .agents.sql_agent import run_sql_agent
from .agents.analyst_agent import run_analyst


def execute_step(state: AgentState) -> AgentState:
    bq = BigQueryRunner()

    def _run(sql: str):
        df = bq.query_to_df(sql, max_rows=2000)
        return {
            "estimated_bytes": bq.estimate_bytes(sql),
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "columns": list(df.columns),
            "preview_markdown": df.head(8).to_markdown(index=False),
            "sql": sql,
        }

    try:
        state["result"] = _run(state["sql"])
        state.setdefault("trace", {})["execution"] = {
            "estimated_bytes": state["result"]["estimated_bytes"],
            "preview_markdown": state["result"]["preview_markdown"],
        }
        return state

    except Exception as e:
        err1 = f"{type(e).__name__}: {e}"
        state.setdefault("trace", {})["execution_error_first"] = err1

        # Retry once: ask SQL agent to fix the query using the error message
        repair_prompt = (
            "The previous SQL failed in BigQuery.\n"
            f"User question: {state['question']}\n\n"
            f"Failed SQL:\n{state.get('sql','')}\n\n"
            f"BigQuery error:\n{err1}\n\n"
            "Return a corrected BigQuery Standard SQL query only."
        )

        repaired_state: AgentState = {"question": repair_prompt, "trace": state.get("trace", {})}
        repaired_state = run_sql_agent(repaired_state)
        repaired_sql = repaired_state.get("sql", "")

        state["sql"] = repaired_sql
        state.setdefault("trace", {})["sql_repair"] = repaired_sql

        try:
            state["result"] = _run(repaired_sql)
            state.setdefault("trace", {})["execution_retry_success"] = True
            return state
        except Exception as e2:
            err2 = f"{type(e2).__name__}: {e2}"
            state["error"] = err2
            state.setdefault("trace", {})["execution_error_second"] = err2
            return state


def build_orchestrator():
    g = StateGraph(AgentState)

    g.add_node("planner", run_planner)
    g.add_node("sql_agent", run_sql_agent)
    g.add_node("execute", execute_step)
    g.add_node("analyst", run_analyst)

    g.set_entry_point("planner")
    g.add_edge("planner", "sql_agent")
    g.add_edge("sql_agent", "execute")
    g.add_edge("execute", "analyst")
    g.add_edge("analyst", END)

    return g.compile()
