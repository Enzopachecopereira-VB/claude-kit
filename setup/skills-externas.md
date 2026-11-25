# Skills de terceiros

Nada aqui é autoria minha — são skills instaladas de repositórios públicos.

Existem **dois caminhos** para tê-las numa máquina nova. Os dois funcionam; a
diferença é se você quer a versão congelada ou a mais recente.

---

## Caminho A — espelho deste repo (recomendado)

As 59 skills estão versionadas em `skills/` na raiz do repo. Restaurar:

```powershell
git clone https://github.com/Enzopachecopereira-VB/claude-kit.git
cd claude-kit
./install-skills.ps1
```

**Use este quando:** quiser exatamente o mesmo conjunto que roda na máquina de
origem, sem surpresa de versão, e sem depender dos repos de terceiros
continuarem no ar.

O script recria o layout original — arquivos reais em `~/.agents/skills/` e
junctions em `~/.claude/skills/` — e restaura o `skills-lock.json`, para o CLI
`skills` continuar sabendo a origem de cada uma.

Se já existir uma skill com o mesmo nome, ele faz backup (`.bak-<timestamp>`)
antes de sobrescrever.

---

## Caminho B — reinstalar da fonte

```bash
# Pika — 20 skills de geração de vídeo/imagem
npx skills add Pika-Labs/Pika-Plugins

# Caveman — 7 skills de compressão de contexto
npx skills add JuliusBrussee/caveman

# Vercel — performance, deploy, design e writing guidelines
npx skills add vercel/agent-skills

# Matt Pocock — 9 skills de engenharia (grilling, tdd, code-review...)
npx skills add mattpocock/skills -g -a claude-code -y \
  -s grill-me -s grilling -s grill-with-docs -s tdd -s diagnosing-bugs \
  -s code-review -s domain-modeling -s codebase-design -s setup-matt-pocock-skills

# claude-video — não passa pelo CLI `skills`, tem installer próprio no npm
npx claude-video-install

# notebooklm-research — pacote PyPI, o install.sh do repo é Unix-only
uv tool install notebooklm-skill
uvx --from notebooklm-skill playwright install chromium
notebooklm-install-skill --target "$HOME/.agents/skills/notebooklm-research"
```

**Use este quando:** quiser as versões mais recentes, ou depois de restaurar pelo
Caminho A e querer atualizar.

Os dois convivem — rodar o B por cima do A simplesmente atualiza.

**Atenção:** o Caminho B sozinho **não** traz tudo. Veja a nota no fim.

---

## Plugins (dentro do Claude Code)

Estes não passam pelo CLI `skills` — são plugins, instalam por marketplace. O
`setup/settings.json` já traz os três marketplaces e os 8 plugins habilitados,
então restaurar o settings resolve. Para instalar na mão:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install superpowers@claude-plugins-official

/plugin marketplace add trailofbits/skills
/plugin install static-analysis@trailofbits        # + insecure-defaults, fp-check,
                                                   # supply-chain-risk-auditor,
                                                   # testing-handbook-skills,
                                                   # differential-review

