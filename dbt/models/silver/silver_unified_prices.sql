SELECT *
FROM OPENROWSET(
    BULK 'https://foodpricestorage.dfs.core.windows.net/silver/unified_full_data.parquet',
    FORMAT = 'PARQUET'
) AS data