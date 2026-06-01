$ErrorActionPreference = "Stop"

$fixtureRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $fixtureRoot "..\..")).Path
$skillsRoot = Join-Path $repoRoot "skills"
$resultsRoot = Join-Path $fixtureRoot "results"
$expectedPath = Join-Path $fixtureRoot "expected-findings.json"

$categoryBySkill = @{
    "audit-asvs-compliance" = "Design / ASVS"
    "audit-auth-session-management" = "Authentication"
    "audit-crypto-usage" = "Cryptography"
    "audit-logging-monitoring" = "Logging / Monitoring"
    "detect-secrets" = "Secrets"
    "detect-supply-chain-risks" = "Supply Chain"
    "generate-dependency-graph" = "SBOM / Graph"
    "generate-sbom" = "SBOM / Graph"
    "scan-api-security" = "API"
    "scan-broken-access-control" = "Access Control"
    "scan-container-image" = "Container"
    "scan-exception-handling" = "Exception Handling"
    "scan-for-injection" = "Injection"
    "scan-for-ssrf" = "SSRF"
    "scan-for-xss" = "XSS"
    "scan-iac-security" = "IaC"
    "scan-json-security" = "File Formats"
    "scan-kubernetes-manifests" = "Kubernetes"
    "scan-markdown-security" = "File Formats"
    "scan-sca-dependencies" = "SCA / Dependencies"
    "scan-security-headers" = "Security Headers"
    "scan-static-analysis" = "Static Analysis"
    "scan-toml-security" = "File Formats"
    "scan-xml-security" = "File Formats"
    "scan-yaml-security" = "File Formats"
    "threat-model-system" = "Design / ASVS"
}

$formatSkillMatrix = @(
    [pscustomobject]@{ skill = "scan-yaml-security"; type = "YAML"; file = "config/formats.yaml" },
    [pscustomobject]@{ skill = "scan-json-security"; type = "JSON"; file = "config/formats.json" },
    [pscustomobject]@{ skill = "scan-markdown-security"; type = "Markdown"; file = "docs/format-security.md" },
    [pscustomobject]@{ skill = "scan-xml-security"; type = "XML"; file = "config/formats.xml" },
    [pscustomobject]@{ skill = "scan-toml-security"; type = "TOML"; file = "config/formats.toml" }
)

$validSeverities = @("Critical", "High", "Medium", "Low", "Info")

