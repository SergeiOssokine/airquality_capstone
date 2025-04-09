{{ config(materialized = "view") }}

select
    location AS location_name,
    parameter as quantity,
    units,
    value,
    TIMESTAMP(datetime) as time_stamp
from {{ source("staging", "sensors_data") }}
