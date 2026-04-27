/*
    Export this result set as columns.csv.

    The PowerShell builders expect these column names exactly:
        schema_name, table_name, column_name, data_type, max_length,
        precision, scale, is_nullable, column_id
*/

SELECT
    s.name AS schema_name,
    t.name AS table_name,
    c.name AS column_name,
    ty.name AS data_type,
    c.max_length,
    c.precision,
    c.scale,
    c.is_nullable,
    c.column_id
FROM sys.tables t
JOIN sys.schemas s
  ON s.schema_id = t.schema_id
JOIN sys.columns c
  ON c.object_id = t.object_id
JOIN sys.types ty
  ON ty.user_type_id = c.user_type_id
WHERE t.is_ms_shipped = 0
ORDER BY
    s.name,
    t.name,
    c.column_id;

