# Iconografia para BI Enterprise

Ícone em dashboard é **rótulo funcional**, não decoração. Esta reference define qual conjunto usar, como dimensionar, e a linha exata entre uso funcional (permitido) e decorativo (banido) — a régua que decide se um card de métrica parece "ferramenta profissional" ou "template gerado por IA".

## Regra de ouro

> Se remover o ícone e a informação continua 100% legível, o ícone era decorativo — remova.
> Se remover o ícone e o usuário perde uma informação (ordem, direção, ação disponível), o ícone é funcional — mantenha.

## 1. Conjunto de Ícones — Qual Escolher

Nunca deixe o modelo "inventar" ícone SVG ad-hoc nem misturar bibliotecas. Escolha **uma única biblioteca por produto** e trave via lint (ver script de auditoria no `SKILL.md`).

| Biblioteca | Pacote | Grid/stroke | Por que | Quando escolher |
|---|---|---|---|---|
| **Tabler Icons** (default recomendado) | `@tabler/icons-react` | 24px grid, stroke 1.5-2px | Maior cobertura (5.900+ ícones) com consistência total; validado por múltiplas fontes 2025-2026 como "a escolha prática para dashboards, admin panels e interfaces data-heavy". MIT. | Produto BI novo, sem vínculo prévio com outro set. **Default desta skill.** |
| **Lucide** | `lucide-react` | 24px grid, stroke 2px (ajustável) | Menor bundle por ícone, geometria mais "estrita" (pareia bem com Inter), é o default do ecossistema shadcn/ui. ISC. | Projeto já usa shadcn/ui ou já tem Lucide instalado em outra parte do app — não duplicar biblioteca. |
| **IBM Carbon Icons** | `@carbon/icons-react` | grid nativo 16/20/24/32px (não escalado — cada tamanho é desenhado à parte), stroke 2px (1.5px em detalhe complexo) | Fidelidade total de linhagem com o design system-mãe desta skill (Carbon). `aria-hidden` por padrão, `size` prop nativa. | Produto já usa componentes Carbon (`@carbon/react`) ou quer fidelidade estrita de pixel-grid. |
| **Phosphor Icons** | `@phosphor-icons/react` | 24px grid multi-peso (thin/light/regular/bold/fill/duotone) | Útil só quando o produto precisa de **estado visual do ícone** (ex.: `regular` para padrão, `fill` para item ativo/selecionado). | Sidebar de navegação com estado ativo/inativo que precisa de ícone preenchido vs contornado. Não usar `duotone` em contexto denso — é ilustrativo, não funcional. |

**Nunca**: `react-icons` (agrega múltiplos sets, quebra consistência de peso/grid entre ícones vizinhos), ícone de fonte (`<i class="fa-...">`, `Material Icons` via ligature), emoji como ícone funcional, SVG desenhado à mão pelo modelo.

### Delivery via `@iconify/react` (opcional)

Se o projeto já tem uma regra de lint que bane import direto de lib de ícone, use `@iconify/react` como camada de entrega on-demand — ele serve os mesmos sets acima por prefixo (`tabler:`, `lucide:`, `carbon:`, `ph:`) sem mudar a decisão de qual set usar:

```tsx
import { Icon } from "@iconify/react";

<Icon icon="tabler:arrow-up-right" width={16} />
```

Isso é uma troca de **mecanismo de import**, não de **critério de escolha de set** — a tabela acima continua valendo.

## 2. Sizing — Trava por Contexto

| Contexto | Tamanho | Alinhamento com texto |
|---|---|---|
| Dentro de célula de tabela densa (sort indicator, status) | 14-16px | Baseline com o texto da célula |
| Botão de toolbar/ação (filtro, exportar, refresh) | 16-20px | Centralizado no touch target de 32-40px |
| Item de navegação em sidebar | 18-20px | Ao lado do label, nunca sozinho em modo expandido |
| Delta de KPI (seta de tendência ↑↓ ao lado do número) | 14-16px, mesma altura do dígito | Inline com o número, cor semântica (verde/vermelho), nunca maior que o número |
| Badge de estado semântico | 12-14px | Inline com o texto do badge |

**Nunca** ultrapassar 20px em ícone dentro de card de métrica (KPI). Ícone grande (24px+) só é aceitável em ilustração de empty state — e mesmo assim monocromático, nunca colorido/duotone.

Regra Carbon aplicada: **16px e 20px são otimizados para parear com corpo de 12-14pt/14-16pt**; não alterar a proporção ícone-texto arbitrariamente.

## 3. Stroke Width — Um Valor Só

Escolha **um** stroke e trave em todo o app (via wrapper/adapter, nunca prop solta por tela):

- `1.5px` — mais leve, editorial (combina com peso 300 de KPI, linha "Stripe")
- `2px` — padrão, mais presente (combina com peso 600 de KPI, linha "Carbon/dense")

Nunca misturar 1.5 e 2 no mesmo layout — ícones de peso visual diferente lado a lado é o mesmo erro que misturar duas fontes de corpo.

