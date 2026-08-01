"""
Runs 00_setup_snowflake.sql directly against your Snowflake account via
the Python connector — use this if the Snowsight Workspaces UI in the
browser won't load.

Setup:
1. Copy .env.example to .env and fill in your Snowflake credentials
2. Run: python ingestion/run_setup_sql.py
"""

import os
import re
import sys
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

SQL_FILE = Path(__file__).parent / "00_setup_snowflake.sql"

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
]


def check_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        print(f"Missing environment variables: {missing}")
        print("Copy .env.example to .env and fill in your Snowflake credentials.")
        sys.exit(1)


def get_connection():
    # Note: no warehouse/database/schema here yet, since this script is
    # what CREATES them. Uses ACCOUNTADMIN role by default so it has
    # permission to create a warehouse and database.
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )


def split_statements(sql_text: str):
    # Strip full-line comments, then split on semicolons.
    lines = [line for line in sql_text.splitlines() if not line.strip().startswith("--")]
    cleaned = "\n".join(lines)
    statements = [s.strip() for s in cleaned.split(";")]
    return [s for s in statements if s]


def main():
    check_env()

    if not SQL_FILE.exists():
        print(f"Could not find {SQL_FILE}")
        sys.exit(1)

    sql_text = SQL_FILE.read_text()
    statements = split_statements(sql_text)

    print(f"Connecting to Snowflake account {os.getenv('SNOWFLAKE_ACCOUNT')} ...")
    conn = get_connection()
    cur = conn.cursor()

    try:
        for stmt in statements:
            print(f"\nRunning:\n  {stmt[:80]}{'...' if len(stmt) > 80 else ''}")
            cur.execute(stmt)
            for row in cur.fetchall():
                print(f"  -> {row}")
        print("\nSetup complete. Warehouse, database, and schemas are ready.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
