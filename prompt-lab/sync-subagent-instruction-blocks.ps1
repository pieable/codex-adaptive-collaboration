param(
    [switch]$Check
)

$ErrorActionPreference = 'Stop'

$sourcePath = Join-Path $PSScriptRoot 'shared-subagent-instruction-blocks.md'
$agentRoot = Join-Path (Split-Path -Parent $PSScriptRoot) 'agents'
$targets = @(
    Get-ChildItem -LiteralPath $agentRoot -Filter '*-base-instructions.txt' -File |
        Sort-Object Name |
        Select-Object -ExpandProperty FullName
)

$blockPattern = '(?ms)^<(?<tag>shared_[a-z0-9_]+)>\r?\n.*?^</\k<tag>>$'
$sourceText = Get-Content -LiteralPath $sourcePath -Raw
$sourceBlocks = @{}

foreach ($match in [regex]::Matches($sourceText, $blockPattern)) {
    $tag = $match.Groups['tag'].Value
    if ($sourceBlocks.ContainsKey($tag)) {
        throw "Duplicate source block: $tag"
    }
    $sourceBlocks[$tag] = $match.Value
}

if ($sourceBlocks.Count -eq 0) {
    throw 'No shared instruction blocks found in the source file.'
}

$changed = @()
$checked = @()

foreach ($target in $targets) {
    $targetText = Get-Content -LiteralPath $target -Raw
    $targetMatches = [regex]::Matches($targetText, $blockPattern)
    $seen = @{}

    foreach ($match in $targetMatches) {
        $tag = $match.Groups['tag'].Value
        if ($seen.ContainsKey($tag)) {
            throw "Duplicate block $tag in $target"
        }
        $seen[$tag] = $true
        if (-not $sourceBlocks.ContainsKey($tag)) {
            throw "Block $tag in $target has no source definition"
        }
        $targetText = $targetText.Replace($match.Value, $sourceBlocks[$tag])
    }

    $originalText = Get-Content -LiteralPath $target -Raw
    if ($targetText -ne $originalText) {
        if ($Check) {
            throw "Shared blocks are out of sync: $target"
        }
        Set-Content -LiteralPath $target -Value $targetText -Encoding utf8 -NoNewline
        $changed += $target
    }
    $checked += $target
}

[pscustomobject]@{
    Mode = if ($Check) { 'check' } else { 'sync' }
    SourceBlocks = $sourceBlocks.Keys | Sort-Object
    CheckedFiles = $checked
    ChangedFiles = $changed
} | ConvertTo-Json -Depth 4
