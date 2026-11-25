# Contribuindo para {{NOME_DO_PROJETO}}

Obrigado por considerar contribuir! Este documento descreve o processo.

## Código de Conduta

Este projeto segue o [Contributor Covenant](CODE_OF_CONDUCT.md). Ao participar, você concorda com seus termos.

## Como contribuir

### 🐛 Reportar bugs

1. Verifique se já não existe [issue aberta](https://github.com/{{ORG}}/{{REPO}}/issues)
2. Abra novo issue usando o template `Bug Report`
3. Inclua: passos pra reproduzir, comportamento esperado vs atual, ambiente (OS, versão)

### 💡 Sugerir features

1. Abra issue usando template `Feature Request`
2. Descreva o problema, não só a solução
3. Aguarde discussão antes de começar implementação

### 🔧 Submeter PR

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/SEU_USUARIO/{{REPO}}.git
   cd {{REPO}}
   ```
3. **Setup**:
   ```bash
   {{SETUP_COMMAND}}
   lefthook install
   ```
4. **Crie branch**:
   ```bash
   git checkout -b feat/minha-feature
   # ou: fix/meu-bug, docs/atualiza-readme, etc.
   ```
5. **Faça commits atômicos** seguindo [Conventional Commits](https://www.conventionalcommits.org/):
   ```
    feat(auth): add OAuth2 login
    fix(api): fix timeout on /users
    docs: atualiza guia de instalação
   ```
6. **Push e abra PR**:
   ```bash
   git push -u origin feat/minha-feature
   ```
7. Preencha o template do PR

## Padrões de Código

### Commits

Conventional Commits **obrigatório** — hook bloqueia mensagens fora do padrão.

| Tipo | Uso |
|---|---|
| `feat` | Nova feature |
| `fix` | Bug fix |
| `docs` | Só documentação |
| `style` | Formatação (sem mudança de código) |
| `refactor` | Refactor sem feature nem fix |
| `perf` | Performance |
| `test` | Testes |
| `build`, `ci`, `chore` | Outros |

Adicione `!` no tipo (`feat!:`) ou `BREAKING CHANGE:` no rodapé para mudanças incompatíveis.

### Commits atômicos

Cada commit = uma mudança lógica. Use `git add -p` para separar.

### Linting e formatação

Validação **automática** antes do commit (lefthook):

- Lint
- Format check
- Conventional Commits
- Secret scan (gitleaks)

Se falhar, commit é rejeitado. Corrija antes.

### Antes do push

Validação **automática** antes do push (lefthook):

- Verifica se branch está atualizada com `origin`
- Roda testes
- Scan completo de secrets

Se falhar, push é rejeitado. **Use `git pull --rebase` se branch está atrás**.

### Testes

- Toda feature nova precisa de teste
- Bug fix precisa de teste regression
- Cobertura mínima: {{COBERTURA_MIN}}%

```bash
{{CMD_TEST}}
```

### Documentação

- Funções públicas: comentar com docstring quando comportamento não é óbvio
- README atualizado se mudança afeta interface
- Adicionar entrada em `CHANGELOG.md` quando a mudança altera comportamento, documentação pública ou processo de release.

## Review Process

1. PR criado → CI roda
2. CI passa? Revisor designado automaticamente via CODEOWNERS
3. Pelo menos **1 approval** necessário
4. Comments resolvidos? Pode mergir
5. Merge → mudança fica pronta para o próximo PR de release SemVer

## Releases SemVer

O processo canônico é local e auditável:

1. Escolher a versão SemVer.
2. Atualizar `CHANGELOG.md`.
3. Criar `docs/release/X.Y.Z.md`.
4. Atualizar `docs/release/ledger.json`.
5. Rodar `make release-check` e os gates locais do projeto.
6. Abrir PR de release e fazer merge apenas com CI verde.
7. Publicar da `main` limpa e sincronizada:
   ```bash
   make release-publish VERSION=X.Y.Z
   ```

Não mover tag publicada. Corrigir falhas em novo commit e publicar novo `PATCH` quando necessário.

### Tipo de merge

- **Squash and merge** (padrão para features) — commits WIP viram 1 commit Conventional limpo
- **Rebase and merge** (para refactors com histórico significativo) — preserva history linear
- **Merge commit** (raro) — só pra integrações grandes que merecem destaque

## Setup de desenvolvimento

### Pré-requisitos
- {{REQUISITO_1}}
- {{REQUISITO_2}}
- [lefthook](https://github.com/evilmartians/lefthook) — `brew install lefthook`
- [gitleaks](https://github.com/gitleaks/gitleaks) — `brew install gitleaks`

### Setup inicial

```bash
git clone https://github.com/{{ORG}}/{{REPO}}.git
cd {{REPO}}
{{INSTALL_DEPS}}
lefthook install
```

### Comandos úteis

| Comando | Descrição |
|---|---|
| `{{CMD_DEV}}` | Dev mode |
| `{{CMD_TEST}}` | Testes |
| `{{CMD_LINT}}` | Lint |
| `{{CMD_BUILD}}` | Build |
| `lefthook run pre-commit` | Validação manual pré-commit |
| `lefthook run pre-push` | Validação manual pré-push |

## Worktrees (paralelismo)

Para hotfixes urgentes sem largar feature atual:

```bash
git worktree add ../{{REPO}}.wt/hotfix-X hotfix-X
cd ../{{REPO}}.wt/hotfix-X
lefthook install  # cada worktree precisa
# trabalha, push
cd -
git worktree remove ../{{REPO}}.wt/hotfix-X
```

Ver `references/worktrees-workflow.md` da skill `git-pro` para padrão completo.

## Dúvidas?

Abra [Discussion](https://github.com/{{ORG}}/{{REPO}}/discussions) ou comente em issue existente.

Obrigado! 🙌
