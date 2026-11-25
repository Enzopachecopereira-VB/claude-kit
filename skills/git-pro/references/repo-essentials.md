# Repo Essentials — Checklist de Arquivos

Lista do que TODO repo profissional deve ter, na raiz, em `docs/`, em `scripts/` e em `.github/`.

## Raiz obrigatória

| Arquivo | Propósito | Stack |
|---|---|---|
| `README.md` | Documentação principal | Todas |
| `LICENSE` | Licença legal | Todas |
| `.gitignore` | Files/dirs que NÃO vão pro git | Todas |
| `CHANGELOG.md` | Histórico de mudanças (Keep a Changelog) | Todas |
| `CONTRIBUTING.md` | Como contribuir | Todas |
| `.editorconfig` | Config consistente entre editores | Todas |

## Raiz altamente recomendada

| Arquivo | Propósito |
|---|---|
| `SECURITY.md` | Política de reporte de vulnerabilidades |
| `CODE_OF_CONDUCT.md` | Código de conduta da comunidade |
| `.env.example` | Template de variáveis (sem valores reais) |
| `lefthook.yml` | Config de hooks Git |
| `gitleaks.toml` | Config de secret scan |
| `.gitattributes` | line endings, diff customizations |
| `.nvmrc` ou `.tool-versions` | Versão de Node/runtime |

## Release harness obrigatório

| Path | Propósito |
|---|---|
| `docs/release/ledger.json` | Registro canônico de releases publicadas |
| `docs/release/X.Y.Z.md` | Nota narrativa por versão |
| `scripts/validate-release-process.sh` | Validação local de changelog, ledger e notas |
| `scripts/publish-release.sh` | Publicação local via `git` + `gh` |

## Stack-specific (por linguagem)

| Stack | Arquivos típicos |
|---|---|
| Node/TS | `package.json`, `tsconfig.json`, `.npmrc` |
| Python | `pyproject.toml`, `requirements.txt`, `.python-version` |
| Go | `go.mod`, `go.sum` |
| Rust | `Cargo.toml`, `Cargo.lock` |
| Java | `pom.xml` ou `build.gradle` |
| PHP | `composer.json`, `composer.lock` |
| Ruby | `Gemfile`, `Gemfile.lock`, `.ruby-version` |

## .github/ — GitHub-specific

```
.github/
├── workflows/
│   └── ci.yml                          # testes/lint/release-check
├── pull_request_template.md
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   ├── feature_request.md
│   └── config.yml                      # config geral issues
├── CODEOWNERS                          # quem revisa cada path
├── dependabot.yml                      # updates auto de deps
└── FUNDING.yml                         # sponsorship (opcional)
```

## Checklist completo (repo top)

### Documentação
- [ ] README.md completo (ver `readme-completo.md`)
- [ ] CHANGELOG.md (Keep a Changelog)
- [ ] CONTRIBUTING.md
- [ ] SECURITY.md (mesmo que diga "report via email X")
- [ ] CODE_OF_CONDUCT.md (Contributor Covenant é padrão)
- [ ] LICENSE (MIT/Apache/etc — não invente)
- [ ] `docs/` se README ficou > 500 linhas

### Config Git
- [ ] .gitignore (base + stack + agents-repo se aplicável)
- [ ] .gitattributes (line endings normalizados)
- [ ] .editorconfig
- [ ] lefthook.yml + `lefthook install` rodado
- [ ] gitleaks.toml

### Stack
- [ ] Arquivo de manifesto da stack (package.json, etc)
- [ ] Lockfile commitado (package-lock, poetry.lock, Cargo.lock)
- [ ] .nvmrc / .python-version / .tool-versions

### Variáveis de ambiente
- [ ] .env.example (com TODAS as vars necessárias, valores vazios ou exemplos)
- [ ] .env no .gitignore (NUNCA commitar)

### CI/CD
- [ ] .github/workflows/ci.yml (testes, lint)
- [ ] Branch protection ativa em `main` (settings GitHub)

### Release
- [ ] `CHANGELOG.md` mantém `## [Unreleased]`
- [ ] `docs/release/ledger.json` existe e é validado
- [ ] `docs/release/<versão>.md` existe para cada versão lançada
- [ ] `scripts/validate-release-process.sh` roda local e no CI
- [ ] `scripts/publish-release.sh` publica apenas da `main` limpa e sincronizada
- [ ] Release usa `gh` local, sem secret dedicado no repositório

### Templates
- [ ] .github/pull_request_template.md
- [ ] .github/ISSUE_TEMPLATE/bug_report.md
- [ ] .github/ISSUE_TEMPLATE/feature_request.md
- [ ] .github/CODEOWNERS (se equipe)

### Dependências
- [ ] .github/dependabot.yml (updates auto)

## SECURITY.md — exemplo mínimo

```markdown
# Política de Segurança

## Versões Suportadas

| Versão | Suporte |
|---|---|
| 2.x | ✅ |
| 1.x | ⚠️ Só patches críticos |
| < 1.0 | ❌ |

## Reportar Vulnerabilidade

**Não abra issue público.** Envie email para: security@example.com

Inclua:
- Descrição
- Passos pra reproduzir
- Impacto
- Versão afetada

Resposta inicial: até 72h.
```

## CODE_OF_CONDUCT.md

Use [Contributor Covenant](https://www.contributor-covenant.org/) v2.1:

```bash
# Gerar com 1 comando
curl -o CODE_OF_CONDUCT.md https://www.contributor-covenant.org/version/2/1/code_of_conduct.md
```

Ajustar email no fim.

## CODEOWNERS — quem revisa cada path

`.github/CODEOWNERS`:
```
# Default — qualquer mudança
* @your-handle

# Frontend
/web/ @your-handle @frontend-team

# Backend
/api/ @your-handle @backend-team

# Docs
*.md @docs-team
```

Auto-atribui revisor em PRs que tocam paths específicos.

## dependabot.yml — updates de deps

`.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"     # ou pip, gomod, cargo, composer, bundler
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels: ["dependencies"]

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Templates de issues

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug Report
about: Reporte um bug
labels: bug
---

**Descrição**
[O que aconteceu]

**Passos para reproduzir**
1. ...
2. ...

**Esperado vs atual**
Esperado: ...
Atual: ...

**Ambiente**
- OS:
- Versão do tool:
- Node/Python/etc:

**Logs / screenshots**
```

## Anti-patterns

- ❌ README como única documentação (mover detalhes pra docs/)
- ❌ LICENSE inventada (use SPDX padrão: MIT, Apache-2.0, GPL-3.0)
- ❌ .gitignore esquecido de `.env` (gitleaks pega, mas evite o risco)
- ❌ Release sem nota em `docs/release/`
- ❌ Release sem ledger validado
- ❌ Depender de bot/secret de release sem justificativa explícita
- ❌ Sem branch protection em `main` (qualquer um pode forçar push)
- ❌ CODEOWNERS sem ninguém (fica genérico, PRs sem reviewer auto)
- ❌ Dependabot off (security updates não chegam)
- ❌ `.github/` esquecido no repo de agentes (CI também vale lá)

## Repo top (visualmente)

GitHub auto-detecta e exibe:
- 🛡️ Badge "Security policy" → SECURITY.md presente
- 📜 Badge "License" → LICENSE com SPDX válido
- 🤝 Badge "Contributing" → CONTRIBUTING.md presente
- 📋 Aba "Insights" → ativa community standards check

Atingir 100% no [Community Standards Checklist](https://github.com/<user>/<repo>/community) = repo top.
