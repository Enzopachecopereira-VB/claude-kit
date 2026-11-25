# Sistema de Cor — Fundo, Neutros, Paleta Categórica, Dark-First

## 1. Fundo — Sólido, Nunca Gradiente

| Tema | Token | Valor | Fonte |
|---|---|---|---|
| Claro | `--bi-bg-base` | `#FFFFFF` ou `#FAFAFA` | Carbon White theme / convenção geral |
| Claro (alt) | `--bi-bg-base` | `#F4F4F4` | Carbon Gray 10 theme |
| **Escuro (default)** | `--bi-bg-base` | `#0D1117`–`#111827` | Convenção GitHub/Tailwind dark |
| Escuro (produção real, mais contido) | `--bi-bg-base` | `#08090A` | Linear (`--color-void`) |

Nenhum dos dois temas usa gradiente de fundo. Elevação de superfície é feita por **passo de camada** (seção 4), não por escurecer/clarear com `linear-gradient`.

## 2. Escala Neutra (tokens semânticos, não hex direto em componente)

Nunca hardcode hex em componente — sempre token. Nomeie por **papel**, não por valor (`text-primary`, não `gray-900`), para permitir troca de tema sem reescrever componente (mesmo princípio de `$text-01`/`colorNeutralForeground1` do Carbon/Fluent 2).

```css
:root[data-theme="light"] {
  --bi-bg-base: #FAFAFA;
  --bi-bg-layer-1: #FFFFFF;      /* card, painel */
  --bi-bg-layer-2: #F4F4F4;      /* elevação seguinte, hover de row */
  --bi-text-primary: #111827;
  --bi-text-secondary: #6B7280;
  --bi-text-tertiary: #9CA3AF;
  --bi-border-subtle: #E5E7EB;
  --bi-border-strong: #D1D5DB;
  color-scheme: light;
}

:root[data-theme="dark"] {
  --bi-bg-base: #08090A;         /* void — Linear */
  --bi-bg-layer-1: #0F1011;      /* carbon */
  --bi-bg-layer-2: #161718;      /* obsidian */
  --bi-bg-layer-3: #23252A;      /* graphite — card sobre card, raro */
  --bi-text-primary: #E5E5E6;    /* bone, não branco puro */
  --bi-text-secondary: #8A8F98;  /* fog */
  --bi-text-tertiary: #62666D;   /* ash */
  --bi-border-subtle: #23252A;
  --bi-border-strong: #383B3F;   /* smoke */
  color-scheme: dark;
}
```

Regra: texto primário em dark **não é branco puro** (`#FFFFFF`) — usar um quase-branco (`#E5E5E6`/`#e5e7eb`) reduz glare/eye strain. Branco puro só para o KPI de maior destaque na tela, se necessário.

## 3. Dark-First Real (não é só `prefers-color-scheme`)

Dark-first significa: **o produto abre em dark por padrão**, independente da preferência de SO do usuário — light é a escolha explícita e persistida, igual ao padrão que Linear e Vercel consolidaram. Isso é diferente de "suportar dark mode": é dark ser o tema-âncora do produto.

Implementação:

```html
<!-- SSR: default sempre dark, sem flash -->
<html data-theme="dark">
```

```ts
// theme-store.ts — resolve tema no boot, antes do primeiro paint
function resolveInitialTheme(): "dark" | "light" {
  const stored = typeof window !== "undefined"
    ? localStorage.getItem("bi-theme")
    : null;
  if (stored === "dark" || stored === "light") return stored;
  return "dark"; // default do produto — não é prefers-color-scheme
}
```

`prefers-color-scheme` **não** decide o tema inicial nesta skill — é só um sinal secundário que pode pré-popular o toggle na primeira visita, se o produto quiser esse detalhe. O contrato é: dark é o default de produto, a escolha do usuário (persistida) sempre vence.

### `light-dark()` como reforço (opcional, browsers modernos)

Depois que `color-scheme` está setado corretamente por `data-theme` (acima), `light-dark()` pode simplificar tokens que não precisam de camada:

```css
:root {
  --bi-color-danger: light-dark(#DA1E28, #FA4D56);
  --bi-color-success: light-dark(#198038, #42BE65);
}
```

