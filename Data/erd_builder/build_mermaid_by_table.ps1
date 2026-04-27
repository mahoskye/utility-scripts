param(
    # CSV exported from the Columns query in sql_server_metadata_queries.sql.
    [string]$ColumnsCsv = ".\columns.csv",

    # CSV exported from the PrimaryKeys query in sql_server_metadata_queries.sql.
    [string]$PrimaryKeysCsv = ".\primary_keys.csv",

    # CSV exported from the ForeignKeys query in sql_server_metadata_queries.sql.
    [string]$ForeignKeysCsv = ".\foreign_keys.csv",

    # Directory that receives one .mmd file per table.
    [string]$OutputDir = ".\erd-by-table",

    # Include a synthetic relationship entity showing child/parent column pairs.
    # This makes Mermaid diagrams more useful without needing column-level edges.
    [switch]$IncludeRelationshipEntities
)

# Mermaid ER diagrams are best for focused views. This script creates one file
# per table that includes:
#   - the focus table
#   - immediate parent tables referenced by the focus table
#   - immediate child tables that reference the focus table
#   - direct FK relationships touching the focus table

$columns = Import-Csv $ColumnsCsv
$primaryKeys = Import-Csv $PrimaryKeysCsv
$foreignKeys = Import-Csv $ForeignKeysCsv | Where-Object {
    # Disabled foreign keys are skipped because they do not represent active
    # enforced relationships in SQL Server.
    ([string]$_.is_disabled).Trim() -ne "1"
}

if (!(Test-Path $OutputDir)) {
    [void](New-Item -ItemType Directory -Path $OutputDir)
}

function EntityName($schema, $table) {
    # Mermaid entity identifiers need to be simple. The visible schema/table
    # name is preserved in the filename; entity names use schema__table.
    return ((([string]$schema).Trim() + "__" + ([string]$table).Trim()) -replace '[^A-Za-z0-9_]', '_')
}

function FileSafeName($schema, $table) {
    return ((([string]$schema).Trim() + "." + ([string]$table).Trim()) -replace '[^A-Za-z0-9_.-]', '_')
}

function TableKey($schema, $table) {
    return (([string]$schema).Trim() + "." + ([string]$table).Trim()).ToLower()
}

function TryParseInt($value, $fallback) {
    $result = 0
    if ([int]::TryParse(([string]$value), [ref]$result)) {
        return $result
    }

    return $fallback
}

function MermaidType($sqlType) {
    # Mermaid ER supports broad type labels. These are intentionally generic.
    switch -Regex (([string]$sqlType).Trim().ToLower()) {
        'char|text|xml|uniqueidentifier' { return "string" }
        'date|time' { return "datetime" }
        'int|decimal|numeric|money|float|real|bit' { return "number" }
        'binary|image|varbinary' { return "binary" }
        default { return "string" }
    }
}

# Fast lookup to mark columns as PK/FK in entity blocks.
$pkLookup = @{}
foreach ($pk in $primaryKeys) {
    $key = "$(TableKey $pk.schema_name $pk.table_name).$(([string]$pk.column_name).Trim().ToLower())"
    $pkLookup[$key] = $true
}

$fkLookup = @{}
foreach ($fk in $foreignKeys) {
    $key = "$(TableKey $fk.child_schema $fk.child_table).$(([string]$fk.child_column).Trim().ToLower())"
    $fkLookup[$key] = $true
}

$allTables =
    $columns |
    Group-Object schema_name, table_name |
    ForEach-Object {
        $first = $_.Group[0]
        [PSCustomObject]@{
            schema_name = $first.schema_name
            table_name = $first.table_name
            table_key = TableKey $first.schema_name $first.table_name
        }
    } |
    Sort-Object table_key

