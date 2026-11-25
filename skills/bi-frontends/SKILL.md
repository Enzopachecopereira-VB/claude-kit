---
name: bi-frontends
description: Constrói frontends de BI/analytics/dashboards enterprise no padrão neutro-primeiro (IBM Carbon + Observable + Stripe Dashboard + Linear) com dark-first como tema default, cor reservada exclusivamente a dado/estado semântico, paleta categórica testada (Observable 10 / Tableau 10), tabular-nums obrigatório, densidade 8px e tokens semânticos claro/escuro. Use ao criar ou revisar dashboard, painel de KPI, tabela densa de dados, gráfico categórico, sidebar/topbar de admin, ou qualquer tela cuja função é apresentar dado — não landing page, não marketing site.
metadata:
  version: "1.0.0"
  author: "community"
  category: "bi-frontend"
  tags: ["frontend", "bi", "dashboard", "analytics", "dark-mode", "dark-first", "design-tokens", "ibm-carbon", "observable", "stripe-dashboard", "linear", "data-visualization", "tabular-nums", "enterprise", "typescript", "react", "brand-accent"]
references:
  - path: references/color-system.md
    description: "Fundo sólido, escala neutra, paleta categórica exata (Observable 10 / Tableau 10 / Carbon), cores semânticas, acento único de marca (neutros + uma cor de acento em doses pequenas; exemplo: laranja), dark-first como default real (data-theme + color-scheme + light-dark())."
  - path: references/typography.md
    description: "Stack tipográfico (Inter/IBM Plex Sans), escala completa, font-variant-numeric: tabular-nums obrigatório, dois modos de peso de KPI (denso 600 vs editorial 300), rótulos uppercase."
  - path: references/spacing-density-elevation.md
    description: "Grid de 8px, padding de célula, radius máximo, borda vs sombra, elevação por camada de cor (layering model) em vez de box-shadow."
  - path: references/chart-standards.md
    description: "Wiring de paleta categórica no recharts-adapter (canônico), regras de gráfico denso (sem 3D, sem animação em série, sem gradiente de preenchimento), acessibilidade daltonismo, tooltip/legend."
  - path: references/component-patterns.md
    description: "Anatomia de KPI card, tabela densa com sticky header, sidebar/topbar de admin, badge de estado semântico, empty/loading/error states."
  - path: references/iconography.md
    description: "Conjuntos de ícones aprovados para BI (Tabler/Lucide/Carbon Icons), sizing 16-20px, stroke único, uso funcional vs decorativo, delivery via @iconify/react, regras de a11y."
  - path: references/anti-patterns-and-scope.md
    description: "O que fica fora de escopo (bento grid, glassmorphism, brutalismo, 3D chart) e por quê; catálogo de tells de 'AI-generated dashboard'; checklist de validação pré-ship."
---

# BI Frontends — Padrão Enterprise Neutro-Primeiro, Dark-First

Skill de domínio vertical para telas cuja função é **apresentar dado**: dashboard, painel de KPI, tabela analítica, gráfico, admin de BI. Baseada em pesquisa direta dos design systems reais de **IBM Carbon** (data visualization), **Observable Plot**, **Stripe Dashboard**, **Linear** (contenção cromática) e no que **Power BI (Fluent 2)**, **Tableau**, **Looker Studio**, **Apache Superset** e **Grafana** shippam hoje em produção (2025-2026) — não é opinião, é o que já é padrão de fato na indústria.

Complementar a `building-nextjs-applications` (setup). Esta skill cobre o que é **vertical de BI**: cor, tipografia, densidade, paleta de gráfico, tema dark-first.

## Tese central (por que dark-first e por que neutro)

1. **Dado é a única cor.** UI em cinza; cor reservada a série categórica e estado semântico (sucesso/erro/alerta). Confirmado como token oficial em IBM Carbon (`$interactive` só para elementos interativos) e Fluent 2 (`colorBrandPrimary` "used sparingly to accent and highlight").
2. **Fundo é sólido, nunca gradiente.** Claro: `#FFFFFF` / `#FAFAFA`. Escuro (**default desta skill**): `#0D1117`–`#111827`, ou a escala real de produção do Linear (`#08090A` → `#0F1011` → `#161718`).
3. **Dark é o tema padrão, não o alternativo.** Linear e Vercel tratam dark como substrato, não como toggle — "darkness as a substrate, not a theme". Esta skill implementa dark como `data-theme` default; claro é o override.
4. **Paleta categórica é escolhida de biblioteca testada**, nunca inventada pelo modelo: Observable 10 (default) ou Tableau 10 (alternativa), ambas com contraste revisado para daltonismo.
5. **Elevação por cor de camada, não por sombra.** Carbon: `layer-01`/`layer-02` alternando tom; Linear: borda hairline "to let geometry do the work that shadows usually would".
6. **Números tabulares é o detalhe que separa profissional de amador.** `font-variant-numeric: tabular-nums` obrigatório em toda tabela/KPI.

