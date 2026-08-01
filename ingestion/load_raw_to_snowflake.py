"""
Loads NYC TLC trip data (Parquet) and the taxi zone lookup (CSV) from
data/raw/ into Snowflake's RAW schema.

Setup:
1. Download monthly yellow_tripdata_YYYY-MM.parquet files and
   taxi_zone_lookup.csv from the NYC TLC site into data/raw/
2. Copy .env.example to .env and fill in your Snowflake credentials
3. Run: python ingestion/load_raw_to_snowflake.py

Each file becomes one table in TLC_DB.RAW, named after the file
(e.g. yellow_tripdata_2026-03.parquet -> RAW_YELLOW_TRIPDATA_2026_03,
taxi_zone_lookup.csv -> RAW_TAXI_ZONE_LOOKUP). Multiple monthly trip
files are loaded as separate tables here; they get unioned into one
table in the dbt staging layer (Day 2).
"""

import os
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Rows per batch when reading large parquet files. Lower this further
# (e.g. 50_000) if running on very memory-constrained machines/containers.
BATCH_SIZE = 200_000

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]


def check_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        print(f"Missing environment variables: {missing}")
        print("Copy .env.example to .env and fill in your Snowflake credentials.")
        sys.exit(1)


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Snowflake likes uppercase, no-space column names."""
    df.columns = [c.strip().upper().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df


def table_name_from_filename(filename: str) -> str:
    # yellow_tripdata_2026-03.parquet -> RAW_YELLOW_TRIPDATA_2026_03
    # taxi_zone_lookup.csv -> RAW_TAXI_ZONE_LOOKUP
    stem = Path(filename).stem.replace("-", "_")
    return f"RAW_{stem.upper()}"


def load_csv(conn, file_path: Path, table_name: str) -> bool:
    """Small reference files - load in one shot, no batching needed."""
    df = pd.read_csv(file_path)
    df = clean_column_names(df)
    success, _, nrows, _ = write_pandas(
        conn, df, table_name, auto_create_table=True, overwrite=True
    )
    print(f"  -> {'OK' if success else 'FAILED'}: {nrows} rows loaded into {table_name}")
    return success


def load_parquet_in_batches(conn, file_path: Path, table_name: str) -> bool:
    """
    Streams a large parquet file in small batches instead of loading it
    entirely into memory at once. This is what makes ingestion work on
    memory-constrained machines/containers (e.g. Docker with only 2GB
    available) - the file itself is ~65MB on disk, but the equivalent
    in-memory pandas DataFrame for millions of rows is much larger, and
    was previously causing an out-of-memory error.
    """
    parquet_file = pq.ParquetFile(file_path)
    total_rows = 0
    first_batch = True

    for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
        df = batch.to_pandas()
        df = clean_column_names(df)

        # First batch creates/overwrites the table; later batches append.
        success, _, nrows, _ = write_pandas(
            conn,
            df,
            table_name,
            auto_create_table=True,
            overwrite=first_batch,
        )
        if not success:
            print(f"  -> FAILED on batch starting at row {total_rows}")
            return False

        total_rows += nrows
        first_batch = False
        print(f"  ... {total_rows:,} rows loaded so far", end="\r")

    print(f"  -> OK: {total_rows:,} rows loaded into {table_name}" + " " * 10)
    return True


def load_file(conn, file_path: Path) -> bool:
    table_name = table_name_from_filename(file_path.name)
    print(f"Loading {file_path.name} -> {table_name} ...")

    if file_path.suffix == ".parquet":
        return load_parquet_in_batches(conn, file_path, table_name)
    elif file_path.suffix == ".csv":
        return load_csv(conn, file_path, table_name)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")


def main():
    check_env()

    source_files = sorted(RAW_DATA_DIR.glob("*.parquet")) + sorted(RAW_DATA_DIR.glob("*.csv"))

    if not RAW_DATA_DIR.exists() or not source_files:
        print(f"No .parquet or .csv files found in {RAW_DATA_DIR}")
        print("Download the NYC TLC monthly trip files (parquet) and")
        print("taxi_zone_lookup.csv from nyc.gov/site/tlc and place them there.")
        sys.exit(1)

    print(f"Found {len(source_files)} files to load.\n")

    conn = get_connection()
    try:
        results = []
        for file_path in source_files:
            results.append(load_file(conn, file_path))

        print(f"\nDone. {sum(results)}/{len(results)} tables loaded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
