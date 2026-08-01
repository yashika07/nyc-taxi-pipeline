-- Combines all monthly yellow taxi staging models into a single table.
-- Downstream models (marts, dashboards) query this instead of each
-- monthly table individually.

with combined as (

    select * from {{ ref('stg_yellow_tripdata_2026_03') }}
    union all
    select * from {{ ref('stg_yellow_tripdata_2026_04') }}
    union all
    select * from {{ ref('stg_yellow_tripdata_2026_05') }}

)

select * from combined
