# Pre-Push Validation com lefthook

**lefthook** = gerenciador de hooks Git, escrito em Go. Configuração YAML, paralelismo nativo, cross-language (não exige Node ou Python no repo).

Repo: https://github.com/evilmartians/lefthook

## Por que lefthook (vs Husky vs pre-commit framework)

| Tool | Pros | Cons |
|---|---|---|
| **lefthook** ⭐ | Binary único Go, paralelismo, cross-stack, simples | Menos conhecido |
| Husky | Popular em ecossistema Node | Só Node, lento (boot Node) |
| pre-commit (Python) | Muitas integrações prontas | Só Python na máquina |
| Git hooks raw | Zero deps | Sem paralelismo, manuten ruim |

## Instalação

```bash
brew install lefthook            # macOS
# ou: scoop install lefthook     # Windows
# ou: pacote npm/cargo/etc
```

## Setup no repo

### 1. Criar `lefthook.yml` na raiz

Template em `templates/lefthook.yml`. Estrutura:

```yaml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{ts,tsx,js,jsx}"
      run: bunx --bun eslint {staged_files}
    format-check:
      glob: "*.{ts,tsx,js,jsx,md,json}"
      run: bunx --bun prettier --check {staged_files}
    gitleaks:
      run: gitleaks protect --staged --verbose --redact

commit-msg:
  commands:
    conventional:
      run: npx --yes @commitlint/cli --config @commitlint/config-conventional --edit {1}

pre-push:
  parallel: true
  commands:
    anti-stale:
      run: |
        git fetch --quiet origin "$LEFTHOOK_LOCAL_BRANCH" 2>/dev/null || exit 0
        BEHIND=$(git rev-list --count "HEAD..origin/$LEFTHOOK_LOCAL_BRANCH" 2>/dev/null || echo 0)
        if [ "$BEHIND" -gt 0 ]; then
          echo "🚫 Sua branch está $BEHIND commit(s) atrás de origin/$LEFTHOOK_LOCAL_BRANCH"
          echo "   Rode: git pull --rebase"
          exit 1
        fi
    gitleaks-full:
      run: gitleaks detect --no-banner --redact
    tests:
      run: bun test
```

### 2. Instalar hooks no repo (ativa lefthook)

```bash
lefthook install
```

Cria `.git/hooks/pre-commit`, `pre-push`, `commit-msg` apontando pro lefthook.

### 3. Verificar funcionamento

```bash
lefthook run pre-commit       # roda manualmente
lefthook run pre-push
```

## Hooks padrão recomendados (por momento)

### `pre-commit` (rápido — segundos)
- Lint (só arquivos staged)
- Format check
- gitleaks (staged files)
- Não rodar testes aqui (lento)

### `commit-msg` (instantâneo)
- Validar Conventional Commits via commitlint

### `pre-push` (mais lento — ok)
- **Anti-stale check** (`git fetch` + verifica branch atrás) ⭐
- gitleaks completo (todo working tree)
- Testes
- Build (se rápido)
- Type check completo (`tsc --noEmit`)

### NUNCA em pre-commit
- Testes (lento, distrai)
- Build completo
- Deploy

## Anti-stale check (detalhado)

Problema: você trabalha, esquece de fazer `git pull`, push, conflito em produção.

Solução: hook `pre-push` verifica antes:

```bash
git fetch --quiet origin "$LEFTHOOK_LOCAL_BRANCH" 2>/dev/null || exit 0
BEHIND=$(git rev-list --count "HEAD..origin/$LEFTHOOK_LOCAL_BRANCH" 2>/dev/null || echo 0)
if [ "$BEHIND" -gt 0 ]; then
  echo "🚫 Sua branch está $BEHIND commit(s) atrás de origin"
  echo "   Rode: git pull --rebase"
  exit 1
fi
```

`$LEFTHOOK_LOCAL_BRANCH` é env automática do lefthook = nome da branch sendo pushed.

**Bypass legítimo** (raro): `git push --no-verify`.

**Por que `--rebase`** (não merge): mantém history linear, sem merge commit feio.

## Skip hooks pontual

```bash
git commit --no-verify -m "..."      # pula pre-commit + commit-msg
git push --no-verify                 # pula pre-push
```

Use raramente, com motivo. Se virar hábito, hook está mal-configurado (muito invasivo).

## Output / verbose

```bash
lefthook run pre-commit -v           # verbose
LEFTHOOK_VERBOSE=1 git commit ...    # via env
```

## Configurações úteis

### Tags (rodar só certos hooks)

```yaml
pre-commit:
  commands:
    lint:
      tags: backend
      run: ...
```

Rodar só backend: `lefthook run pre-commit --tags backend`

### Glob (filtrar arquivos staged)

```yaml
lint-ts:
  glob: "*.{ts,tsx}"
  run: tsc --noEmit
```

### exclude (excluir paths)

```yaml
gitleaks:
  exclude:
    - "tests/fixtures/.*"
    - "docs/examples/.*"
  run: gitleaks protect --staged
```

### Skip em CI

```yaml
pre-commit:
  commands:
    lint:
      skip:
        - merge
        - rebase
        - run: '[ "$CI" = "true" ]'    # pula em CI
```

## Multi-stack (monorepo)

```yaml
pre-commit:
  parallel: true
  commands:
    lint-frontend:
      root: "frontend/"
      glob: "*.{ts,tsx}"
      run: cd frontend && bun lint {staged_files}

    lint-backend:
      root: "backend/"
      glob: "*.py"
      run: cd backend && ruff check {staged_files}

    lint-go:
      root: "services/"
      glob: "*.go"
      run: cd services && go vet ./...
```

## Performance

- `parallel: true` em comandos independentes (não estiver rodando mesmos files)
- `glob` pra restringir só arquivos relevantes
- Mover testes longos pra `pre-push` (não `pre-commit`)
- CI roda mesmos checks como redundância

## Compartilhar com time

Após criar `lefthook.yml`:

1. **Commit**: vai pro repo
2. Time clona repo e roda `lefthook install` 1x
3. Adicionar no README setup:
   ```markdown
   ## Setup dev
   \`\`\`bash
   brew install lefthook gitleaks
   lefthook install
   \`\`\`
   ```

Ou automatizar via `postinstall` (Node):
```json
{
  "scripts": {
    "prepare": "lefthook install"
  }
}
```

## Comandos úteis

```bash
lefthook install                     # ativa hooks no repo
lefthook uninstall                   # desativa
lefthook run pre-commit              # roda manual
lefthook run pre-push --files file1  # roda em arquivos específicos
lefthook dump                        # exibe config resolvida
lefthook version
```

## Anti-patterns

- ❌ Hook que roda > 30s em `pre-commit` (mover pra `pre-push`)
- ❌ Hook que escreve arquivos automaticamente (`prettier --write`) em `pre-commit` — confunde diff staged
- ❌ Bypass `--no-verify` rotineiro (revisar hook se está chato)
- ❌ Sem anti-stale check (clássico: trabalhar 1h sem pull, push, conflito)
- ❌ Não commitar `lefthook.yml` (time não vê)
- ❌ Esquecer de `lefthook install` em clone novo (hooks ficam off)
- ❌ Confiar SÓ em hook local (CI redundância obrigatória)

## Validação de funcionamento

```bash
# Forçar erro de lint pra ver se hook bloqueia
echo "import lol from 'invalid'" > test.ts
git add test.ts
git commit -m "test"
# → deve BLOQUEAR
```
