SELECT *
FROM OPENROWSET(
    BULK 'https://foodpricestorage.dfs.core.windows.net/silver/unified_prices_final.parquet',
    FORMAT = 'PARQUET'
) AS data