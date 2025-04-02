{{ config(materialized="table") }}

SELECT
  s.*,
  c.name as location_name,
  c.osm_id as osm_id
FROM
  {{source("staging","sensors")}} s
INNER JOIN
  {{source("staging","places")}} c
ON
  ST_WITHIN(s.geometry, c.geometry)