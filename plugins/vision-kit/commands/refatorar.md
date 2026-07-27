---
description: Migração/refatoração em larga escala — explorar, planejar, codar em fatias, verificar cada fatia
---

Objetivo: $ARGUMENTS

Execute o ciclo completo:

1. Invoque `explorador-codebase` para mapear a base em relação ao objetivo acima. Ele salva `refactor/mapa.md`.
2. Invoque `planejador-migracao` para transformar o mapa em `refactor/plano.md`, um plano em fatias pequenas.
3. Para cada fatia do plano, em ordem, faça o loop:
   a. Invoque `migrador` para executar a fatia.
   b. Invoque `verificador-migracao` para validar (build + testes + lint).
   c. Se houver erro, devolva a lista de correções ao `migrador` e repita a verificação. Só avance para a próxima fatia quando `verificador-migracao` aprovar.
4. A cada 3 fatias concluídas com sucesso, pare e peça revisão do usuário antes de continuar para as próximas.

Nunca pule a etapa de verificação entre fatias, mesmo que a mudança pareça simples.
