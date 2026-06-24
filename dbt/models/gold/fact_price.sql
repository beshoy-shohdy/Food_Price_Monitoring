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
)
SELECT
    ROW_NUMBER() OVER (ORDER BY p.product_id, s.source_id, d.date_id) AS price_sk,
    p.product_id,
    s.source_id,
    d.date_id,
    pr.price,
    pr.price_per_unit
FROM prices pr
LEFT JOIN products p
    ON pr.sku = p.sku
LEFT JOIN sources s
    ON pr.source = s.source_name
LEFT JOIN dates d
    ON CAST(pr.date AS DATE) = d.full_date