import os
from typing import Any, Dict, List

import pandas as pd
from google.cloud import bigquery


class BigQueryRunner:
    def __init__(self):
        self.project_id = os.getenv("BIGQUERY_PROJECT_ID") or None
        self.dataset_id = os.getenv("BIGQUERY_DATASET_ID", "bigquery-public-data.thelook_ecommerce")
        self.max_bytes = int(os.getenv("BQ_MAX_BYTES", "2000000000"))
        self.client = bigquery.Client(project=self.project_id)

    def _enforce_readonly(self, sql: str) -> None:
        lowered = sql.strip().lower()
        if ";" in lowered:
            raise ValueError("Only single-statement SQL allowed (no semicolons).")
        disallowed = ["insert ", "update ", "delete ", "merge ", "create ", "drop ", "alter ", "truncate "]
        if any(tok in lowered for tok in disallowed):
            raise ValueError("Only read-only SELECT queries allowed.")
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ValueError("Query must start with SELECT or WITH.")

    def estimate_bytes(self, sql: str) -> int:
        self._enforce_readonly(sql)
        job = self.client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=True))
        return int(job.total_bytes_processed or 0)

    def query_to_df(self, sql: str, max_rows: int = 2000) -> pd.DataFrame:
        self._enforce_readonly(sql)
        est = self.estimate_bytes(sql)
        if est > self.max_bytes:
            raise ValueError(f"Query too large: {est:,} bytes > limit {self.max_bytes:,}. Add filters/aggregation.")
        job = self.client.query(sql, job_config=bigquery.QueryJobConfig(use_query_cache=True))
        df = job.result().to_dataframe(create_bqstorage_client=False)
        if len(df) > max_rows:
            df = df.head(max_rows)
        return df

    def table_schema(self, table: str) -> List[Dict[str, Any]]:
        table_ref = bigquery.TableReference.from_string(f"{self.dataset_id}.{table}")
        t = self.client.get_table(table_ref)
        return [{"name": f.name, "type": f.field_type, "mode": f.mode} for f in t.schema]