/*
    Export this result set as primary_keys.csv.

    Composite primary keys return one row per key column. key_ordinal preserves
    the declared primary-key column order.

    The PowerShell builders expect these column names exactly:
        schema_name, table_name, primary_key_name, column_name, key_ordinal
*/

SELECT
    s.name  AS schema_name,
    t.name  AS table_name,
    kc.name AS primary_key_name,
    c.name  AS column_name,
    ic.key_ordinal
FROM sys.key_constraints kc
JOIN sys.tables t
  ON t.object_id = kc.parent_object_id
JOIN sys.schemas s
  ON s.schema_id = t.schema_id
JOIN sys.index_columns ic
  ON ic.object_id = kc.parent_object_id
 AND ic.index_id = kc.unique_index_id
JOIN sys.columns c
  ON c.object_id = ic.object_id
 AND c.column_id = ic.column_id
WHERE kc.type = 'PK'
ORDER BY
    s.name,
    t.name,
    kc.name,
    ic.key_ordinal;

