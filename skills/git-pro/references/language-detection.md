# Detecção Automática de Linguagem/Stack

Identifica a stack do projeto procurando arquivos marcadores. Decide qual `gitignore`, quais comandos de CI e como adaptar o harness local de release.

## Detecção por marcador (heurística)

Skill checa a raiz do projeto e ancestrais:

| Marcador presente | Stack inferida | `gitignore` adicional | Comandos de validação típicos |
|---|---|---|---|
| `package.json` | Node/TypeScript | `node` | `pnpm test`, `pnpm lint`, `pnpm build` |
| `bun.lockb` ou `bunfig.toml` | Bun (variant Node) | `node` | `bun test`, `bun lint`, `bun run build` |
| `deno.json` ou `deno.lock` | Deno | `node` (similar) | `deno task test`, `deno lint`, `deno check` |
| `pyproject.toml` | Python (moderno) | `python` | `pytest`, `ruff check`, `python -m build` |
| `requirements.txt` ou `setup.py` (sem pyproject) | Python (legado) | `python` | `pytest`, `python -m build` |
| `Pipfile` | Python (Pipenv) | `python` | `pipenv run pytest` |
| `poetry.lock` | Python (Poetry) | `python` | `poetry run pytest`, `poetry build` |
| `go.mod` | Go | `go` | `go test ./...`, `go vet ./...`, `go build ./...` |
| `Cargo.toml` | Rust | `rust` | `cargo test`, `cargo clippy`, `cargo build --locked` |
| `pom.xml` | Java (Maven) | `java` | `mvn test`, `mvn package` |
| `build.gradle` ou `build.gradle.kts` | Java (Gradle) | `java` | `./gradlew test`, `./gradlew build` |
| `composer.json` | PHP | `php` | `composer test`, `composer validate` |
| `Gemfile` | Ruby | `ruby` | `bundle exec rspec`, `bundle exec rubocop` |
| `pubspec.yaml` | Dart/Flutter | `dart` | `dart test`, `flutter test` |
| `mix.exs` | Elixir | `elixir` | `mix test`, `mix format --check-formatted` |
| `*.csproj`, `*.sln` | .NET/C# | `dotnet` | `dotnet test`, `dotnet build` |
| `pyproject.toml` com `[tool.maturin]` | Python+Rust (PyO3) | `python` + `rust` | combinar Python + Rust |

## Detecção de "repo de agentes"

Marcadores que indicam que o repo é **principalmente** de agentes/skills (não código compilado):

- `SKILL.md` na raiz ou em `skills/`
- Arquivos `.md` em `agents/`, `commands/`
- `AGENTS.md` na raiz com size > 1KB (instruções substanciais)
- Ausência de `package.json` / `pyproject.toml` / etc.
- Maioria dos files são `.md`/`.yaml`/`.json`

Se for, aplicar `gitignore/agents-repo` (em vez de stack tradicional).

Pode ser HÍBRIDO: repo de agentes que também tem scripts Python/Node. Aí concat: `agents-repo` + `python`/`node`.

## Monorepo

Múltiplos marcadores em sub-paths:

```
projeto/
├── package.json              # Node root
├── apps/
│   ├── web/package.json      # Node
│   ├── api/pyproject.toml    # Python
│   └── worker/Cargo.toml     # Rust
```

Detecção:
- Stack principal: Node (package.json na raiz)
- Sub-stacks: Python, Rust
- `.gitignore`: combinar base + node + python + rust
- release harness: usar um ledger único se o monorepo versiona junto; usar ledgers por pacote se o versionamento for independente

## Workflow no SKILL.md

```
1. ls raiz do projeto
2. Identificar marcadores presentes
3. Inferir stack(s)
4. Verificar se é repo de agentes (heurística acima)
5. Sugerir templates apropriados
6. Confirmar com user antes de aplicar
```

## Detecção via comandos (Bash)

```bash
# Quick detect Node
test -f package.json && echo "node"

# Python
test -f pyproject.toml -o -f requirements.txt -o -f Pipfile && echo "python"

# Go
test -f go.mod && echo "go"

# Rust
test -f Cargo.toml && echo "rust"

# Multi-detect
detect_stack() {
  local stacks=()
  [ -f package.json ] && stacks+=("node")
  [ -f pyproject.toml ] || [ -f requirements.txt ] && stacks+=("python")
  [ -f go.mod ] && stacks+=("go")
  [ -f Cargo.toml ] && stacks+=("rust")
  [ -f pom.xml ] || [ -f build.gradle ] && stacks+=("java")
  [ -f composer.json ] && stacks+=("php")
  [ -f Gemfile ] && stacks+=("ruby")

  # Agents repo
  if find . -maxdepth 3 -name "SKILL.md" -type f 2>/dev/null | head -1 | grep -q .; then
    stacks+=("agents-repo")
  fi

  echo "${stacks[@]}"
}
```

## Casos especiais

### Projeto vazio / inicialização

Se nenhum marcador encontrado, **PERGUNTAR ao usuário**:
```
Não detectei stack. Você está iniciando:
1. Node/TypeScript
2. Python
3. Go
4. Rust
5. Repo de agentes (só .md/yaml)
6. Outro (especificar)
```

### Sub-projeto vs projeto principal

Skill deve sempre operar na raiz do `git rev-parse --show-toplevel`, não no `pwd` aleatório.

### Detecção falsa (false positive)

`requirements.txt` pode existir só pra scripts auxiliares em repo Node. Heurística:
- Se `package.json` tem `"main"` ou `"scripts"` significativo + `requirements.txt` < 5 linhas → Node primário, Python auxiliar
- `.gitignore` cobre ambos (não custa)

## Versão da linguagem (sub-detecção)

| Stack | Onde achar versão | Arquivo |
|---|---|---|
| Node | `engines.node` em package.json | `.nvmrc` ou `.tool-versions` |
| Python | classifiers em pyproject.toml ou requirements | `.python-version` |
| Go | `go` directive em go.mod | go.mod |
| Rust | `rust-version` em Cargo.toml | `rust-toolchain.toml` |
| Java | `<maven.compiler.source>` ou `sourceCompatibility` | pom.xml / build.gradle |

Skill sugere criar arquivo de versão (`.nvmrc`, `.tool-versions`, etc.) se ausente.

## Anti-patterns

- ❌ Aplicar `gitignore/python` por achar `__pycache__/` antigo (sem `pyproject.toml`)
- ❌ Ignorar stack secundária em monorepo
- ❌ Não confirmar com user em casos ambíguos
- ❌ Aplicar template sem inspecionar — sempre mostra preview antes
