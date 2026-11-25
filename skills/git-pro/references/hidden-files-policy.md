# Política de Hidden Files (`.*`)

Decisão clara sobre QUAL arquivo/pasta oculto VAI pro git vs FICA local.

## Regra de ouro

**Commita SE**: é config compartilhada do time, infra do projeto, instrução pra agentes/CI.
**NUNCA commita SE**: tem secret, é cache/build/temp, é preferência pessoal, é sessão de agente.

## Tabela definitiva

### ✅ COMMITAR (compartilhado, faz parte do projeto)

| Path | Razão |
|---|---|
| `.gitignore` | Define o que ignorar (óbvio) |
| `.gitattributes` | line endings, diff custom |
| `.github/` (workflows, templates, CODEOWNERS, dependabot.yml) | CI/CD e config do GitHub |
| `.editorconfig` | Config consistente entre editores |
| `.nvmrc`, `.node-version` | Versão Node travada |
| `.tool-versions` (asdf/mise) | Versões de runtimes travadas |
| `.python-version` (pyenv) | Versão Python |
| `.ruby-version` (rbenv) | Versão Ruby |
| `.eslintrc*`, `.prettierrc*`, `.biome.json` | Lint/format config |
| `.stylelintrc*` | CSS lint |
| `.ruff.toml`, `.flake8` | Python lint |
| `.golangci.yml` | Go lint |
| `.dockerignore` | Build context Docker |
| `.docker/`, `.devcontainer/` | Docker dev env |
| `.env.example` | Template de env vars (SEM valores) |
| `.npmrc` (sem token) | Config registry, prefer-offline, etc. |
| `lefthook.yml` ou `.lefthook.yml` | Config de hooks |
| `gitleaks.toml` | Config secret scanner |
| `docs/release/`, `scripts/validate-release-process.sh`, `scripts/publish-release.sh` | Harness local de release |
| `.commitlintrc*` | Config commit lint |
| `.husky/` (se usa Husky) | Hooks Git |
| `.vscode/extensions.json` | Extensões recomendadas pro time |
| `.vscode/settings.json` (SELETIVO) | Settings que TODO time deve ter (formatter, etc) — não preferências pessoais |
| `.vscode/launch.json`, `.vscode/tasks.json` | Debug/tasks compartilhadas |
| `.idea/codeStyles/` (parcial) | Code style JetBrains compartilhado |
| **`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`** | Instruções pra agentes AI — TIME inteiro precisa |
| **`.claude/skills/`** (projeto) | Skills compartilhadas do projeto |
| **`.opencode/agents/`, `.opencode/skills/`, `.opencode/commands/`** (projeto) | Subagents/skills do projeto |
| **`.cursor/rules`** | Rules Cursor compartilhadas |
| **`.agents/skills/`, `.agents/agents/`** (projeto) | Convention cross-tool de agentes |

### ❌ NUNCA COMMITAR (secret/pessoal/gerado)

