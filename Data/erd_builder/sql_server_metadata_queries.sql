/*
    SQL Server ERD metadata extraction queries.

    Run each result set separately and export to CSV using these names:

        1. Columns      -> columns.csv
        2. PrimaryKeys  -> primary_keys.csv
        3. ForeignKeys  -> foreign_keys.csv

    These queries use sys catalog views instead of INFORMATION_SCHEMA because
    the sys views expose constraint ordering and SQL Server-specific details
    needed by ERD generators.
*/

/* -------------------------------------------------------------------------
   Columns

   Export this result set as columns.csv.

   Notes:
   - max_length is bytes in sys.columns. The PowerShell SQL builder divides
     nchar/nvarchar lengths by 2 when reconstructing type declarations.
   - max_length = -1 means MAX for varchar/nvarchar/varbinary.
   ------------------------------------------------------------------------- */
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

/* -------------------------------------------------------------------------
   PrimaryKeys

   Export this result set as primary_keys.csv.

   Composite primary keys return one row per key column. key_ordinal preserves
   the column order declared by the primary key index.
   ------------------------------------------------------------------------- */
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

/* -------------------------------------------------------------------------
   ForeignKeys

   Export this result set as foreign_keys.csv.

   Composite foreign keys return one row per column mapping.
   column_ordinal preserves each child-column to parent-column pairing.
   ------------------------------------------------------------------------- */
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

