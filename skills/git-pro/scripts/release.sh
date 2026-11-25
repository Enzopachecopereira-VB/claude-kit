#!/usr/bin/env bash
# Cerimonial de release portatil. Funciona em QUALQUER repo git, sem instalacao.
#
#   release.sh status  [--repo P] [--json]        orientacao: o que existe, o que falta
#   release.sh init    [--repo P]                 cria o contrato (idempotente)
#   release.sh gate    [--repo P]                 gate anti-segredo do repo ALVO
#   release.sh check   [--repo P] [--strict] [--json]
#   release.sh prepare X.Y.Z [--repo P] [--date D] [--release-name N]
#   release.sh publish X.Y.Z [--repo P] [--dry-run] [--json] [--allow-no-remote-checks]
#
# PRINCIPIO ANTI-FALSO-VERDE: toda saida nomeia a raiz do repositorio avaliado.
# Gate que nao diz QUAL arvore leu nao prova nada — foi exatamente assim que um
# `ci` global respondeu "limpo" sobre o repo errado. Aqui o alvo e resolvido de
# --repo, senao do CWD, NUNCA do local onde este script mora.
#
# Toda operacao git usa `git -C "$REPO"`. bash 3.2 compativel (macOS de fabrica):
# sem declare -A, sem ${v,,}, sem mapfile.
set -euo pipefail

ENGINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/release_engine.py"

REPO=""
JSON=0
STRICT=0
DRY_RUN=0
ALLOW_NO_CHECKS=0
VERSION=""
DATE_ARG=""
NAME_ARG=""

die() { printf 'release: %s\n' "$*" >&2; exit 2; }

# Em modo --json o stdout pertence ao JSON. Texto humano vai para stderr, senao
# o consumidor de maquina recebe lixo antes do payload.
say() { if [ "$JSON" -eq 1 ]; then printf '%s\n' "$*" >&2; else printf '%s\n' "$*"; fi; }
fail() { say "  ERRO  $*"; }

need() { command -v "$1" >/dev/null 2>&1 || die "comando ausente: $1"; }

# Aceitar --json e devolver texto humano no stdout quebra quem faz parse. Onde
# nao ha payload de maquina, a flag e recusada em vez de ignorada.
reject_json() {
  [ "$JSON" -eq 0 ] || die "--json nao se aplica a '$1' (use status, check ou publish)"
}

parse_flags() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --repo) [ $# -ge 2 ] || die "--repo exige caminho"; REPO="$2"; shift 2 ;;
      --repo=*) REPO="${1#--repo=}"; shift ;;
      --json) JSON=1; shift ;;
      --strict) STRICT=1; shift ;;
      --dry-run|-n) DRY_RUN=1; shift ;;
      --allow-no-remote-checks) ALLOW_NO_CHECKS=1; shift ;;
      --date) [ $# -ge 2 ] || die "--date exige valor"; DATE_ARG="$2"; shift 2 ;;
      --release-name) [ $# -ge 2 ] || die "--release-name exige valor"; NAME_ARG="$2"; shift 2 ;;
      -*) die "flag desconhecida: $1" ;;
      *)
        if [ -z "$VERSION" ]; then VERSION="$1"; shift
        else die "argumento extra: $1"; fi ;;
    esac
  done
}

resolve_repo() {
  local start root
  start="${REPO:-${GIT_PRO_RELEASE_REPO:-.}}"
  [ -d "$start" ] || die "diretorio inexistente: $start"
  root=$(git -C "$start" rev-parse --show-toplevel 2>/dev/null) \
    || die "nao e repositorio git: $start"
  REPO="$root"
}

engine() { python3 "$ENGINE" "$@"; }

json_field() { # json_field <json> <chave>
  printf '%s' "$1" | python3 -c \
    'import json,sys; print(json.load(sys.stdin).get(sys.argv[1]) or "")' "$2"
}

