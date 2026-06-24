WITH source AS (
    SELECT *
    FROM {{ ref('silver_wfp') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY product_name, date) AS price_sk,
    product_id,
    product_name,
    market_name,
    country,
    currency,
    unit,
    price,
    date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DATENAME(MONTH, date) AS month_name
FROM source