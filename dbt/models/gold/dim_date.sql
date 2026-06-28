WITH source AS (
    SELECT DISTINCT
        CAST(date AS DATE) AS full_date
    FROM {{ ref('silver_unified_prices') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY full_date) AS date_id,
    full_date,
    DAY(full_date) AS day,
    MONTH(full_date) AS month,
    DATENAME(MONTH, full_date) AS month_name,
    YEAR(full_date) AS year
FROM source