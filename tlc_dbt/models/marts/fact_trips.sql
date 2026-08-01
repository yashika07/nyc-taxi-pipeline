-- Fact: one row per taxi trip. Holds measurable numbers (fares, distance,
-- duration) plus foreign keys into dim_zones and dim_date.

with trips as (
    select
        *,
        -- tiebreaker for trips that share identical vendor/times/zones -
        -- real TLC data has no genuine unique trip ID, and with 11M+ rows
        -- some trips legitimately look identical on these fields alone
        row_number() over (
            partition by vendor_id, pickup_datetime, dropoff_datetime,
                         pickup_location_id, dropoff_location_id
            order by pickup_datetime
        ) as dedup_rn
    from {{ ref('stg_yellow_tripdata') }}
),

final as (
    select
        md5(
            cast(vendor_id as varchar) || '-' ||
            cast(pickup_datetime as varchar) || '-' ||
            cast(dropoff_datetime as varchar) || '-' ||
            cast(pickup_location_id as varchar) || '-' ||
            cast(dropoff_location_id as varchar) || '-' ||
            cast(dedup_rn as varchar)
        ) as trip_id,

        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        cast(pickup_datetime as date)  as pickup_date,
        cast(dropoff_datetime as date) as dropoff_date,
        pickup_location_id,
        dropoff_location_id,

        passenger_count,
        trip_distance_miles,
        rate_code_id,
        payment_type,

        datediff(minute, pickup_datetime, dropoff_datetime) as trip_duration_minutes,

        fare_amount,
        extra_amount,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        congestion_surcharge,
        total_amount,

        trip_month
    from trips
    -- basic sanity filter: drop trips with impossible/corrupt values,
    -- including the small number of rows with corrupted timestamps that
    -- fall outside our known March-May 2026 data range
    where pickup_datetime is not null
      and dropoff_datetime is not null
      and dropoff_datetime >= pickup_datetime
      and pickup_datetime >= '2026-03-01'::timestamp
      and pickup_datetime < '2026-06-06'::timestamp
)

select * from final
