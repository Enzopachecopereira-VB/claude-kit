# Restaura as skills espelhadas neste repo numa maquina nova (Windows / PowerShell).
#
# Reproduz o layout da maquina de origem:
#   ~/.agents/skills/<nome>   arquivos reais
#   ~/.claude/skills/<nome>   junction apontando para o de cima
#
# A junction e o que faz o Claude Code enxergar a skill sem duplicar arquivo,
# e mantem o CLI `npx skills list` funcionando.
#
# Nao precisa de admin: junction de diretorio e permitida para usuario comum.
#
# Se der "a execucao de scripts foi desabilitada neste sistema", rode assim:
#   powershell -ExecutionPolicy Bypass -File .\install-skills.ps1

param(
    # Raiz onde instalar. Existe para poder testar o script sem tocar no HOME
    # real -- $HOME e somente leitura no PowerShell e nao da para sobrescrever.
    [string]$Root = $HOME
)

$ErrorActionPreference = 'Stop'

$kit       = Split-Path -Parent $PSCommandPath
$origem    = Join-Path $kit 'skills'
$agentsDir = Join-Path $Root '.agents\skills'
$claudeDir = Join-Path $Root '.claude\skills'
$stamp     = Get-Date -Format 'yyyyMMdd-HHmmss'

if (-not (Test-Path $origem)) {
    throw "Pasta 'skills' nao encontrada em $kit. Clone o repo completo."
}

foreach ($d in @($agentsDir, $claudeDir)) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}

$skills = Get-ChildItem $origem -Directory
Write-Host "Restaurando $($skills.Count) skills..." -ForegroundColor Cyan
Write-Host ''

$instaladas = 0
$puladas    = 0

foreach ($s in $skills) {
    $destAgents = Join-Path $agentsDir $s.Name
    $destClaude = Join-Path $claudeDir $s.Name

    # --- arquivos reais em ~/.agents/skills ---
    if (Test-Path $destAgents) {
        $backup = "$destAgents.bak-$stamp"
        Move-Item $destAgents $backup
        Write-Host "  backup: $($s.Name) -> $(Split-Path -Leaf $backup)" -ForegroundColor DarkYellow
    }
    Copy-Item $s.FullName $destAgents -Recurse

    # --- junction em ~/.claude/skills ---
    $existente = Get-Item $destClaude -Force -ErrorAction SilentlyContinue
    if ($existente) {
        # Remove-Item numa junction apaga so o link, nao o alvo.
        Remove-Item $destClaude -Force -Recurse
    }

    try {
        New-Item -ItemType Junction -Path $destClaude -Target $destAgents | Out-Null
        $instaladas++
        Write-Host "  ok: $($s.Name)" -ForegroundColor Green
    } catch {
        # Se junction falhar por qualquer motivo, cai para copia simples.
        Copy-Item $destAgents $destClaude -Recurse
        $puladas++
        Write-Host "  copiada (sem junction): $($s.Name)" -ForegroundColor Yellow
    }
}

# --- lock file, para o CLI `skills` saber a origem de cada uma ---
$lockOrigem = Join-Path $kit 'setup\skills-lock.json'
if (Test-Path $lockOrigem) {
    $lockDest = Join-Path $Root 'skills-lock.json'
    if (Test-Path $lockDest) {
        Copy-Item $lockDest "$lockDest.bak-$stamp"
    }
    Copy-Item $lockOrigem $lockDest -Force
    Write-Host ''
    Write-Host "skills-lock.json -> $lockDest"
}

Write-Host ''
Write-Host "Feito: $instaladas com junction, $puladas copiadas." -ForegroundColor Green
Write-Host ''
Write-Host 'Confira com:' -ForegroundColor Cyan
Write-Host '  npx skills list'
Write-Host ''
Write-Host 'Para atualizar as de terceiros a partir da fonte, em vez do espelho:'
Write-Host '  npx skills add Pika-Labs/Pika-Plugins'
Write-Host '  npx skills add JuliusBrussee/caveman'
Write-Host '  npx skills add vercel/agent-skills'
Write-Host '  npx skills add mattpocock/skills   (veja as flags em setup/skills-externas.md)'
