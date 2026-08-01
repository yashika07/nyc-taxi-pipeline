-- Cleans the taxi zone lookup reference table.

with source as (
    select * from {{ source('raw', 'raw_taxi_zone_lookup') }}
),

renamed as (
    select
        locationid    as location_id,
        borough       as borough,
        zone          as zone_name,
        service_zone  as service_zone
    from source
)

select * from renamed