## 4. Cor — Monocromático, Segue Texto

Regra Carbon, literal: **"Icons are always a solid, monochromatic color"**. Ícone herda `currentColor` / token de texto (`--bi-color-text-primary` ou `--bi-color-text-secondary`), nunca um hex de accent decorativo.

**Exceções permitidas** (ícone carrega semântica de estado, não decoração):
- Seta de tendência de KPI: cor semântica (`--bi-color-success`/`-danger`) — mas só a seta, nunca o card inteiro tingido.
- Ícone de severidade em badge (erro/alerta/sucesso): cor do token semântico correspondente, sempre acompanhado de texto (nunca cor sozinha carregando o significado — regra de acessibilidade, não repetir só com cor).
- Ícone ativo/selecionado em nav: pode usar `--bi-color-interactive`, o único azul reservado do sistema.

Fora dessas três exceções, ícone é cinza.

## 5. Uso Funcional (permitido) vs Decorativo (banido)

### ✅ Funcional — sempre com propósito de informação/ação
- Indicador de ordenação em header de coluna (seta up/down ao lado do label).
- Chevron de expandir/colapsar linha de tabela, sidebar, accordion de filtro.
- Ícone de ação em toolbar: filtro, exportar, refresh, mais-opções (`⋮`) — sempre com `aria-label`.
- Seta de tendência ao lado de delta numérico em KPI.
- Ícone de severidade dentro de badge de status, sempre com texto ao lado (`⚠ Atrasado`, não só `⚠`).
- Ícone de navegação em sidebar, ao lado do label (nunca ícone sozinho em modo expandido; ok sozinho + `aria-label` em modo colapsado/rail).
- Ícone de busca dentro de input.

### ❌ Decorativo — banido nesta skill
- **Icon tile acima de heading** em card de métrica (quadrado arredondado com ícone centralizado acima do título) — é o template universal de "feature-card gerado por IA", um antipattern conhecido. Se precisar de ícone no card, vai **inline ao lado** do label, nunca empilhado acima.
- Ícone grande decorando header de seção sem função (ex.: ícone de gráfico de barras do lado do título "Vendas").
- Ícone duotone/colorido "só pra ficar bonito" em painel denso.
- Ilustração/mascote em vazio de dado que não seja um empty state real com CTA.
- Ícone repetido em cada card de uma grid idêntica só para "quebrar" o visual (sintoma de grid de cards clonados).

## 6. Acessibilidade

- Ícone puramente decorativo (redundante com texto visível ao lado): `aria-hidden="true"`.
- Ícone que é o **único** conteúdo de um botão (ex.: botão de ícone só, sem label visível): `aria-label` descritivo obrigatório (`aria-label="Exportar tabela"`, não `aria-label="Ícone"`).
- Ícone com significado semântico embutido em texto teria fallback verbal — nunca depender só da forma/cor do ícone para transmitir estado crítico (WCAG: não usar cor como único indicador).
- `@carbon/icons-react` já vem com `aria-hidden="true"` por padrão até você passar `aria-label` — outras libs (Tabler/Lucide/Phosphor) exigem isso explícito no wrapper.

### Wrapper canônico (aplica a qualquer uma das 4 libs)

```tsx
// icon-adapter.tsx
import type { ComponentType, SVGProps } from "react";

type IconWrapperProps = SVGProps<SVGSVGElement> & {
  icon: ComponentType<SVGProps<SVGSVGElement>>;
  label?: string;
  size?: 14 | 16 | 18 | 20;
};

export function BiIcon({ icon: Icon, label, size = 16, ...props }: IconWrapperProps) {
  return (
    <Icon
      width={size}
      height={size}
      strokeWidth={2}
      aria-hidden={!label}
      aria-label={label}
      role={label ? "img" : undefined}
      focusable={false}
      {...props}
    />
  );
}
```

```tsx
// uso funcional (com label, ícone é o único conteúdo do botão)
<button aria-label="Exportar tabela">
  <BiIcon icon={IconDownload} label="Exportar tabela" size={16} />
</button>

// uso funcional (redundante com texto visível — decorativo pro leitor de tela)
<span className="table-header-cell">
  Receita <BiIcon icon={IconArrowUp} size={14} />
</span>
```

## 7. Checklist Rápido

- [ ] Só uma biblioteca de ícone instalada e usada no projeto (`audit_bi_tokens.mjs` sinaliza import misto).
- [ ] Todo ícone passa pelo wrapper canônico (`BiIcon` ou equivalente do projeto) — nunca import direto na tela.
- [ ] Nenhum ícone > 20px dentro de card de KPI.
- [ ] Nenhum ícone com cor hex hardcoded — sempre `currentColor`/token.
- [ ] Nenhum "icon tile acima de heading" em card de métrica.
- [ ] Todo botão ícone-só tem `aria-label`.
- [ ] Stroke width único no app inteiro (1.5 **ou** 2, não os dois).
