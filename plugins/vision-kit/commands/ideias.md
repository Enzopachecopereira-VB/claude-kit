---
description: Gera 30 ideias e refina as 5 melhores via crítica rigorosa (técnica Critique & Refine)
---

Briefing recebido: $ARGUMENTS

Execute o ciclo Critique & Refine:

1. Invoque o subagente `gerador-ideias` passando o briefing acima. Ele deve devolver exatamente 30 ideias numeradas em tabela.
2. Passe as 30 ideias geradas, na íntegra, para o subagente `juiz-ideias` avaliar.
3. Apresente ao usuário: a tabela completa de notas/críticas do juiz e a seção Top 5 refinadas.
4. Se o usuário responder "de novo" (ou equivalente), identifique quais ângulos (literal, metafórico, provocativo, minimalista, inesperado) tiveram a melhor média no lote anterior, peça ao `gerador-ideias` um novo lote de 30 ideias focado nesses ângulos, e repita a avaliação com o `juiz-ideias`.

Não gere ideias você mesmo — a geração é sempre delegada ao `gerador-ideias`, e a avaliação sempre ao `juiz-ideias`.
