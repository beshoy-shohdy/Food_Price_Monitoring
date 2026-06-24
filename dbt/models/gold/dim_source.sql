WITH source AS (
    SELECT DISTINCT
        source
    FROM {{ ref('silver_unified_prices') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY source) AS source_id,
    source AS source_name
FROM source