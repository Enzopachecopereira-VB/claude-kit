# claude-kit

Meu ambiente do Claude Code — agentes, comandos, skills e settings — versionado
para não ficar preso a uma máquina.

O repositório é ao mesmo tempo um **marketplace**, o **plugin** `vision-kit` e um
**espelho das 37 skills** que uso.

## Instalar numa máquina nova

São três passos, nesta ordem.

### 1. Autenticar

O repo é privado e o Claude Code usa o `git`/`gh` da máquina:

```bash
gh auth login
```

### 2. Agentes e comandos — dentro do Claude Code

```
/plugin marketplace add Enzopachecopereira-VB/claude-kit
/plugin install vision-kit@enzo-claude-kit
```

Traz os 13 agentes e os 4 comandos.

### 3. Skills, settings e statusline — no terminal

```powershell
git clone https://github.com/Enzopachecopereira-VB/claude-kit.git
cd claude-kit
powershell -ExecutionPolicy Bypass -File .\install.ps1          # settings + statusline
powershell -ExecutionPolicy Bypass -File .\install-skills.ps1   # as 37 skills
```

O `-ExecutionPolicy Bypass` não é frescura: no Windows padrão, chamar `./install.ps1`
direto falha com *"a execução de scripts foi desabilitada neste sistema"*. O
`Bypass` vale só para aquela chamada — não altera a política da máquina.

Os dois scripts fazem backup do que já existir antes de sobrescrever.

Falta só o plugin `superpowers`, que vem do marketplace oficial — o comando está
em `setup/skills-externas.md`.

## O que tem aqui

```
plugins/vision-kit/
  agents/     13 agentes especialistas
  commands/    4 slash commands
skills/       37 skills de terceiros (Pika, caveman, Vercel) — espelho
setup/
  settings.json      modelo, tema, effort level
  statusline.js      statusline customizada
  skills-lock.json   origem e hash das skills rastreadas pelo CLI
  skills-externas.md os dois caminhos para restaurar as skills
install.ps1          aplica settings + statusline nesta máquina
install-skills.ps1   restaura as 37 skills nesta máquina
```

### Agentes

| Agente | Para quê |
|---|---|
| `especialista-backend` | escrever/revisar backend seguindo `docs/regras/backend.md` |
| `especialista-frontend` | idem para frontend |
| `especialista-database` | schema, queries e migrations |
| `explorador-codebase` | mapear a base antes de uma migração grande |
| `planejador-migracao` | transformar o mapa num plano fatiado |
| `migrador` | executar uma fatia do plano |
| `verificador-migracao` | portão de qualidade — build, testes, lint |
| `pesquisador-profundo` | pesquisa web sempre com fonte |
| `verificador-fatos` | cruzar fontes e atribuir confiança |
| `gerador-ideias` | 30 ideias a partir de um briefing |
| `juiz-ideias` | pontuar e refinar ideias por rubrica |
| `designer-visual` | briefing/Figma → protótipo animado |
| `revisor-design` | auditar protótipo contra a identidade visual |

### Comandos

| Comando | Fluxo |
|---|---|
| `/ideias` | gerar 30 ideias e refinar as 5 melhores |
| `/investigar` | pesquisa profunda + verificação cruzada |
| `/prototipar` | gerar protótipo, auditar, ajustar |
| `/refatorar` | explorar → planejar → migrar em fatias → verificar |

Os agentes esperam encontrar `docs/regras/*.md` na raiz do projeto atual.

### Skills

37 skills de terceiros espelhadas em `skills/` — 20 do Pika, 7 do caveman, 9 da
Vercel e a `find-skills`. Restaura com `./install-skills.ps1`.

O espelho existe porque o `skills-lock.json` só rastreia 27 delas: as 9 da Vercel
e a `find-skills` aparecem como `Source: local` no CLI, então **nada as
reinstalaria** numa máquina nova. Detalhes e o caminho alternativo (reinstalar da
fonte, para pegar versões mais novas) em `setup/skills-externas.md`.

## Máquina autora vs. máquinas consumidoras

**Autora** (onde eu edito os agentes): `~/.claude/agents` e `~/.claude/commands` são
*junctions* para as pastas deste repo. Editar em `~/.claude/agents/` é editar o arquivo
versionado — não existe passo de cópia. Nessa máquina o plugin **não** fica instalado,
senão os agentes apareceriam duplicados.

Para montar as junctions numa máquina (não precisa de admin):

```powershell
$claude = "$HOME\.claude"; $kit = "$HOME\Downloads\claude-kit\plugins\vision-kit"
foreach ($n in 'agents','commands') {
    Rename-Item "$claude\$n" "$n.bak-$(Get-Date -Format yyyyMMdd)"
    cmd /c mklink /J "$claude\$n" "$kit\$n"
}
```

**Consumidoras**: instalam o plugin normalmente (seção acima) e não têm junction.

## Atualizar

Na máquina autora, depois de editar um agente:

```powershell
git add -A; git commit -m "atualiza agentes"; git push
```

Bump o `version` em `plugins/vision-kit/.claude-plugin/plugin.json` a cada mudança
relevante — é o que o Claude Code usa para detectar atualização.

Nas consumidoras, dentro do Claude Code: `/plugin update vision-kit@enzo-claude-kit`

## Fora do kit, de propósito

- **Memórias de projeto** (`~/.claude/projects/*/memory/`) — contexto interno, fica local.
- **MCP servers** — têm credenciais; reconfigure por máquina.
