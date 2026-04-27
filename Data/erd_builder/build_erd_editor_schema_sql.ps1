param(
    # CSV exported from the Columns query in sql_server_metadata_queries.sql.
    [string]$ColumnsCsv = ".\columns.csv",

    # CSV exported from the PrimaryKeys query in sql_server_metadata_queries.sql.
    [string]$PrimaryKeysCsv = ".\primary_keys.csv",

    # CSV exported from the ForeignKeys query in sql_server_metadata_queries.sql.
    [string]$ForeignKeysCsv = ".\foreign_keys.csv",

    # Schema-only SQL file to import into ERD Editor.
    [string]$OutputFile = ".\erd-schema.sql"
)

# This script targets Windows PowerShell 5.1 / PowerShell ISE, so it avoids
# newer operators and generic collection syntax that can be awkward in ISE.

$columns = Import-Csv $ColumnsCsv
$primaryKeys = Import-Csv $PrimaryKeysCsv
$foreignKeys = Import-Csv $ForeignKeysCsv | Where-Object {
    # Ignore disabled FKs by default. They are not active logical relationships.
    ([string]$_.is_disabled).Trim() -ne "1"
}

function SqlName($name) {
    # Bracket and escape SQL Server identifiers, including names containing ].
    return "[" + (([string]$name).Trim() -replace "]", "]]") + "]"
}

function FullTableName($schema, $table) {
    return "$(SqlName $schema).$(SqlName $table)"
}

function TableKey($schema, $table) {
    # Stable case-insensitive key used to join CSV rows in PowerShell.
    return (([string]$schema).Trim() + "." + ([string]$table).Trim()).ToLower()
}

function TryParseInt($value, $fallback) {
    $result = 0
    if ([int]::TryParse(([string]$value), [ref]$result)) {
        return $result
    }

    return $fallback
}

function ColumnType($col) {
    # Reconstruct enough SQL Server type detail for an ERD parser.
    # This does not try to preserve every exotic type modifier.
    $type = ([string]$col.data_type).Trim().ToLower()
    $maxLength = TryParseInt $col.max_length 0
    $precision = TryParseInt $col.precision 0
    $scale = TryParseInt $col.scale 0

    switch ($type) {
        "varchar" {
            if ($maxLength -eq -1) { return "varchar(MAX)" }
            return "varchar($maxLength)"
        }
        "char" {
            return "char($maxLength)"
        }
        "nvarchar" {
            if ($maxLength -eq -1) { return "nvarchar(MAX)" }
            return "nvarchar($([int]($maxLength / 2)))"
        }
        "nchar" {
            return "nchar($([int]($maxLength / 2)))"
        }
        "varbinary" {
            if ($maxLength -eq -1) { return "varbinary(MAX)" }
            return "varbinary($maxLength)"
        }
        "binary" {
            return "binary($maxLength)"
        }
        "decimal" {
            return "decimal($precision,$scale)"
        }
        "numeric" {
            return "numeric($precision,$scale)"
        }
        "datetime2" {
            return "datetime2($scale)"
        }
        "datetimeoffset" {
            return "datetimeoffset($scale)"
        }
        "time" {
            return "time($scale)"
        }
        default {
            # Types such as int, bigint, bit, date, datetime, uniqueidentifier,
            # text, xml, geography, and hierarchyid are emitted without length.
            return $type
        }
    }
}

# Build one primary-key definition per table. Composite keys are kept in
# key_ordinal order so generated SQL matches the catalog definition.
$pkByTable = @{}
foreach ($pkGroup in ($primaryKeys | Group-Object schema_name, table_name, primary_key_name)) {
    $first = $pkGroup.Group[0]
    $key = TableKey $first.schema_name $first.table_name

    $pkByTable[$key] = [PSCustomObject]@{
        name = $first.primary_key_name
        columns = @(
            $pkGroup.Group |
            Sort-Object { TryParseInt $_.key_ordinal 0 } |
            ForEach-Object { $_.column_name }
        )
    }
}

$lines = New-Object System.Collections.ArrayList
[void]$lines.Add("/*")
[void]$lines.Add("    Schema-only SQL generated from SQL Server metadata CSVs.")
[void]$lines.Add("    Intended for ERD Editor schema SQL import, not production deployment.")
[void]$lines.Add("*/")
[void]$lines.Add("")

$tableGroups =
    $columns |
    Group-Object schema_name, table_name |
    Sort-Object Name

foreach ($tableGroup in $tableGroups) {
    $first = $tableGroup.Group[0]
    $tableKey = TableKey $first.schema_name $first.table_name
    $defs = New-Object System.Collections.ArrayList

    [void]$lines.Add("CREATE TABLE $(FullTableName $first.schema_name $first.table_name) (")

    foreach ($col in ($tableGroup.Group | Sort-Object { TryParseInt $_.column_id 0 })) {
        $nullable = ([string]$col.is_nullable).Trim().ToLower()
        $nullText = "NULL"

        if ($nullable -eq "0" -or $nullable -eq "no" -or $nullable -eq "false") {
            $nullText = "NOT NULL"
        }

        [void]$defs.Add("    $(SqlName $col.column_name) $(ColumnType $col) $nullText")
    }

    if ($pkByTable.ContainsKey($tableKey)) {
        $pk = $pkByTable[$tableKey]
        $pkColumns = ($pk.columns | ForEach-Object { SqlName $_ }) -join ", "
        [void]$defs.Add("    CONSTRAINT $(SqlName $pk.name) PRIMARY KEY ($pkColumns)")
    }

    for ($i = 0; $i -lt $defs.Count; $i++) {
        $suffix = ","
        if ($i -eq $defs.Count - 1) {
            $suffix = ""
        }

        [void]$lines.Add($defs[$i] + $suffix)
    }

    [void]$lines.Add(");")
    [void]$lines.Add("")
}

# Emit FKs after all CREATE TABLE statements so table declaration order does not
# matter. Composite FKs are grouped and ordered by column_ordinal.
$fkGroups =
    $foreignKeys |
    Group-Object foreign_key_name, child_schema, child_table, parent_schema, parent_table |
    Sort-Object Name

foreach ($fkGroup in $fkGroups) {
    $first = $fkGroup.Group[0]
    $orderedRows = $fkGroup.Group | Sort-Object { TryParseInt $_.column_ordinal 0 }

    $childColumnSql = ($orderedRows | ForEach-Object { SqlName $_.child_column }) -join ", "
    $parentColumnSql = ($orderedRows | ForEach-Object { SqlName $_.parent_column }) -join ", "

    [void]$lines.Add("ALTER TABLE $(FullTableName $first.child_schema $first.child_table) ADD CONSTRAINT $(SqlName $first.foreign_key_name)")
    [void]$lines.Add("    FOREIGN KEY ($childColumnSql)")
    [void]$lines.Add("    REFERENCES $(FullTableName $first.parent_schema $first.parent_table) ($parentColumnSql);")
    [void]$lines.Add("")
}

Set-Content -Path $OutputFile -Value $lines -Encoding UTF8

Write-Host "Wrote $OutputFile"