Não usar `light-dark()` como **substituto** do sistema de `data-theme` acima — ele segue `color-scheme` do elemento, então só funciona corretamente se `color-scheme` já estiver explicitamente setado por tema (como na seção 2), nunca deixado para o navegador inferir sozinho via `prefers-color-scheme`.

## 4. Elevação por Camada (não por sombra)

```
bg-base → bg-layer-1 → bg-layer-2 → bg-layer-3
```

Cada nível sobe um degrau de luminosidade (claro: mais claro → mais escuro que o fundo é raro, geralmente mais claro; escuro: sempre mais claro que o fundo, nunca mais escuro). Nunca pular direto de `bg-base` pra `bg-layer-3` — siga a sequência. Máximo 3 níveis de profundidade visual numa mesma tela (card dentro de card dentro de card é antipattern, ver `anti-patterns-and-scope.md`).

## 5. Paleta Categórica — Dado, Não UI

Escolha **uma** das duas abaixo por produto. Nunca misturar as duas na mesma tela.

### Observable 10 — default recomendado
Testada explicitamente para claro **e** escuro simultaneamente (ajuste de luminosidade do laranja no claro, do verde no escuro).

```
--bi-cat-1: #4269d0;  --bi-cat-2: #efb118;  --bi-cat-3: #ff725c;
--bi-cat-4: #6cc5b0;  --bi-cat-5: #3ca951;  --bi-cat-6: #ff8ab7;
--bi-cat-7: #a463f2;  --bi-cat-8: #97bbf5;  --bi-cat-9: #9c6b4e;
--bi-cat-10: #9498a0;
```

### Tableau 10 — alternativa (paridade com relatório/migração existente)
Mais quente, tom "vintage sofisticado" — Tableau reformulou de propósito pra sair do "Crayola bright".

```
--bi-cat-1: #4e79a7;  --bi-cat-2: #f28e2c;  --bi-cat-3: #e15759;
--bi-cat-4: #76b7b2;  --bi-cat-5: #59a14f;  --bi-cat-6: #edc949;
--bi-cat-7: #af7aa1;  --bi-cat-8: #ff9da7;  --bi-cat-9: #9c755f;
--bi-cat-10: #bab0ab;
```

**Regra de uso**: exibir no máximo 5-7 cores simultâneas num mesmo gráfico (além disso, distinguibilidade cai — ver `chart-standards.md`). Sempre pegar as cores **em sequência** a partir da `--bi-cat-1`, nunca pular ou escolher aleatoriamente — a ordem foi desenhada pra maximizar contraste entre vizinhas.

**Nunca usar**: D3 `schemeCategory10` cru (`#1f77b4`, `#ff7f0e`...) — mais saturado, não revisado para dark, é o "look Crayola" que Tableau e Observable deliberadamente abandonaram.

## 6. Cores Semânticas (estado, não decoração)

```css
--bi-color-success: #198038;   /* claro */ / #42be65 (escuro)
--bi-color-danger:  #da1e28;   /* claro */ / #fa4d56 (escuro)
--bi-color-warning: #f1c21b;   /* claro */ / #f1c21b (escuro, ajustar contraste)
--bi-color-interactive: #0f62fe; /* único azul do sistema — link, ação primária, seleção */
```

Regra crítica: `--bi-color-interactive` é **reservado** para elemento interativo (link, botão primário, item selecionado) e **nunca** aparece em série categórica de gráfico — evita ambiguidade entre "isso é clicável" e "isso é uma categoria de dado". Mesma regra do Carbon (`$interactive` = Blue 60, fora da paleta de chart). Se a marca tiver uma cor de acento própria (no exemplo da seção 6.1, laranja), o valor desse token passa a ser essa cor em vez de azul — a regra de isolamento continua idêntica, só muda a cor.

## 6.1 Paleta de Marca — Neutros + Acento Único (exemplo: laranja)

> Exemplo: esta seção usa laranja como acento de marca. Troque pelo hex da sua marca; as regras de uso valem para qualquer cor.

No padrão recomendado, a identidade visual da marca **é** a escala neutra das seções 1-2 (branco/off-white/cinza/preto) — nada novo a definir aí. O único acréscimo é um **acento único** (aqui, laranja), usado em doses pequenas e propositais. Isso não é uma paleta de marca *paralela* à lógica de cor do sistema — é o mesmo princípio "cor só para dado e estado" (`SKILL.md` §2), só que o slot de "interativo" que normalmente seria azul agora é laranja, porque é essa a cor de identidade da marca do exemplo.