default_branch() {
  local d
  d=$( { git -C "$REPO" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null \
         || true; } | sed 's#^origin/##' )
  if [ -n "$d" ]; then printf '%s' "$d"; return; fi
  local c
  for c in main master; do
    if git -C "$REPO" show-ref --verify --quiet "refs/heads/$c"; then printf '%s' "$c"; return; fi
  done
  printf 'main'
}

is_github_remote() {
  local url
  url=$(git -C "$REPO" remote get-url origin 2>/dev/null || printf '')
  case "$url" in *github.com*) return 0 ;; *) return 1 ;; esac
}

# `gh` resolve owner/repo pelo CWD. Rodado de outro diretorio, publicaria a
# release no repositorio ERRADO — a mesma classe de falso-verde que este script
# existe para impedir. Toda chamada gh recebe --repo derivado do remote do ALVO.
gh_slug() {
  local url
  url=$(git -C "$REPO" remote get-url origin 2>/dev/null || printf '')
  printf '%s' "$url" \
    | sed -e 's#^git@github\.com:#https://github.com/#' \
          -e 's#^ssh://git@github\.com/#https://github.com/#' \
          -e 's#^https://[^/]*github\.com/##' -e 's#\.git$##' \
    | awk -F/ 'NF>=2 {print $(NF-1) "/" $NF}'
}

# Consulta a ref EXATA. `ls-remote --tags origin v1.0.0` casa por PADRAO e
# tambem devolveria `refs/tags/foo/v1.0.0`, deixando passar uma tag divergente.
# Falha de rede NAO pode virar "tag ausente": sai 2 para o chamador recusar.
remote_tag_commit() { # remote_tag_commit <tag>
  local out peeled plain
  if ! git -C "$REPO" remote get-url origin >/dev/null 2>&1; then printf ''; return 0; fi
  out=$(git -C "$REPO" ls-remote origin "refs/tags/$1" "refs/tags/$1^{}" 2>/dev/null) || return 2
  [ -n "$out" ] || { printf ''; return 0; }
  peeled=$(printf '%s\n' "$out" | awk '$2 == "refs/tags/'"$1"'^{}" {print $1; exit}')
  if [ -n "$peeled" ]; then printf '%s' "$peeled"; return 0; fi
  plain=$(printf '%s\n' "$out" | awk '$2 == "refs/tags/'"$1"'" {print $1; exit}')
  printf '%s' "$plain"
}

# ---------------------------------------------------------------------------

cmd_status() {
  resolve_repo
  local info
  info=$(engine detect "$REPO")
  if [ "$JSON" -eq 1 ]; then printf '%s\n' "$info"; return 0; fi
  printf 'repo:      %s\n' "$REPO"
  printf 'branch:    %s   base: %s\n' \
    "$(git -C "$REPO" rev-parse --abbrev-ref HEAD)" "$(default_branch)"
  printf '%s' "$info" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("ledger:    %s (%s entradas)%s" % (
    d["ledger"], d["ledgerCount"],
    "" if d["ledgerPresent"] else "  AUSENTE -> rode: release.sh init"))
print("changelog: %s%s" % (d["changelog"], "" if d["changelogPresent"] else "  AUSENTE"))
print("manifesto: %s" % (d["manifest"] or "nenhum (ok: e opcional)"))
print("convencao: tag=%s%s  releaseName=%s" % (d["tagPrefix"], "X.Y.Z", d["releaseNameStyle"]))
print("corrente:  %s" % (d["currentVersion"] or "-"))
'
  if [ "$(json_field "$info" ledgerPresent)" != "True" ]; then
    printf 'HINT: contrato ausente. Comece com: release.sh init\n'
  fi
  return 0
}

cmd_init() {
  resolve_repo
  say "== release init: $REPO =="
  engine init "$REPO"
}

cmd_gate() {
  resolve_repo
  say "== gate anti-segredo: $REPO =="
  engine scan "$REPO"
}

