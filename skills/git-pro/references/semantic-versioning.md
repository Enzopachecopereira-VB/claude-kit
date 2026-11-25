# Semantic Versioning (SemVer)

Versão `MAJOR.MINOR.PATCH` (ex: `1.4.2`).

Spec oficial: https://semver.org/lang/pt-BR/

## Regras

| Componente | Quando incrementar | Exemplo |
|---|---|---|
| **MAJOR** | Mudança incompatível (breaking change) | 1.2.3 → 2.0.0 |
| **MINOR** | Nova feature compatível | 1.2.3 → 1.3.0 |
| **PATCH** | Bug fix compatível | 1.2.3 → 1.2.4 |

Quando bumps:
- MINOR/PATCH bump → MENOR sempre zera
- MAJOR bump → MINOR e PATCH zeram (1.4.2 → 2.0.0)

## Mapping com Conventional Commits

Use os commits para escolher a versão, mas a decisão final deve considerar a superfície pública real entregue.

| Commit | Bump |
|---|---|
| `fix:` | PATCH |
| `feat:` | MINOR |
| `feat!:` ou `BREAKING CHANGE:` no rodapé | MAJOR |
| `docs:`, `style:`, `refactor:`, `chore:`, `test:`, `build:`, `ci:` | nenhum (não gera release) |
| `perf:` | PATCH |

## Versão pré-release

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta
1.0.0-rc.1
1.0.0
```

Ordem: `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0`

## Versão 0.x.y — "API ainda instável"

Convencionalmente:
- `0.x.y` = projeto pré-1.0, qualquer mudança pode quebrar
- Promova pra `1.0.0` quando API for estável e merece compromisso

**Para repos novos**: começar em `0.1.0`.

## Quando bumpar MAJOR (zero tolerance)

Qualquer mudança que pode quebrar consumidor:

- Renomear/remover função pública
- Mudar assinatura de função pública
- Mudar comportamento default
- Subir versão major de runtime (Node 18 → 22)
- Mudar formato de config (config antiga não parseia)
- Mudar URL de API/endpoint
- Mudar formato de retorno

## Quando NÃO bumpar MAJOR

Mesmo que pareça grande:
- Refactor interno (API pública igual)
- Performance gain (mesmo enorme)
- Deprecar feature SEM remover (deprecar = MINOR, remover = MAJOR)
- Adicionar feature opcional

## Lockfiles e SemVer

Em `package.json`/`pyproject.toml`/etc, regra de range:
- `^1.2.3` — aceita até <2.0.0 (não bump major, ok minor/patch)
- `~1.2.3` — aceita até <1.3.0 (só patch)
- `1.2.3` — exato
- `>=1.2.3 <2.0.0` — explícito

**Preferência**: `^1.2.3` pra confiar em SemVer dos deps.

## Releases especiais

- **Hotfix em versão antiga**: criar branch `release/1.x` da tag `1.x.y`, fix, publicar `1.x.(y+1)`
- **LTS** (long-term support): manter `1.x` por meses paralelos a `2.x`
- **Yanked release** (gravemente bugada): NPM `npm deprecate`, Cargo `cargo yank`. Não delete tag — só marca como yanked.

## Onde declarar versão

| Stack | Arquivo |
|---|---|
| Node | `package.json` → `"version": "1.2.3"` |
| Python | `pyproject.toml` → `[project] version = "1.2.3"` ou `__version__` no `__init__.py` |
| Go | tag git é a versão (`v1.2.3`) |
| Rust | `Cargo.toml` → `version = "1.2.3"` |
| Java | `pom.xml` ou `build.gradle` |

O harness local não altera arquivos de versão automaticamente. Atualize o manifesto da stack no mesmo PR de release quando ele existir.

## Tag git — formato

Convenção: **`v` prefix obrigatório**.

```bash
git tag -a v1.2.3 -m "Release 1.2.3"
git push origin v1.2.3
```

Por quê `v`: `1.2.3` poderia ser branch/tag/path, `v1.2.3` é inequívoco.

O publicador local deve criar/reusar a tag e falhar se tag local/remota existente não apontar para o `HEAD`.

## Anti-patterns

- ❌ Tag sem `v` prefix
- ❌ Tag lightweight para release pública quando tag anotada é possível
- ❌ Pular versões (1.2.3 → 1.5.0 sem 1.3/1.4)
- ❌ Deletar tag publicada (use yank, não delete)
- ❌ Reusar versão (publicar `1.2.3` duas vezes diferentes)
- ❌ MAJOR bump por refactor interno (não é breaking pro user)
