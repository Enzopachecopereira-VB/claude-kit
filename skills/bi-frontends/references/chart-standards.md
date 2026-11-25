# Padrões de Gráfico — Paleta, Wiring, Regras de Chart Denso

## 1. Engine Canônica: recharts

`recharts` é a engine de chart padrão desta skill (escolha uma engine por projeto; não duplique). Esta reference assume `recharts` como padrão; os mesmos princípios de paleta/regra se aplicam se o projeto usar Observable Plot, ECharts (Superset) ou D3 direto — só muda a sintaxe de wiring.

## 2. Wiring da Paleta Categórica

Nunca hardcode hex direto num componente de chart. Injetar via um `recharts-adapter` que lê os tokens de `color-system.md`:

```ts
// recharts-adapter.ts
export const categoricalPalette = [
  "var(--bi-cat-1)", "var(--bi-cat-2)", "var(--bi-cat-3)",
  "var(--bi-cat-4)", "var(--bi-cat-5)", "var(--bi-cat-6)",
  "var(--bi-cat-7)", "var(--bi-cat-8)", "var(--bi-cat-9)",
  "var(--bi-cat-10)",
] as const;

export function getSeriesColor(index: number): string {
  return categoricalPalette[index % categoricalPalette.length];
}
```

```tsx
// uso em BarChart/LineChart
{series.map((s, i) => (
  <Bar key={s.key} dataKey={s.key} fill={getSeriesColor(i)} />
))}
```

**Nota técnica**: `recharts`/SVG geralmente aceita `var(--token)` em `fill`/`stroke` em browsers modernos; se o projeto precisar de fallback (export de imagem, SSR sem CSS resolvido), resolva os tokens pra hex real no build (ex.: ler de um arquivo `tokens.json` compartilhado entre CSS e o adapter) em vez de duplicar hex manualmente nas duas pontas.

## 3. Regra de Contagem — 5-7 Séries Visíveis

Acima de 7 categorias simultâneas num mesmo gráfico, distinguibilidade cai abaixo do que é confiável mesmo em visão normal (pesquisa cross-referenciada: ColorBrewer só oferece paleta categórica colorblind-safe até 4 cores garantidas; acima de 8, é "close to impossible to find colors that can be readily distinguished"). Acima de 7:

- Agrupar categorias menores em "Outros".
- Trocar de `BarChart`/`LineChart` categórico para pequenos múltiplos (small multiples) — vários gráficos simples em vez de um gráfico com muitas séries sobrepostas.
- Usar ordenação + destaque (1 série em cor, resto em cinza neutro) quando o ponto é comparar 1 contra o resto.

## 4. Sem Animação em Série Densa

```tsx
<Bar dataKey="value" fill={getSeriesColor(0)} isAnimationActive={false} />
```

Dado não deve ser animado em painel denso de BI — animação de série compete com leitura de dado e atrasa a percepção do valor real em cada refresh/filtro. Animar só o **elemento ao redor** (card que revela, skeleton→conteúdo), nunca a série SVG em si.

## 5. Proibido em Gráfico de BI

- **Chart 3D** (barra 3D, pizza 3D) — distorce proporção, sempre pior leitura que a versão 2D equivalente. Nenhuma das 4 referências (Carbon/Observable/Stripe/Linear) usa 3D.
- **Gradiente de preenchimento** em barra/área como decoração — cor sólida do token categórico. Gradiente é aceitável **só** em heatmap/choropleth genuinamente sequencial (representando intensidade), nunca em barra categórica.
- **Pizza/donut com mais de 5-6 fatias** — vira ilegível; trocar por barra horizontal ordenada.
- **Eixo Y não começando em zero** em gráfico de barra (distorce percepção de magnitude) — exceção só quando explicitamente anotado como "eixo truncado" e justificado (ex.: variação muito pequena em série de linha, nunca em barra).
- **Legenda com mais cores do que o olho consegue mapear de cabeça pro gráfico** — se a série tem nome longo ou mais de 5 itens, preferir rótulo direto na série (`label` no fim da linha) a legenda separada.

## 6. Acessibilidade de Cor

- Nunca codificar estado **só** por cor — combinar com posição, forma, ou rótulo de texto redundante (regra POUR/WCAG 1.4.1).
- Testar a paleta escolhida contra simulação de daltonismo antes de shipar (deuteranopia é a forma mais comum — ~8% dos homens). Observable 10 e Tableau 10 já passaram por essa revisão na origem; se o produto customizar a paleta, repetir o teste.
- Gráfico de linha com múltiplas séries: variar também `strokeDasharray` (linha sólida vs tracejada) quando há mais de 4 séries, não confiar só na cor pra diferenciação.
- Tooltip de chart deve ter contraste suficiente (usar `--bi-bg-layer-2` + `--bi-text-primary`, nunca fundo semi-transparente sobre o próprio gráfico).

## 7. Tooltip e Legend — Padrão

```tsx
<Tooltip
  contentStyle={{
    background: "var(--bi-bg-layer-2)",
    border: "1px solid var(--bi-border-subtle)",
    borderRadius: "var(--bi-radius-md)",
    fontSize: "13px",
  }}
  itemStyle={{ fontVariantNumeric: "tabular-nums" }}
/>
<Legend
  wrapperStyle={{ fontSize: "12px", color: "var(--bi-text-secondary)" }}
/>
```

Valores dentro do tooltip seguem a mesma regra de `tabular-nums` de `typography.md` — é o lugar onde o usuário mais frequentemente compara números lado a lado.

## 8. Tabela de Decisão — Qual Paleta

| Situação | Paleta |
|---|---|
| Produto novo, sem paridade visual prévia | **Observable 10** (default) |
| Produto migrando de/paridade com relatório Tableau existente | Tableau 10 |
| Produto já usa `@carbon/charts` ou é literalmente Carbon-based | Paleta categórica nativa do Carbon Charts (sequência de 14, via lib — não copiar hex manualmente) |
| Heatmap / choropleth (sequencial, não categórico) | Escala sequencial mono-hue (ex.: Carbon "Blues"), nunca a paleta categórica |
| Diverging (variação positiva/negativa contra um centro) | Escala diverging de 2 hues (ex.: vermelho↔azul ou vermelho↔verde só se não houver contexto de daltonismo crítico) |

## 9. Checklist Rápido

- [ ] Paleta vem de `getSeriesColor()`/tokens, nunca hex hardcoded no componente de chart.
- [ ] Máximo 7 séries visíveis simultâneas; acima disso, agrupar ou trocar de visualização.
- [ ] `isAnimationActive={false}` em série de dado denso.
- [ ] Nenhum gráfico 3D, nenhum gradiente decorativo de preenchimento.
- [ ] Eixo Y de barra começa em zero.
- [ ] Estado nunca depende só de cor (forma/posição/texto redundante presente).
- [ ] Tooltip usa `tabular-nums` e token de superfície, não fundo transparente.
