---
name: git-pro
description: >-
  Padrões Git profissionais e cerimonial de release executável. Use ao commitar,
  versionar, taguear, publicar release, escrever CHANGELOG, padronizar
  repositório ou montar README. Entrega scripts/release.sh — cerimonial portátil
  (status, init, gate anti-segredo, check, prepare, publish) que roda em
  qualquer repo git sem instalação, detecta as convenções do próprio repositório
  (prefixo de tag, estilo de nome, manifesto de versão, formato de changelog) e
  impõe as guardas em código: worktree limpa, branch base sincronizada, CI local
  e remoto verde, tag imutável e GitHub Release via gh. Cobre ainda Conventional
  Commits, commits atômicos, SemVer, validação local pre-push e política de
  hidden files.
license: proprietary
metadata:
  version: "2.0.0"
  category: "workflow"
  tags: ["git", "release", "semver", "changelog", "conventional-commits", "security"]
  scripts:
    - path: scripts/release.sh
      description: "Cerimonial de release portátil. Bash 3.2 + git + gh + python3. Opera sobre --repo ou o repo do CWD, nunca sobre o diretório do script."
    - path: scripts/release_engine.py
      description: "Engine estruturado (ledger, changelog, notas, manifesto, scan de segredo). Só stdlib."
---

# Git-Pro — disciplina de Git com cerimonial executável

## Caminho rápido: o cerimonial é UM comando

**Não leia reference nenhuma para operar uma release.** O contrato inteiro está
implementado em `scripts/release.sh`, que funciona em qualquer repo git sem
instalação e sem configuração:

```bash
S=~/.agents/skills/git-pro/scripts/release.sh

bash "$S" status                 # o que este repo tem e o que falta
bash "$S" init                   # cria o contrato (idempotente)
bash "$S" prepare 1.2.0          # changelog + nota + ledger + bump do manifesto
# revise a narrativa, commit, PR, merge com CI verde
bash "$S" publish 1.2.0          # guardas + tag imutável + GitHub Release
```

Todo subcomando aceita `--repo <path>` e **imprime a raiz do repositório que
avaliou**. Se o repo já tem publicador próprio (`make release-publish`,
`<repo>/scripts/publish-release.sh`, `pnpm release:publish`), use o dele — ele conhece
particularidades que este script não tem.

As references abaixo existem para **decidir** (qual bump, o que escrever) e para
**construir** o que ainda não existe. Não para reexecutar à mão o que o script
já impõe: reler doutrina para deduzir um procedimento que um script já garante
custa contexto e reabre, a cada ciclo, decisão que já está tomada em código.

## Gate anti-segredo (passo zero, inegociável)

JAMAIS commitar/subir chave. Antes de TODO commit e como primeiro passo de
qualquer release:

1. **Rode o gate DO REPO EM QUE VOCÊ ESTÁ.**
   ```bash
   bash ~/.agents/skills/git-pro/scripts/release.sh gate        # varre a árvore rastreada
   ```
   Ele lê `git ls-files` do repo alvo — o que inclui arquivo novo apenas staged,
   então serve como gate de pre-commit — e nomeia arquivo e linha de cada achado.

2. **Confirme que o gate leu os SEUS arquivos.** Uma CLI global instalada na
   máquina costuma resolver o próprio diretório de instalação, não o seu `cwd`:
   rodada de outro repositório, ela devolve verde sobre árvore alheia. Verde de
   gate que não nomeia a sua raiz **não vale**. Este é um modo de falha real e
   observado, não hipotético.

3. **Qualquer hit = PARE.** Remover o segredo, usar placeholder `{env:VAR}` ou
   referência 1Password (`op://...`) — as únicas formas aceitáveis em arquivo.
   Segredo que tocou commit está QUEIMADO: rotacione imediatamente. Remover do
   arquivo não remove do histórico.

4. **Falso positivo se resolve UMA vez, no gate — nunca na conversa.** Allowlist
   por **valor exato** em `.release.json` (`secretAllowlist`), documentada.
   Allowlist por **caminho** (isentar `docs/`, `README`, `CHANGELOG`) é
   proibida: ela deixa o scan verde exatamente sobre os artefatos que são
   publicados. Triar o mesmo achado a cada release é o anti-pattern.

