-- Dimension: one row per taxi zone. Referenced by fact_trips for both
-- pickup and dropoff locations.

select
    location_id,
    coalesce(borough, 'Outside of NYC') as borough,
    zone_name,
    service_zone
from {{ ref('stg_taxi_zone_lookup') }}