```css
--bi-color-brand-accent: #F97316; /* exemplo (laranja) — substituir pelo hex do manual da sua marca */
--bi-color-interactive: var(--bi-color-brand-accent);
```

### Onde o laranja é bem-vindo (whitelist)

| Contexto | Uso |
|---|---|
| Logo / wordmark | Cor de marca, fora do sistema de tokens de produto |
| Botão de ação primária (CTA) | 1 por tela/seção — nunca 2 CTAs laranja competindo na mesma view |
| Link / texto clicável | Cor de texto em `:hover`/estado ativo, opcional em repouso |
| Foco de teclado (`:focus-visible`) | Outline/ring — reforça acessibilidade e usa a cor de marca ao mesmo tempo |
| Indicador de item ativo em nav | Ícone/texto na cor, **ou** barra fina de 2px (nunca barra grossa — ver nota abaixo) |
| Badge de destaque pontual ("Novo", "Beta", contador de notificação) | Uso raro, 1 elemento por tela |

### Onde o laranja **não entra** (blacklist — é aqui que a lógica de dado fica protegida)

- **Série categórica de gráfico.** A paleta de `--bi-cat-1..10` (seção 5) já tem sua própria cor laranja/âmbar em posição fixa (`--bi-cat-2` em ambas Observable 10 e Tableau 10) — isso é dado do teste de acessibilidade da paleta, não é o laranja de marca, e os dois **não devem ser o mesmo hex**. Se o laranja de marca e `--bi-cat-2` ficarem parecidos demais, um usuário pode confundir "isso é uma categoria no gráfico" com "isso é um botão/CTA da marca". Escolher tons perceptualmente distintos (ex.: marca mais vermelho-alaranjada e saturada; `--bi-cat-2` mais âmbar/amarelada) resolve isso — não precisa trocar a paleta categórica testada.
- **Estado semântico de warning.** `--bi-color-warning` (seção 6) continua sendo o token funcional de alerta, independente de parecer laranja/âmbar também — os dois podem coincidir em tom por acaso, mas são conceitualmente diferentes (um é identidade, o outro é estado) e **nunca se substituem um pelo outro** no código: não usar `--bi-color-brand-accent` onde a semântica pede `--bi-color-warning`, e vice-versa.
- **Fundo de área grande** (hero, card inteiro, sidebar inteira tingida de laranja). Acento é traço fino, texto, ícone ou botão pontual — nunca superfície.
- **Mais de 1 elemento de destaque em laranja por tela.** Se a tela já tem um CTA laranja, o badge "Novo" ao lado não é laranja também — vira cinza/neutro. Concorrência de acento dilui o próprio acento.
- **Dentro de tabela/KPI como cor de dado** — número, delta, badge de status seguem as regras normais das seções 5-6 (categórica ou semântica), nunca a cor de marca.

## 7. Checklist Rápido

- [ ] Zero `linear-gradient`/`radial-gradient` em `background` de superfície de produto.
- [ ] Zero hex hardcoded fora deste arquivo de token.
- [ ] `data-theme="dark"` é o default de SSR/boot, light é override persistido.
- [ ] Texto primário em dark não é `#FFFFFF` puro.
- [ ] Paleta categórica vem de `--bi-cat-1..10` (Observable 10 ou Tableau 10), nunca inventada.
- [ ] `--bi-color-interactive` nunca aparece como cor de série de dado.
- [ ] Elevação usa `--bi-bg-layer-N`, nunca `box-shadow` colorido em card estático.
- [ ] Laranja de marca (`--bi-color-brand-accent`) só em CTA/link/foco/logo/indicador de ativo — nunca em superfície grande, nunca em série categórica.
- [ ] `--bi-color-brand-accent` e `--bi-cat-2` (laranja/âmbar da paleta categórica) são hexs visualmente distintos, não o mesmo tom.
- [ ] `--bi-color-warning` nunca é substituído pelo laranja de marca no código (são tokens diferentes, mesmo que o tom seja parecido).
- [ ] No máximo 1 elemento em destaque laranja por tela.
