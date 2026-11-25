---
name: git-contribution
description: >-
  Use when contributing to a third-party or external git repository on any host
  (GitHub, GitLab, Gitea, Bitbucket, …) — filing or replying to an issue,
  diagnosing a suspected bug, opening a PR/MR, or responding to a maintainer's
  review. Enforces an explicit account-confirmation gate, mandatory secret/PII
  sanitization before any public post, and a senior-engineer, courteous en-US
  voice. Also enforces attribution etiquette: map who is who before writing, ask
  whether someone already claimed the work, credit the reporter explicitly, and
  cite adjacent issues/PRs. All public artifacts are en-US.
license: proprietary
metadata:
  version: "1.1.0"
  category: "workflow"
  tags: ["git", "contribution", "issue", "pull-request", "merge-request", "code-review", "communication", "safety", "attribution", "etiquette"]
  scripts:
    - path: scripts/gh-post.sh
      description: "Fail-closed reference helper for the GitHub case (uses gh CLI): requires an explicit account, runs the mechanical deny-class scan, posts, restores prior active account. shellcheck-clean. Adapt for GitLab/Gitea/Bitbucket."
---

# Git Contribution

## Purpose
Padronizar a atuação em repositórios git de terceiros (externos), em qualquer host, com postura de engenheiro sênior: diagnóstico honesto, tom cortês e colaborativo, e disciplina operacional que evita dois danos irreversíveis num repo público — **postar com a identidade errada** e **vazar segredos/dados internos** — mais o dano reputacional que não tem rollback social: **passar por cima do trabalho de quem chegou antes**. Vale para OSS ou proprietário, GitHub ou não. Todo artefato público é em **en-US**.

## When to use / when NOT to use
- Use when:
  - abrir ou responder issue em repo de terceiro
  - investigar um bug suspeito em dependência/ferramenta de terceiro
  - abrir PR/MR ou responder review de um mantenedor
- Do NOT use when:
  - trabalho em repo próprio/privado da equipe (use `git-pro`)
  - redação genérica sem alvo de repo

## GATE #1 — Confirmação de perfil (inegociável, precede QUALQUER escrita pública)
Antes de qualquer ação que escreva no repo remoto (comentário, PR, review, reação):
1. Listar as identidades disponíveis e a ativa: `gh auth status`.
2. **Perguntar explicitamente ao usuário com qual perfil postar.** Nunca assumir a conta ativa como default. Em máquinas com múltiplas contas, a conta ativa raramente é a certa para contribuição externa.
3. Só prosseguir com o handle confirmado. Toda operação de escrita passa o handle **explicitamente**; nunca inferir da sessão.
4. Ao terminar, **restaurar a conta ativa anterior** (não deixar a conta trocada como efeito colateral).

> Postar com a conta errada num repo público é vazamento de identidade irreversível — não há "desfazer". Este gate vem antes de tudo.

## GATE #2 — Sanitização antes de qualquer post público
Nenhum texto vai para um repo público sem passar pelo scanner fail-closed e por julgamento humano:
- O `scripts/gh-post.sh --check-only` prova mecanicamente apenas estas classes: caminhos home POSIX/Windows, `~/` e `$HOME/`, hostnames `.local`/`.lan`/`.internal` e saída `hostname:`, e-mail, tokens GitHub/Slack/AWS/Anthropic/Stripe (`sk_live_`), Bearer genérico, JWT, PEM private key, `ses_*` e timestamp absoluto com data+hora. Data ISO sem hora (`2026-07-24`) é permitida pelo scanner.
- Nomes internos de projeto/repo só são provados mecanicamente quando o repo passa padrões em `GH_POST_DENY_EXTRA` (lista de EREs separada por newline). Ex.: `GH_POST_DENY_EXTRA=$'codename-1\nrepo-interno' scripts/gh-post.sh --check-only body.md`.
- O script **não prova** username real sem contexto de path, hostnames arbitrários sem sufixo/linha `hostname:`, nem nomes internos não declarados em `GH_POST_DENY_EXTRA`; esses itens exigem revisão do agente antes de postar.
- Paths → placeholders (`$PARENT`, `<repo>`); tempos → offsets relativos (`T+Ns`); nomes internos → genéricos. Se o scanner encontrar qualquer classe, **abortar o post** e corrigir.

