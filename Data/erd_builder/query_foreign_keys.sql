/*
    Export this result set as foreign_keys.csv.

    Composite foreign keys return one row per column mapping. column_ordinal
    preserves each child-column to parent-column pairing.

    The PowerShell builders expect these column names exactly:
        foreign_key_name, child_schema, child_table, child_column,
        parent_schema, parent_table, parent_column, column_ordinal,
        on_delete, on_update, is_disabled, is_not_trusted
*/

SELECT
    fk.name AS foreign_key_name,

    child_schema.name AS child_schema,
    child_table.name  AS child_table,
    child_col.name    AS child_column,

    parent_schema.name AS parent_schema,
    parent_table.name  AS parent_table,
    parent_col.name    AS parent_column,

    fkc.constraint_column_id AS column_ordinal,

    fk.delete_referential_action_desc AS on_delete,
    fk.update_referential_action_desc AS on_update,

    fk.is_disabled,
    fk.is_not_trusted
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc
  ON fkc.constraint_object_id = fk.object_id

JOIN sys.tables child_table
  ON child_table.object_id = fkc.parent_object_id
JOIN sys.schemas child_schema
  ON child_schema.schema_id = child_table.schema_id
JOIN sys.columns child_col
  ON child_col.object_id = fkc.parent_object_id
 AND child_col.column_id = fkc.parent_column_id

JOIN sys.tables parent_table
  ON parent_table.object_id = fkc.referenced_object_id
JOIN sys.schemas parent_schema
  ON parent_schema.schema_id = parent_table.schema_id
JOIN sys.columns parent_col
  ON parent_col.object_id = fkc.referenced_object_id
 AND parent_col.column_id = fkc.referenced_column_id

WHERE child_table.is_ms_shipped = 0
  AND parent_table.is_ms_shipped = 0
ORDER BY
    child_schema.name,
    child_table.name,
    fk.name,
    fkc.constraint_column_id;

