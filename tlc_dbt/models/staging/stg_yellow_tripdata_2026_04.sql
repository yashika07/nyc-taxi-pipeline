-- Cleans and standardizes April 2026 yellow taxi trip data.
-- Raw timestamps come in as nanoseconds since epoch; convert to real timestamps.

with source as (
    select * from {{ source('raw', 'raw_yellow_tripdata_2026_04') }}
),

renamed as (
    select
        vendorid                                           as vendor_id,
        to_timestamp_ntz(tpep_pickup_datetime / 1000000) as pickup_datetime,
        to_timestamp_ntz(tpep_dropoff_datetime / 1000000) as dropoff_datetime,
        passenger_count                                    as passenger_count,
        trip_distance                                      as trip_distance_miles,
        ratecodeid                                         as rate_code_id,
        store_and_fwd_flag                                 as store_and_fwd_flag,
        pulocationid                                        as pickup_location_id,
        dolocationid                                        as dropoff_location_id,
        payment_type                                       as payment_type,
        fare_amount                                        as fare_amount,
        extra                                              as extra_amount,
        mta_tax                                            as mta_tax,
        tip_amount                                         as tip_amount,
        tolls_amount                                       as tolls_amount,
        improvement_surcharge                              as improvement_surcharge,
        total_amount                                       as total_amount,
        congestion_surcharge                               as congestion_surcharge,
        '2026-04' as trip_month
    from source
)

select * from renamed