/plugin marketplace add pbakaus/impeccable
/plugin install impeccable@impeccable
```

Fora do Claude Code também existe o CLI: `claude plugin marketplace add <repo>` e
`claude plugin install <plugin>@<marketplace>` fazem o mesmo sem abrir o menu.

### impeccable (07/08/2026)

`pbakaus/impeccable` (Apache-2.0). Plugin **4.0.4**: 1 skill, 23 comandos, 4
agentes, 2 hooks, ~527 tokens sempre ativos. O CLI no npm é versionado à parte
(`impeccable` 3.5.0).

**Não espelhe os arquivos desta skill em `skills/`.** O plugin já entrega tudo no
Claude Code; se o espelho existisse, o `install-skills.ps1` criaria uma junction em
`~/.claude/skills/impeccable` e você teria a skill duas vezes. O marketplace no
`settings.json` é o registro correto.

O `npx impeccable install` foi rodado **só para Cursor e Codex**, que o plugin não
alcança:

```
npx impeccable install --global --providers cursor,codex -y
```

Isso escreve `~/.cursor/skills/impeccable`, `~/.agents/skills/impeccable` e hooks em
`.cursor/hooks.json` + `.codex/hooks.json`. **Não** cria
`~/.claude/skills/impeccable` nem `~/.claude/settings.local.json`, que é o ponto.

Cuidado com o escopo: rodar `npx impeccable install` sem `--providers` a partir de
`~` instala em escopo global e inclui o `.claude`, duplicando a skill e registrando
o hook de edição no seu settings.

---

## Adicionadas em 25/11/2026

11 skills que estavam na máquina atual e faltavam no espelho, mais a atualização
de `diagnosing-bugs` e `tdd` para a versão instalada aqui (outubro/2026).

| Skill | Origem | Reinstalar da fonte |
|---|---|---|
| design-taste-frontend | `leonxlnx/taste-skill` | `npx skills add leonxlnx/taste-skill` |
| frontend-design | `anthropics/skills` | `npx skills add anthropics/skills -s frontend-design` |
| reverse-engineer-anything | `rea-agents` (npm, par do MCP `rea`) | vem com o REA |
| bi-frontends | comunidade | só pelo espelho |
| building-nextjs-applications | comunidade | só pelo espelho |
| improve-ui | — | só pelo espelho |
| security-audit | — | só pelo espelho |
| resolving-merge-conflicts | MIT | só pelo espelho |
| git-contribution | proprietária | só pelo espelho |
| git-pro | proprietária | só pelo espelho |
| worktree-agent-workflow | proprietária | só pelo espelho |

A `impeccable` também está instalada como skill na máquina atual (via
`npx skills add pbakaus/impeccable`), mas **continua fora do espelho** pelo motivo
da seção acima: o plugin já a entrega.

O `skills-lock.json` não foi alterado — estas entram como `Source: local`, como
as da Vercel e do Matt Pocock.

---

## Estado do espelho (10/08/2026)

48 skills.

| Fonte | Qtd | Skills |
|---|---|---|
| `mattpocock/skills` | 9 | code-review, codebase-design, diagnosing-bugs, domain-modeling, grill-me, grill-with-docs, grilling, setup-matt-pocock-skills, tdd |
| `Pika-Labs/Pika-Plugins` | 20 | 4k-vfx, anime-soccer, app-sizzle, app-store-screens, baseball-trend, build-a-brand, content-director, explainer, fix-my-look, founder-product-video, gameday, kiss-cam, language-swap, persona-builder, podcast, stagefight, ugc-ads, vfx, viral-hook, voxel-it |
| `JuliusBrussee/caveman` | 7 | cavecrew, caveman, caveman-commit, caveman-compress, caveman-help, caveman-review, caveman-stats |
| `vercel/agent-skills` | 9 | deploy-to-vercel, vercel-cli-with-tokens, vercel-composition-patterns, vercel-optimize, vercel-react-best-practices, vercel-react-native-skills, vercel-react-view-transitions, web-design-guidelines, writing-guidelines |
| CLI `skills` | 1 | find-skills |
| npm `claude-video-install` | 1 | claude-video |
| PyPI `notebooklm-skill` | 1 | notebooklm-research |
| `anthropics/claude-plugins-official` | 1 plugin | superpowers v6.1.1 |

### matt pocock (10/08/2026)

Origem: `mattpocock/skills` (MIT, © 2026 Matt Pocock). O repo tem **35** skills; só
9 foram espelhadas. Também existe como plugin oficial
(`claude plugins install mattpocock-skills`) — **não use os dois**, senão cada skill
aparece duas vezes.

Como as skills do Vercel, o `npx skills add -g` **não** escreve no
`skills-lock.json`. Elas entram no espelho como `Source: local`.

**Pegadinha das flags:** o agente chama-se `claude-code` (não `claude`), e o `-s`
aceita **um** nome por flag — `-s a,b` não casa com nada e o CLI apenas lista as
skills disponíveis, saindo com sucesso. Parece que instalou; não instalou.

Pedi 4 skills; as outras 5 são dependências declaradas dentro dos `SKILL.md`:

| Pedida | Puxa |
|---|---|
| `grill-with-docs` | `grilling` + `domain-modeling` |
| `tdd` | `codebase-design` |
| `code-review` | `setup-matt-pocock-skills` (para achar `docs/agents/issue-tracker.md`) |
| `diagnosing-bugs` | — (só referencia `improve-codebase-architecture`, que ficou de fora) |

`grill-me`, `grill-with-docs` e `setup-matt-pocock-skills` têm
`disable-model-invocation: true` — são slash command puro, o modelo não as invoca
sozinho.

**Antes do primeiro uso em cada repo**, rode `/setup-matt-pocock-skills`: ele
pergunta o issue tracker, as labels de triagem e onde salvar docs, e escreve
`docs/agents/*`. Sem isso, `code-review` não acha o spec e degrada para só o eixo
de Standards.

### claude-video (07/08/2026)

Origem: `marques-hue/claude-video-watch`, publicada no npm como
`claude-video-install`. Não passa pelo CLI `skills`, então **não** aparece no
`skills-lock.json` — como as 9 da Vercel.

Instalada aqui na mão (o installer é interativo e pede a chave num prompt).
Duas coisas ficaram **fora** do espelho de propósito:

- **`.env`** — contém a API key. O `.gitignore` da própria skill já o exclui.
  Numa máquina nova, crie com `VIDEO_PROVIDER=gemini`, `GEMINI_MODEL=gemini-2.5-flash`
  e `GEMINI_API_KEY=<chave de aistudio.google.com/app/apikey>`.
- **deps Python** — `pip install google-genai python-dotenv`. Só isso basta para
  o caminho Gemini nativo: os imports de `faster_whisper`/`easyocr` são lazy e só
  disparam no caminho Anthropic. O `requirements.txt` completo puxa torch (~500MB).

O bloco de voz do `SKILL.md` original mandava seguir as regras de marca do autor
(*"Marques' brand rules"*); foi trocado por pt-BR seguindo o CLAUDE.md daqui.

### notebooklm-research (07/08/2026)

Origem: `claude-world/notebooklm-skill` (MIT), publicada no PyPI como
`notebooklm-skill` **1.3.0** — o HEAD do repo (`dc38bd8`) é essa mesma versão.
Fora do `skills-lock.json`, como as outras não-CLI.

**O `install.sh` do repo não roda no Windows**: assume `venv/bin/python` e `ln -s`.
Use o `uv` (Caminho B acima), que já resolve isso.

Só o `SKILL.md` está espelhado. O resto **não é versionável**:

- **`~/.notebooklm/profiles/<perfil>/storage_state.json`** — sessão do navegador,
  equivalente a cookie da conta Google. Nunca ler, copiar nem commitar. Recriar
  com `notebooklm-auth setup` (abre um Chromium e pede login).
- **CLI + venv** — gerenciados pelo `uv` em `%APPDATA%\uv\tools\notebooklm-skill`,
  com 5 comandos linkados em `~/.local/bin` (já está no PATH do usuário).
- **Chromium do Playwright** — ~115MB em `%LOCALAPPDATA%\ms-playwright`. É separado
  do MCP `playwright` do Node, que continua independente.

MCP registrado em escopo user: `uvx --from notebooklm-skill notebooklm-mcp`,
13 tools `nlm_*`. Como é `uvx`, numa máquina nova basta ter `uv` — não precisa
pré-instalar nada além da autenticação.

**Ressalva de estabilidade:** o NotebookLM não tem API pública. Isso aqui é a API
web não-oficial dirigida por navegador. Se o Google mexer no front, quebra, e não
há SLA nenhum.

### Por que o espelho existe

O `skills-lock.json` rastreia só **27** das 48 — as do Pika e do caveman. As 9 da
Vercel, as 9 do Matt Pocock, a `find-skills`, a `claude-video` e a
`notebooklm-research` aparecem como `Source: local` no `npx skills list`, ou seja,
**nada as reinstala automaticamente**. Numa máquina nova, o Caminho B sozinho
traria 27 e deixaria 21 para trás, em silêncio.

O espelho inclui todas as 48, e não só as 21 órfãs, para que o repo seja a
resposta única — em vez de uma lista de exceções que alguém precisa lembrar.

Verificado em 29/07/2026 com `npx skills list` (CLI v1.5.20).

---

## MCP servers

MCPs ficam fora deste kit — têm credenciais e não podem ser versionados. São o
**único** passo manual que sobra numa máquina nova.

Eles se dividem em dois tipos, e só um dá trabalho:

### Locais — precisam ser reconfigurados (5)

Vivem em `~/.claude.json`, na chave `mcpServers`:

| Server | Reautenticar |
|---|---|
| `supabase` | token de acesso |
| `firecrawl` | API key |
| `pika-mcp` | conta Pika |
| `playwright` | nenhum — só instalar |
| `notebooklm` | login Google via `notebooklm-auth setup` |

Reconfigure com `claude mcp add` ou pela UI (`/mcp`).

### Da conta claude.ai — vêm sozinhos

`Figma`, `higgsfield`, `Notion` e `Box` estão conectados à sua conta claude.ai,
não ao computador. Aparecem sozinhos ao logar na máquina nova — não faça nada.
(`Box` pede reautenticação pela UI; os outros já vêm conectados.)

Verificado em 07/08/2026 com `claude mcp list`.
