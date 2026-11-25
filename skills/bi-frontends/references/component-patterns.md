# Padrões de Componente — KPI Card, Tabela Densa, Shell de Admin, Estados

## 1. KPI Card — Anatomia

```
┌─────────────────────────────┐
│ RECEITA TOTAL                │  ← rótulo: 11px, uppercase, tracked, --bi-text-secondary
│ R$ 284.921,00      +12.4% ↑ │  ← valor: tabular-nums, peso 600 (ou 300 editorial) + delta semântico
│ vs. período anterior         │  ← contexto: 12px, --bi-text-tertiary
└─────────────────────────────┘
```

```tsx
function KpiCard({ label, value, delta, context }: KpiCardProps) {
  const isPositive = delta > 0;
  return (
    <div className="bi-card bi-kpi-card">
      <span className="bi-label">{label}</span>
      <div className="bi-kpi-row">
        <span className="bi-kpi-value">{formatCurrency(value)}</span>
        <span
          className={cn(
            "bi-kpi-delta",
            isPositive ? "bi-kpi-delta--positive" : "bi-kpi-delta--negative"
          )}
        >
          {isPositive ? "+" : ""}
          {delta.toFixed(1)}%
        </span>
      </div>
      {context && <span className="bi-kpi-context">{context}</span>}
    </div>
  );
}
```

Regras de anatomia:
- Sem ícone acima do rótulo ("icon tile stacked above heading" — banido, ver `iconography.md`).
- Sem gradiente de fundo ou de texto no valor.
- Delta é opcional mas, quando presente, sempre com sinal explícito e cor semântica.
- `border`, não `box-shadow` (ver `spacing-density-elevation.md`).

## 2. Tabela Densa

```tsx
<table className="bi-table">
  <thead className="bi-table-head--sticky">
    <tr>
      <th className="bi-table-header" scope="col">Cliente</th>
      <th className="bi-table-header bi-table-header--numeric" scope="col">
        Receita <SortIcon />
      </th>
      <th className="bi-table-header" scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr className="bi-table-row">
      <td className="bi-table-cell">Acme Corp</td>
      <td className="bi-table-cell bi-table-cell--numeric">R$ 12.480,00</td>
      <td className="bi-table-cell"><StatusBadge status="active" /></td>
    </tr>
  </tbody>
</table>
```

```css
.bi-table-head--sticky {
  position: sticky;
  top: 0;
  background: var(--bi-bg-layer-1);
  z-index: 1;
  border-bottom: 1px solid var(--bi-border-strong);
}
.bi-table-header {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--bi-text-secondary);
  padding: 8px 12px;
  text-align: left;
}
.bi-table-header--numeric,
.bi-table-cell--numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.bi-table-cell {
  padding: 8px 12px;
  font-size: 13px;
  color: var(--bi-text-primary);
  border-bottom: 1px solid var(--bi-border-subtle);
}
.bi-table-row:hover {
  background: var(--bi-bg-layer-2);
}
```

Regras:
- Header de coluna numérica alinhado à direita, header textual à esquerda — nunca centralizado (convenção universal de tabela financeira).
- `sticky` header em tabela com scroll — nunca perder contexto de coluna ao rolar centenas de linhas.
- Zebra striping (linha alternada) é **opcional** e só em tabela muito densa sem outra forma de guiar o olho — hover state geralmente já basta.
- Linha vazia/sem dado: célula mostra `—` (em-dash único), não string vazia nem `null`/`undefined` literal.

## 3. Shell de Admin — Sidebar + Topbar

```
┌────────┬──────────────────────────────────────┐
│        │  Topbar: breadcrumb, filtros, busca    │
│ Side   ├──────────────────────────────────────┤
│  bar   │                                        │
│        │  Conteúdo (grid de KPI, tabela, chart) │
│  nav   │                                        │
└────────┴──────────────────────────────────────┘
```

