WITH source AS (
    SELECT DISTINCT
        category,
        sub_category
    FROM {{ ref('silver_unified_prices') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY category, sub_category) AS category_id,
    category,
    sub_category
FROM source