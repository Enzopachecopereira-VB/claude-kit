# Git Worktrees — ver skill worktree-agent-workflow

Doutrina de worktrees não vive mais neste arquivo. Dona: skill
**worktree-agent-workflow** (`~/.agents/skills/worktree-agent-workflow/`) +
módulo sempre-ativo `harness/20-worktrees.md`.

## Orientação (rodar no início da sessão)

    ~/.agents/skills/worktree-agent-workflow/scripts/worktree.sh status

## Invariantes inegociáveis

- Worktrees adicionais SOMENTE sob `$WT_BASE/<repo>/<branch-slug>` (default
  `~/wt`) — nunca como irmão de outro repositório.
- Nunca `worktree remove --force`, nunca `branch -D` à mão — deleção provada
  é papel do `worktree.sh close`. Nunca tocar fora de `$WT_BASE`.

## Por que este arquivo não tem mais o procedimento

Fonte única de verdade evita divergência: a convenção anterior descrita aqui
(sufixo `.wt/` ao lado do clone) contradizia a doutrina do harness
(`$WT_BASE` isolado), então o procedimento completo passou a viver só na skill
**worktree-agent-workflow** — este arquivo fica como ponteiro.
