# NYC Taxi Trip Analytics Pipeline

End-to-end data pipeline: Snowflake + dbt + Airflow + Power BI, built on
official NYC TLC (Taxi & Limousine Commission) trip record data.

**Status:** Day 1 — raw ingestion

## Why this dataset

Real, government-published, continuously updated monthly (not a static,
years-old Kaggle CSV). Widely recognized as a benchmark dataset in the
data engineering community — used in official dbt, Airflow, and Databricks
tutorials — so it signals familiarity with industry-standard tooling
rather than a generic student project.

## Architecture (planned)

```
NYC TLC Parquet files -> Python ingestion -> Snowflake RAW
                                                  |
                                              dbt STAGING (clean/typed, union monthly files)
                                                  |
                                              dbt MARTS (star schema: fact_trips, dim_zones, dim_date)
                                                  |
                                        Airflow orchestrates the above daily
                                                  |
                                              Power BI dashboards
```

## Day 1 Setup

1. **Snowflake**: Sign up for a free trial (AWS, region closest to you),
   then run `ingestion/00_setup_snowflake.sql` in a Snowflake worksheet to
   create the warehouse, database, and schemas.
2. **Dataset**: From https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page,
   download 3 recent months of Yellow Taxi trip data (parquet) plus the
   taxi zone lookup table, into `data/raw/`:
   ```bash
   wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-03.parquet
   wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-04.parquet
   wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet
   wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
   ```
   (swap in whichever months are actually available on the page)
3. **Python env**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
4. **Credentials**: Copy `.env.example` to `.env` and fill in your Snowflake
   account identifier, username, and password.
5. **Load raw data**:
   ```bash
   python ingestion/load_raw_to_snowflake.py
   ```
6. **Verify**: In Snowflake, run
   `SELECT COUNT(*) FROM TLC_DB.RAW.RAW_YELLOW_TRIPDATA_2026_03;`
   to confirm the load worked.

## Roadmap

- [x] Day 1: Raw ingestion into Snowflake
- [x] Day 2: dbt staging models (union monthly files, clean types)
- [x] Day 3: dbt marts (star schema: fact_trips, dim_zones, dim_date) + tests + docs
- [x] Day 4: Airflow orchestration
- [x] Day 5: Power BI dashboards (demand by zone/time, fare trends, trip patterns)
- [x] Day 6: Documentation + architecture diagram
- [x] Day 7: Resume writeup
