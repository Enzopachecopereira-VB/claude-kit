# Building Next.js Applications

Skill unificada para construir aplicações Next.js modernas e confiáveis com padrões consolidados de arquitetura, componentes e validação.

**Versão:** 1.0.0 | **Categoria:** Frontend Frameworks | **Autor:** Frontend Standards Team

## Quando Usar

- ✅ Setup de projetos Next.js 16+ com App Router
- ✅ Implementar Server Components e Server Actions
- ✅ Configurar Tailwind CSS 4+ com nova sintaxe
- ✅ Integrar shadcn/ui + Radix UI sempre @latest
- ✅ Garantir builds que não quebram
- ✅ Criar interfaces mobile-first com validação completa

## Filosofia

**Sempre @latest:** Esta skill NÃO trava versões. Documenta padrões que funcionam com famílias de versões modernas (Next.js 16.x+, React 19.x+, Tailwind 4.x+).

**Compatível e confiável:** Combina setup moderno com patterns robustos de error handling e validação.

## Stack Base

- Next.js 16.x+ (App Router, Turbopack, Server Components)
- React 19.x+ (React Compiler)
- TypeScript 5.9+ (strict mode)
- Tailwind CSS 4.x+ (nova sintaxe @import)
- shadcn/ui + Radix UI (@latest)
- Zod 3.x+ (validação)
- Vitest 4.x+ (testing)

## Estrutura da Skill

### SKILL.md (Entry Point)
Carrega sempre. Contém princípios fundamentais, breaking changes e referências rápidas.

### References (Carregam sob demanda)

1. **setup-guide.md** - Setup inicial, Tailwind 4 breaking changes, PostCSS config
2. **architecture-patterns.md** - App Router, Server Components, routing conventions
3. **component-patterns.md** - Mobile-first, composição shadcn/ui, slot patterns
4. **error-handling.md** - Error boundaries, validation com Zod, Server Actions
5. **reliability-checklist.md** - Pre-deploy checklist, build verification
6. **common-problems.md** - Troubleshooting Tailwind 4, Next.js 16, patterns

## Princípios Fundamentais

1. **Sempre Compila** - TypeScript strict, 0 errors, type safety
2. **Sempre Builda** - `npm run build` passa antes de deploy
3. **Sempre Com Error Handling** - Error boundaries em rotas críticas
4. **Sempre Validado** - Zod em Server Actions e forms
5. **Sempre Mobile-First** - Responsive desde início com breakpoints
6. **Sempre @latest** - Usa versões mais recentes das dependências

## Instalação Rápida

```bash
npx create-next-app@latest project-name \
  --typescript \
  --tailwind \
  --app \
  --eslint

cd project-name

# Adicionar shadcn/ui
npx shadcn@latest init -d

# Adicionar componentes base
npx shadcn@latest add button dialog form input
```

## Validação de Build

```bash
# Verificar tipos TypeScript
npx tsc --noEmit

# Build de produção
npm run build

# Preview local
npm run preview
```

## Origem

Esta skill é a **unificação consolidada** de duas skills anteriores:

- **nextjs-modern-stack** (917 linhas) - Stack moderna, setup, arquitetura
- **nextjs-reliability** (609 linhas) - Error handling, validação, confiabilidade

**Total reorganizado:** 1,526 linhas com progressive disclosure para melhor navegação.

## Progressive Disclosure

A skill utiliza progressive disclosure: comece com SKILL.md para entender os princípios, depois consulte as references específicas conforme sua necessidade:

- Começando um projeto novo? → setup-guide.md
- Estruturando aplicação? → architecture-patterns.md
- Criando componentes? → component-patterns.md
- Lidando com erros? → error-handling.md
- Antes de deploy? → reliability-checklist.md
- Resolvendo problemas? → common-problems.md

## Conformidade

**Baseado em:** Next.js 16+ docs, React 19+ docs, Tailwind CSS 4+ docs

**Alinhado com:** Padrões Anthropic de criação de skills (creating-skills)

## Changelog

### v1.0.0 (2025-01-18)
- Unificação oficial de nextjs-modern-stack + nextjs-reliability
- Progressive disclosure com 6 references temáticas
- Foco em @latest versions (não trava versões menores)
- Breaking changes Tailwind CSS 4 documentados
- Reliability patterns integrados com error boundaries
- Validação com Zod em Server Actions
- Mobile-first patterns consolidados

