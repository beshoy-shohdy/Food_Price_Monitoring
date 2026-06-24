SELECT
    country,
    market_name,
    CAST(product_id AS INT) AS product_id,
    product_name,
    currency,
    unit,
    CAST(price AS FLOAT) AS price,
    CAST(
        DATEADD(SECOND, CAST(date AS BIGINT) / 1000000000, '1970-01-01')
    AS DATE) AS date
FROM OPENROWSET(
    BULK 'https://foodpricestorage.dfs.core.windows.net/silver/wfp_egypt_clean3.parquet',
    FORMAT = 'PARQUET'
) AS data