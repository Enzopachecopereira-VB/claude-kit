# Instala o kit numa maquina nova (Windows / PowerShell).
# Aplica settings.json + statusline. Os agentes e comandos vem pelo plugin
# (veja o README) e nao sao copiados por este script.

$ErrorActionPreference = 'Stop'

$kit        = Split-Path -Parent $MyInvocation.MyCommand.Path
$claudeDir  = Join-Path $HOME '.claude'
$stamp      = Get-Date -Format 'yyyyMMdd-HHmmss'

if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir | Out-Null
}

# --- statusline -------------------------------------------------------------
$statuslineDst = Join-Path $claudeDir 'statusline.js'
Copy-Item (Join-Path $kit 'setup\statusline.js') $statuslineDst -Force
Write-Host "statusline.js -> $statuslineDst"

# --- settings.json ----------------------------------------------------------
function Merge-Json($base, $overlay) {
    foreach ($p in $overlay.PSObject.Properties) {
        $existing = $base.PSObject.Properties[$p.Name]
        if ($existing -and
            $existing.Value -is [PSCustomObject] -and
            $p.Value -is [PSCustomObject]) {
            Merge-Json $existing.Value $p.Value
        } else {
            $base | Add-Member -NotePropertyName $p.Name -NotePropertyValue $p.Value -Force
        }
    }
}

$kitSettings = Get-Content (Join-Path $kit 'setup\settings.json') -Raw | ConvertFrom-Json

# o caminho da statusline e absoluto: reescreve para o HOME desta maquina
if ($kitSettings.statusLine) {
    $kitSettings.statusLine.command = "node $($statuslineDst -replace '\\','/')"
}

$settingsPath = Join-Path $claudeDir 'settings.json'
if (Test-Path $settingsPath) {
    $backup = "$settingsPath.bak-$stamp"
    Copy-Item $settingsPath $backup
    Write-Host "backup do settings.json -> $backup"
    $merged = Get-Content $settingsPath -Raw | ConvertFrom-Json
    Merge-Json $merged $kitSettings
} else {
    $merged = $kitSettings
}

$merged | ConvertTo-Json -Depth 20 | Out-File $settingsPath -Encoding utf8
Write-Host "settings.json aplicado -> $settingsPath"

Write-Host ''
Write-Host 'Feito. Agora, dentro do Claude Code:' -ForegroundColor Green
Write-Host '  /plugin marketplace add Enzopachecopereira-VB/claude-kit'
Write-Host '  /plugin install vision-kit@enzo-claude-kit'
Write-Host ''
Write-Host 'Skills de terceiros: veja setup/skills-externas.md'
