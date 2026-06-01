$ErrorActionPreference = "Stop"

$fixtureRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$reportScript = Join-Path $fixtureRoot "generate-report.ps1"
$coverageScript = Join-Path $fixtureRoot "run-fixture-check.ps1"
$matrixPath = Join-Path $fixtureRoot "results\format-skill-matrix.json"

& $coverageScript
& $reportScript

$matrix = Get-Content -Raw -Path $matrixPath | ConvertFrom-Json
$failures = @()

if ($matrix.combinations -ne 25) {
    $failures += "Expected 25 format skill/type combinations, found $($matrix.combinations)"
}

foreach ($row in $matrix.results) {
    if ($row.expectedSignals -gt 0 -and $row.status -ne "Pass") {
        $failures += "$($row.skill) failed $($row.fileType): $($row.matchedSignals)/$($row.expectedSignals)"
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Skill combination suite FAILED" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    exit 1
}

Write-Host "Skill combination suite passed." -ForegroundColor Green
Write-Host "Format matrix: $matrixPath"
