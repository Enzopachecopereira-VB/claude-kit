---
description: Prototipagem visual animada — gera a partir de briefing/Figma, audita e aplica ajustes
---

O que prototipar (+ link/nó do Figma opcional): $ARGUMENTS

Execute o ciclo:

1. Invoque `designer-visual` para criar o protótipo/componente a partir do pedido acima (usando o Figma via MCP se um link/nó foi fornecido).
2. Invoque `revisor-design` para auditar o resultado contra `docs/identidade-visual.md` e o checklist de movimento/performance/acessibilidade.
3. Se houver ajustes pendentes, invoque `designer-visual` novamente para aplicá-los.
4. Ao final, mostre ao usuário as instruções para rodar o preview localmente (comando de dev server do projeto, ou como abrir o arquivo diretamente se for um componente isolado).
