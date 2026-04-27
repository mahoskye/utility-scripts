# ERD Builder Utilities

Utilities for turning SQL Server schema metadata into ERD-friendly artifacts.

The intended workflow is:

1. Run the SQL scripts in `sql_server_metadata_queries.sql`.
2. Export each result set as CSV using the expected file names below.
3. Use one of the PowerShell builders to generate diagram input.

## Expected CSV Files

Place these files in the same directory where you run the PowerShell scripts, or
pass explicit paths with script parameters.

| File | Produced By |
| --- | --- |
| `columns.csv` | `Columns` query |
| `primary_keys.csv` | `PrimaryKeys` query |
| `foreign_keys.csv` | `ForeignKeys` query |

## Scripts

| File | Purpose |
| --- | --- |
| `sql_server_metadata_queries.sql` | SQL Server catalog queries for columns, primary keys, and foreign keys. |
| `query_columns.sql` | Standalone columns query for `columns.csv`. |
| `query_primary_keys.sql` | Standalone primary-key query for `primary_keys.csv`. |
| `query_foreign_keys.sql` | Standalone foreign-key query for `foreign_keys.csv`. |
| `build_mermaid_by_table.ps1` | Builds one focused Mermaid ER diagram per table. |
| `build_erd_editor_schema_sql.ps1` | Builds schema-only MSSQL DDL for ERD Editor schema SQL import. |

## Recommended Path

For large databases, prefer `build_erd_editor_schema_sql.ps1`. Mermaid is useful
for quick per-table views, but large schemas usually exceed Mermaid viewer limits.

```powershell
.\build_erd_editor_schema_sql.ps1 `
  -ColumnsCsv .\columns.csv `
  -PrimaryKeysCsv .\primary_keys.csv `
  -ForeignKeysCsv .\foreign_keys.csv `
  -OutputFile .\erd-schema.sql
```

Then import `erd-schema.sql` into ERD Editor as schema SQL.
