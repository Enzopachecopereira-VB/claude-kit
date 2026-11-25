#!/usr/bin/env bash
# Portable, defensive git-worktree helper for parallel agent workflows.
# No hardcoded paths or usernames. Isolated base = $WT_BASE (default ~/wt).
#
# Subcommands:
#   status  [repo]                  orientation: role/branch/dirty/worktrees/audit
#   create  <branch> [repo]         create worktree under $WT_BASE, print cd hint
#   remove  <path>                  remove worktree ONLY under $WT_BASE (branch kept;
#                                   detached orphan commits are anchored first)
#   close   <path|branch> [--keep-remote]
#                                   post-merge ceremony: proof -> anchor -> worktree
#                                   -> local branch -> remote branch -> prune
#   organize [--apply] [--deep] [repo]
#                                   inventory -> classify -> (--apply: close proven)
#   list    [repo]                  git worktree list
#   audit   [repo]                  rc!=0 if worktree outside base OR absorbed branch alive
#
# PRINCIPLES (hard-won; see project memory):
# - Fail-closed: no proof, no deletion. Every deletion PRINTS its proof and anchor.
# - Absorption proofs, in order: ancestral (merge-base) -> patch-id (git cherry) ->
#   pr-merged (gh; local tip MUST equal the merged PR head). Rebase/squash-merged
#   branches are invisible to `git branch --merged`; ancestry alone is a false negative.
# - Anchor before delete: refs/backups/<name>-<date> is gc-immune. Recover with
#   `git branch <name> <ref>`; list with `git for-each-ref refs/backups`.
# - Detached HEAD with commits outside any branch is silently lost by
#   `git worktree remove` (measured): anchor first, always.
# - Stale remote-tracking refs lie (`branch -r` shows branches the server already
#   deleted): fetch --prune before judging remote state.
set -euo pipefail

WT_BASE="${WT_BASE:-$HOME/wt}"

