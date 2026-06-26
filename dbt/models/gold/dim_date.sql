WITH source AS (
    SELECT DISTINCT
        CAST(
            DATEADD(SECOND, CAST(date AS BIGINT) / 1000000000, '1970-01-01')
        AS DATE) AS full_date
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