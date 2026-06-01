$ErrorActionPreference = "Stop"

$fixtureRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $fixtureRoot "..\..")
$expectedPath = Join-Path $fixtureRoot "expected-findings.json"
$expected = Get-Content -Raw -Path $expectedPath | ConvertFrom-Json

$failures = @()
$skillNames = $expected.PSObject.Properties.Name | Sort-Object

foreach ($skill in $skillNames) {
    $entry = $expected.$skill
    $skillDir = Join-Path $repoRoot "skills\$skill"
    foreach ($required in @("SKILL.md", "references\rules.yaml", "references\report-template.md")) {
        $requiredPath = Join-Path $skillDir $required
        if (-not (Test-Path $requiredPath)) {
            $failures += "$skill missing $required"
        }
    }

    foreach ($target in $entry.targets) {
        $targetPath = Join-Path $fixtureRoot $target
        if (-not (Test-Path $targetPath)) {
            $failures += "$skill target missing: $target"
        }
    }

    $combined = ""
    foreach ($target in $entry.targets) {
        $targetPath = Join-Path $fixtureRoot $target
        if (Test-Path $targetPath) {
            $combined += "`n" + (Get-Content -Raw -Path $targetPath)
        }
    }

    foreach ($signal in $entry.signals) {
        if (-not $combined.Contains($signal)) {
            $failures += "$skill signal missing: $signal"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Skill fixture coverage FAILED" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    exit 1
}

Write-Host "Skill fixture coverage passed for $($skillNames.Count) skills." -ForegroundColor Green
Write-Host "Fixture root: $fixtureRoot"