cmd_check() {
  resolve_repo
  if [ "$JSON" -eq 1 ]; then
    if [ "$STRICT" -eq 1 ]; then engine check "$REPO" --json --strict
    else engine check "$REPO" --json; fi
    return $?
  fi
  printf '== release check: %s ==\n' "$REPO"
  if [ "$STRICT" -eq 1 ]; then engine check "$REPO" --strict; else engine check "$REPO"; fi
}

cmd_prepare() {
  [ -n "$VERSION" ] || die "uso: release.sh prepare X.Y.Z [--repo P]"
  resolve_repo
  say "== release prepare $VERSION: $REPO =="
  # Argumentos vao como argv separado. Acumular numa string e expandir sem aspas
  # permitia injecao: --date "2026-01-01 --release-name outra-coisa".
  set -- prepare "$REPO" "$VERSION"
  [ -n "$DATE_ARG" ] && set -- "$@" --date "$DATE_ARG"
  [ -n "$NAME_ARG" ] && set -- "$@" --release-name "$NAME_ARG"
  engine "$@"
}


main_publish() {
  [ -n "$VERSION" ] || die "uso: release.sh publish X.Y.Z [--repo P] [--dry-run]"
  resolve_repo
  say "== release publish $VERSION$( [ "$DRY_RUN" -eq 1 ] && printf ' (dry-run)' ): $REPO =="

  # 1. contrato, em modo estrito: publicar e o momento de exigir tudo.
  if [ "$JSON" -eq 1 ]; then
    engine check "$REPO" --strict >&2 || { fail "contrato de release nao esta verde"; exit 1; }
  else
    engine check "$REPO" --strict || { fail "contrato de release nao esta verde"; exit 1; }
  fi

  # 2. gate anti-segredo do repo ALVO (passo zero da doutrina).
  if [ "$JSON" -eq 1 ]; then
    engine scan "$REPO" >&2 || { fail "gate anti-segredo barrou a publicacao"; exit 1; }
  else
    engine scan "$REPO" || { fail "gate anti-segredo barrou a publicacao"; exit 1; }
  fi

  # 3. worktree limpa: release publica exatamente o que esta commitado.
  if [ -n "$(git -C "$REPO" status --porcelain)" ]; then
    fail "worktree suja: a release tem que ser exatamente o que esta commitado"
    exit 1
  fi
  say "  ok    worktree limpa"

  # 4. branch base.
  local base branch
  base=$(default_branch)
  branch=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
  if [ "$branch" != "$base" ]; then
    fail "publicacao so na branch base ($base); atual: $branch"
    exit 1
  fi
  say "  ok    branch $base"

  # 5. sincronia com origin (quando ha remote).
  local head remote_head
  head=$(git -C "$REPO" rev-parse HEAD)
  if git -C "$REPO" remote get-url origin >/dev/null 2>&1; then
    if [ "$DRY_RUN" -eq 1 ]; then
      # ls-remote e read-only. `fetch` escreveria refs e FETCH_HEAD, ou seja,
      # mutaria o repo — dry-run nao muta nada.
      remote_head=$(git -C "$REPO" ls-remote origin "refs/heads/$base" 2>/dev/null | awk '{print $1; exit}')
    else
      git -C "$REPO" fetch -q origin "$base" 2>/dev/null || true
      remote_head=$(git -C "$REPO" rev-parse "origin/$base" 2>/dev/null || printf '')
    fi
    if [ -n "$remote_head" ] && [ "$head" != "$remote_head" ]; then
      fail "HEAD difere de origin/$base: sincronize antes de publicar"
      exit 1
    fi
    say "  ok    HEAD == origin/$base"
  else
    say "  WARN  sem remote origin: publicacao apenas local"
  fi

  # 6. a versao precisa existir no ledger e ser a ultima.
  local entry
  entry=$(engine ledger-entry "$REPO" "$VERSION") || {
    fail "$(json_field "$entry" error)"; exit 1; }
  if [ "$(json_field "$entry" isLast)" != "True" ]; then
    fail "$VERSION nao e a ultima entrada do ledger"
    exit 1
  fi
  local tag name notes
  tag=$(json_field "$entry" tag)
  name=$(json_field "$entry" releaseName)
  notes="$REPO/$(json_field "$entry" evidence)"
  # Aceita o mesmo que o check aceita: arquivo OU diretorio de evidencias.
  # Divergencia entre validador e publicador e contrato quebrado.
  if [ -d "$notes" ]; then
    local first
    first=$(find "$notes" -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort | head -1)
    [ -n "$first" ] || { fail "evidencia e diretorio sem .md para corpo da release: $notes"; exit 1; }
    notes="$first"
  fi
  [ -f "$notes" ] || { fail "nota da release ausente: $notes"; exit 1; }

  # 7. TAG E IMUTAVEL. Nunca move, nunca reaponta.
  local local_tag remote_tag
  local_tag=$(git -C "$REPO" rev-list -n 1 "$tag" 2>/dev/null || printf '')
  if [ -n "$local_tag" ] && [ "$local_tag" != "$head" ]; then
    fail "tag $tag ja existe localmente e NAO aponta para HEAD ($local_tag != $head)"
    exit 1
  fi
  remote_tag=$(remote_tag_commit "$tag")
  if [ -n "$remote_tag" ] && [ "$remote_tag" != "$head" ]; then
    fail "tag $tag ja existe em origin e NAO aponta para HEAD ($remote_tag != $head)"
    exit 1
  fi
  say "  ok    tag $tag livre ou ja correta"

  # 8. CI REMOTO: a doutrina promete "CI verde". Promessa sem verificacao e
  #    exatamente o que fazia a promessa ser falsa. So aplica em remote GitHub.
  local checks_state="nao-aplicavel" slug
  if is_github_remote; then
    slug=$(gh_slug)
    [ -n "$slug" ] || { fail "nao consegui derivar owner/repo do remote de $REPO"; exit 1; }
    local pending verdicts
    # Allowlist de conclusoes, nunca denylist: estado novo ou desconhecido
    # (action_required, startup_failure, stale...) tem que BARRAR, nao passar.
    pending=$(gh api "repos/$slug/commits/$head/check-runs" \
      --jq '[.check_runs[] | select(.status != "completed")] | length' 2>/dev/null || printf '')
    verdicts=$(gh api "repos/$slug/commits/$head/check-runs" \
      --jq '[.check_runs[] | select(.status == "completed") | .conclusion] | unique | join(",")' 2>/dev/null || printf '')
    if [ -z "$verdicts" ]; then
      if [ "$ALLOW_NO_CHECKS" -eq 1 ]; then
        say "  WARN  nenhum check remoto em $head; seguindo por --allow-no-remote-checks"
        checks_state="ausente-permitido"
      else
        fail "nenhum check de CI remoto concluido em $head ($slug)."
        fail "Use --allow-no-remote-checks se este repositorio nao tem CI."
        exit 1
      fi
    elif [ -n "$pending" ] && [ "$pending" != "0" ]; then
      fail "ha $pending check(s) remotos ainda em execucao em $head: aguarde"
      exit 1
    else
      local bad
      bad=$(printf '%s' "$verdicts" | tr ',' '\n' \
            | grep -vx 'success\|neutral\|skipped' | tr '\n' ' ' || true)
      if [ -n "$(printf '%s' "$bad" | tr -d ' ')" ]; then
        fail "CI remoto NAO esta verde em $head: conclusoes [$verdicts]"
        exit 1
      fi
      say "  ok    CI remoto verde em $head ($slug): [$verdicts]"
      checks_state="verde"
    fi
  else
    say "  WARN  remote nao e GitHub: verificacao de CI remoto nao se aplica"
  fi

  # Nota do review: ciCommand era detectado, documentado e NUNCA executado.
  # Promessa de "CI local verde" sem executar o CI local e o mesmo defeito que
  # este trabalho existe para corrigir.
  local ci_cmd
  ci_cmd=$(engine detect "$REPO" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("ciCommand") or "")')
  if [ -n "$ci_cmd" ]; then
    if ( cd "$REPO" && eval "$ci_cmd" ) >/dev/null 2>&1; then
      say "  ok    CI local verde: $ci_cmd"
    else
      fail "CI local falhou: $ci_cmd"
      exit 1
    fi
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    say "  dry-run: nenhuma tag criada, nenhuma release publicada."
    emit_summary "$tag" "$name" "$head" "$checks_state" true
    exit 0
  fi

  # 9. publicacao.
  if [ -z "$local_tag" ]; then
    git -C "$REPO" tag -a "$tag" -m "$name"
    say "  ok    tag anotada $tag criada"
  fi
  if [ -z "$remote_tag" ] && git -C "$REPO" remote get-url origin >/dev/null 2>&1; then
    git -C "$REPO" push -q origin "$tag"
    say "  ok    tag $tag publicada em origin"
  fi
  if is_github_remote; then
    slug=$(gh_slug)
    [ -n "$slug" ] || { fail "nao consegui derivar owner/repo do remote de $REPO"; exit 1; }
    if gh release view "$tag" --repo "$slug" >/dev/null 2>&1; then
      gh release edit "$tag" --repo "$slug" --title "$name" --notes-file "$notes" >/dev/null
      say "  ok    GitHub Release atualizada em $slug: $name"
    else
      gh release create "$tag" --repo "$slug" --title "$name" --notes-file "$notes" >/dev/null
      say "  ok    GitHub Release criada em $slug: $name"
    fi
  fi
  emit_summary "$tag" "$name" "$head" "$checks_state" false
}

