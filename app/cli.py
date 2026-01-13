from dotenv import load_dotenv
from .orchestrator import build_orchestrator

HELP = """Commands:
  /help   Show help
  /exit   Quit
  /trace  Toggle showing intermediate steps
Example:
  Which states have the highest AOV in the last 90 days?
"""

def main():
    load_dotenv()
    graph = build_orchestrator()
    show_trace = True

    print("Data Analysis Agent (BigQuery thelook_ecommerce)")
    print("Type /help for commands.\n")

    while True:
        q = input("You> ").strip()
        if not q:
            continue
        if q == "/exit":
            break
        if q == "/help":
            print(HELP)
            continue
        if q == "/trace":
            show_trace = not show_trace
            print(f"(trace {'ON' if show_trace else 'OFF'})")
            continue

        out = graph.invoke({"question": q, "trace": {}})

        if show_trace:
            print("\n--- TRACE: Planner ---")
            print(out.get("plan", ""))

            print("\n--- TRACE: SQL ---")
            print(out.get("sql", ""))

            if out.get("error"):
                print("\n--- TRACE: Execution Error ---")
                print(out["error"])
            else:
                print("\n--- TRACE: Result Preview ---")
                print(out["result"]["preview_markdown"])

            # Optional: show sql_agent tool calls/messages
            msgs = out.get("trace", {}).get("sql_agent_messages")
            if msgs:
                print("\n--- TRACE: SQL Agent Messages (includes tool calls) ---")
                print(f"(messages captured: {len(msgs)})")

        print("\nAgent> " + out.get("answer", "(no answer)") + "\n")

if __name__ == "__main__":
    main()