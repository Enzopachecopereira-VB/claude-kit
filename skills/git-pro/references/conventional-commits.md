# Conventional Commits

Padrão de mensagens de commit que viabiliza review objetivo, changelog legível e escolha SemVer consistente.

Spec oficial: https://www.conventionalcommits.org/

## Formato

```
<tipo>[escopo opcional]: <descrição curta>

[corpo opcional]

[rodapé opcional]
```

## Tipos (use exatamente esses)

| Tipo | Quando usar | Bump SemVer |
|---|---|---|
| `feat` | Nova feature pro usuário | **minor** |
| `fix` | Bug fix | **patch** |
| `docs` | Só documentação | nenhum |
| `style` | Formatação (espaço, vírgula). Sem mudança de código | nenhum |
| `refactor` | Refactor sem feature nem fix | nenhum |
| `perf` | Performance | patch |
| `test` | Adicionar/corrigir testes | nenhum |
| `build` | Build system, dependências | nenhum |
| `ci` | CI/CD | nenhum |
| `chore` | Outras manutenções | nenhum |
| `revert` | Reverter commit anterior | depende |

## Breaking changes — bump MAJOR

Duas formas:

```
feat!: muda API de auth (breaking)
```

ou no rodapé:

```
feat: nova API de auth

BREAKING CHANGE: o método login() agora exige objeto credentials.
```

Qualquer das duas → a próxima release deve ser **major**.

## Escopo (opcional, mas recomendado)

```
feat(auth): adiciona OAuth2
fix(api): corrige timeout em /users
chore(deps): bump axios pra 1.7.0
```

Escopo padroniza: `auth`, `api`, `ui`, `deps`, `ci`, `docs`, ou nome de módulo.

## Exemplos práticos (PT-BR vs EN-US)

### EN-US (convenção mais comum, recomendada)
```
feat(auth): add OAuth2 login flow
fix(api): handle null user in /me endpoint
refactor(db): extract query builder
docs: update README install section
chore(deps): bump fastify to 4.28.0
ci: add release process check
test(auth): cover edge case empty token
perf(parser): cache compiled regex
build: switch from npm to bun
```

### PT-BR (válido, mas changelog fica em PT)
```
feat(auth): adiciona fluxo de login OAuth2
fix(api): trata usuário nulo no endpoint /me
docs: atualiza seção de instalação no README
```

**Recomendação**: commits em EN, docs (README/CHANGELOG) em qualquer idioma. EN-only no changelog facilita contribuição externa.

## Anti-patterns

```
❌ "update stuff"           → faltando tipo
❌ "fix bug"                → vago, sem contexto
❌ "FIX: corrige isso"      → tipo em maiúsculas
❌ "feat: Add feature."     → ponto final no título; "Add" sem padronização (use lower)
❌ "feat: implementa toda a refatoração do sistema de auth + adiciona logs + corrige typo"
                            → não atômico, mistura
❌ "asdf"                   → mensagem inútil
```

## Mensagens longas (corpo)

Use quando explicação importa:

```
feat(auth): add rate limit per user

Implements token bucket algorithm with Redis backend.
Default: 100 req/min per user. Configurable via RATE_LIMIT_RPM env.

Closes #123
```

## Trailers (rodapé)

```
Closes #123              # fecha issue
Refs #456                # referencia issue
Refs: #123               # forma alternativa com dois-pontos (ambas aceitas)
Signed-off-by: Nome <email>   # DCO — certifica que você é o autor/tem direito de submeter
BREAKING CHANGE: ...     # marca breaking
```

**Proibido em qualquer commit, sem exceção**: trailers de atribuição de
agente/IA (`Co-authored-by`, "Generated with ...", "Ultraworked with ..." ou
qualquer assinatura/atribuição de ferramenta/agente). Ver harness `00-core.md`.

## Validação automática (commitlint via lefthook)

`lefthook.yml` já vem com regra:
```yaml
commit-msg:
  commands:
    conventional:
      run: npx --yes @commitlint/cli --config @commitlint/config-conventional --edit {1}
```

Se mensagem não bate, commit é REJEITADO. Você reescreve.

## Padrões para casos especiais

### Múltiplas mudanças relacionadas no mesmo commit
**Não faça**. Split com staging seletivo ou `git reset --soft` + recommits atômicos (ver `atomic-commits.md`).

### Commit em WIP (work in progress)
Em feature branch é OK ter commits livres (`wip: testing X`). **Antes do merge pra main**, reescreva o histórico (non-interactive, ver `atomic-commits.md`) e squash/fixup em commits Conventional.

### Revert
```
revert: feat(auth): add OAuth2 login flow

This reverts commit abc123.
Motivo: causou regressão em login com senha simples.
```

### Merge commits
Geralmente preferir **rebase** ou **squash merge** ao invés de merge commit, pra manter history linear.

### Initial commit
```
chore: initial commit
```
ou
```
feat: project bootstrap
```
