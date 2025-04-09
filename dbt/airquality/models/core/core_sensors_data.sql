{{ config(materialized = "table") }}


with spatial_averages as (
    select
        time_stamp,
        quantity,
        AVG(value) as spatial_average
    from {{ ref("stg_sensors_data") }}
    group by 1,2
)

select
    location_name,
    time_stamp,
    quantity,
    value
from {{ ref("stg_sensors_data") }}
union all
select
    "Spatial average" as location_name,
    time_stamp,
    quantity,
    spatial_average as value
from spatial_averages