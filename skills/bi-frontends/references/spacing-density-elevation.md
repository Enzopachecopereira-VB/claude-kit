# Densidade, Espaçamento, Radius, Elevação

## 1. Grid de 8px

Toda medida de espaçamento (padding, margin, gap) é múltiplo de 8px, com 4px permitido só como ajuste fino interno de componente pequeno (ícone + label).

```css
--bi-space-1: 4px;   /* ajuste fino apenas */
--bi-space-2: 8px;   /* unidade base */
--bi-space-3: 12px;
--bi-space-4: 16px;
--bi-space-6: 24px;
--bi-space-8: 32px;
--bi-space-12: 48px;
--bi-space-16: 64px;
```

Fonte: Stripe (`spacingUnit: 8px` em produção real), IBM Carbon (`2x Grid`, mini unit de 8px), Linear (escala 8/16/32/64).

## 2. Padding de Célula e Componente

| Elemento | Padding | Fonte |
|---|---|---|
| Célula de tabela densa | 8-12px vertical, 12-16px horizontal | Stripe (`tableRowPaddingY: 8px` real) |
| Card de KPI | 16-24px | Convenção geral enterprise |
| Botão (padrão) | 8px vertical, 12-16px horizontal | Stripe/Carbon |
| Input de filtro | 8-10px vertical, 12px horizontal | Stripe (`inputFieldPaddingY: 4-8px`) |
| Toolbar/topbar | 12-16px vertical | Convenção admin shell |

Regra: nunca menos de 8px de padding em qualquer container que tenha texto — texto colado na borda é antipattern catalogado ("cramped padding", "body text touching viewport edge").

## 3. Border-Radius — Teto Explícito

```css
--bi-radius-sm: 4px;   /* badge, chip, tag */
--bi-radius-md: 6px;   /* input, botão, célula selecionada */
--bi-radius-lg: 8px;   /* modal, overlay */
--bi-radius-xl: 12px;  /* container/card grande — teto real, Linear/Stripe */
```

**Nunca** passar de 12px em card/container. Radius 16px+ ("over-rounding") é antipattern catalogado — "cards topam em 12-16px; pill só para tag/botão" (aplica pill/`border-radius: 999px` só a badge/chip/botão pequeno, nunca a card).

Fonte real: Stripe `borderRadius` de produção 4-6px em componente, `overlayBorderRadius: 8px`; Linear usa 6px e 12px como os dois únicos níveis reais em produção.

## 4. Borda em Vez de Sombra — Regra de Delimitação

Card/painel estático delimita com **borda de 1px** (ou 0.5px hairline se o browser/DPI suportar bem), não com `box-shadow`. Elevação real (modal, popover, dropdown que flutua sobre conteúdo) pode usar sombra sutil — mas nunca card de conteúdo estático dentro do fluxo normal da página.

```css
.bi-card {
  border: 1px solid var(--bi-border-subtle);
  border-radius: var(--bi-radius-xl);
  background: var(--bi-bg-layer-1);
  /* sem box-shadow */
}

.bi-overlay {
  /* elevação real: popover, dropdown, modal */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: var(--bi-radius-lg);
}
```

**Nunca combinar** borda + sombra ampla no mesmo elemento estático ("hairline + soft shadow wide ao mesmo tempo" — antipattern catalogado, escolher um dos dois).

## 5. Elevação por Camada de Cor (Layering Model)

Em vez de simular profundidade com sombra, sobe-se um degrau de `--bi-bg-layer-N` (ver `color-system.md` seção 4):

```
Página (bg-base)
 └─ Painel/seção (bg-layer-1) — borda 1px
     └─ Card dentro do painel (bg-layer-2) — só se genuinamente necessário
```

Máximo **2 níveis de aninhamento visual** por tela. Card dentro de card dentro de card ("cardocalypse") é o antipattern mais comum em dashboard mal estruturado — achatar com `section` + divisor + tipografia em vez de empilhar containers.

## 6. Densidade de Tabela — Padrão de Altura de Linha

| Densidade | Altura de linha | Uso |
|---|---|---|
| Compacta | 32-36px | Tabela operacional com muitas linhas visíveis simultaneamente (padrão BI enterprise) |
| Confortável | 40-44px | Tabela com ação por linha (checkbox, menu de contexto) |
| Espaçosa | 48px+ | Raro em BI — só quando linha carrega conteúdo rico (avatar + 2 linhas de texto) |

Default desta skill: **compacta**. BI enterprise prioriza "ver mais linhas por scroll" sobre respiro decorativo — oposto de landing page.

## 7. Checklist Rápido

- [ ] Todo espaçamento é múltiplo de 8px (4px só em ajuste fino de ícone+label).
- [ ] Padding de célula de tabela entre 8-12px vertical.
- [ ] Nenhum `border-radius` acima de 12px em card/container.
- [ ] Card estático usa borda 1px, não `box-shadow`.
- [ ] Nenhum elemento combina borda + sombra ampla simultaneamente.
- [ ] Máximo 2 níveis de card aninhado visualmente numa mesma tela.
- [ ] Densidade de tabela é compacta (32-36px de altura de linha) por padrão.
