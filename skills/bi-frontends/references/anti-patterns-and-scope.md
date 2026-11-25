# Fora de Escopo e Anti-Patterns — O Que Recusar Explicitamente

Esta reference existe porque, em 2025-2026, existem trends de UI reais e populares que **parecem** modernização mas quebram a função de um dashboard de dado. Leia isto antes de aceitar qualquer sugestão de "deixar mais moderno" vinda de fora desta skill.

## 1. Fora de Escopo — E Por Quê

| Trend | Por que não em BI enterprise |
|---|---|
| **Bento grid** | Documentado em discussão de UX (Stack Exchange) como "completamente impraticável para qualquer UI [de dashboard]" — o usuário de BI precisa **interagir** com dado (ordenar, filtrar, drill-down), não admirar uma composição estática assimétrica. Bento é para landing page/marketing. |
| **Glassmorphism** (blur + transparência) | Quebra contraste de tabela numérica e texto sobre fundo variável — risco direto de acessibilidade (WCAG 1.4.3) num contexto onde legibilidade de número é a função central da tela. |
| **Brutalismo** (cores em choque, tipografia crua) | É uma escolha de marca/identidade, não de utilidade — o oposto do objetivo desta skill (usuário termina uma tarefa, não é impressionado). |
| **Chart 3D** | Distorce proporção e piora leitura em qualquer caso, sem exceção — nenhuma das 4 referências de linhagem (Carbon/Observable/Stripe/Linear) usa. |
| **Ícone decorativo/ilustração grande** | Ver `iconography.md` — ícone em BI é rótulo funcional, não elemento de composição visual. |
| **Paleta "AI" (gradiente roxo/violeta, cyan-on-dark)** | O tell mais reconhecível de interface gerada por IA sem direção. Esta skill usa paleta categórica testada (Observable 10/Tableau 10), nunca gradiente decorativo. |

Se alguém pedir para "modernizar com bento grid" ou "adicionar glassmorphism" num dashboard real de produto, a resposta correta é explicar o trade-off acima antes de implementar — não implementar silenciosamente.

## 2. Catálogo de Tells — Adaptado ao Contexto de BI

Abaixo, as regras **específicas de dashboard/BI** — mais estritas que um catálogo genérico de antipatterns de UI.

### Visual
- **Icon tile acima de heading** em card de KPI — o template universal de "feature card gerada por IA". Ver `iconography.md` seção 5.
- **Side-stripe** (borda colorida grossa lateral) em card de status/prioridade — trocar por badge semântica.
- **Over-rounding** (radius 16px+) em card/container — teto real é 12px (`spacing-density-elevation.md`).

### Cor
- **Gradiente em qualquer superfície** — fundo, texto de KPI, botão. Zero exceções nesta skill.
- **Mais de 7 cores distintas** simultâneas numa mesma tela de gráfico/legenda.
- **Cor sozinha carregando estado crítico** (sem texto/ícone redundante) — falha WCAG 1.4.1.
- **Azul de interativo reaproveitado como cor de série de dado** — quebra a distinção "isso é clicável" vs "isso é categoria".
- **Laranja de marca usado como cor de dado** (série categórica, valor de KPI, badge de status) ou em superfície grande (fundo de hero/card/sidebar inteiro) — acento de marca é detalhe pontual (CTA, link, foco, logo), não cor de dado nem preenchimento decorativo. Ver `color-system.md` §6.1.
- **Laranja de marca idêntico ao laranja/âmbar da paleta categórica** (`--bi-cat-2`) — gera ambiguidade entre "isso é clicável/marca" e "isso é uma categoria no gráfico". Os dois tokens existem, mas precisam de hex perceptualmente distintos.

### Tipografia
- **Peso misto de KPI** — denso (600) e editorial (300) no mesmo dashboard (ver `typography.md` seção 4, escolher um).
- **Ausência de `tabular-nums`** em qualquer tabela/KPI — o tell nº1 de dashboard amador.

### Layout
- **Hero metric layout** (número gigante + 3 stats + accent gradiente) — dashboard denso usa densidade de tabela/grid real, não vitrine.
- **Grid de cards idênticos infinito** — quebrar com agrupamento por status/prioridade ou tamanho variável.
- **Modal com 12 campos de filtro e scrollbar** — se precisa de 3+ colunas de filtro, vira página própria, não modal.

### Motion
- **Animar série de chart** em painel denso — `isAnimationActive: false` sempre (ver `chart-standards.md`).

### Copy
- **Buzzword de marketing** ("Supercharge seus dados", "enterprise-grade insights") em empty state ou tooltip — dizer o que a tela faz: "Nenhum dado no período. Ajuste o filtro de data."

## 3. Checklist de Validação Pré-Ship

Rodar antes de considerar uma tela de BI pronta:

**Cor**
- [ ] Zero gradiente em qualquer superfície.
- [ ] Paleta categórica vem de token (`--bi-cat-*`), nunca hex solto.
- [ ] Nenhuma cor carrega estado crítico sozinha (sempre com texto/forma redundante).

**Tipografia**
- [ ] `tabular-nums` em 100% das tabelas e KPIs.
- [ ] Peso de KPI consistente (denso ou editorial, não misto).
- [ ] Nenhum texto abaixo de 12px.

**Estrutura**
- [ ] Nenhum card acima de radius 12px.
- [ ] Nenhum card estático com `box-shadow` (só borda).
- [ ] Máximo 2 níveis de card aninhado.
- [ ] Nenhum icon tile acima de heading em card de métrica.

**Gráfico**
- [ ] Máximo 7 séries visíveis por gráfico.
- [ ] Zero chart 3D, zero gradiente decorativo de preenchimento.
- [ ] `isAnimationActive={false}` em série densa.

**Acessibilidade**
- [ ] Contraste AA (4.5:1 texto normal, 3:1 gráfico/elemento grande).
- [ ] Todo botão ícone-só tem `aria-label`.
- [ ] Empty/error state tem ação de recuperação, `role="alert"` quando aplicável.

**Escopo**
- [ ] Nenhum bento grid, glassmorphism ou elemento 3D presente.
- [ ] Motion respeitando `prefers-reduced-motion`, sober (≤120ms funcional).
