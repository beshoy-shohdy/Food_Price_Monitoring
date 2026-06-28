WITH prices AS (
    SELECT * FROM {{ ref('silver_unified_prices') }}
),
products AS (
    SELECT * FROM {{ ref('dim_product') }}
),
sources AS (
    SELECT * FROM {{ ref('dim_source') }}
),
dates AS (
    SELECT * FROM {{ ref('dim_date') }}
),
categories AS (
    SELECT * FROM {{ ref('dim_category') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY p.product_id, s.source_id, d.date_id) AS price_sk,
    p.product_id,
    s.source_id,
    d.date_id,
    c.category_id,
    pr.price,
    pr.price_per_unit
FROM prices pr
LEFT JOIN products p
    ON pr.sku = p.sku
LEFT JOIN sources s
    ON pr.source = s.source_name
LEFT JOIN dates d
    ON CAST(DATEADD(SECOND, CAST(pr.date AS BIGINT) / 1000000000, '1970-01-01') AS DATE) = d.full_date
LEFT JOIN categories c
    ON pr.category = c.category
    AND pr.sub_category = c.sub_category