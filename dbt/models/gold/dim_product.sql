WITH source AS (
    SELECT DISTINCT
        sku,
        product_name,
        product_type,
        brand,
        category,
        sub_category,
        number_of_items,
        item_weight_grams
    FROM {{ ref('silver_unified_prices') }}
),
categories AS (
    SELECT *
    FROM {{ ref('dim_category') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY s.product_name) AS product_id,
    c.category_id,
    s.sku,
    s.product_name,
    s.product_type,
    s.brand,
    s.number_of_items,
    s.item_weight_grams,
    -- matching_key = product_type + brand + item_weight_grams
    LOWER(
        COALESCE(s.product_type, '') + '_' +
        COALESCE(s.brand, '') + '_' +
        COALESCE(CAST(s.item_weight_grams AS VARCHAR), '')
    ) AS matching_key
FROM source s
LEFT JOIN categories c
    ON s.category = c.category
    AND s.sub_category = c.sub_category