emit_summary() { # tag name commit checks dryRun
  # Resumo determinista: fecha o ciclo de memoria em UMA escrita, sem busca
  # reconciliatoria depois.
  local payload
  payload=$(python3 -c '
import json,sys
print(json.dumps({
  "topic": "release " + sys.argv[2],
  "repo": sys.argv[1], "version": sys.argv[6], "tag": sys.argv[2],
  "releaseName": sys.argv[3], "commit": sys.argv[4],
  "remoteChecks": sys.argv[5], "dryRun": sys.argv[7] == "true",
}, ensure_ascii=False, indent=2))' \
    "$REPO" "$1" "$2" "$3" "$4" "$VERSION" "$5")
  if [ "$JSON" -eq 1 ]; then
    printf '%s\n' "$payload"
  else
    printf '\n== resumo para memoria (UMA escrita) ==\n%s\n' "$payload"
  fi
}

# ---------------------------------------------------------------------------

need git
need python3
[ -f "$ENGINE" ] || die "engine ausente: $ENGINE"

SUB="${1:-}"
[ $# -gt 0 ] && shift || true
case "$SUB" in
  status)  parse_flags "$@"; cmd_status ;;
  init)    parse_flags "$@"; reject_json init; cmd_init ;;
  gate)    parse_flags "$@"; reject_json gate; cmd_gate ;;
  check)   parse_flags "$@"; cmd_check ;;
  prepare) parse_flags "$@"; reject_json prepare; cmd_prepare ;;
  publish) parse_flags "$@"; need gh; main_publish ;;
  ""|-h|--help|help)
    printf 'uso: release.sh {status|init|gate|check|prepare X.Y.Z|publish X.Y.Z} [--repo P]\n'
    printf '  status   o que o repo tem e o que falta (nunca falha)\n'
    printf '  init     cria CHANGELOG + ledger + docs/release (idempotente)\n'
    printf '  gate     scan anti-segredo da arvore rastreada do repo ALVO\n'
    printf '  check    valida o contrato   [--strict] [--json]\n'
    printf '  prepare  monta changelog + nota + ledger + bump  [--date] [--release-name]\n'
    printf '  publish  guardas + tag imutavel + GitHub Release  [--dry-run] [--json]\n'
    exit 0 ;;
  *) die "subcomando desconhecido: $SUB" ;;
esac
