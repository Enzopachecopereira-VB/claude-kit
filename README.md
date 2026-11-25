# claude-kit

Meu ambiente do Claude Code — agentes, comandos, skills e settings — versionado
para não ficar preso a uma máquina.

O repositório é ao mesmo tempo um **marketplace**, o **plugin** `vision-kit` e um
**espelho das 59 skills** que uso.

## Instalar numa máquina nova

São três passos, nesta ordem.

### 1. Autenticar

O repo é privado e o Claude Code usa o `git`/`gh` da máquina:

```bash
gh auth login
```

### 2. Skills, settings e statusline — no terminal

```powershell
git clone https://github.com/Enzopachecopereira-VB/claude-kit.git
cd claude-kit
powershell -ExecutionPolicy Bypass -File .\install.ps1          # settings + statusline
powershell -ExecutionPolicy Bypass -File .\install-skills.ps1   # as 59 skills
```

### 3. Agentes e comandos — dentro do Claude Code

```
/plugin install vision-kit@enzo-claude-kit
/plugin install superpowers@claude-plugins-official
```

Não precisa de `/plugin marketplace add`: o `settings.json` do passo 2 já
registra os dois marketplaces. Por isso o passo 3 vem **depois** do 2.

O `-ExecutionPolicy Bypass` não é frescura: no Windows padrão, chamar `./install.ps1`
direto falha com *"a execução de scripts foi desabilitada neste sistema"*. O
`Bypass` vale só para aquela chamada — não altera a política da máquina.

Os dois scripts fazem backup do que já existir antes de sobrescrever.

## O que tem aqui

```
plugins/vision-kit/
  agents/     13 agentes especialistas
  commands/    4 slash commands
skills/       59 skills (Pika, caveman, Vercel, Matt Pocock, git, segurança, frontend) — espelho
setup/
  settings.json      modelo, tema, effort level
  statusline.js      statusline customizada (Node)
  statusline.ps1     statusline alternativa em PowerShell (sem depender do Node)
  skills-lock.json   origem e hash das skills rastreadas pelo CLI
  skills-externas.md os dois caminhos para restaurar as skills
install.ps1          aplica settings + statusline nesta máquina
install-skills.ps1   restaura as 59 skills nesta máquina
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

59 skills espelhadas em `skills/` — 20 do Pika, 7 do caveman, 9 da Vercel,
9 do Matt Pocock, a `find-skills`, a `claude-video`, a `notebooklm-research` e
mais 11 adicionadas em 25/11/2026 (engenharia, git, segurança, frontend e
engenharia reversa — lista em `setup/skills-externas.md`). Restaura com `./install-skills.ps1`.

O espelho existe porque o `skills-lock.json` só rastreia 27 delas: as 9 da Vercel,
as 9 do Matt Pocock, a `find-skills`, a `claude-video` e a `notebooklm-research`
aparecem como `Source: local` no CLI, então **nada as reinstalaria** numa máquina
nova. Detalhes e o caminho alternativo (reinstalar da fonte, para pegar versões
mais novas) em `setup/skills-externas.md`.

As do Matt Pocock (MIT) são de engenharia, não de mídia: `grill-me` /
`grill-with-docs` (entrevista antes de construir), `tdd`, `diagnosing-bugs` e
`code-review`. Rode `/setup-matt-pocock-skills` uma vez por repositório antes de
usá-las.

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

Depois dos 3 passos acima, **só sobra isto** para fazer à mão:

- **MCP servers locais** — têm credenciais/login, não dá para versionar.
  Reconfigure com `claude mcp add` (escopo `-s user`) ou `/mcp`:

  | MCP | Comando |
  |---|---|
  | playwright | `claude mcp add playwright -s user -- npx @playwright/mcp@latest` |
  | rea (engenharia reversa) | `claude mcp add rea -s user -- cmd.exe /d /c npx -y rea-agents@6.8.0 mcp` |
  | runway | `claude mcp add runway -s user --transport http https://mcp.runwayml.com/mcp` (autentica no `/mcp`) |
  | supabase | precisa do token da conta |
  | firecrawl | precisa da API key |
  | pika-mcp | precisa da API key |

  O **vercel** vem pelo plugin `vercel@claude-plugins-official` (já no
  `settings.json`); só falta autenticar no `/mcp`.

  Os conectores da conta claude.ai (Notion, Figma, Claude Docs, Google Slides,
  Google Drive, Box, Runway, SlidesGPT, higgsfield) vêm sozinhos ao logar —
  **desde que `ANTHROPIC_API_KEY` não esteja definida**; senão o Claude Code usa a
  chave, ignora os conectores e o `/mcp` mostra só os locais.
  Detalhes em `setup/skills-externas.md`.
- **Memórias de projeto** (`~/.claude/projects/*/memory/`) — contexto interno de
  cada projeto, fica local de propósito.

Todo o resto — agentes, comandos, skills, settings, statusline, marketplaces —
está coberto.