## Marca — Neutros + Acento Único (exemplo: laranja)

O padrão recomendado é a marca usar **predominantemente branco/off-white/tons de cinza/preto** — ou seja, exatamente a escala neutra que já é a base desta skill (§1-§2 de `references/color-system.md`). O único elemento de identidade fora da escala neutra é **uma cor de acento** (nos exemplos desta skill, laranja; troque pela cor da sua marca), bem-vinda em **detalhes** — CTA primário, link, foco de teclado, logo, indicador de item ativo — nunca em superfície grande, nunca competindo com a paleta categórica de gráfico, nunca substituindo um token semântico (`--bi-color-warning` continua sendo warning, mesmo se o tom for parecido). Detalhe completo, whitelist/blacklist de uso e o motivo de manter o acento de marca visualmente distinto das cores da paleta categórica em `references/color-system.md` §6.1.

## Quando Usar Esta Skill

- Criar ou revisar dashboard, home de analytics, painel de KPI executivo.
- Implementar tabela densa de dados (financeira, operacional, relatório).
- Escolher/wire paleta de cor para gráfico categórico (bar, line, area, donut).
- Montar shell de admin BI (sidebar de navegação, topbar de filtros, cards de métrica).
- Auditar uma tela de dashboard existente contra o padrão enterprise (`/audit` — ver seção de diretivas).
- Decidir entre claro/escuro como tema default de um produto de dado novo.

**Não é esta skill quando:** a tela é landing page, marketing site, ou onboarding com apelo emocional — use uma skill de landing/marketing. Motion/interação mais expressiva **dentro** de app de produto com identidade de marca também fica fora do escopo desta skill.

## Linhagem de referência (por que estas 4 fontes)

| Fonte | O que empresta |
|---|---|
| **IBM Carbon Design System** | Tokens semânticos de cor (`$text-primary`, `$layer-01`), layering model, paleta categórica 14 cores sequenciada, escala de cinza 10-100 |
| **Observable (Plot)** | Paleta categórica `Observable10` testada para claro **e** escuro simultaneamente (sucessora do Tableau10 desde 2023) |
| **Stripe Dashboard** | `tableRowPaddingY: 8px`, `borderRadius: 4-6px`, `tabular-nums` obrigatório em valor financeiro, densidade de token real de produção |
| **Linear** | Contenção cromática (1 accent só), bordas hairline 0.5-1px em vez de sombra, dark como substrato/default, tokens de camada `void→carbon→obsidian→graphite` |

Validado contra o estado real de 2025-2026: **Power BI** migrou o tema default para **Fluent 2** (mesma filosofia — neutral/shared/brand, 3 paletas, cor "used sparingly"); **Tableau** mantém Tableau 10 como paleta categórica default; **Apache Superset 6.0** implementou dark mode "de verdade" sobre tokens Ant Design v5; **Grafana** é dark-first há anos. Este não é um estilo de nicho — é o vocabulário atual dos dois maiores fornecedores de BI corporativo do mundo (Microsoft e IBM).

## Os 7 Princípios (resumo executável)

### 1. Fundo sólido, tema dark-first
Ver `references/color-system.md`. Default do produto é `data-theme="dark"` no `<html>`, light é o override persistido (não é `prefers-color-scheme` puro — é escolha do produto, com fallback pro SO se o usuário nunca escolheu).

### 2. Cor só para dado e estado
Nunca hardcode hex fora de token. Interativo/link usa `--bi-color-interactive` (um único acento reservado — azul por padrão, ou a cor de acento da marca, como o laranja do exemplo; ver `references/color-system.md` §6.1). Série categórica usa a paleta de `references/color-system.md`. Sucesso/erro/alerta usam `--bi-color-success/-danger/-warning`, nunca reaproveitados como cor decorativa de UI — e nunca reaproveitados pelo acento de marca, mesmo quando o tom é parecido: são tokens diferentes com funções diferentes (identidade vs. estado).

### 3. Paleta categórica testada, 5-7 cores visíveis por vez
Default: **Observable 10**. Se o produto já usa Tableau em algum lugar (migração, paridade visual com relatório existente): **Tableau 10**. Nunca D3 `category10` cru (mais saturado, "Crayola", não testado pra dark). Ver tabela de decisão em `references/chart-standards.md`.

### 4. Tipografia neutra com tabular-nums obrigatório
Inter ou IBM Plex Sans. `font-variant-numeric: tabular-nums` em toda célula de tabela e todo KPI — sem exceção. Ver `references/typography.md` para os dois modos de peso de KPI (denso vs editorial) e quando escolher cada um.