die() { printf 'worktree: %s\n' "$*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }

canon() {
  if [ -d "$1" ]; then (cd "$1" && pwd -P); else
    local d b; d=$(dirname -- "$1"); b=$(basename -- "$1")
    [ -d "$d" ] || die "diretorio inexistente: $d"
    printf '%s/%s\n' "$(cd "$d" && pwd -P)" "$b"
  fi
}

repo_root() { git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null || die "nao e repo git: ${1:-.}"; }
main_worktree() { git -C "$1" worktree list --porcelain | awk '/^worktree /{print $2; exit}'; }

default_branch() {
  local d
  d=$( { git -C "$1" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true; } | sed 's#^origin/##' )
  [ -n "$d" ] && { printf '%s' "$d"; return; }
  local c; for c in main master; do
    git -C "$1" show-ref --verify --quiet "refs/heads/$c" && { printf '%s' "$c"; return; }
  done
  printf ''
}

slug() {
  local s
  s=$(printf '%s' "$1" | LC_ALL=C tr -c 'A-Za-z0-9._-' '-')
  s=$(printf '%s' "$s" | sed 's#-\{2,\}#-#g; s#\.\{2,\}#.#g; s#^[-.]*##; s#[-.]*$##')
  printf '%s' "$s"
}

under_base() {
  local b; b=$(canon "$WT_BASE")
  [ "$b" != "$(canon "$HOME")" ] || die "WT_BASE nao pode ser \$HOME"
  case "$(canon "$1")/" in "$b"/*) return 0 ;; *) return 1 ;; esac
}

is_github_remote() {
  local url; url=$(git -C "$1" remote get-url origin 2>/dev/null || printf '')
  case "$url" in *github.com*) return 0 ;; *) return 1 ;; esac
}

dirty_count() { git -C "$1" status --porcelain | awk 'END{print NR+0}'; }

branch_worktree() { # branch_worktree <repo> <branch> -> worktree path or empty
  git -C "$1" worktree list --porcelain | awk -v b="refs/heads/$2" '
    /^worktree /{w=$2} /^branch /{if ($2==b) print w}'
}

# ---------------------------------------------------------------------------
# Absorption cascade. is_absorbed <repo> <base> <ref> [local]
# Echoes the proof that authorizes deletion: "ancestral" | "patch-id" |
# "pr-merged #N". 4th arg "local" restricts to offline proofs (audit).
# Fail-closed: any doubt (bad ref, cherry failure, PR head != tip) -> rc 1.
# ---------------------------------------------------------------------------
is_absorbed() {
  local repo="$1" base="$2" ref="$3" net="${4:-net}"
  [ -n "$base" ] || return 1
  git -C "$repo" rev-parse -q --verify "$ref^{commit}" >/dev/null 2>&1 || return 1
  # 1. ancestral: ref ja contida na base (merge normal / ff)
  if git -C "$repo" merge-base --is-ancestor "$ref" "$base" 2>/dev/null; then
    printf 'ancestral'; return 0
  fi
  # 2. patch-id: todo commit exclusivo tem patch equivalente na base (rebase remoto)
  local out plus
  if out=$(git -C "$repo" cherry "$base" "$ref" 2>/dev/null); then
    plus=$(printf '%s\n' "$out" | grep -c '^+' || true)
    if [ "$plus" -eq 0 ] 2>/dev/null; then printf 'patch-id'; return 0; fi
  fi
  # 3. estado do PR (autoritativo p/ squash); exige tip local == head mergeado
  if [ "$net" != "local" ] && is_github_remote "$repo" && command -v gh >/dev/null 2>&1; then
    local br tip line prnum prhead
    br=${ref#origin/}
    tip=$(git -C "$repo" rev-parse "$ref" 2>/dev/null) || return 1
    line=$( (cd "$repo" && gh pr list --head "$br" --state merged \
      --json number,headRefOid \
      --jq 'if length>0 then "\(.[0].number) \(.[0].headRefOid)" else empty end') 2>/dev/null ) || line=""
    if [ -n "$line" ]; then
      prnum=${line%% *}; prhead=${line##* }
      if [ "$prhead" = "$tip" ]; then printf 'pr-merged #%s' "$prnum"; return 0; fi
    fi
  fi
  return 1
}

# ---------------------------------------------------------------------------
# Anchor: gc-immune backup ref before any deletion. Prints the ref created
# (or reused when it already points to the same sha).
# ---------------------------------------------------------------------------
anchor_ref() { # anchor_ref <repo> <name> <sha>
  local repo="$1" name="$2" sha="$3" ref cur n=1
  ref="refs/backups/${name}-$(date +%Y%m%d)"
  while cur=$(git -C "$repo" rev-parse -q --verify "$ref" 2>/dev/null); do
    [ "$cur" = "$sha" ] && { printf '%s' "$ref"; return 0; }
    ref="refs/backups/${name}-$(date +%Y%m%d)-$n"; n=$((n+1))
  done
  git -C "$repo" update-ref "$ref" "$sha"
  printf '%s' "$ref"
}

# Detached HEAD whose commit is outside every branch would be silently lost
# by worktree removal (measured). Anchor it before touching the worktree.
guard_detached() { # guard_detached <repo> <wtpath>
  local sha contains ref
  git -C "$2" symbolic-ref -q HEAD >/dev/null 2>&1 && return 0
  sha=$(git -C "$2" rev-parse HEAD)
  contains=$(git -C "$1" branch --contains "$sha" --format='%(refname)' 2>/dev/null | head -1)
  if [ -z "$contains" ]; then
    ref=$(anchor_ref "$1" "detached-$(basename -- "$2")" "$sha")
    say "AVISO: HEAD detached $(git -C "$1" rev-parse --short "$sha") fora de qualquer branch — ancorado em $ref"
  fi
}

# ---------------------------------------------------------------------------

cmd_status() {
  local start repo cur main role branch def dirty nb
  start="${1:-.}"; repo=$(repo_root "$start")
  cur=$(canon "$(git -C "$start" rev-parse --show-toplevel)")
  main=$(canon "$(main_worktree "$repo")")
  role=MAIN; [ "$cur" != "$main" ] && role=LINKED
  branch=$(git -C "$repo" rev-parse --abbrev-ref HEAD)
  def=$(default_branch "$repo")
  dirty=$(dirty_count "$repo")
  nb=$(git -C "$repo" for-each-ref --format='%(refname:short)' refs/heads | awk 'END{print NR+0}')
  printf 'repo:      %s\n' "$repo"
  printf 'cwd:       %s (%s)\n' "$role" "$cur"
  printf 'branch:    %s   default: %s   dirty: %s   local-branches: %s\n' "$branch" "${def:-?}" "$dirty" "$nb"
  printf 'worktrees:\n'; git -C "$repo" worktree list | sed 's/^/  /'
  cmd_audit "$repo" || true
  if [ "$role" = MAIN ] && [ -n "$def" ] && [ "$branch" = "$def" ]; then
    printf 'HINT: worktree principal na branch base. Para feature/fix use: worktree.sh create <branch>\n'
  fi
}

cmd_create() {
  local branch repo name sl dest
  branch="${1:?uso: create <branch> [repo]}"; repo=$(repo_root "${2:-.}")
  git -C "$repo" check-ref-format --branch "$branch" >/dev/null 2>&1 || die "branch invalida: $branch"
  name=$(basename -- "$repo"); sl=$(slug "$branch")
  [ -n "$sl" ] && [ "$sl" != "." ] && [ "$sl" != ".." ] || die "slug invalido para: $branch"
  mkdir -p -- "$WT_BASE/$name"; dest="$WT_BASE/$name/$sl"
  under_base "$dest" || die "dest fora de WT_BASE ($WT_BASE): $dest"
  [ -e "$dest" ] && die "dest ja existe: $dest"
  if git -C "$repo" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$repo" worktree add -- "$dest" "$branch"
  else
    git -C "$repo" worktree add -b "$branch" -- "$dest"
  fi
  printf 'OK  worktree: %s\n' "$dest"
  printf 'NEXT (troque a sessao): cd %q\n' "$dest"
}

cmd_remove() {
  local target="${1:-}" t main cmain
  [ -n "$target" ] || die "uso: remove <path-do-worktree>"
  [ $# -le 1 ] || die "argumento extra: $2 (delecao de branch e papel do 'close')"
  t=$(canon "$target")
  under_base "$t" || die "RECUSADO: alvo fora de WT_BASE ($WT_BASE): $t"
  git -C "$t" rev-parse --git-dir >/dev/null 2>&1 || die "nao e worktree git: $t"
  main=$(main_worktree "$t"); cmain=$(canon "$main")
  [ "$t" = "$cmain" ] && die "RECUSADO: e o worktree principal"
  guard_detached "$cmain" "$t"
  git -C "$cmain" worktree remove -- "$t"   # git recusa worktree sujo/untracked (nao forcamos)
  git -C "$cmain" worktree prune
  printf 'removido worktree: %s (branch preservada)\n' "$t"
}

# ---------------------------------------------------------------------------
# close: cerimonia canonica pos-merge. Idempotente e fail-closed.
# ordem: prova -> ancora -> worktree -> branch local -> branch remota -> prune
# ---------------------------------------------------------------------------
cmd_close() {
  local target="" keep_remote=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --keep-remote) keep_remote=1 ;;
      -*) die "flag desconhecida: $1" ;;
      *) if [ -z "$target" ]; then target="$1"; else die "argumento extra: $1"; fi ;;
    esac; shift
  done
  [ -n "$target" ] || die "uso: close <path-do-worktree|branch> [--keep-remote]"

  local repo cmain base br wtpath d proof tip ref rproof
  repo=$(repo_root .); cmain=$(canon "$(main_worktree "$repo")")
  base=$(default_branch "$cmain"); [ -n "$base" ] || die "branch base indetectavel"
  git -C "$cmain" fetch -qp origin 2>/dev/null || true   # visao fresca; offline tolerado

  if [ -d "$target" ]; then
    wtpath=$(canon "$target")
    br=$(git -C "$wtpath" rev-parse --abbrev-ref HEAD 2>/dev/null) || die "nao e worktree git: $wtpath"
    [ "$br" != "HEAD" ] || die "worktree detached — use: remove $wtpath"
  else
    br="$target"; wtpath=$(branch_worktree "$cmain" "$br")
  fi
  [ "$br" != "$base" ] || die "RECUSADO: close da branch base"

  if [ -n "$wtpath" ]; then
    [ "$wtpath" != "$cmain" ] || die "RECUSADO: worktree principal"
    under_base "$wtpath" || die "RECUSADO: worktree fora de WT_BASE: $wtpath"
    d=$(dirty_count "$wtpath")
    [ "$d" -eq 0 ] || die "worktree sujo ($d itens) — commit/stash antes; NADA removido"
  fi

  if ! git -C "$cmain" show-ref --verify --quiet "refs/heads/$br"; then
    [ -z "$wtpath" ] || die "branch '$br' inexistente mas worktree presente ($wtpath) — estado inconsistente, resolva manualmente"
    say "nada a fazer: branch '$br' ja nao existe localmente"
  else
    proof=$(is_absorbed "$cmain" "$base" "$br") \
      || die "SEM PROVA de absorcao para '$br' em $base — nada removido. Triagem: worktree.sh organize"
    tip=$(git -C "$cmain" rev-parse "$br")
    ref=$(anchor_ref "$cmain" "$(slug "$br")" "$tip")
    if [ -n "$wtpath" ]; then
      git -C "$cmain" worktree remove -- "$wtpath"
      git -C "$cmain" worktree prune
      say "worktree removido: $wtpath"
    fi
    # prova exigida acima; -d cobre o caso ancestral, -D e o caminho provado
    git -C "$cmain" branch -d -- "$br" 2>/dev/null || git -C "$cmain" branch -D -- "$br"
    say "branch local removida: $br  prova: $proof  ancora: $ref"
  fi

  if [ "$keep_remote" -eq 0 ] && git -C "$cmain" remote get-url origin >/dev/null 2>&1; then
    if git -C "$cmain" ls-remote --exit-code --heads origin "refs/heads/$br" >/dev/null 2>&1; then
      if rproof=$(is_absorbed "$cmain" "$base" "origin/$br"); then
        git -C "$cmain" push -q origin --delete "$br"
        say "branch remota removida: origin/$br  prova: $rproof"
      else
        say "branch remota PRESERVADA (sem prova de absorcao): origin/$br"
      fi
    else
      say "branch remota: ja ausente no servidor"
    fi
    git -C "$cmain" fetch -qp origin 2>/dev/null || true
  fi
  say "close concluido: $br"
}

# ---------------------------------------------------------------------------
# organize: inventario -> classificacao -> (--apply) acao so sobre provadas.
# Classes: ABSORVIDA (prova impressa) | UNICA (trabalho sem prova: preservar)
#          SUJO (worktree com mudancas: decisao humana) | DESCONHECIDA
#          (detached / base indetectavel)
# ---------------------------------------------------------------------------
cmd_organize() {
  local apply=0 deep=0 start="."
  while [ $# -gt 0 ]; do
    case "$1" in
      --apply) apply=1 ;;
      --deep)  deep=1 ;;
      -*) die "flag desconhecida: $1" ;;
      *) start="$1" ;;
    esac; shift
  done
  local repo cmain base to_close="" rc=0
  repo=$(repo_root "$start"); cmain=$(canon "$(main_worktree "$repo")")
  base=$(default_branch "$cmain")
  git -C "$cmain" fetch -qp origin 2>/dev/null || true
  git -C "$cmain" worktree prune 2>/dev/null || true
  say "== organize: $cmain (base: ${base:-?}) =="

  say "-- worktrees --"
  local w cw b d proof ahead
  while IFS= read -r w; do
    cw=$(canon "$w")
    b=$(git -C "$cw" rev-parse --abbrev-ref HEAD 2>/dev/null || printf '?')
    d=$(dirty_count "$cw")
    if [ "$cw" = "$cmain" ]; then
      say "  [PRINCIPAL]    $cw ($b) dirty=$d"
    elif [ "$b" = "HEAD" ]; then
      say "  [DESCONHECIDA] $cw @$(git -C "$cw" rev-parse --short HEAD) detached dirty=$d — 'remove' ancora orfaos"
    elif [ "$d" -gt 0 ]; then
      say "  [SUJO]         $cw ($b) dirty=$d — decisao humana antes de qualquer acao"
    elif [ -n "$base" ] && [ "$(git -C "$cmain" rev-parse "$b")" = "$(git -C "$cmain" rev-parse "$base")" ]; then
      # tip exato da base: workspace novo/pronto, nao sobra de merge
      # (indistinguivel por refs de um ff recem-mergeado; fail-closed no auto).
      say "  [EM-USO]       $cw ($b) no tip da base — workspace pronto"
    elif [ -n "$base" ] && proof=$(is_absorbed "$cmain" "$base" "$b"); then
      say "  [ABSORVIDA]    $cw ($b) prova: $proof -> worktree.sh close $b"
      to_close="$to_close $b"
    else
      ahead=$(git -C "$cmain" rev-list --count "${base:-HEAD}..$b" 2>/dev/null || printf '?')
      say "  [UNICA]        $cw ($b) ahead-de-${base:-?}=$ahead — preservar (push/PR)"
    fi
  done < <(git -C "$cmain" worktree list --porcelain | awk '/^worktree /{print $2}')

  say "-- branches locais sem worktree --"
  local any=0 up
  for b in $(git -C "$cmain" for-each-ref --format='%(refname:short)' refs/heads); do
    [ "$b" = "$base" ] && continue
    [ -n "$(branch_worktree "$cmain" "$b")" ] && continue
    any=1
    if [ -n "$base" ] && proof=$(is_absorbed "$cmain" "$base" "$b"); then
      say "  [ABSORVIDA]    $b  prova: $proof -> worktree.sh close $b"
      to_close="$to_close $b"
    elif [ -z "$base" ]; then
      say "  [DESCONHECIDA] $b  base indetectavel"
    else
      up=$(git -C "$cmain" for-each-ref --format='%(upstream:short)%(upstream:track)' "refs/heads/$b")
      ahead=$(git -C "$cmain" rev-list --count "$base..$b" 2>/dev/null || printf '?')
      say "  [UNICA]        $b  upstream: ${up:-nenhum}  ahead-de-$base=$ahead — preservar"
    fi
  done
  [ "$any" -eq 0 ] && say "  (nenhuma)"

  say "-- stashes --"
  if [ -n "$(git -C "$cmain" stash list 2>/dev/null)" ]; then
    git -C "$cmain" stash list | sed 's/^/  /'
  else
    say "  (nenhum)"
  fi
  if [ "$deep" -eq 1 ]; then
    say "-- stashes perdidos (fsck --unreachable) --"
    local s m found=0
    while IFS= read -r s; do
      m=$(git -C "$cmain" log -1 --format='%s' "$s" 2>/dev/null || printf '')
      case "$m" in
        "WIP on "*|"On "*)
          say "  perdido: $(git -C "$cmain" rev-parse --short "$s") \"$m\" -> git stash apply $s"; found=1 ;;
      esac
    done < <(git -C "$cmain" fsck --unreachable 2>/dev/null | awk '/commit/{print $3}')
    [ "$found" -eq 0 ] && say "  (nenhum)"
  fi

  if [ "$apply" -eq 1 ]; then
    say "-- apply (so classe ABSORVIDA) --"
    local closed=0
    for b in $to_close; do
      if ( cd "$cmain" && cmd_close "$b" ); then closed=$((closed+1)); else
        say "  FALHOU close: $b (preservado)"; rc=1
      fi
    done
    [ -z "$to_close" ] && say "  (nada a aplicar)"
    say "-- apply: $closed close(s) concluido(s) --"
  elif [ -n "$to_close" ]; then
    say "AVISO: relatorio apenas (fail-closed). Para agir sobre as ABSORVIDAS: worktree.sh organize --apply"
  fi
  cmd_audit "$cmain" || rc=1
  return "$rc"
}

cmd_list() { git -C "$(repo_root "${1:-.}")" worktree list; }

cmd_audit() {
  local repo wbase main cw w rc=0 def b proof
  repo=$(repo_root "${1:-.}")
  wbase=$(canon "$WT_BASE" 2>/dev/null || printf '%s' "$WT_BASE")
  main=$(canon "$(main_worktree "$repo")")
  while IFS= read -r w; do
    cw=$(canon "$w"); [ "$cw" = "$main" ] && continue
    case "$cw/" in "$wbase"/*) : ;; *) printf 'FORA-DE-BASE: %s\n' "$cw"; rc=1 ;; esac
  done < <(git -C "$repo" worktree list --porcelain | awk '/^worktree /{print $2}')
  def=$(default_branch "$repo")
  if [ -n "$def" ]; then
    for b in $(git -C "$repo" for-each-ref --format='%(refname:short)' refs/heads); do
      [ "$b" = "$def" ] && continue
      if proof=$(is_absorbed "$repo" "$def" "$b" local); then
        # workspace novo/pronto (tip exato da base + worktree anexado): nao acusar
        if [ "$(git -C "$repo" rev-parse "$b")" = "$(git -C "$repo" rev-parse "$def")" ] \
           && [ -n "$(branch_worktree "$repo" "$b")" ]; then continue; fi
        printf 'ABSORVIDA-VIVA: %s (prova local: %s) -> worktree.sh close %s\n' "$b" "$proof" "$b"; rc=1
      fi
    done
  fi
  [ "$rc" -eq 0 ] && printf 'OK: worktrees sob %s; nenhuma branch absorvida viva\n' "$wbase"
  return "$rc"
}

case "${1:-}" in
  status)   shift; cmd_status   "$@" ;;
  create)   shift; cmd_create   "$@" ;;
  remove)   shift; cmd_remove   "$@" ;;
  close)    shift; cmd_close    "$@" ;;
  organize) shift; cmd_organize "$@" ;;
  list)     shift; cmd_list     "$@" ;;
  audit)    shift; cmd_audit    "$@" ;;
  *) die "uso: worktree.sh {status|create <branch>|remove <path>|close <path|branch> [--keep-remote]|organize [--apply] [--deep]|list|audit} [repo]" ;;
esac