- Sidebar: item de nav com ícone (16-20px) + label; modo colapsado (rail) mostra só ícone com `aria-label`.
- Item ativo: `--bi-color-interactive` no ícone/texto + fundo `--bi-bg-layer-2`. Indicador extra opcional: barra fina de **2px** (`border-left: 2px solid var(--bi-color-interactive)`) — isso não é o mesmo antipattern de "side-stripe" (que é uma borda **grossa**, 4px+, cobrindo a lateral inteira de um *card de conteúdo* pra indicar status/prioridade). 2px em item de nav é indicador de estado de navegação, não decoração de card — a linha fica em ~90-95% menor de espessura e some com o hover normal do item.
- CTA primário usa o mesmo token: `background: var(--bi-color-interactive); color: var(--bi-bg-base);` — só **um** CTA nesse tom por tela/seção (ver `color-system.md` §6.1, whitelist de uso do laranja de marca).
- Topbar: filtros como `Chip`/`Select` compactos, nunca modal para filtro simples (reservar modal pra filtro com 4+ campos relacionados).
- Ambos usam `border-bottom`/`border-right` de 1px pra se separar do conteúdo, nunca sombra.

## 4. Badge de Estado Semântico

```tsx
function StatusBadge({ status }: { status: "active" | "warning" | "error" | "neutral" }) {
  return (
    <span className={cn("bi-badge", `bi-badge--${status}`)}>
      <StatusDot status={status} />
      {statusLabel[status]}
    </span>
  );
}
```

```css
.bi-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--bi-radius-sm);
  font-size: 12px;
  font-weight: 500;
}
.bi-badge--active  { background: color-mix(in srgb, var(--bi-color-success) 12%, transparent); color: var(--bi-color-success); }
.bi-badge--error   { background: color-mix(in srgb, var(--bi-color-danger) 12%, transparent); color: var(--bi-color-danger); }
.bi-badge--warning { background: color-mix(in srgb, var(--bi-color-warning) 16%, transparent); color: #92700a; }
.bi-badge--neutral { background: var(--bi-bg-layer-2); color: var(--bi-text-secondary); }
```

Badge sempre carrega **texto**, não só cor/ícone (regra WCAG de não depender só de cor). Fundo em tint suave (12-16% de opacidade da cor semântica), não a cor sólida cheia — mantém a UI predominantemente neutra mesmo com múltiplos badges na tela.

## 5. Empty / Loading / Error States

### Empty
```tsx
<div className="bi-empty-state">
  <p className="bi-empty-state__message">Nenhum dado no período selecionado.</p>
  <button className="bi-button--secondary" onClick={onResetFilters}>
    Limpar filtros
  </button>
</div>
```
Sem ilustração/mascote decorativo. Mensagem direta + ação de recuperação (nunca só "Nenhum dado encontrada" sem próximo passo).

### Loading
Skeleton com mesma geometria do conteúdo final (mesmo grid de KPI card, mesma altura de linha de tabela) — nunca spinner genérico centralizado substituindo um layout inteiro de dashboard.

```css
.bi-skeleton {
  background: var(--bi-bg-layer-2);
  border-radius: var(--bi-radius-md);
  animation: bi-skeleton-pulse 1.5s ease-in-out infinite;
}
@media (prefers-reduced-motion: reduce) {
  .bi-skeleton { animation: none; opacity: 0.6; }
}
```

### Error
```tsx
<div className="bi-error-state" role="alert">
  <p className="bi-error-state__message">Não foi possível carregar os dados.</p>
  <button className="bi-button--secondary" onClick={onRetry}>Tentar novamente</button>
</div>
```
`role="alert"` pra leitor de tela anunciar. Mensagem específica quando possível (timeout, permissão, dado indisponível) em vez de genérica "Algo deu errado".

## 6. Checklist Rápido

- [ ] KPI card sem ícone decorativo acima do rótulo.
- [ ] Header de tabela numérico alinhado à direita, textual à esquerda.
- [ ] Sticky header em tabela com scroll.
- [ ] Item de nav ativo sem side-stripe colorido.
- [ ] Badge sempre com texto, fundo em tint suave (não cor sólida cheia).
- [ ] Skeleton reflete geometria real do conteúdo, respeita `prefers-reduced-motion`.
- [ ] Empty/error state tem ação de recuperação, não é dead-end.
