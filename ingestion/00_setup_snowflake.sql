-- Run this once in a Snowflake worksheet (using ACCOUNTADMIN or SYSADMIN role)
-- after your trial account is active.

-- Warehouse: X-Small is plenty for this project and keeps trial credits alive longer
CREATE WAREHOUSE IF NOT EXISTS TLC_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Database
CREATE DATABASE IF NOT EXISTS TLC_DB;

-- Schemas: RAW for ingested data, later dbt will create STAGING and MARTS
CREATE SCHEMA IF NOT EXISTS TLC_DB.RAW;
CREATE SCHEMA IF NOT EXISTS TLC_DB.STAGING;
CREATE SCHEMA IF NOT EXISTS TLC_DB.MARTS;

-- Sanity check
USE WAREHOUSE TLC_WH;
USE DATABASE TLC_DB;
USE SCHEMA RAW;
SHOW SCHEMAS IN DATABASE TLC_DB;