`gitleaks` continua válido como ferramenta complementar em repo sem gate próprio.

## Quando ativar

`commit`, `git push`, `release`, `tag`, `versão`, `changelog`, `bump`,
`criar repo`, `padronizar repo`, `readme`, `pull request`, projeto novo com
`.git` presente e README ausente.

## O cerimonial completo

### 1. Escolher a versão (julgamento — é seu, não do script)

- `PATCH`: correção compatível, hardening, doc de release.
- `MINOR`: feature compatível, comando novo, API/tool pública nova.
- `MAJOR`: quebra de contrato, remoção, migração incompatível.

Detalhe e casos-limite em `references/semantic-versioning.md`.

### 2. Montar os artefatos

```bash
bash "$S" prepare X.Y.Z
```

Move `## [Unreleased]` para a seção da versão, cria `docs/release/X.Y.Z.md`,
registra no `docs/release/ledger.json` e bumpa o manifesto **se existir**
(`package.json`, `Cargo.toml`, `pyproject.toml`, `VERSION`, `deno.json`,
`composer.json`; repo sem manifesto é caso válido e suportado).

Depois **revise a narrativa da nota**. O script monta a estrutura; o que a
release entrega, como foi verificado e o que ela não resolve é redação sua.

### 3. Revisar e mesclar

Um PR por versão, carregando o commit de conteúdo **e** o `chore(release):`.
Merge só com CI verde. A tag nasce depois, na base já mesclada — nunca na branch
do PR.

### 4. Publicar

```bash
bash "$S" publish X.Y.Z            # --dry-run roda só as guardas
```

O publicador é quem impõe o contrato, nesta ordem, falhando fechado:

| # | Guarda |
|---|---|
| 1 | contrato de release em modo estrito (ledger, changelog, notas e manifesto) |
| 2 | gate anti-segredo da árvore rastreada |
| 3 | worktree limpa |
| 4 | branch base (detectada de `origin/HEAD`, senão `main`/`master`) |
| 5 | `HEAD == origin/<base>` |
| 6 | a versão é a última entrada do ledger e tem nota existente |
| 7 | tag **imutável**: recusa se a tag local ou remota aponta para outro commit |
| 8 | CI remoto verde no commit (via `gh`), em remote GitHub |
| 9 | tag anotada, push, GitHub Release via `gh` |

**Não refaça essas checagens à mão antes de chamar o publicador.** Duplicar o
gate em prosa é o que torna o cerimonial lento.

### 5. Registro final

O publicador imprime um resumo de máquina (repo, versão, tag, commit, estado do
CI remoto). Se você mantém algum registro de releases (notas, issue, log do
time), copie esse resumo para lá e pare: ele já é determinista e completo. O CI
valida apenas o ledger versionado no git.

## Convenções: detectadas, não impostas

O script lê as convenções do próprio repositório antes de escrever qualquer
coisa. Nada é hardcoded, porque repositórios reais divergem:

| Convenção | Como é detectada | Override |
|---|---|---|
| Prefixo de tag | entradas do ledger, senão tags existentes; default `v` | `.release.json` → `tagPrefix` |
| Estilo do release name | entradas do ledger: `bare` (`X.Y.Z`), `tag` (`vX.Y.Z`), `tag-desc` | `releaseNameStyle` ou `--release-name` |
| Manifesto de versão | primeiro dos 6 formatos encontrado; ausência é válida | `manifest` |
| Formato do changelog | `## [X.Y.Z] - data`, `## X.Y.Z - data`, com ou sem colchete/travessão | — |
| Shape do ledger | objeto com `releases` (com `$schema`/`project`/`schemaVersion`/`schema_version`) ou array | `ledger` |
| Aliases de campo | `releaseName`/`release_name`; `evidence`/`evidence_path`/`notes` | — |
| Branch base | `origin/HEAD`, senão `main`, senão `master` | — |
| Comando de CI local | `.release.json` → `ciCommand` | `ciCommand` |

