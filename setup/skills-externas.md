# Skills e plugins de terceiros

Nada aqui é autoria minha — são skills instaladas de repositórios públicos.
Numa máquina nova, rode os comandos abaixo para reinstalar tudo.

## Plugin oficial (dentro do Claude Code)

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install superpowers@claude-plugins-official
```

## Skills via CLI `skills`

Rodar no terminal, fora do Claude Code:

```bash
# Pika — 20 skills de geração de vídeo/imagem
npx skills add Pika-Labs/Pika-Plugins

# Caveman — 7 skills de compressão de contexto
npx skills add JuliusBrussee/caveman

# Vercel — performance, deploy, design e writing guidelines
npx skills add vercel/agent-skills
```

Depois de instalar, confira com `npx skills list` ou `/plugin` dentro do Claude Code.

## Estado de referência (27/07/2026)

| Fonte | Qtd | Skills |
|---|---|---|
| `Pika-Labs/Pika-Plugins` | 20 | 4k-vfx, anime-soccer, app-sizzle, app-store-screens, baseball-trend, build-a-brand, content-director, explainer, fix-my-look, founder-product-video, gameday, kiss-cam, language-swap, persona-builder, podcast, stagefight, ugc-ads, vfx, viral-hook, voxel-it |
| `JuliusBrussee/caveman` | 7 | cavecrew, caveman, caveman-commit, caveman-compress, caveman-help, caveman-review, caveman-stats |
| `vercel/agent-skills` | 8 | deploy-to-vercel, vercel-cli-with-tokens, vercel-composition-patterns, vercel-optimize, vercel-react-best-practices, vercel-react-native-skills, vercel-react-view-transitions, web-design-guidelines, writing-guidelines |
| `anthropics/claude-plugins-official` | 1 plugin | superpowers v6.1.1 |

`find-skills` veio junto com o CLI `skills` — não precisa instalar separado.

> As skills da Vercel e `find-skills` não estavam no `skills-lock.json` local, então a
> origem acima foi inferida. Se algum comando falhar, use `/find-skills` dentro do
> Claude Code para localizar a fonte correta.

## MCP servers

MCPs ficam fora deste kit (têm credenciais). Os que uso hoje:
Figma, Firecrawl, Pika, Playwright, Supabase.
Reconfigure com `claude mcp add` ou pela UI, e reautentique em cada máquina.
