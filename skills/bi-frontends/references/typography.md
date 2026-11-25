# Tipografia — Stack Neutro, Escala, Tabular-Nums Obrigatório

## 1. Stack Tipográfico

```css
--bi-font-sans: "Inter", "IBM Plex Sans", -apple-system, BlinkMacSystemFont,
  "Segoe UI", system-ui, sans-serif;
--bi-font-mono: "IBM Plex Mono", "Berkeley Mono", ui-monospace, SFMono-Regular,
  Menlo, monospace; /* IDs, hashes, código de erro — não para número de negócio */
```

Uma sans neutra só, sem par de display face. BI não é editorial — a variação de hierarquia vem de **peso e tamanho**, não de trocar de fonte (ver `component-patterns.md` e a regra de "estrutura cria hierarquia, não decoração" do `SKILL.md`).

## 2. `font-variant-numeric: tabular-nums` — Não-Negociável

Todo número em contexto tabular ou de KPI usa tabular-nums. Sem exceção. É o detalhe que separa dashboard profissional de amador — dígitos de mesma largura alinham em coluna; sem isso, "111" e "888" têm larguras visualmente diferentes e a tabela "treme" ao rolar/atualizar.

```css
.bi-table-cell--numeric,
.bi-kpi-value,
.bi-badge--numeric {
  font-variant-numeric: tabular-nums;
}

/* fintech/financeiro: adicionar slashed-zero pra diferenciar 0 de O */
.bi-table-cell--currency {
  font-variant-numeric: tabular-nums slashed-zero;
}
```

Ou via classe utilitária Tailwind: `tabular-nums` (e `slashed-zero` quando aplicável). **Nunca** resolver isso trocando pra fonte monoespaçada inteira — isso deixa o texto ao redor (labels, headers) com aparência de "terminal", que é o efeito colateral que `tabular-nums` evita ao manter letras proporcionais e só travar a largura dos dígitos.

## 3. Escala de Tipo

| Papel | Tamanho | Peso | Line-height | Uso |
|---|---|---|---|---|
| KPI hero | 32-40px | 600 (denso) ou 300 (editorial — ver seção 4) | 1.1 | Métrica principal da tela |
| KPI secundário | 20-24px | 600 | 1.2 | Métricas de apoio em grid de cards |
| Heading de seção | 16-18px | 600 | 1.3 | Título de card/painel |
| Corpo / célula de tabela | 13-14px | 400 | 1.4 | Texto de tabela, descrição |
| Rótulo pequeno (caps) | 11px | 500-600 | 1.2 | Rótulo de KPI, header de coluna |
| Legenda/nota de rodapé | 12px | 400 | 1.4 | Footnote de gráfico, timestamp |

Mínimo absoluto: **12px** em qualquer texto do produto (WCAG/legibilidade). Nunca abaixo disso, nem em legenda.

## 4. Peso de KPI — Dois Modos, Escolher Um

Pesquisa nas 4 referências mostra duas escolas válidas e **opostas** — decidir por produto, documentar a escolha, nunca misturar as duas no mesmo dashboard.

### Modo Denso (recomendado default para BI enterprise)
- Peso **600** no valor do KPI.
- Tracking neutro (0 a -0.01em).
- Efeito: "dado é destaque", mais IBM Carbon / Power BI Fluent 2.
- Usar quando: dashboard operacional, denso, múltiplos KPIs visíveis simultaneamente.

### Modo Editorial (alternativa, estilo Stripe)
- Peso **300** no valor do KPI, tamanho maior para compensar (36-56px).
- Tracking negativo pronunciado (-0.02em a -0.025em em tamanhos grandes).
- Efeito: "confiança silenciosa", leveza como sofisticação.
- Usar quando: dashboard executivo com poucos KPIs por tela, ênfase editorial.

```css
/* modo denso — default */
.bi-kpi-value {
  font-weight: 600;
  letter-spacing: -0.01em;
  font-variant-numeric: tabular-nums;
}

/* modo editorial — opt-in explícito */
.bi-kpi-value--editorial {
  font-weight: 300;
  font-size: 3rem;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}
```

## 5. Rótulos — Caps Pequeno, Tracked

```css
.bi-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--bi-text-secondary);
}
```

Regra: uppercase tracked **só** em rótulo curto (1-3 palavras). Nunca em corpo de texto ou frase — destrói reconhecimento de forma de palavra e é ilegível em frase longa (antipattern conhecido: "All-caps body").

## 6. Delta/Variação — Formatação Consistente

Delta de KPI (`+12.4%`, `-3.1%`) segue as mesmas regras: `tabular-nums`, cor semântica (`--bi-color-success`/`-danger`), sinal sempre explícito (`+` visível em variação positiva, não implícito).

```tsx
<span className="bi-kpi-delta bi-kpi-delta--positive">
  +12.4%
</span>
```

```css
.bi-kpi-delta {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  font-size: 13px;
}
.bi-kpi-delta--positive { color: var(--bi-color-success); }
.bi-kpi-delta--negative { color: var(--bi-color-danger); }
```

## 7. Checklist Rápido

- [ ] Uma sans só (Inter ou IBM Plex Sans) — sem par de display face.
- [ ] `tabular-nums` em toda célula numérica de tabela e todo KPI.
- [ ] `slashed-zero` adicionado em contexto financeiro/fintech.
- [ ] Peso de KPI é consistente no produto inteiro — denso (600) ou editorial (300), nunca os dois.
- [ ] Rótulo uppercase só em texto curto (≤3 palavras), nunca em corpo.
- [ ] Nenhum texto abaixo de 12px.
- [ ] Delta numérico usa cor semântica + sinal explícito, nunca cor sozinha.
