{{ config(materialized="table") }}

SELECT
    s.*,
    c.name AS location_name,
    c.osm_id,
    ST_AREA(c.geometry) / 1000000 AS area_in_square_km
FROM
    {{ source("staging","sensors") }} AS s
INNER JOIN
    {{ source("staging","places") }} AS c
    ON
        ST_WITHIN(s.geometry, c.geometry)
/*
We need to associate a unique location with every sensor
Since bounding boxes we are given can overlap we do the following:
- Compute the area of every bounding box for every place
- Partition by location_id and within each partition pick the location
with the _largest_ area
Thus we assign every sensor to a geographical place such that:
- its coordinates fall inside the bounding box
- the bounding box is the largest of all that fit these coordinates
*/
QUALIFY
    RANK()
        OVER (
            PARTITION BY s.location_id
            ORDER BY ST_AREA(c.geometry) DESC
        )
    = 1
