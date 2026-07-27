# claude-kit

Meus agentes e comandos do Claude Code, versionados para não ficarem presos a uma máquina.

O repositório é ao mesmo tempo um **marketplace** e o **plugin** `vision-kit`.

## Instalar numa máquina nova

Dentro do Claude Code:

```
/plugin marketplace add Enzopachecopereira-VB/claude-kit
/plugin install vision-kit@enzo-claude-kit
```

Repositório privado: o Claude Code usa o `git`/`gh` da máquina, então basta estar
autenticado (`gh auth login`) antes do primeiro comando.

Depois, no terminal, para `settings.json` + statusline:

```powershell
git clone https://github.com/Enzopachecopereira-VB/claude-kit.git
cd claude-kit
./install.ps1
```

E siga `setup/skills-externas.md` para as skills de terceiros.

## O que tem aqui

```
plugins/vision-kit/
  agents/     13 agentes especialistas
  commands/    4 slash commands
setup/
  settings.json      modelo, tema, effort level
  statusline.js      statusline customizada
  skills-externas.md como reinstalar Pika, Vercel, caveman, superpowers
install.ps1          aplica settings + statusline nesta máquina
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
