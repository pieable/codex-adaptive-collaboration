[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string]$DshHome = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.dsh'),
    [string]$DshModuleRoot
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$bundle = Join-Path $repo 'deepseek-harness'
$agentTemplate = Join-Path $bundle 'preset\agent.cordis.yml.template'
$pluginTemplate = Join-Path $bundle 'preset\plugins\compaction-custom-prompt.mjs.template'
$scanFiles = @($agentTemplate, $pluginTemplate, (Join-Path $bundle 'templates\AGENTS.md'))

function Resolve-DshModuleRoot([string]$ExplicitRoot, [string]$HomePath) {
    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        if (-not (Test-Path -LiteralPath $ExplicitRoot)) { throw "DshModuleRoot not found: $ExplicitRoot" }
        return (Resolve-Path -LiteralPath $ExplicitRoot).Path
    }
    $homeCandidate = Join-Path $HomePath 'profiles\node_modules\@deepseek-ai'
    if (Test-Path -LiteralPath $homeCandidate) { return (Resolve-Path -LiteralPath $homeCandidate).Path }
    $dshCommand = Get-Command dsh -ErrorAction SilentlyContinue | Where-Object { $_.Source } | Select-Object -First 1
    if ($null -ne $dshCommand) {
        $npmBin = Split-Path -Parent $dshCommand.Source
        $packageRoot = Join-Path $npmBin 'node_modules\@deepseek-ai\dsh'
        $packageManifest = Join-Path $packageRoot 'package.json'
        $installedRoot = Join-Path $packageRoot 'node_modules\@deepseek-ai'
        if ((Test-Path -LiteralPath $packageManifest) -and ((Get-Content -LiteralPath $packageManifest -Raw | ConvertFrom-Json).name -eq '@deepseek-ai/dsh') -and (Test-Path -LiteralPath $installedRoot)) { return (Resolve-Path -LiteralPath $installedRoot).Path }
    }
    throw 'DshModuleRoot was not supplied and no DSH package closure was found. Pass -DshModuleRoot <.../node_modules/@deepseek-ai> explicitly.'
}

foreach ($file in $scanFiles) {
    if (-not (Test-Path -LiteralPath $file)) { throw "Missing bundle file: $file" }
    $content = Get-Content -LiteralPath $file -Raw
    if ($content -match '(?i)[A-Z]:[\\/]|session-[0-9a-f]{8,}|deepseek-harness-migration[/\\]outputs') { throw "Portable source contains machine/session evidence: $file" }
}

$agent = Get-Content -LiteralPath $agentTemplate -Raw
$agent = $agent.Replace('__REPOSITORY_SKILLS_DIR__', '/opt/portable/repository/skills')
$agent = $agent.Replace('__COMPACTION_PLUGIN_FILE_URL__', 'file:///opt/portable/dsh/.agent-presets/dsh-collaboration/plugins/compaction-custom-prompt.mjs')
if ($agent -match '__[A-Z0-9_]+__') { throw 'Unresolved placeholder after test substitution.' }

$moduleRoot = Resolve-DshModuleRoot $DshModuleRoot $DshHome
$yamlModule = Join-Path (Split-Path -Parent $moduleRoot) 'js-yaml'
if (-not (Test-Path -LiteralPath (Join-Path $yamlModule 'package.json'))) { throw "Current DSH js-yaml dependency not found: $yamlModule" }

$temp = Join-Path ([IO.Path]::GetTempPath()) ('dsh-agent-template-' + [guid]::NewGuid().ToString('N') + '.yml')
$pluginSyntaxTemp = Join-Path ([IO.Path]::GetTempPath()) ('dsh-compaction-template-' + [guid]::NewGuid().ToString('N') + '.mjs')
try {
    Set-Content -LiteralPath $temp -Value $agent -NoNewline -Encoding utf8
    $env:DSH_BUNDLE_YAML = $temp
    $env:DSH_BUNDLE_JS_YAML = $yamlModule
    @'
import fs from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const yaml = require(process.env.DSH_BUNDLE_JS_YAML);
const source = fs.readFileSync(process.env.DSH_BUNDLE_YAML, 'utf8').replaceAll('!!js ', '!!str ');
const parsed = yaml.load(source);
if (!Array.isArray(parsed)) throw new Error('DSH entry-list YAML must be an array');
const wanted = ['subagent_explorer','subagent_web_researcher','subagent_browser_operator','subagent_research_lead','subagent_worker','subagent_code_executor'];
const expectedModels = Object.fromEntries(wanted.map(name => [name, name === 'subagent_code_executor' ? 'deepseek-v4-pro' : 'deepseek-v4-flash']));
const found = new Map();
const visit = value => { if (Array.isArray(value)) return value.forEach(visit); if (!value || typeof value !== 'object') return; if (wanted.includes(value.toolName)) found.set(value.toolName, value); Object.values(value).forEach(visit); };
visit(parsed);
if (found.size !== wanted.length) throw new Error(`Missing fixed role entries: ${wanted.filter(x => !found.has(x)).join(', ')}`);
const forbidden = new Set(['subagent','subagent_fork','send_message','list_agents','interrupt_agent','workflow','ralph']);
for (const [name, item] of found) {
  if (item.agentOptions?.provider !== 'deepseek-official' || item.agentOptions?.model !== expectedModels[name]) throw new Error(`Wrong fixed model route: ${name}`);
  const allow = item.toolFilter?.allow;
  if (!Array.isArray(allow) || allow.some(tool => forbidden.has(tool) || tool.startsWith('subagent_'))) throw new Error(`Non-leaf tool surface: ${name}`);
}
const rootTools = new Set();
const collectRoot = value => { if (Array.isArray(value)) return value.forEach(collectRoot); if (!value || typeof value !== 'object') return; if (typeof value.toolName === 'string') rootTools.add(value.toolName); Object.values(value).forEach(collectRoot); };
collectRoot(parsed);
if (!rootTools.has('subagent') || !rootTools.has('subagent_fork')) throw new Error('Root delegation tools missing');
console.log(JSON.stringify({yaml: 'parsed', fixedRoles: [...found.keys()].sort(), rootDelegation: ['subagent','subagent_fork']}));
'@ | node --input-type=module
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Copy-Item -LiteralPath $pluginTemplate -Destination $pluginSyntaxTemp -Force
    & node --check $pluginSyntaxTemp
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $pluginSyntaxTemp -Force -ErrorAction SilentlyContinue
    Remove-Item Env:DSH_BUNDLE_YAML -ErrorAction SilentlyContinue
    Remove-Item Env:DSH_BUNDLE_JS_YAML -ErrorAction SilentlyContinue
}

Write-Output 'DeepSeek Harness bundle static validation passed.'
