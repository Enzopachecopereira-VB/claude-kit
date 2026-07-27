---
description: Pesquisa profunda + verificação cruzada de fatos, com relatório de inteligência final
---

Alvo: $ARGUMENTS

Execute o pipeline de inteligência:

1. Invoque `pesquisador-profundo` sobre o alvo acima. Ele salva os achados brutos em `research/<alvo>-bruto.md`.
2. Passe esse arquivo para `verificador-fatos` validar cada afirmação.
3. Monte o relatório final em `research/<alvo>-relatorio.md` com as seções:
   - **Resumo executivo** (5 linhas)
   - **Fatos verificados** (somente os marcados ✅ pelo verificador)
   - **Pontos de conversa / ganchos** (ângulos úteis derivados dos fatos verificados)
   - **Red flags e contradições** (o que veio como ⚠️, com a divergência explicada)
   - **Lacunas** (o que ficou ❌ ou "não encontrado" na pesquisa bruta)
4. Inclua no relatório final SOMENTE o que passou pela verificação — afirmações ❌ não entram como fato, só na seção de lacunas.

Apresente o relatório ao usuário ao final.
