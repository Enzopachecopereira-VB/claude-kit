---
name: worktree-agent-workflow
description: Use when orienting at session start (are we on the base branch, are there worktrees/branches), creating or removing git worktrees for parallel AI-agent work, closing a merged branch (worktree + local + remote cleanup with absorption proof), or organizing a repo with accumulated branches/worktrees without losing code. Ships a hardened script with fail-closed create/remove/close/organize, absorption-proof cascade and gc-immune backup anchors.
license: proprietary
metadata:
  version: "2.0.0"
  category: "workflow"
  tags: ["git", "worktree", "agents", "safety", "parallel", "cleanup"]
  scripts:
    - path: scripts/worktree.sh
      description: "status/create/remove/close/organize/list/audit. Fail-closed; deletion only with printed proof + anchor. shellcheck-clean."
    - path: scripts/test_worktree.py
      description: "16 testes em repos git temporarios; cobre os vetores de perda medidos."
---

# Worktree Agent Workflow

## Purpose
Padronizar git worktrees para trabalho paralelo de agentes, com isolamento por
construção — e encerrar o ciclo: pós-merge, a limpeza (worktree, branch local,
branch remota) é parte da tarefa, com prova de absorção impressa e âncora de
recuperação gravada antes de qualquer deleção. Nada se perde por construção.

## When to use / when NOT to use
- Use when:
  - orientar-se no início da sessão (`status`)
  - iniciar tarefa numa branch nova ou paralela (`create`)
  - encerrar branch mergeada — worktree, local e remota (`close`)
  - chegar num repo com branches/worktrees acumulados (`organize`)
- Do NOT use when:
  - o trabalho é direto na branch base do principal
  - o diretório não é um repositório git

## Convention (parametrizável)
- `WT_BASE` — base isolada. Default: `~/wt`. Fora de qualquer diretório com
  múltiplos repositórios.
- Caminho final: `$WT_BASE/<repo>/<branch-slug>` (`/` -> `-`).

## Invariantes (inegociáveis)
- Worktrees adicionais SEMPRE sob `$WT_BASE/<repo>/<branch-slug>`; nunca como
  irmão de outro repositório. Um agente por worktree, uma branch por agente.
- **Deleção exige prova impressa + âncora prévia.** A cascata de provas:
  `ancestral` (merge-base) → `patch-id` (`git cherry`) → `pr-merged` (gh; tip
  local == head mergeado do PR). Sem prova = preservar e reportar. `branch -D`
  à mão continua proibido — o caminho provado do `close` é o único que o usa.
- Âncora antes de apagar: `refs/backups/<nome>-<data>` (imune a gc).
  Restaurar: `git branch <nome> <ref>`. Listar: `git for-each-ref refs/backups`.
- Nunca `worktree remove --force`. Worktree sujo/untracked aborta (git nativo).
- HEAD detached com commit fora de qualquer branch é ancorado antes do remove
  (vetor de perda silenciosa medido).
- Nenhum comando pode renomear/mover o diretório-pai de um repositório.

## Scripts (hardened — preferir a git cru)
      WT_BASE="${WT_BASE:-$HOME/wt}"
      scripts/worktree.sh status   [repo]              # orientacao + audit
      scripts/worktree.sh create   <branch> [repo]     # cria + imprime o cd
      scripts/worktree.sh remove   <path>              # so worktree (branch fica)
      scripts/worktree.sh close    <path|branch> [--keep-remote]
      scripts/worktree.sh organize [--apply] [--deep]  # triagem; --apply age nas provadas
      scripts/worktree.sh list     [repo]
      scripts/worktree.sh audit    [repo]              # rc!=0 = pendencia real

## Process
0. **Orientar:** `status`. Na base e a tarefa é feature/fix? `create` — não
   trabalhe na base.
1. **Criar e trocar a sessão:** executar o `cd` impresso; operar dali.
2. **Trabalhar:** commits atômicos; nunca commit na base.
3. **Integrar:** PR; merge com CI verde.
4. **Encerrar (obrigatório):** `close <branch>` — na ordem: prova → âncora →
   worktree → branch local → branch remota → `fetch --prune`. Idempotente.
5. **Conferir:** `audit` limpo. Tarefa não conclui com audit acusando.

## Organizar repo bagunçado (sem perder nada)
`organize` = inventário (worktrees, branches, stashes; `fetch --prune` antes,
porque tracking refs obsoletas mentem) → classificação → relatório:

- `ABSORVIDA` prova impressa → única classe onde `--apply` age (via `close`)
- `UNICA` trabalho sem prova → preservar (push/PR); nunca tocada
- `SUJO` worktree com mudanças → decisão humana
- `EM-USO` branch no tip da base → workspace pronto, não é sobra
- `DESCONHECIDA` detached/estado estranho → reportar

`--deep` varre `fsck --unreachable` por stashes perdidos (dropados/pop) e
imprime o comando de resgate. Default é relatório (fail-closed); agir exige
`--apply` explícito.

## Guardrails
- Durante organização, git cru destrutivo é proibido: `clean -fd`,
  `reset --hard`, `stash drop`, `worktree remove --force`, `push --delete`
  fora do `close`. A organização usa só os verbos do script.
- Exit code se lê da fonte — `cmd | tail` devolve o exit do tail (falso-verde).
- Se houver tripwire de rename estrutural nos roots, não desativá-lo.

## Outputs
- Worktree em `$WT_BASE/<repo>/<branch-slug>`, sessão operando a partir dele.
- Pós-merge: worktree/branch local/branch remota removidos com prova impressa
  e âncora `refs/backups/`; `audit` limpo.
- Repo bagunçado: relatório classificado; ação só sobre o provado.