`bare` é o default por ser a convenção majoritária observada. Um repo que use
outra coisa é seguido, não corrigido.

**Estrutura quebrada é ERRO; convenção divergente é WARN.** `--strict` promove
todo WARN a erro — é o modo do CI e da publicação. Um validador que só aceita um
formato não valida nada, porque ninguém consegue adotá-lo.

## Refs (carregue sob demanda)

### Decisão e redação
- `references/semantic-versioning.md` — SemVer, quando bump major/minor/patch
- `references/conventional-commits.md` — spec, tipos, exemplos, trailers
- `references/atomic-commits.md` — split e reescrita de histórico, formas não-interativas
- `references/release-automation.md` — contrato de release, wrappers por repo, exceções

### Documentação e estrutura
- `references/readme-completo.md` — estrutura padrão de README
- `references/repo-essentials.md` — LICENSE, .gitignore, CONTRIBUTING, SECURITY
- `references/hidden-files-policy.md` — política de `.*` (commitar vs ignorar)
- `references/language-detection.md` — heurística de detecção de stack

### Validação local
- `references/security-pre-commit.md` — gitleaks e afins
- `references/pre-push-validation.md` — lefthook, hooks, anti-stale
- `references/worktrees-workflow.md` — ponteiro: doutrina vive em `worktree-agent-workflow`

## Templates

README (pt-br/en-us/bilíngue), CONTRIBUTING, CHANGELOG, PR, `.editorconfig`,
`.env.example`, `lefthook.yml`, `gitleaks.toml`, `github-actions-ci.yml`,
`release/ledger.template.json`, `release/release-note.template.md` e um
`.gitignore` por stack em `templates/gitignore/` (base, node, python, go, rust,
java, php, ruby, agents-repo).

`templates/scripts/*.sh` são wrappers finos para `scripts/release.sh` — existem
para o repo ter um entrypoint local familiar, não para reimplementar o contrato.

## Config global

Lê `~/.config/git-pro.json`; se não existir, pergunte ao usuário e crie.
Modelo em `config.example.json` (`docs_language`, `commit_language`,
`default_license`, `default_author`, `default_org`).

Config **por repositório** é `.release.json` na raiz, e só carrega override do
que foi detectado errado. Repo bem-comportado não precisa dele.

## Anti-patterns

- ❌ Commit misturando múltiplas mudanças lógicas (não-atômico)
- ❌ Mensagem fora do Conventional Commits (`update stuff`, `fix bug`)
- ❌ Qualquer trailer de atribuição de agente/IA no commit
- ❌ Push sem `pull --rebase` quando a branch está atrás
- ❌ Validação só no CI remoto (lento, descobre tarde — local primeiro)
- ❌ Release sem CHANGELOG, nota narrativa e ledger
- ❌ Tag manual sem harness, sem CI verde ou fora da base sincronizada
- ❌ Mover, deletar ou reapontar tag já publicada
- ❌ Reusar versão para conteúdo diferente
- ❌ Reexecutar à mão, em prosa, gate que o publicador já impõe em código
- ❌ Allowlist de segredo por CAMINHO em vez de por valor exato
- ❌ Confiar em verde de gate que não nomeia a árvore que leu
- ❌ Rodar ferramenta genérica de scan por cima de gate curado do próprio repo
- ❌ Duas implementações do mesmo contrato de release no mesmo ecossistema
- ❌ Commit de `.env`, credenciais, `node_modules/`, sessions de AI

## Bypass legítimos (raros, conscientes)

- `git push --no-verify` / `git commit --no-verify` — bypass de hook, pontual
- `publish --allow-no-remote-checks` — repo sem CI remoto; o resumo registra
- WIP em feature branch com mensagem livre, **squash antes do merge**

## Princípio guia

> Disciplina previne dor, mas disciplina que só existe em prosa é relida,
> reinterpretada e renegociada a cada ciclo. Contrato que importa vira código
> que falha sozinho. Release boa é local, explícita, SemVer, auditável,
> reprodutível — e barata de executar.
