import json
import pandas as pd
from typing import Any, Dict
from langchain_core.tools import tool
from .bq_client import BigQueryRunner

def _df_preview(df: pd.DataFrame, n: int = 8) -> Dict[str, Any]:
    return {
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "columns": list(df.columns),
        "preview_markdown": df.head(n).to_markdown(index=False),
    }

def build_tools():
    bq = BigQueryRunner()

    @tool("bq_table_schema")
    def bq_table_schema(table_name: str) -> str:
        """Get schema for a table (orders, order_items, products, users)."""
        return json.dumps({"table": table_name, "schema": bq.table_schema(table_name)}, indent=2)

    @tool("bq_query")
    def bq_query(sql: str) -> str:
        """Run a read-only SELECT query and return a compact preview."""
        df = bq.query_to_df(sql, max_rows=2000)
        payload = {"sql": sql, **_df_preview(df)}
        return json.dumps(payload, indent=2)

    @tool("bq_estimate_bytes")
    def bq_estimate_bytes(sql: str) -> str:
        """Dry-run estimate bytes processed."""
        return json.dumps({"estimated_bytes": bq.estimate_bytes(sql)}, indent=2)

    return [bq_table_schema, bq_estimate_bytes, bq_query]
