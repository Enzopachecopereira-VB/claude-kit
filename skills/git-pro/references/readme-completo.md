# README Completo — Estrutura Padrão

README profissional cobre: descoberta (badges), entendimento (description), uso (install + quickstart), referência (config + components), comunidade (contributing + license).

## Estrutura padrão (ordem importa)

```markdown
# Nome do Projeto

[badges]

> Tagline em 1 linha — o que faz, pra quem

[Imagem/screenshot/logo, opcional]

[Tabela de conteúdos, se README > 500 linhas]

## ✨ Features

## 🚀 Quickstart

## 📦 Instalação

## 🔧 Configuração

## 📖 Uso

## 🧩 Componentes / Módulos

## 🛠 Desenvolvimento

## 🗺 Roadmap

## 🤝 Contribuindo

## 📝 Licença

## 🙏 Agradecimentos
```

## Por seção (o que vai em cada)

### Title + Tagline
```markdown
# Nome do Projeto

> Uma frase clara que diga: o que faz + pra quem + diferencial
```

Exemplo bom: `> Skills profissionais Git pra times que querem disciplina sem fricção`
Exemplo ruim: `> Um projeto incrível!` (vago, sem info)

### Badges (logo abaixo do título)

Geradas em https://shields.io/

```markdown
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/release/USER/REPO)](https://github.com/USER/REPO/releases)
[![License](https://img.shields.io/github/license/USER/REPO)](LICENSE)
[![Downloads](https://img.shields.io/npm/dt/PACKAGE)](https://www.npmjs.com/package/PACKAGE)
```

Padrão: CI + version + license. Stack-specific opcional (npm downloads, PyPI, crates.io).

### Features (3-7 bullets)

```markdown
## ✨ Features

- 🚀 **Velocidade**: compila em < 100ms
- 🔒 **Seguro**: secret scanning automático
- 📦 **Zero config**: funciona out-of-the-box
- 🌍 **Multi-stack**: Node, Python, Go, Rust
```

Use ícones (sutil, não exagere). Foco em benefício, não feature técnica isolada.

### Quickstart (60 segundos)

```markdown
## 🚀 Quickstart

\`\`\`bash
brew install <tool>
<tool> init my-project
cd my-project
<tool> start
\`\`\`

→ Acesse http://localhost:3000
```

**Regra**: usuário copia/cola e funciona. Sem placeholders confusos.

### Instalação (detalhada por plataforma)

```markdown
## 📦 Instalação

### macOS
\`\`\`bash
brew install <tool>
\`\`\`

### Linux
\`\`\`bash
curl -sSL https://install.example.com | bash
\`\`\`

### Windows
\`\`\`powershell
winget install <tool>
\`\`\`

### Via npm / pip / cargo / go
\`\`\`bash
npm install -g <package>
\`\`\`

### Pré-requisitos
- Node 22+ ou Bun 1.x
- Git 2.40+
```

### Configuração

```markdown
## 🔧 Configuração

Arquivo `~/.config/<tool>.json`:

\`\`\`json
{
  "language": "pt-br",
  "default_author": "<author>"
}
\`\`\`

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `language` | string | `en-us` | Idioma das docs geradas |
| `default_author` | string | — | Nome em LICENSE |

Variáveis de ambiente:

| Var | Default | Descrição |
|---|---|---|
| `TOOL_DEBUG` | `0` | Verbose logs |
```

### Uso (cenários reais)

```markdown
## 📖 Uso

### Caso 1: Criar projeto novo
\`\`\`bash
<tool> init my-app
\`\`\`

### Caso 2: Adicionar componente
\`\`\`bash
<tool> add component <name>
\`\`\`

Ver [documentação completa](docs/usage.md) para casos avançados.
```

Mostre 3-5 cenários comuns. Profundos → linkar pra `docs/`.

### Componentes / Módulos / Arquitetura

```markdown
## 🧩 Componentes

| Componente | Responsabilidade |
|---|---|
| `core/` | Engine principal |
| `cli/` | Interface CLI |
| `web/` | Dashboard web |
| `sdk/` | SDK para integração |

### Arquitetura

\`\`\`
user → cli → core → adapters → providers
\`\`\`

Detalhes em [ARCHITECTURE.md](docs/ARCHITECTURE.md).
```

Se for skill/agente: listar refs/templates/scripts disponíveis.

### Desenvolvimento

```markdown
## 🛠 Desenvolvimento

### Setup
\`\`\`bash
git clone <repo>
cd <repo>
bun install
\`\`\`

### Comandos
| Comando | Descrição |
|---|---|
| `bun dev` | Modo dev com hot reload |
| `bun test` | Testes |
| `bun lint` | Lint |
| `bun build` | Build produção |

### Estrutura
\`\`\`
src/
├── core/
├── cli/
└── utils/
tests/
docs/
\`\`\`
```

### Roadmap (opcional, projetos pequenos podem pular)

```markdown
## 🗺 Roadmap

- [x] CLI básico
- [x] Suporte Node
- [ ] Suporte Python
- [ ] Plugin system
- [ ] Web UI

Ver [GitHub Projects](https://github.com/USER/REPO/projects/1) para detalhes.
```

### Contribuindo

```markdown
## 🤝 Contribuindo

PRs são bem-vindos! Antes de abrir:

1. Leia [CONTRIBUTING.md](CONTRIBUTING.md)
2. Discuta features novas via [Issues](https://github.com/USER/REPO/issues)
3. Siga [Conventional Commits](https://www.conventionalcommits.org/)
4. Garanta que `lefthook` está instalado (`lefthook install`)
```

### Licença

```markdown
## 📝 Licença

[MIT](LICENSE) © <author>
```

Exato 1-2 linhas. Link pra `LICENSE`.

### Agradecimentos (opcional)

```markdown
## 🙏 Agradecimentos

- [Tool X](https://...) — pela inspiração
- @contributor — pelos PRs iniciais
```

## Princípios

1. **Usuário não-técnico entende o tagline** — não jargão
2. **Quickstart funciona copy-paste** — sem placeholders
3. **Tabelas > prosa** pra config e comandos
4. **Links pra docs detalhadas** — não inflar README
5. **Badges no topo** — sinaliza projeto vivo
6. **Estrutura previsível** — usuário sabe onde achar cada coisa

## Tamanho ideal

| Projeto | README ideal |
|---|---|
| CLI/biblioteca pequena | 100-200 linhas |
| Framework médio | 200-400 linhas |
| Mega-projeto | 200-300 linhas + extensa pasta `docs/` |

**Acima de 500 linhas** = adicionar TOC no topo. Acima de 800 = considerar mover seções pra `docs/`.

## Idioma (segue config.json)

- `pt-br` → README inteiro em PT
- `en-us` → README inteiro em EN
- `bilingual` → dois arquivos: `README.md` (EN, default GitHub) + `README.pt-BR.md`, com link no topo do EN: `> 🇧🇷 [Leia em Português](README.pt-BR.md)`

## Anti-patterns

- ❌ Tagline vaga ("um projeto incrível pra fazer coisas")
- ❌ Quickstart com placeholders confusos (`<your-token-here>` sem explicar onde pegar)
- ❌ Sem badges
- ❌ Sem `## Licença`
- ❌ Roadmap eterno em READMEs de projeto morto (sinaliza abandono)
- ❌ README de 2000 linhas (mover pra `docs/`)
- ❌ README só em uma linguagem quando projeto é internacional (bilingual)
- ❌ Screenshots quebrados (host imagens no repo em `docs/img/`, não imgur)
