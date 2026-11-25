# Atomic Commits

Cada commit = **uma mudança lógica coesa**. Reverter o commit deve fazer sentido em isolado.

## Por que importa

- `git bisect` funciona (encontra commit que quebrou)
- Code review fica focado (1 ideia por commit)
- Revert cirúrgico (`git revert <hash>`) sem efeitos colaterais
- CHANGELOG limpo e SemVer mais fácil de auditar

## Sinais de commit NÃO-atômico

- Mensagem usa "e", "+", "também" ("fix bug + add tests + refactor")
- Diff muda múltiplos módulos sem relação
- > 500 linhas modificadas (provável mistura)
- Mistura `feat` + `fix` + `refactor` no mesmo commit

## Como fazer atômico — staging seletivo (non-interactive)

Stage por caminho explícito em vez da mudança inteira de uma vez:

```bash
git add caminho/especifico/arquivo.ts    # stage só esse arquivo
git add caminho/a.ts caminho/b.ts        # múltiplos arquivos relacionados
git commit -m "feat: parte A"
git add caminho/c.ts
git commit -m "fix: parte B"
```

Quando os hunks não-relacionados estão **dentro do mesmo arquivo**, separe via patch editado (sem prompt interativo):

```bash
git diff -- arquivo.ts > /tmp/hunk.patch   # gera patch do diff do arquivo
# edita /tmp/hunk.patch removendo os hunks que NÃO entram neste commit
git apply --cached /tmp/hunk.patch         # aplica só o que sobrou, direto no index
git commit -m "feat: hunk relevante"
git add arquivo.ts                         # resto do arquivo vai no próximo commit
git commit -m "fix: hunk restante"
```

> `git add -p` / `git add --patch` fazem essa mesma seleção de forma interativa
> (prompt `Stage this hunk [y,n,q,a,d,s,e,?]?`). São **banidos no shell do
> agente**: não há TTY pra responder ao prompt, o comando trava até timeout.
> Use os equivalentes acima. Para humanos operando fora do harness, `git add -p`
> continua sendo o jeito mais rápido.

## Split de commit já feito

Cometeu commit grande, quer separar:

```bash
git reset HEAD~                # desfaz o commit, mantém as mudanças staged
git add caminho/parte-a/       # re-stage por partes (caminhos explícitos)
git commit -m "feat: parte A"
git add caminho/parte-b/
git commit -m "fix: parte B"
```

## Reescrever histórico recente — non-interactive

`git rebase -i` abre um editor (`vi`/`nano`) esperando edição manual da
todo-list de picks — **banido no shell do agente** (sem TTY, o comando trava
até timeout). Os mesmos resultados (reorder, squash, fixup, reword, drop) são
alcançáveis sem editor interativo:

### Squash/fixup automático — `--autosquash`

```bash
git commit -m "wip: rascunho"
# ... mais commits depois ...
git commit --fixup=<hash-do-commit-alvo>          # marca como fixup do commit alvo
GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash HEAD~5
```

`GIT_SEQUENCE_EDITOR=:` troca o editor por um no-op (`:` sempre sai com
sucesso sem abrir nada) — o rebase aplica o plano de `--autosquash`
automaticamente, sem prompt.

### Editar o plano programaticamente (reorder, drop, reword)

Quando o objetivo não é só autosquash, gere a edição do plano via script em vez
de abrir editor:

```bash
# Troca 'pick' por 'drop' na 2ª linha do plano de HEAD~3
GIT_SEQUENCE_EDITOR="sed -i '' '2s/^pick/drop/'" git rebase -i HEAD~3
```

### Mover branch inteira pra outra base — `rebase --onto`

```bash
git rebase --onto main old-base feature-x   # replaya feature-x sobre main, descartando old-base..main
```

### Colapsar em um commit limpo — `reset --soft`

Quando o objetivo é "1 commit Conventional por unidade lógica" e não importa
preservar os commits WIP intermediários:

```bash
git reset --soft HEAD~5      # desfaz os últimos 5 commits, mantém tudo staged
git commit -m "feat: unidade lógica completa"
```

> As formas acima cobrem os mesmos objetivos de um `git rebase -i` manual. A
> forma interativa continua válida para humanos fora do harness; o agente
> sempre usa `GIT_SEQUENCE_EDITOR` fixo ou os comandos não-interativos
> equivalentes.

## Workflow recomendado pra feature branch

```
1. Trabalha livre na branch, commits WIP livres (`git commit --fixup=<hash>` quando for corrigir um commit anterior)
2. Antes de abrir PR:
   GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash main
   → aplica os fixups e deixa commits Conventional limpos, sem editor
3. git push --force-with-lease
4. Abre PR — revisor vê commits limpos
```

`--force-with-lease` é seguro: só sobrescreve se ninguém mais commitou em cima.

## Commits muito grandes — sinal de design ruim

Se você PRECISA de commit gigante, geralmente significa:
- Feature mal recortada (split em sub-tickets)
- Refactor + feature misturados (refactor primeiro como commit separado)
- Falta de planejamento

## Anti-patterns

- ❌ `git commit -am "WIP"` repetidamente sem squash depois
- ❌ Commit que mistura mudança de produção + reformat código (separar)
- ❌ Commit que mistura feature comum com preparação de release (faça PR/commit de release separado)
- ❌ Reverter commit grande no PR review (split antes)

## Comando útil — preview do que vai commitar

```bash
git diff --staged              # ver o que está staged
git diff --staged --stat       # resumo
git status -s                  # short status
```

## Ferramentas que ajudam (uso humano, fora do shell do agente)

- **lazygit** — TUI pra Git, facilita stage hunk-by-hunk
- **fugitive.vim** ou **vim-fugitive** — pra usuários vim
- **GitLens** (VSCode) — diff inline
- VSCode "Source Control" → click "+" em hunks individuais
