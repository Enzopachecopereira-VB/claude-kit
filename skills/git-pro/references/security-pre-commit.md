# Security Pre-Commit — Anti-Credenciais com gitleaks

**gitleaks** = scanner de secrets em código/histórico Git. Padrão de facto pra prevenção de credential leak.

Repo: https://github.com/gitleaks/gitleaks

## Por que gitleaks

- **Binary Go único** — sem deps Python/Node
- **Rápido** (~ms por arquivo)
- **Regras built-in** pra 100+ tipos (AWS, GCP, Slack, Stripe, GitHub tokens, etc.)
- **Custom rules** via TOML
- **Histórico** — pode scan repo inteiro retroativo

## Instalação

```bash
brew install gitleaks            # macOS
# ou: scoop install gitleaks     # Windows
# ou: docker run zricethezav/gitleaks
```

## Setup no repo

### 1. Config — `gitleaks.toml` na raiz

Template em `templates/gitleaks.toml`. Resumo do que cobre:

- AWS keys (AKIA*, ASIA*)
- GitHub PAT (ghp_*, gho_*, ghu_*, ghs_*, ghr_*)
- GitLab token
- Stripe (sk_live_*, pk_live_*)
- Slack (xoxb-*, xoxp-*)
- Anthropic API key (sk-ant-*)
- OpenAI API key (sk-*)
- Generic high-entropy strings em variáveis de env
- Private keys (-----BEGIN RSA/EC/OPENSSH PRIVATE KEY-----)
- Database URLs com senha (`postgres://user:pass@`)
- JWT-like tokens
- Senhas em URLs

### 2. Hook via lefthook

`lefthook.yml`:
```yaml
pre-commit:
  commands:
    gitleaks:
      run: gitleaks protect --staged --verbose --redact

pre-push:
  commands:
    gitleaks-full:
      run: gitleaks detect --no-banner --redact
```

- `pre-commit` rápido — só staged files
- `pre-push` completo — scan repo inteiro (mais devagar mas catch tudo antes do push)

### 3. Bypass legítimo (raro)

Se gitleaks marca **false positive**:

#### A. Comentário inline pra ignorar 1 linha
```python
api_key = "sk-test-1234567890abcdef"  # gitleaks:allow
```

#### B. Whitelist no gitleaks.toml
```toml
[allowlist]
paths = [
    "tests/fixtures/.*",      # fixtures de teste podem ter dummy keys
    "docs/examples/.*",
]
regexes = [
    "EXAMPLE_KEY_DO_NOT_USE",
    "sk-test-DUMMY",
]
```

#### C. Bypass via comando (uso pontual, justificado)
```bash
git push --no-verify
```

## Custom rules (avançado)

Adicionar regra pra padrão específico:

```toml
[[rules]]
id = "minha-empresa-internal-token"
description = "Token interno da empresa"
regex = '''(?i)minhaempresa[_-]?(?:api|key|token)[_-]?[:=]\s*['"]?([a-z0-9]{32,})['"]?'''
tags = ["secret", "internal"]
```

## Scan retroativo (1x quando adotar)

Antes de adotar pre-commit, scan TODO o histórico do repo:

```bash
gitleaks detect --no-banner --redact --report-path gitleaks-report.json
```

Se achar secrets no histórico:
1. **NÃO BASTA deletar do código atual** — secret está no git history
2. Rotacionar IMEDIATAMENTE o secret afetado (mudar key/senha)
3. Considerar `git-filter-repo` pra remover do histórico (complexo, last resort)
4. Considerar BFG Repo-Cleaner (https://rtyley.github.io/bfg-repo-cleaner/)

## Comandos úteis

```bash
# Scan staged files (pre-commit típico)
gitleaks protect --staged --verbose

# Scan working dir (não-staged)
gitleaks protect --verbose

# Scan repo inteiro (histórico completo)
gitleaks detect --verbose

# Scan com report JSON
gitleaks detect --report-path report.json

# Scan ignorando paths
gitleaks detect --no-banner --report-path report.json --redact

# Versão
gitleaks version
```

## Anti-patterns

- ❌ Commitar `.env` "só por agora pra testar" — pode estar no histórico pra sempre
- ❌ Ignorar warning achando que é fixture — confirme antes
- ❌ Usar `--no-verify` recorrente (vira hábito ruim)
- ❌ Comentar `# gitleaks:allow` sem entender por quê
- ❌ Skipar scan retroativo ao adotar (pode ter sujeira velha)
- ❌ Confiar SÓ no gitleaks — também use:
  - `.gitignore` correto pra `.env*`
  - Vault de secrets em prod (1Password, Vault, AWS Secrets Manager)
  - `direnv` pra carregar `.env.local` (gitignored) em dev

## Validação que está funcionando

```bash
# Criar arquivo com secret de teste
echo 'AWS_KEY="AKIAIOSFODNN7EXAMPLE"' > test-secret.txt
git add test-secret.txt
git commit -m "test"
# → lefthook deve BLOQUEAR commit por causa do gitleaks
```

Se passou, gitleaks NÃO está configurado certo. Revisa `lefthook.yml`.

## Integração com `.env.example`

Boa prática: cada `.env*` real está no `.gitignore`, mas existe `.env.example` versionado:

```bash
# .env.example
DATABASE_URL=postgres://user:password@localhost:5432/db
API_KEY=your-api-key-here
JWT_SECRET=change-me-in-production
```

Gitleaks ignora `.env.example` por convenção (em `gitleaks.toml` allowlist).

## Reportar leak descoberto em outro repo público

Se encontrar credencial leaked em qualquer repo (não seu):
1. **Não use** a credencial (legal/ético)
2. Avisar o owner via SECURITY.md ou email
3. Plataforma (GitHub) tem Secret Scanning Alert automático pra muitas APIs — eles avisam o owner sozinhos
