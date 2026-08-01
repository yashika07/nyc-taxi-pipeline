-- Dimension: one row per calendar day, covering the full range of our
-- trip data (March-May 2026, with a small buffer for trips that started
-- late one month and ended early the next).

with raw_dates as (
    select
        dateadd(day, seq4(), '2026-03-01'::date) as date_day
    from table(generator(rowcount => 100))
),

date_spine as (
    select date_day
    from raw_dates
    where date_day <= '2026-06-05'::date
)

select
    date_day,
    year(date_day)                as year,
    month(date_day)                as month,
    day(date_day)                  as day_of_month,
    dayofweek(date_day)            as day_of_week,
    dayname(date_day)              as day_name,
    monthname(date_day)            as month_name,
    weekofyear(date_day)           as week_of_year,
    quarter(date_day)              as quarter,
    case when dayofweek(date_day) in (0, 6) then true else false end as is_weekend
from date_spine
