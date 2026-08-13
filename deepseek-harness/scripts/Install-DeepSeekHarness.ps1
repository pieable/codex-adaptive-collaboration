[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$DshHome = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.dsh'),
    [string]$RepositoryRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string]$DshModuleRoot
)

$ErrorActionPreference = 'Stop'
$requiredVersion = '0.1.0-rc.6'

function Get-AbsolutePath([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "$Label not found: $Path" }
    return (Resolve-Path -LiteralPath $Path).Path
}

function ConvertTo-FileUrl([string]$Path) {
    return ([Uri]([IO.Path]::GetFullPath($Path))).AbsoluteUri
}

function Assert-PackageVersion([string]$Root, [string]$PackageName) {
    $manifest = Join-Path $Root "$PackageName\package.json"
    if (-not (Test-Path -LiteralPath $manifest)) { throw "Required DSH package missing: $manifest" }
    $actual = (Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json).version
    if ($actual -ne $requiredVersion) { throw "Required $PackageName version is $requiredVersion; found $actual at $manifest" }
}

function Resolve-DshModuleRoot([string]$ExplicitRoot, [string]$HomePath) {
    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) { return Get-AbsolutePath $ExplicitRoot 'DshModuleRoot' }
    $homeCandidate = Join-Path $HomePath 'profiles\node_modules\@deepseek-ai'
    if (Test-Path -LiteralPath $homeCandidate) { return Get-AbsolutePath $homeCandidate 'DshModuleRoot' }
    $dshCommand = Get-Command dsh -ErrorAction SilentlyContinue | Where-Object { $_.Source } | Select-Object -First 1
    if ($null -ne $dshCommand) {
        $npmBin = Split-Path -Parent $dshCommand.Source
        $packageRoot = Join-Path $npmBin 'node_modules\@deepseek-ai\dsh'
        $packageManifest = Join-Path $packageRoot 'package.json'
        $installedRoot = Join-Path $packageRoot 'node_modules\@deepseek-ai'
        if ((Test-Path -LiteralPath $packageManifest) -and ((Get-Content -LiteralPath $packageManifest -Raw | ConvertFrom-Json).name -eq '@deepseek-ai/dsh') -and (Test-Path -LiteralPath $installedRoot)) { return Get-AbsolutePath $installedRoot 'DSH npm dependency closure' }
    }
    throw 'DshModuleRoot was not supplied and no DSH package closure was found. Pass -DshModuleRoot <.../node_modules/@deepseek-ai> explicitly.'
}

$repo = Get-AbsolutePath $RepositoryRoot 'RepositoryRoot'
$bundle = Join-Path $repo 'deepseek-harness'
$template = Join-Path $bundle 'preset\agent.cordis.yml.template'
$pluginTemplate = Join-Path $bundle 'preset\plugins\compaction-custom-prompt.mjs.template'
$presetMetadata = Join-Path $bundle 'preset\preset.yml'
$agentsTemplate = Join-Path $bundle 'templates\AGENTS.md'
$skills = Get-AbsolutePath (Join-Path $repo 'skills') 'Repository skills directory'
foreach ($file in @($template, $pluginTemplate, $presetMetadata, $agentsTemplate)) {
    if (-not (Test-Path -LiteralPath $file)) { throw "Bundle file missing: $file" }
}

$moduleRoot = Resolve-DshModuleRoot $DshModuleRoot $DshHome
Assert-PackageVersion $moduleRoot 'dsh-compaction-basic'
Assert-PackageVersion $moduleRoot 'dsh-llm'

$dshRootFull = [IO.Path]::GetFullPath($DshHome)
$targetPreset = Join-Path $dshRootFull '.agent-presets\dsh-collaboration'
$targetAgents = Join-Path $dshRootFull 'AGENTS.md'
$backupRoot = Join-Path $dshRootFull ('backups\codex-adaptive-collaboration\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$generatedPlugin = Join-Path $targetPreset 'plugins\compaction-custom-prompt.mjs'

$plugin = Get-Content -LiteralPath $pluginTemplate -Raw
$plugin = $plugin.Replace('__DSH_COMPACTION_BASIC_FILE_URL__', (ConvertTo-FileUrl (Join-Path $moduleRoot 'dsh-compaction-basic\lib\index.js')))
$plugin = $plugin.Replace('__DSH_LLM_FILE_URL__', (ConvertTo-FileUrl (Join-Path $moduleRoot 'dsh-llm\lib\index.js')))
if ($plugin -match '__[A-Z0-9_]+__') { throw 'Unresolved placeholder in generated compaction plugin.' }

$agent = Get-Content -LiteralPath $template -Raw
$agent = $agent.Replace('__REPOSITORY_SKILLS_DIR__', $skills.Replace('\', '/'))
$agent = $agent.Replace('__COMPACTION_PLUGIN_FILE_URL__', (ConvertTo-FileUrl $generatedPlugin))
if ($agent -match '__[A-Z0-9_]+__') { throw 'Unresolved placeholder in generated agent preset.' }

$plan = [ordered]@{
    dshHome = $dshRootFull
    repositoryRoot = $repo
    skillsDirectory = $skills
    moduleRoot = $moduleRoot
    backupRoot = $backupRoot
    writes = @($targetAgents, $targetPreset)
    excludes = @('settings.yaml', 'sessions', 'storages', 'profiles', 'node_modules', 'credentials')
}
$plan | ConvertTo-Json -Depth 4 | Write-Output

if (-not $PSCmdlet.ShouldProcess($dshRootFull, 'Install generated DeepSeek Harness collaboration preset')) { return }

New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
if (Test-Path -LiteralPath $targetAgents) { Copy-Item -LiteralPath $targetAgents -Destination (Join-Path $backupRoot 'AGENTS.md') -Force }
if (Test-Path -LiteralPath $targetPreset) { Copy-Item -LiteralPath $targetPreset -Destination (Join-Path $backupRoot 'dsh-collaboration') -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $targetPreset 'plugins') | Out-Null
Set-Content -LiteralPath $targetAgents -Value (Get-Content -LiteralPath $agentsTemplate -Raw) -NoNewline -Encoding utf8
Set-Content -LiteralPath (Join-Path $targetPreset 'agent.cordis.yml') -Value $agent -NoNewline -Encoding utf8
Set-Content -LiteralPath $generatedPlugin -Value $plugin -NoNewline -Encoding utf8
Copy-Item -LiteralPath $presetMetadata -Destination (Join-Path $targetPreset 'preset.yml') -Force

[ordered]@{ backupRoot = $backupRoot; installedPreset = $targetPreset; installedAgents = $targetAgents } | ConvertTo-Json -Depth 3 | Write-Output