### 5. Densidade 8px, radius 4-6px, borda em vez de sombra
Grid de espaçamento em múltiplos de 8px. Padding de célula 8-12px. Radius interno 4-6px (Stripe real), até 12px em container (Linear real). Elevação por camada de cor. Ver `references/spacing-density-elevation.md`.

### 6. Estrutura cria hierarquia, não decoração
KPI grande em peso 600 (denso) — rótulo em caps 11px, letter-spacing 0.05em. Sem ícone decorativo em card de métrica. Sem gradiente em texto. Ver `references/component-patterns.md`.

### 7. Ícone funcional, um set só, monocromático
Um único conjunto de ícones por produto (nunca misturar Lucide + Tabler + Phosphor no mesmo app). Ícone segue cor do texto (nunca accent decorativo), sizing travado em 16/20px, stroke único. Ícone é funcional (ordenação, ação de toolbar, estado ao lado de texto) — nunca decorativo isolado acima de heading. Ver `references/iconography.md`.

## Fora de Escopo — Declarado Explicitamente

Bento grid, glassmorphism, brutalismo e chart 3D **não fazem parte desta skill**, mesmo sendo trend de UI 2025-2026 — porque são trends de produto de consumo/marketing, não de BI enterprise (bento grid é documentadamente "impraticável para dashboard" porque o usuário precisa *interagir* com dado, não admirar composição estática; glassmorphism quebra contraste de tabela numérica). Detalhe completo e catálogo de tells em `references/anti-patterns-and-scope.md` — **leia antes de aplicar qualquer sugestão de "modernizar" um dashboard que venha de fora desta skill.**

## Vocabulário de Design (diretivas de prompt)

| Diretiva | Aplicação em BI |
|---|---|
| `/quieter <seletor>` | Reduzir agressão cromática de um dashboard que "colore tudo" — o caso de uso mais comum desta skill |
| `/typeset <seletor>` | Ajustar hierarquia de KPI vs rótulo vs corpo de tabela |
| `/simplify <seletor>` | Achatar card-dentro-de-card em painel de métricas |
| `/audit <seletor>` | Rodar o checklist de `references/anti-patterns-and-scope.md` numa tela existente |
| `/harden <seletor>` | Stress-test com número negativo grande, nome de série longo, tabela vazia, 500 linhas |
| `/polish <seletor>` | Passo final: conferir tabular-nums, radius, borda vs sombra antes de shipar |

> Diretivas de prompt, não slash-commands instalados. Escreva: *"aplique /quieter no dashboard de vendas"*.

## Relação com Outras Skills

- **`building-nextjs-applications`** — setup do app. Esta skill assume que o app já existe; cobre só o que é visual/token de BI dentro dele.
- **Motion em BI** é **sóbria**: `duration: 120ms` no máximo, `isAnimationActive: false` em série de chart (recharts), nunca animar dado. Para overlay e dialog acessível, libs como `@floating-ui/react` e `react-aria` funcionam bem.

## Como Consultar as References

- **color-system.md** — ao definir tokens de cor (claro/escuro), escolher paleta categórica, implementar dark-first de verdade (não só `prefers-color-scheme`).
- **typography.md** — ao definir escala de tipo, decidir peso de KPI, implementar tabular-nums.
- **spacing-density-elevation.md** — ao definir grid de espaçamento, radius, decidir borda vs sombra, layering de elevação.
- **chart-standards.md** — ao integrar paleta em gráfico (recharts como engine canônica), regras de chart denso, acessibilidade de cor.
- **component-patterns.md** — ao construir KPI card, tabela densa, shell de admin, badge de estado.
- **iconography.md** — ao escolher conjunto de ícones do projeto, decidir sizing/stroke, distinguir uso funcional de decorativo, wire de a11y (`aria-hidden`/`aria-label`).
- **anti-patterns-and-scope.md** — antes de aceitar qualquer sugestão de trend visual externo (bento/glass/3D); checklist pré-ship.

## Script de Auditoria

`scripts/audit_bi_tokens.mjs` — varredura estática (Node, zero deps) que sinaliza violações comuns: `linear-gradient`/`radial-gradient` em background, `backdrop-filter: blur` em card de dado, `box-shadow` colorido, hex hardcoded fora de arquivo de token, `border-radius` acima de 16px, ausência de `tabular-nums` em seletor de classe `.kpi`/`.table-cell`, mais de 7 cores distintas num mesmo arquivo de tema.

```bash
node ~/.agents/skills/bi-frontends/scripts/audit_bi_tokens.mjs src/
```

Rode como gate de PR (passo no CI) se o projeto não tiver guard própria. Se o projeto já tem uma guard de lint/estilo de frontend, **não duplique** — este script cobre só as regras específicas de BI que aquelas guards genéricas não conhecem (paleta categórica, tabular-nums, layering de elevação).

---

**Consulte `references/*.md` para tokens exatos, snippets canônicos e checklists completos.**