## GATE #3 — Mapa de atores e prior art (antes de redigir)
Thread pública tem mais de uma pessoa. Escrever sem saber quem é quem gera dano reputacional: pergunta endereçada a quem não decide, crédito no lugar errado, e aparência de atropelo.

1. **Nomeie os atores e o papel de cada um.** Quem abriu a issue, quem mantém o repo, quem mais reportou ou comentou: `gh issue view <n> --json author,assignees,comments`. Sem esse mapa, não redija.
2. **Verifique claim antes de produzir patch.** Alguém já está nisso? Procure assignee, sinal de trabalho nos comentários ("I'm on it", "taking a look") e PR aberto referenciando a issue (`gh pr list --search "<n>"`). Havendo dono aparente, **pergunte antes** em vez de aparecer com solução pronta.
3. **Varra os vizinhos.** Issues e PRs abertos na mesma superfície (`gh issue list --search "<termo> state:open"`, `gh pr list --search "<termo>"`). O que for relevante entra **citado** no seu texto, com o handle de quem reportou.

> Regra de saída: nenhuma análise pública sai sem (a) papéis identificados, (b) claim verificado, (c) vizinhos citados.

## Voice & tone (senior dev, courteous, en-US)
- **Idioma:** todo artefato público em en-US. Sem emojis.
- **Colaborativo, não adversarial.** Você e o mantenedor estão do mesmo lado do problema. Evite frases que anticipam ataque ("saying it before you do"), sarcasmo ("the opposite of a fix"), ou tom de acusação ("you never use it" → "it isn't currently scoped").
- **Enderece por handle; nunca "you" solto.** Em thread com mais de uma pessoa, "you" é ambíguo e manda a pergunta para o alvo errado. Decisão de projeto vai ao mantenedor ("@maintainer: your call on the scope"); crédito do achado vai ao autor ("@author's trace is what narrowed this"). No tone pass, releia cada "you"/"your" e confirme que o referente é único.
- **Crédito explícito e cedo.** Trabalhando em cima do diagnóstico de outra pessoa, diga isso no primeiro parágrafo, com o handle. Crédito enterrado no fim lê como formalidade.
- **Você é convidado na issue alheia.** Apresente o que somou ("adding measurements on top of @author's report"), não o achado inteiro como se fosse seu. Essa é a diferença entre colaborar e parecer tomada de crédito.
- **Cite os vizinhos.** Havendo issue/PR adjacente na mesma superfície, referencie e nomeie quem reportou. Silenciar o vizinho lê como atropelo, mesmo sem intenção.
- **Fato x hipótese, sempre separados.** Diga o que mediu, o que leu no código, e o que ainda não sabe — nessa ordem, com rótulos.
- **Concessão preventiva.** Anteceda a objeção óbvia do mantenedor você mesmo ("being upfront about the limits: even X still only does Y"). Isso separa análise séria de acusação.
- **Corrija os próprios números em público.** Se remediu um dado ("~465" → "~1950"), diga explicitamente que corrige a estimativa anterior — ganha credibilidade, não perde.
- **Não oscile sob pressão social.** Quando um mantenedor discorda, reinvestigue com código antes de responder; não capitule só para agradar nem insista só para não perder a discussão. Mude de posição apenas com evidência nova, e narre por que.

### Voz humana (anti-marcas de LLM)
Texto público não pode "cheirar a IA". Marcas que denunciam, e como evitar:
- **Emojis: nunca.** Em nenhum artefato público (post, PR/MR, commit, review).
- **Em-dash ("—"): nunca.** Não faz parte da voz do autor, e densidade de em-dash é o fingerprint clássico de texto de LLM. Use vírgula, dois-pontos, parênteses ou ponto final. Qualquer "—" em texto público é removido no tone pass, sem exceção.
- **Corte fórmulas de LLM:** "moreover", "furthermore", "it's worth noting", "delve", "robust", "crucial", "great question", elogio genérico de abertura.
- **Quebre a simetria.** Nem toda lista precisa de 3 itens com bold lead-in; nem todo post precisa de resumo final. Varie comprimento de frase e de parágrafo.
- **Teste de leitura:** leia em voz alta. Se soa como release notes de IA, reescreva como você explicaria a um colega no chat.