| Path | Razão |
|---|---|
| `.env`, `.env.local`, `.env.*.local`, `.env.production` | Secrets reais |
| `.envrc` (direnv, se contém secrets) | Idem |
| `.npmrc` COM `_authToken` | Token NPM |
| `.pypirc` | Token PyPI |
| `.aws/`, `.gcp/`, `.azure/` (credentials) | Cloud secrets |
| `.ssh/` | Keys SSH |
| `id_rsa*`, `*.pem`, `*.key` (sem .pub) | Private keys |
| `.netrc` | Credenciais HTTP |
| `.DS_Store`, `Thumbs.db`, `desktop.ini` | Lixo do OS |
| `.vscode/settings.json` PRIVADO | Preferências pessoais (font size, theme, etc) |
| `.vscode/.ropeproject/` | Cache de extensão |
| `.idea/workspace.xml`, `.idea/usage.statistics.xml` | Personal preferences JetBrains |
| `.cache/`, `.tmp/`, `.temp/`, `tmp/`, `temp/` | Cache/temp |
| `node_modules/` | Deps Node |
| `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Cache Python |
| `vendor/` (algumas stacks) | Deps PHP/Go |
| `target/` (Rust/Java) | Build |
| `build/`, `dist/`, `out/`, `.next/`, `.nuxt/` | Build output |
| `coverage/`, `.coverage`, `.nyc_output/` | Cobertura |
| `*.log`, `logs/`, `npm-debug.log*` | Logs |
| `*.db`, `*.sqlite`, `*.sqlite3` | Banco local |
| `*.pid`, `*.seed`, `*.gz` (gerados) | Runtime files |
| **`.claude/sessions/`, `.claude/projects/`** | Sessões Claude Code (pessoal) |
| **`.opencode/sessions/`, `.opencode/.sisyphus/`, `.opencode/storage/`** | Sessões opencode (pessoal) |
| **`.sisyphus/`** (raiz do projeto) | Plans/evidence/drafts do agent (pessoal por run) |
| **`.agent-memory-store/`** | Memory store local (pessoal) |
| **`.playwright-mcp/`** | Cache Playwright MCP |
| **`.pi/sessions/`** | Sessões Pi |
| **`.cache/opencode/`, `.cache/claude/`** | Caches de AI |

### ⚠️ DEPENDE (caso-a-caso)

| Path | Quando commitar |
|---|---|
| `.vscode/settings.json` | Se contém SÓ settings de time (formatter on save, etc), commita parcial. Preferências pessoais → não. Solução: `.vscode/settings.shared.json` + script que merge |
| `.idea/` (JetBrains) | Sub-paths específicos (codeStyles, inspectionProfiles). Resto fica fora |
| `.devcontainer/` | Sim se time usa devcontainers padrão; não se cada um tem o seu |
| `.bundle/` (Ruby) | Não (config local), exceto `.bundle/config` se for compartilhado |

## Padrão pro `.gitignore`

`templates/gitignore/base` cobre o NUNCA-COMMITAR universal. Stack-specific (`gitignore/node`, etc.) adiciona o resto.

`gitignore/agents-repo` é específico pra repos cujo conteúdo principal é agente:
- ✅ commita: `*.md`, `*.yaml`, `*.yml`, `*.json`, `skills/`, `agents/`, `commands/`, `references/`, `templates/`, `scripts/`, `docs/`
- ❌ ignora: tudo de cache/sessions/preferences acima

## Validação no setup

Skill faz checklist ao iniciar repo:

```
1. Existe .gitignore? Se não, criar
2. .env está no .gitignore? Se não, adicionar
3. node_modules/__pycache__/etc baseados em stack? Adicionar
4. Sessões de agentes (.sisyphus, .agent-memory-store) gitignored? Adicionar
5. .env.example existe? Sugerir criar se .env presente
```

## Reverso: arquivo já commitado por engano

Se commitou algo que NÃO deveria:

```bash
# 1. Remover do tracking (mantém local)
git rm --cached <arquivo>

# 2. Adicionar ao .gitignore
echo "<arquivo>" >> .gitignore

# 3. Commit
git add .gitignore
git commit -m "chore: untrack <arquivo> + add to gitignore"

# 4. Push
git push
```

**SE o arquivo era secret** (.env, key, etc):
- Acima limpa só do HEAD futuro
- Histórico antigo AINDA contém o secret
- Necessário: rotacionar o secret + usar `git-filter-repo` ou BFG para limpar histórico

## Multi-OS notes

`.DS_Store` (macOS), `Thumbs.db` (Windows), `desktop.ini` (Windows), `*~` (Linux editor backup) — todos no `gitignore/base`.

Global `.gitignore` no perfil pessoal também ajuda (não polui repo de cada projeto):
```bash
git config --global core.excludesfile ~/.gitignore_global
```

`~/.gitignore_global`:
```
.DS_Store
.idea/
*.swp
*~
.vscode/settings.json
```

## Anti-patterns

- ❌ `git add .` sem `.gitignore` adequado (commita node_modules, .DS_Store, etc.)
- ❌ Commitar `.env` "só temporariamente" (não existe — histórico permanente)
- ❌ Ignorar `.github/` (perde CI templates)
- ❌ Commitar config de bot de release como padrão global sem decisão explícita do projeto
- ❌ NÃO commitar `AGENTS.md` (time perde instrução de agente)
- ❌ NÃO commitar `.claude/skills/` do projeto (time perde skills)
- ❌ Commitar lockfile só às vezes (commitar SEMPRE — reproduzibilidade)
- ❌ Commitar `.vscode/settings.json` com tudo (filtrar só o compartilhado)