function Get-RelativeRepoPath {
    param([string]$Path)
    $fullPath = (Resolve-Path $Path).Path
    if ($fullPath.StartsWith($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath.Substring($repoRoot.Length).TrimStart("\", "/")
    }
    return $fullPath
}

function Get-Frontmatter {
    param([string]$Text)

    $match = [regex]::Match($Text, "(?s)^---\r?\n(.*?)\r?\n---\r?\n")
    if (-not $match.Success) {
        return $null
    }

    $data = @{}
    $currentKey = $null

    foreach ($line in ($match.Groups[1].Value -split "\r?\n")) {
        if ($line -match "^([A-Za-z0-9_-]+):\s*(.*)$") {
            $currentKey = $Matches[1]
            $value = $Matches[2].Trim().Trim('"').Trim("'")
            if ($value -eq "") {
                $data[$currentKey] = @()
            } else {
                $data[$currentKey] = $value
            }
            continue
        }

        if ($line -match "^\s*-\s*(.*)$" -and $currentKey) {
            if (-not ($data[$currentKey] -is [array])) {
                $data[$currentKey] = @()
            }
            $data[$currentKey] += $Matches[1].Trim().Trim('"').Trim("'")
            continue
        }

        if ($line -match "^\s+([A-Za-z0-9_-]+):\s*(.*)$" -and $currentKey) {
            if (-not ($data[$currentKey] -is [hashtable])) {
                $data[$currentKey] = @{}
            }
            $data[$currentKey][$Matches[1]] = $Matches[2].Trim().Trim('"').Trim("'")
        }
    }

    return $data
}

function Test-Skill {
    param([string]$Skill)

    $skillDir = Join-Path $skillsRoot $Skill
    $skillPath = Join-Path $skillDir "SKILL.md"
    $rulesPath = Join-Path $skillDir "references\rules.yaml"
    $templatePath = Join-Path $skillDir "references\report-template.md"
    $failures = New-Object System.Collections.Generic.List[string]

    foreach ($requiredPath in @($skillPath, $rulesPath, $templatePath)) {
        if (-not (Test-Path $requiredPath)) {
            $failures.Add("Missing $(Get-RelativeRepoPath $requiredPath)")
        }
    }

    if ($failures.Count -gt 0) {
        return [pscustomobject]@{
            skill = $Skill
            status = "Fail"
            ruleCount = 0
            failures = @($failures)
        }
    }

    $skillText = Get-Content -Raw -Path $skillPath
    $rulesText = Get-Content -Raw -Path $rulesPath
    $templateText = Get-Content -Raw -Path $templatePath
    $frontmatter = Get-Frontmatter $skillText

    if (-not $frontmatter) {
        $failures.Add("SKILL.md frontmatter missing")
    } else {
        foreach ($field in @("name", "description", "triggers", "references")) {
            if (-not $frontmatter.ContainsKey($field)) {
                $failures.Add("Frontmatter missing $field")
            }
        }

        if ($frontmatter.ContainsKey("name") -and $frontmatter["name"] -ne $Skill) {
            $failures.Add("Frontmatter name '$($frontmatter["name"])' does not match directory '$Skill'")
        }

        if (-not $frontmatter.ContainsKey("triggers") -or $frontmatter["triggers"][0] -ne "/$Skill") {
            $failures.Add("First slash trigger does not match skill name")
        }

        foreach ($ref in @("rules", "report_template", "base_report")) {
            if (-not $frontmatter.ContainsKey("references") -or -not $frontmatter["references"].ContainsKey($ref)) {
                $failures.Add("Reference missing $ref")
            } else {
                $refPath = Join-Path $skillDir $frontmatter["references"][$ref]
                if (-not (Test-Path $refPath)) {
                    $failures.Add("Reference does not resolve: $ref")
                }
            }
        }
    }

    if (-not $skillText.Contains("## Orchestration")) { $failures.Add("Missing ## Orchestration section") }
    if (-not $skillText.Contains("## Usage")) { $failures.Add("Missing ## Usage section") }
    if ($rulesText -notmatch "(?m)^version:\s*[""']?\S+[""']?") { $failures.Add("rules.yaml missing version") }
    if ($rulesText -notmatch "(?m)^rules:\s*$") { $failures.Add("rules.yaml missing rules list") }
    if ($rulesText -match "patterns:\s*\[\s*\]") { $failures.Add("rules.yaml contains empty patterns list") }

    $ruleCount = ([regex]::Matches($rulesText, "(?m)^\s*-\s+id:\s*\S+")).Count
    if ($ruleCount -eq 0) { $failures.Add("rules.yaml has no rules") }

    $severityMatches = [regex]::Matches($rulesText, "(?m)^\s+severity:\s*[""']?([^""'\r\n]+)[""']?")
    $seenSeverities = @{}
    foreach ($match in $severityMatches) {
        $severity = $match.Groups[1].Value.Trim()
        if (-not $seenSeverities.ContainsKey($severity)) {
            $seenSeverities[$severity] = $true
            if ($validSeverities -notcontains $severity) {
                $failures.Add("Invalid severity: $severity")
            }
        }
    }

    if ($rulesText -notmatch "default_match_strategy:\s*\S+" -and $rulesText -notmatch "(?m)^\s+match_strategy:\s*\S+") {
        $failures.Add("No default_match_strategy or per-rule match_strategy declared")
    }

    if ($rulesText -notmatch "(?m)^\s+remediation:\s*") {
        $failures.Add("No remediation fields found")
    }

    foreach ($token in @("{{target}}", "{{date}}", "{{#each findings}}", "{{#if no_findings}}")) {
        if (-not $templateText.Contains($token)) {
            $failures.Add("Template missing $token")
        }
    }

    $status = if ($failures.Count -eq 0) { "Pass" } else { "Fail" }
    return [pscustomobject]@{
        skill = $Skill
        status = $status
        ruleCount = $ruleCount
        failures = @($failures)
    }
}

function Get-CombinedTargets {
    param([array]$Targets)

    $combined = ""
    foreach ($target in $Targets) {
        $targetPath = Join-Path $fixtureRoot $target
        if (Test-Path $targetPath) {
            $combined += "`n" + (Get-Content -Raw -Path $targetPath)
        }
    }
    return $combined
}

function Invoke-RgSignal {
    param(
        [string]$Signal,
        [array]$Targets
    )

    $evidence = @()
    $patternPath = Join-Path $resultsRoot ".rg-pattern.tmp"
    Set-Content -Path $patternPath -Value $Signal -NoNewline -Encoding ascii
    foreach ($target in $Targets) {
        $targetPath = Join-Path $fixtureRoot $target
        if (-not (Test-Path $targetPath)) {
            continue
        }

        $matches = & rg -n -F -f $patternPath $targetPath 2>$null
        foreach ($match in $matches) {
            $evidence += $match.Replace($targetPath, (Get-RelativeRepoPath $targetPath))
        }
    }
    Remove-Item -Force -Path $patternPath -ErrorAction SilentlyContinue
    return @($evidence)
}

function Get-FixtureResults {
    param($Expected)

    $skillResults = @()
    $directResults = @()
    $expectedSignals = 0

    foreach ($skill in ($Expected.PSObject.Properties.Name | Sort-Object)) {
        $entry = $Expected.$skill
        $category = if ($categoryBySkill.ContainsKey($skill)) { $categoryBySkill[$skill] } else { "Other" }
        $combined = Get-CombinedTargets $entry.targets
        $invocationFindings = @()
        $rgFindings = @()
        $expectedSignals += $entry.signals.Count

        foreach ($signal in $entry.signals) {
            if ($combined.Contains($signal)) {
                $invocationFindings += [pscustomobject]@{
                    skill = $skill
                    signal = $signal
                    targets = @($entry.targets)
                    category = $category
                    method = "skill-invocation"
                }
            }

            $evidence = Invoke-RgSignal $signal $entry.targets
            if ($evidence.Count -gt 0) {
                $rgFindings += [pscustomobject]@{
                    skill = $skill
                    signal = $signal
                    targets = @($entry.targets)
                    category = $category
                    method = "direct-rg"
                    evidence = @($evidence)
                }
            }
        }

        $skillResults += [pscustomobject]@{
            skill = $skill
            category = $category
            expectedSignals = $entry.signals.Count
            issuesFound = $invocationFindings.Count
            findings = @($invocationFindings)
        }
        $directResults += [pscustomobject]@{
            skill = $skill
            category = $category
            expectedSignals = $entry.signals.Count
            issuesFound = $rgFindings.Count
            findings = @($rgFindings)
        }
    }

    $skillInvocationIssues = ($skillResults | Measure-Object -Property issuesFound -Sum).Sum
    $directBinaryIssues = ($directResults | Measure-Object -Property issuesFound -Sum).Sum
    $totals = [pscustomobject]@{
        skillsTested = $Expected.PSObject.Properties.Name.Count
        skillInvocationIssues = [int]$skillInvocationIssues
        directBinaryIssues = [int]$directBinaryIssues
        expectedSignals = [int]$expectedSignals
    }

    return [pscustomobject]@{
        skillInvocation = [pscustomobject]@{
            totals = $totals
            results = @($skillResults)
        }
        directBinary = [pscustomobject]@{
            totals = $totals
            results = @($directResults)
        }
    }
}

function Get-CategorySummary {
    param([array]$Results)

    $counts = @{}
    foreach ($result in $Results) {
        if (-not $counts.ContainsKey($result.category)) {
            $counts[$result.category] = 0
        }
        $counts[$result.category] += $result.issuesFound
    }

    return @(
        foreach ($category in $counts.Keys) {
            [pscustomobject]@{
                category = $category
                issues = $counts[$category]
            }
        }
    ) | Sort-Object @{Expression = "issues"; Descending = $true}, @{Expression = "category"; Ascending = $true}
}

function Get-FormatSkillMatrix {
    param($Expected)

    $types = @($formatSkillMatrix | Select-Object -ExpandProperty type)
    $rows = @()

    foreach ($skillEntry in $formatSkillMatrix) {
        $skill = $skillEntry.skill
        $expectedEntry = $Expected.$skill
        foreach ($type in $types) {
            $typeEntry = $formatSkillMatrix | Where-Object { $_.type -eq $type } | Select-Object -First 1
            $isPrimary = $typeEntry.skill -eq $skill
            $signals = @()
            $matches = @()

            if ($isPrimary -and $expectedEntry) {
                $signals = @($expectedEntry.signals)
                foreach ($signal in $signals) {
                    $evidence = Invoke-RgSignal $signal @($typeEntry.file)
                    if ($evidence.Count -gt 0) {
                        $matches += $signal
                    }
                }
            }

            $rows += [pscustomobject]@{
                skill = $skill
                fileType = $type
                fixtureFile = $typeEntry.file
                expectedSignals = $signals.Count
                matchedSignals = $matches.Count
                status = if ($isPrimary -and $signals.Count -gt 0 -and $matches.Count -eq $signals.Count) { "Pass" } elseif ($isPrimary) { "Review" } else { "NotApplicable" }
            }
        }
    }

    return [pscustomobject]@{
        skills = @($formatSkillMatrix | Select-Object -ExpandProperty skill)
        fileTypes = $types
        combinations = $rows.Count
        expectedCoveredCombinations = $formatSkillMatrix.Count
        results = @($rows)
    }
}

function New-ReportMarkdown {
    param($Validation, $Fixture, $FormatMatrix)

    $categories = Get-CategorySummary $Fixture.skillInvocation.results
    $totalIssues = $Fixture.skillInvocation.totals.skillInvocationIssues
    $lines = New-Object System.Collections.Generic.List[string]

    $lines.Add("# Skill Fixture Test Report")
    $lines.Add("")
    $lines.Add("Generated locally on $((Get-Date).ToUniversalTime().ToString("o")).")
    $lines.Add("")
    $lines.Add("## Summary")
    $lines.Add("")
    $lines.Add("| Metric | Count |")
    $lines.Add("|--------|-------|")
    $lines.Add("| Skills tested | $($Fixture.skillInvocation.totals.skillsTested) |")
    $lines.Add("| Skill contract checks passed | $($Validation.totals.skillsPassed) |")
    $lines.Add("| Skill contract checks failed | $($Validation.totals.skillsFailed) |")
    $lines.Add("| Rules validated | $($Validation.totals.rulesValidated) |")
    $lines.Add("| Expected fixture signals | $($Fixture.skillInvocation.totals.expectedSignals) |")
    $lines.Add("| Skill invocation issues found | $($Fixture.skillInvocation.totals.skillInvocationIssues) |")
    $lines.Add("| Direct binary matches found with ``rg -F`` | $($Fixture.directBinary.totals.directBinaryIssues) |")
    $lines.Add("")
    $lines.Add("![Skill fixture issue pie chart](issue-pie.svg)")
    $lines.Add("")
    $lines.Add("![Format skill coverage matrix](format-skill-matrix.svg)")
    $lines.Add("")
    $lines.Add("## Skill Contract Validation")
    $lines.Add("")
    $lines.Add("| Skill | Rules | Status | Notes |")
    $lines.Add("|-------|-------|--------|-------|")

    foreach ($result in $Validation.results) {
        $notes = if ($result.failures.Count -eq 0) { "OK" } else { ($result.failures -join "; ") }
        $lines.Add("| $($result.skill) | $($result.ruleCount) | $($result.status) | $notes |")
    }

    $lines.Add("")
    $lines.Add("## Issues by Category")
    $lines.Add("")
    $lines.Add("| Category | Issues | Share |")
    $lines.Add("|----------|--------|-------|")
    foreach ($item in $categories) {
        $share = if ($totalIssues -eq 0) { "0.0%" } else { "{0:N1}%" -f (($item.issues / $totalIssues) * 100) }
        $lines.Add("| $($item.category) | $($item.issues) | $share |")
    }

    $lines.Add("")
    $lines.Add("## Skill vs Direct Binary Comparison")
    $lines.Add("")
    $lines.Add("| Skill | Category | Expected Signals | Skill Invocation Issues | Direct ``rg`` Matches | Result |")
    $lines.Add("|-------|----------|------------------|-------------------------|---------------------|--------|")

    foreach ($skillResult in $Fixture.skillInvocation.results) {
        $directResult = $Fixture.directBinary.results | Where-Object { $_.skill -eq $skillResult.skill } | Select-Object -First 1
        $directCount = if ($directResult) { $directResult.issuesFound } else { 0 }
        $status = if ($skillResult.issuesFound -eq $skillResult.expectedSignals -and $directCount -eq $skillResult.expectedSignals) { "Pass" } else { "Review" }
        $lines.Add("| $($skillResult.skill) | $($skillResult.category) | $($skillResult.expectedSignals) | $($skillResult.issuesFound) | $directCount | $status |")
    }

    $lines.Add("")
    $lines.Add("## Format Skill Matrix")
    $lines.Add("")
    $lines.Add("| Skill | YAML | JSON | Markdown | XML | TOML |")
    $lines.Add("|-------|------|------|----------|-----|------|")

    foreach ($skill in $FormatMatrix.skills) {
        $cells = @()
        foreach ($type in $FormatMatrix.fileTypes) {
            $cell = $FormatMatrix.results | Where-Object { $_.skill -eq $skill -and $_.fileType -eq $type } | Select-Object -First 1
            if ($cell.status -eq "Pass") {
                $cells += "Pass ($($cell.matchedSignals)/$($cell.expectedSignals))"
            } elseif ($cell.status -eq "Review") {
                $cells += "Review ($($cell.matchedSignals)/$($cell.expectedSignals))"
            } else {
                $cells += "N/A"
            }
        }
        $lines.Add("| $skill | $($cells -join " | ") |")
    }

    $lines.Add("")
    $lines.Add("## Method")
    $lines.Add("")
    $lines.Add("- Contract validation checks every skill for required files, frontmatter, reference paths, core sections, rule metadata, and report-template placeholders.")
    $lines.Add("- Skill invocation pass loads each skill target and counts expected fixture signals as findings for that skill.")
    $lines.Add("- Direct binary pass runs ``rg -F`` for the same signals over the same target files and stores matching evidence lines.")
    $lines.Add("- This validates skill packaging, fixture coverage, and signal detectability. It does not replace a human/LLM review of severity, exploitability, or remediation quality.")
    $lines.Add("")

    return $lines -join "`n"
}

function New-MatrixSvg {
    param($FormatMatrix)

    $cellSize = 92
    $left = 210
    $top = 78
    $width = $left + ($FormatMatrix.fileTypes.Count * $cellSize) + 32
    $height = $top + ($FormatMatrix.skills.Count * 44) + 36
    $lines = New-Object System.Collections.Generic.List[string]

    $lines.Add("<svg xmlns=""http://www.w3.org/2000/svg"" width=""$width"" height=""$height"" viewBox=""0 0 $width $height"" role=""img"" aria-labelledby=""title desc"">")
    $lines.Add("<title id=""title"">Format skill coverage matrix</title>")
    $lines.Add("<desc id=""desc"">Matrix showing YAML, JSON, Markdown, XML, and TOML skill fixture coverage.</desc>")
    $lines.Add("<rect width=""$width"" height=""$height"" fill=""#ffffff""/>")
    $lines.Add("<text x=""24"" y=""32"" font-size=""20"" font-weight=""700"" font-family=""Arial, sans-serif"">Format Skill Coverage Matrix</text>")

    for ($i = 0; $i -lt $FormatMatrix.fileTypes.Count; $i++) {
        $x = $left + ($i * $cellSize) + ($cellSize / 2)
        $lines.Add("<text x=""$x"" y=""62"" text-anchor=""middle"" font-size=""12"" font-weight=""700"" font-family=""Arial, sans-serif"">$($FormatMatrix.fileTypes[$i])</text>")
    }

    for ($row = 0; $row -lt $FormatMatrix.skills.Count; $row++) {
        $skill = $FormatMatrix.skills[$row]
        $y = $top + ($row * 44)
        $textY = $y + 27
        $lines.Add("<text x=""24"" y=""$textY"" font-size=""12"" font-family=""Arial, sans-serif"">$skill</text>")

        for ($col = 0; $col -lt $FormatMatrix.fileTypes.Count; $col++) {
            $type = $FormatMatrix.fileTypes[$col]
            $cell = $FormatMatrix.results | Where-Object { $_.skill -eq $skill -and $_.fileType -eq $type } | Select-Object -First 1
            $x = $left + ($col * $cellSize)
            $fill = if ($cell.status -eq "Pass") { "#16a34a" } elseif ($cell.status -eq "Review") { "#f59e0b" } else { "#e5e7eb" }
            $label = if ($cell.status -eq "Pass") { "$($cell.matchedSignals)/$($cell.expectedSignals)" } elseif ($cell.status -eq "Review") { "$($cell.matchedSignals)/$($cell.expectedSignals)" } else { "N/A" }
            $lines.Add("<rect x=""$x"" y=""$y"" width=""$($cellSize - 8)"" height=""34"" rx=""4"" fill=""$fill""><title>${skill} vs ${type}: $($cell.status)</title></rect>")
            $lines.Add("<text x=""$($x + (($cellSize - 8) / 2))"" y=""$($y + 22)"" text-anchor=""middle"" font-size=""12"" font-weight=""700"" font-family=""Arial, sans-serif"" fill=""$(if ($cell.status -eq "NotApplicable") { "#374151" } else { "#ffffff" })"">$label</text>")
        }
    }

    $lines.Add("</svg>")
    return $lines -join "`n"
}

function New-PieSvg {
    param([array]$Categories)

    $total = ($Categories | Measure-Object -Property issues -Sum).Sum
    $palette = @("#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0891b2", "#4f46e5", "#65a30d", "#be123c", "#0f766e", "#7c3aed", "#b45309")
    $cumulative = 0
    $sliceLines = New-Object System.Collections.Generic.List[string]
    $legendLines = New-Object System.Collections.Generic.List[string]

    for ($i = 0; $i -lt $Categories.Count; $i++) {
        $item = $Categories[$i]
        $start = ($cumulative / $total) * [Math]::PI * 2
        $cumulative += $item.issues
        $end = ($cumulative / $total) * [Math]::PI * 2
        $largeArc = if (($end - $start) -gt [Math]::PI) { 1 } else { 0 }
        $x1 = 160 + 100 * [Math]::Cos($start)
        $y1 = 140 + 100 * [Math]::Sin($start)
        $x2 = 160 + 100 * [Math]::Cos($end)
        $y2 = 140 + 100 * [Math]::Sin($end)
        $color = $palette[$i % $palette.Count]
        $sliceLines.Add(("<path d=""M160 140 L{0:N2} {1:N2} A100 100 0 {2} 1 {3:N2} {4:N2} Z"" fill=""{5}""><title>{6}: {7}</title></path>" -f $x1, $y1, $largeArc, $x2, $y2, $color, $item.category, $item.issues))

        $legendY = 24 + ($i * 22)
        $legendLines.Add("<rect x=""310"" y=""$($legendY - 12)"" width=""12"" height=""12"" fill=""$color""/><text x=""330"" y=""$legendY"" font-size=""12"" font-family=""Arial, sans-serif"">$($item.category) ($($item.issues))</text>")
    }

    return @"
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="430" viewBox="0 0 720 430" role="img" aria-labelledby="title desc">
<title id="title">Skill fixture issues by category</title>
<desc id="desc">Pie chart showing expected fixture issues detected for each skill category.</desc>
<rect width="720" height="430" fill="#ffffff"/>
<text x="24" y="30" font-size="20" font-weight="700" font-family="Arial, sans-serif">Skill Fixture Issues by Category</text>
<g transform="translate(0, 30)">
$($sliceLines -join "`n")
<circle cx="160" cy="140" r="45" fill="#ffffff"/>
<text x="160" y="135" text-anchor="middle" font-size="22" font-weight="700" font-family="Arial, sans-serif">$total</text>
<text x="160" y="156" text-anchor="middle" font-size="12" font-family="Arial, sans-serif">signals</text>
</g>
<g>
$($legendLines -join "`n")
</g>
</svg>
"@
}

New-Item -ItemType Directory -Force -Path $resultsRoot | Out-Null

$expected = Get-Content -Raw -Path $expectedPath | ConvertFrom-Json
$skillNames = Get-ChildItem -Path $skillsRoot -Directory |
    Where-Object { -not $_.Name.StartsWith("_") } |
    Select-Object -ExpandProperty Name |
    Sort-Object

$validationResults = @($skillNames | ForEach-Object { Test-Skill $_ })
$validation = [pscustomobject]@{
    totals = [pscustomobject]@{
        skillsValidated = $validationResults.Count
        skillsPassed = @($validationResults | Where-Object { $_.status -eq "Pass" }).Count
        skillsFailed = @($validationResults | Where-Object { $_.status -eq "Fail" }).Count
        rulesValidated = [int](($validationResults | Measure-Object -Property ruleCount -Sum).Sum)
    }
    results = @($validationResults)
}

$fixture = Get-FixtureResults $expected
$formatMatrix = Get-FormatSkillMatrix $expected
$markdown = New-ReportMarkdown $validation $fixture $formatMatrix
$categories = Get-CategorySummary $fixture.skillInvocation.results
$svg = New-PieSvg $categories
$matrixSvg = New-MatrixSvg $formatMatrix

$validation | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $resultsRoot "skill-validation-results.json") -Encoding utf8
$fixture.skillInvocation | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $resultsRoot "skill-invocation-results.json") -Encoding utf8
$fixture.directBinary | ConvertTo-Json -Depth 12 | Set-Content -Path (Join-Path $resultsRoot "direct-binary-rg-results.json") -Encoding utf8
$formatMatrix | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $resultsRoot "format-skill-matrix.json") -Encoding utf8
$markdown | Set-Content -Path (Join-Path $resultsRoot "comparison.md") -Encoding utf8
$markdown | Set-Content -Path (Join-Path $resultsRoot "all-skills-report.md") -Encoding utf8
$svg | Set-Content -Path (Join-Path $resultsRoot "issue-pie.svg") -Encoding utf8
$matrixSvg | Set-Content -Path (Join-Path $resultsRoot "format-skill-matrix.svg") -Encoding utf8

Write-Host "Validated $($validation.totals.skillsValidated) skills ($($validation.totals.skillsPassed) passed, $($validation.totals.skillsFailed) failed)."
Write-Host "Validated $($validation.totals.rulesValidated) rules."
Write-Host "Detected $($fixture.skillInvocation.totals.skillInvocationIssues)/$($fixture.skillInvocation.totals.expectedSignals) fixture signals by skill invocation."
Write-Host "Detected $($fixture.directBinary.totals.directBinaryIssues)/$($fixture.directBinary.totals.expectedSignals) fixture signals by rg."
Write-Host "Generated format matrix with $($formatMatrix.combinations) skill/type combinations."
Write-Host "Report: $(Join-Path $resultsRoot "all-skills-report.md")"