## Process
0. **Account gate (GATE #1):** confirmar o perfil com o usuário. Sem isso, parar.
1. **Recon (GATE #3) + diagnose before claiming.** Mapeie atores, claim e vizinhos antes de qualquer rascunho. Depois reproduza/meça: leia o código-fonte da **versão exata** instalada (não strings de binário, não a `main` se a instalada difere). Rotule cada conclusão: measured / read-in-code / unverified.
2. **Draft (en-US).** Estrutura padrão de report: correção de números (se houver) → achado com arquivo+linha → limite honesto → fix/ask acionável.
3. **Tone pass.** Reler removendo linguagem adversarial ("Voice & tone") e marcas de LLM ("Voz humana"): remover todo em-dash, cortar fórmulas, quebrar simetria. Cortês e humano.
4. **Sanitize (GATE #2).** Rodar o grep de vazamento. Abortar se sujo.
5. **Confirm & post.** Mostrar o texto final ao usuário; postar via `scripts/gh-post.sh <handle> ...`.
6. **PR etiquette (se aplicável):**
   - **Eixo autor (claim):** em issue de outra pessoa, pergunte antes de produzir patch ("are you already working on this? happy to help if not"). Patch pronto em issue recém-aberta de terceiro lê como tomada de crédito, mesmo com boa intenção.
   - **Eixo mantenedor (aceitação): ofereça o PR condicionalmente** ("happy to open a PR if you'd take it") **antes** de abrir. Só abra após o "sim" do mantenedor. PR não solicitado que quebra convenções vira ruído.
   - Siga as convenções do repo: estilo de commit (`git log --oneline`), CHANGELOG, testes/snapshots. Regenere snapshots afetados.
   - Commit sem atribuição de agente. Nunca `Co-authored-by:` de IA.
   - Base no `main`/`dev` upstream atual; mostre o diff ao usuário antes do push.
   - Fork + branch descritiva; PR body referencia a issue e endereça os requisitos do review, um a um.
7. **Restore account (GATE #1, passo 4).** Voltar a conta ativa anterior.

## Guardrails (operacionais, aprendidos na prática)
- **Push com conta secundária (caso GitHub):** um `credential.https://github.com.username` global pode forçar a autenticação com o usuário errado e falhar o push. Use username explícito no remote (`https://<handle>@github.com/<handle>/<repo>.git`) e o helper do host por invocação. Outros hosts têm quirks análogos — verifique o remote antes do push.
- **Nunca** postar antes do grep de sanitização retornar limpo.
- **Nunca** trocar a conta ativa sem restaurá-la ao final.
- Ao anexar logs, prefira **offsets relativos** e placeholders a qualquer timestamp/caminho absoluto.
- **Nunca** publicar análise em thread alheia sem crédito explícito ao autor e sem citar os vizinhos relevantes da mesma superfície.
- **Nunca** deixar "you" ambíguo num fio com mais de um interlocutor.

## Outputs
- Confirmação explícita do perfil antes de escrever; conta restaurada ao final.
- Post/PR em en-US, cortês, com fato e hipótese separados e limites declarados.
- Sanitização verificada (sem username/paths/segredos/nomes internos).
- PR (quando aceito) alinhado às convenções do repo, referenciando a issue.
- Atores identificados por handle, claim verificado e vizinhos citados; zero "you" ambíguo.

## Gate anti-segredo em commits externos

Todo commit em repo de terceiros passa pelo MESMO gate anti-segredo da skill
`git-pro` (scan do staged ANTES do commit), além do grep de sanitização de
posts. Chave em commit externo é irrecuperável — não há delete de histórico
em repo alheio.
