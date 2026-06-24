WITH source AS (
    SELECT DISTINCT
        sku,
        product_name,
        product_type,
        brand,
        number_of_items,
        item_weight_grams
    FROM {{ ref('silver_unified_prices') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY product_name) AS product_id,
    sku,
    product_name,
    product_type,
    brand,
    number_of_items,
    item_weight_grams,
    LOWER(
        COALESCE(product_type, '') + '_' +
        COALESCE(brand, '') + '_' +
        COALESCE(CAST(item_weight_grams AS VARCHAR), '')
    ) AS matching_key
FROM source