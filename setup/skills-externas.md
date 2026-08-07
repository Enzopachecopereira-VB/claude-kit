# Skills de terceiros

Nada aqui é autoria minha — são skills instaladas de repositórios públicos.

Existem **dois caminhos** para tê-las numa máquina nova. Os dois funcionam; a
diferença é se você quer a versão congelada ou a mais recente.

---

## Caminho A — espelho deste repo (recomendado)

As 37 skills estão versionadas em `skills/` na raiz do repo. Restaurar:

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

# claude-video — não passa pelo CLI `skills`, tem installer próprio no npm
npx claude-video-install
```

**Use este quando:** quiser as versões mais recentes, ou depois de restaurar pelo
Caminho A e querer atualizar.

Os dois convivem — rodar o B por cima do A simplesmente atualiza.

**Atenção:** o Caminho B sozinho **não** traz tudo. Veja a nota no fim.

---

## Plugin oficial (dentro do Claude Code)

Este não passa pelo CLI `skills` — é plugin, instala por marketplace:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install superpowers@claude-plugins-official
```

---

## Estado do espelho (07/08/2026)

38 skills.

| Fonte | Qtd | Skills |
|---|---|---|
| `Pika-Labs/Pika-Plugins` | 20 | 4k-vfx, anime-soccer, app-sizzle, app-store-screens, baseball-trend, build-a-brand, content-director, explainer, fix-my-look, founder-product-video, gameday, kiss-cam, language-swap, persona-builder, podcast, stagefight, ugc-ads, vfx, viral-hook, voxel-it |
| `JuliusBrussee/caveman` | 7 | cavecrew, caveman, caveman-commit, caveman-compress, caveman-help, caveman-review, caveman-stats |
| `vercel/agent-skills` | 9 | deploy-to-vercel, vercel-cli-with-tokens, vercel-composition-patterns, vercel-optimize, vercel-react-best-practices, vercel-react-native-skills, vercel-react-view-transitions, web-design-guidelines, writing-guidelines |
| CLI `skills` | 1 | find-skills |
| npm `claude-video-install` | 1 | claude-video |
| `anthropics/claude-plugins-official` | 1 plugin | superpowers v6.1.1 |

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

### Por que o espelho existe

O `skills-lock.json` rastreia só **27** das 38 — as do Pika e do caveman. As 9 da
Vercel, a `find-skills` e a `claude-video` aparecem como `Source: local` no
`npx skills list`, ou seja, **nada as reinstala automaticamente**. Numa máquina
nova, o Caminho B sozinho traria 27 e deixaria 11 para trás, em silêncio.

O espelho inclui todas as 38, e não só as 11 órfãs, para que o repo seja a
resposta única — em vez de uma lista de exceções que alguém precisa lembrar.

Verificado em 29/07/2026 com `npx skills list` (CLI v1.5.20).

---

## MCP servers

MCPs ficam fora deste kit — têm credenciais e não podem ser versionados. São o
**único** passo manual que sobra numa máquina nova.

Eles se dividem em dois tipos, e só um dá trabalho:

### Locais — precisam ser reconfigurados (4)

Vivem em `~/.claude.json`, na chave `mcpServers`:

| Server | Reautenticar |
|---|---|
| `supabase` | token de acesso |
| `firecrawl` | API key |
| `pika-mcp` | conta Pika |
| `playwright` | nenhum — só instalar |

Reconfigure com `claude mcp add` ou pela UI (`/mcp`).

### Da conta claude.ai — vêm sozinhos

`Figma`, `higgsfield`, `Notion` e `Box` estão conectados à sua conta claude.ai,
não ao computador. Aparecem sozinhos ao logar na máquina nova — não faça nada.
(`Box` pede reautenticação pela UI; os outros já vêm conectados.)

Verificado em 07/08/2026 com `claude mcp list`.
