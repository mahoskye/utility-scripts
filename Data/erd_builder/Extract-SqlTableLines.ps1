# ==== CONFIG ====
$InputFile  = "C:\temp\broken_export.csv"
$OutputFile = "C:\temp\sql_tables_only.txt"

$content = Get-Content -Path $InputFile -Raw

# FROM/JOIN can contain comma-separated lists.
$fromJoinRegex = [regex]'(?is)\b(from|join)\b\s+(.+?)(?=\b(where|join|on|group|order|having|union|except|intersect|limit|offset|qualify|$))'

# These usually have one target table immediately after the keyword.
$singleTableRegex = [regex]'(?is)\b(update|insert\s+into|delete\s+from|merge\s+into|truncate\s+table|into)\b\s+([A-Za-z0-9_\[\]\.#"]+)'

$results = @()

# Handle FROM / JOIN, including:
# FROM orders o, results r, comments c
foreach ($m in $fromJoinRegex.Matches($content)) {
    $tableSection = $m.Groups[2].Value

    foreach ($t in ($tableSection -split ',')) {
        $results += (($t.Trim() -split '\s+')[0])
    }
}

# Handle UPDATE / INSERT INTO / DELETE FROM / MERGE INTO / TRUNCATE TABLE / INTO
foreach ($m in $singleTableRegex.Matches($content)) {
    $results += $m.Groups[2].Value
}

$results |
    Where-Object {
        $_ -and
        $_ -notmatch '^\(' -and
        $_ -notmatch '^(select|where|on|and|or|values|set|using)$'
    } |
    ForEach-Object {
        $_.Trim().Trim('"').Trim("'").Trim('[').Trim(']')
    } |
    Where-Object { $_ } |
    Sort-Object -Unique |
    Set-Content -Path $OutputFile

Write-Host "Done. Extracted table names to $OutputFile"