foreach ($table in $allTables) {
    $focusKey = $table.table_key
    Write-Host "Writing $($table.schema_name).$($table.table_name)"

    # Include the focus table and every table on either side of a direct FK.
    $included = @{}
    $included[$focusKey] = $true

    foreach ($fk in $foreignKeys) {
        $childKey = TableKey $fk.child_schema $fk.child_table
        $parentKey = TableKey $fk.parent_schema $fk.parent_table

        if ($childKey -eq $focusKey -or $parentKey -eq $focusKey) {
            $included[$childKey] = $true
            $included[$parentKey] = $true
        }
    }

    $diagramColumns = $columns | Where-Object {
        $key = TableKey $_.schema_name $_.table_name
        $included.ContainsKey($key)
    }

    $diagramForeignKeys = $foreignKeys | Where-Object {
        $childKey = TableKey $_.child_schema $_.child_table
        $parentKey = TableKey $_.parent_schema $_.parent_table

        $included.ContainsKey($childKey) -and
        $included.ContainsKey($parentKey) -and
        ($childKey -eq $focusKey -or $parentKey -eq $focusKey)
    }

    $lines = New-Object System.Collections.ArrayList
    [void]$lines.Add("erDiagram")

    $tableGroups =
        $diagramColumns |
        Group-Object schema_name, table_name |
        Sort-Object Name

    foreach ($tableGroup in $tableGroups) {
        $first = $tableGroup.Group[0]
        $entity = EntityName $first.schema_name $first.table_name

        [void]$lines.Add("    $entity {")

        foreach ($col in ($tableGroup.Group | Sort-Object { TryParseInt $_.column_id 0 })) {
            $columnKey = "$(TableKey $col.schema_name $col.table_name).$(([string]$col.column_name).Trim().ToLower())"
            $type = MermaidType $col.data_type
            $name = (([string]$col.column_name).Trim() -replace '[^A-Za-z0-9_]', '_')

            $markers = @()
            if ($pkLookup.ContainsKey($columnKey)) { $markers += "PK" }
            if ($fkLookup.ContainsKey($columnKey)) { $markers += "FK" }

            $markerText = ""
            if ($markers.Count -gt 0) {
                $markerText = " " + ($markers -join ",")
            }

            [void]$lines.Add("        $type $name$markerText")
        }

        [void]$lines.Add("    }")
        [void]$lines.Add("")
    }

    $relationshipGroups =
        $diagramForeignKeys |
        Group-Object foreign_key_name, child_schema, child_table, parent_schema, parent_table |
        Sort-Object Name

    foreach ($relGroup in $relationshipGroups) {
        $first = $relGroup.Group[0]
        $parent = EntityName $first.parent_schema $first.parent_table
        $child = EntityName $first.child_schema $first.child_table
        $fkName = (([string]$first.foreign_key_name).Trim() -replace '[^A-Za-z0-9_]', '_')

        if ($IncludeRelationshipEntities) {
            # Optional middle entity that makes column mappings visible in
            # Mermaid, which otherwise only connects table to table.
            $relEntity = "REL__$fkName"
            [void]$lines.Add("    $relEntity {")

            $orderedCols = $relGroup.Group | Sort-Object { TryParseInt $_.column_ordinal 0 }
            $n = 1

            foreach ($fkCol in $orderedCols) {
                $parentColumn = "$($fkCol.parent_table).$($fkCol.parent_column)"
                $childColumn = "$($fkCol.child_table).$($fkCol.child_column)"

                $parentComment = (([string]$parentColumn) -replace '"', '')
                $childComment = (([string]$childColumn) -replace '"', '')

                [void]$lines.Add("        string parent_$n `"$parentComment`"")
                [void]$lines.Add("        string child_$n `"$childComment`"")

                $n += 1
            }

            [void]$lines.Add("    }")
            [void]$lines.Add("")
            [void]$lines.Add("    $parent ||--|| $relEntity : parent")
            [void]$lines.Add("    $relEntity ||--o{ $child : child")
        } else {
            # Basic table-level relationship with the FK constraint as label.
            [void]$lines.Add("    $parent ||--o{ $child : $fkName")
        }
    }

    $fileName = FileSafeName $table.schema_name $table.table_name
    $outputPath = Join-Path $OutputDir "$fileName.mmd"

    Set-Content -Path $outputPath -Value $lines -Encoding UTF8
}

Write-Host "Wrote per-table Mermaid diagrams to $OutputDir"

