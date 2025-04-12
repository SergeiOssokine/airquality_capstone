LOAD DATA OVERWRITE {{table_name}}
{% if partition_by %}
PARTITION BY {{ partition_by }}
{% endif %}
{% if cluster_by %}
CLUSTER BY {{ cluster_by }}
{% endif %}
FROM FILES (
  format = 'PARQUET',
  uris = ['{{files_path}}/*.parquet']
);