"""
Orchestrates the NYC Taxi pipeline: ingestion -> dbt run -> dbt test.

Runs against the host project mounted at /usr/local/airflow/host_project
(see docker-compose.override.yml). Credentials are loaded from the
host project's .env file at runtime, so nothing is duplicated here.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

HOST_PROJECT = "/usr/local/airflow/include/host_project"

# Loads .env into the shell session before each command runs, so the
# ingestion script and dbt (via profiles.yml's env_var() calls) can
# both see the Snowflake credentials.
LOAD_ENV = f"cd {HOST_PROJECT} && set -a && source .env && set +a"

with DAG(
    dag_id="tlc_pipeline",
    description="NYC Taxi: ingest raw data, run dbt transformations, run dbt tests",
    start_date=datetime(2026, 7, 1),
    schedule="@daily",
    catchup=False,
    tags=["tlc", "portfolio-project"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_raw_data",
        bash_command=f"{LOAD_ENV} && python ingestion/load_raw_to_snowflake.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{LOAD_ENV} && cd tlc_dbt && DBT_PROFILES_DIR=. dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{LOAD_ENV} && cd tlc_dbt && DBT_PROFILES_DIR=. dbt test",
    )

    ingest >> dbt_run >> dbt_test
