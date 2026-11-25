# Contrato de release

O cerimonial é executável: `scripts/release.sh`. Este documento explica o
**contrato** que ele impõe, como adaptá-lo a um repositório e quando abrir
exceção. Não repete o procedimento — o script é a fonte de verdade.

## Por que o contrato virou código

Este contrato viveu em prosa por muito tempo, com um par de scripts-template ao
lado. O resultado medido: as duas implementações divergiram (o template exigia
`releaseName == X.Y.Z`; a prosa dizia outra coisa), e repositórios reais
acumularam sete formatos incompatíveis do mesmo "registro canônico". Prosa é
relida e reinterpretada a cada ciclo; código falha sozinho e sempre igual.

Regra que saiu disso: **uma implementação, consumida por todos**. Wrapper local
é bem-vindo; segunda implementação, não.

## O contrato

Toda release pública tem:

1. Tag SemVer anotada, com o prefixo praticado pelo repositório.
2. Seção da versão no `CHANGELOG.md`, com `## [Unreleased]` preservado no topo.
3. Nota narrativa por versão (arquivo `.md` ou diretório de evidências).
4. Entrada no ledger (`docs/release/ledger.json` por padrão).
5. Manifesto de versão em sincronia com a última entrada do ledger — quando o
   repositório tem manifesto. Muitos não têm, e isso é válido.
6. Worktree limpa, branch base sincronizada com o remote.
7. CI verde no commit que será taggeado — local e, em remote GitHub, remoto.
8. Tag imutável: nunca move, nunca reaponta.
9. GitHub Release publicada via `gh`, com a nota como corpo.

`release.sh check` valida 1-5. `release.sh publish` impõe 1-9.

## Severidade: estrutura x convenção

| Situação | Severidade |
|---|---|
| ledger ausente ou com raiz inválida | ERRO |
| `version` fora de `MAJOR.MINOR.PATCH` | ERRO |
| versão duplicada no ledger | ERRO |
| evidência apontada pelo ledger não existe | ERRO |
| tag divergente da convenção detectada | WARN |
| `releaseName` ausente | WARN |
| `date` fora de `YYYY-MM-DD` | ERRO |
| changelog sem seção da versão | WARN |
| evidência existe mas não está rastreada pelo git | WARN |
| manifesto fora de sincronia com o ledger | WARN |

`--strict` promove todo WARN a erro. Use `--strict` no CI e na publicação;
o modo tolerante existe para que um repositório com histórico legado consiga
**adotar** o contrato sem reescrever o passado.

## Adaptar a um repositório

Quase nunca é preciso: o script detecta prefixo de tag, estilo de nome,
manifesto, formato de changelog e shape do ledger a partir do que já existe.
Quando a detecção erra, `.release.json` na raiz corrige só o que erra:

```json
{
  "tagPrefix": "v",
  "releaseNameStyle": "bare",
  "manifest": "package.json",
  "ledger": "docs/release/ledger.json",
  "notesDir": "docs/release",
  "ciCommand": "make test",
  "secretAllowlist": ["AKIAIOSFODNN7EXAMPLE"]
}
```

`releaseNameStyle`: `bare` (`1.2.0`), `tag` (`v1.2.0`) ou `tag-desc`
(`v1.2.0 - descrição`). `bare` é o mais comum; siga o que o repositório já faz.

`secretAllowlist` é por **valor exato**. Allowlist por caminho é proibida: ela
deixa o scan verde justamente sobre os arquivos que são publicados.

## Wrapper local

Um repositório pode expor o entrypoint que seu time já conhece. O wrapper
delega, não reimplementa:

```make
release-check:
	@bash "$${GIT_PRO_RELEASE:-$$HOME/.agents/skills/git-pro/scripts/release.sh}" check --strict

release-publish:
	@test -n "$(VERSION)" || { echo "VERSION=X.Y.Z obrigatorio" >&2; exit 1; }
	@bash "$${GIT_PRO_RELEASE:-$$HOME/.agents/skills/git-pro/scripts/release.sh}" publish "$(VERSION)"
```

Em Node, aliases equivalentes em `scripts` do `package.json`.

Repositório que precisa rodar o check em CI sem `~/.agents` disponível deve
**versionar** o script (copiar `release.sh` + `release_engine.py` para
`scripts/`) e apontar `GIT_PRO_RELEASE` para a cópia. Cópia versionada é
legítima; cópia divergente não — ao atualizar, recopie.

## CI: safety net, não dono

O CI roda `release.sh check --strict` junto dos gates normais. Não crie workflow
separado de release: o gate primário é local, o remoto é rede de segurança.

Em remote GitHub, `publish` consulta os check-runs do commit via `gh` e recusa
se houver `failure`/`timed_out`/`cancelled`. Repositório sem CI remoto publica
com `--allow-no-remote-checks`, e o resumo final registra que a exceção foi
usada. Prometer "CI verde" sem consultar o CI foi um defeito real desta skill.

## Assets e checksums

Projeto sem artefato externo publica tag + GitHub Release. Projeto que distribui
binário/pacote gera os assets antes do `gh release upload` e publica
`checksums.txt` com SHA-256. Preferir anexar os checksums como asset **e**
citá-los na nota.

## release-please, semantic-release, changesets, GoReleaser

Exceção explícita por projeto, com justificativa registrada. Se adotados,
documente como o projeto evita:

- secret dedicado desnecessário;
- tag criada por bot sem validação local;
- assets gerados a partir de commit diferente do da tag;
- changelog ilegível para humano;
- workflow que só falha depois do merge.

Default: o harness local.

## Anti-patterns

- Segunda implementação do contrato convivendo com a primeira.
- Ledger cuja evidência aponta para arquivo inexistente.
- Convenção de nome/tag hardcoded em vez de detectada do repositório.
- Publicar de branch que não é a base, ou com a base atrás do remote.
- Deletar, mover ou reapontar tag pública.
- Publicar assets sem checksum.
- Token de release em arquivo, doc ou workflow.
