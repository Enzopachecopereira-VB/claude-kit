---
name: building-nextjs-applications
description: Next.js 16+ apps — setup, App Router, RSC, error boundaries, deploy. Stack @latest (React, Tailwind, shadcn).
metadata:
  version: "2.0.0"
  author: "community"
  category: "frontend-frameworks"
  tags: ["nextjs", "react", "typescript", "tailwind", "shadcn", "latest-versions", "reliability"]
references:
  - path: references/setup-guide.md
    description: "Setup inicial com breaking changes críticos e configurações obrigatórias"
  - path: references/architecture-patterns.md
    description: "Padrões App Router, Server Components e estrutura de rotas"
  - path: references/component-patterns.md
    description: "Padrões de componentes limpos e abordagem mobile-first"
  - path: references/error-handling.md
    description: "Error boundaries, loading states e padrões de validação"
  - path: references/reliability-checklist.md
    description: "Checklist pré-deploy e verificação de build"
  - path: references/common-problems.md
    description: "Problemas conhecidos e soluções para Next.js 16+ e Tailwind 4+"
---

# Construindo Aplicações Next.js Modernas e Confiáveis

Stack modernizado para máxima performance, confiabilidade e manutenibilidade em aplicações React.

## Stack Moderna (Sempre @latest)

Sempre use versões mais recentes das dependências. O ecossistema Next.js/React evolui rapidamente com breaking changes, portanto manter-se atualizado é crítico.

**Abordagem**: Instale com `@latest` e documente breaking changes:

```bash
pnpm add next@latest react@latest react-dom@latest
pnpm add -D @tailwindcss/postcss babel-plugin-react-compiler
```

Nunca travar versões patch (ex: 16.0.3). Use ranges (16.x+) para permitir atualizações automáticas seguras.

## Famílias de Versões Suportadas

| Dependência | Versão Mínima | Versão Atual | Notas |
|---|---|---|---|
| Next.js | 16.0.0+ | @latest | Turbopack estável, reactCompiler no top-level |
| React | 19.0.0+ | @latest | React Compiler integrado |
| TypeScript | 5.9.0+ | @latest | Melhor suporte a JSX automaticamente |
| Tailwind CSS | 4.0.0+ | @latest | Nova sintaxe @import, Breaking changes maiores |
| shadcn/ui | latest canary | @canary | Usa versões canary para compatibilidade |

## Instalação Rápida

```bash
# 1. Criar projeto
npx create-next-app@latest meu-projeto \
  --typescript \
  --tailwind \
  --app \
  --src-dir=false \
  --import-alias "@/*"

cd meu-projeto

# 2. Instalar versões mais recentes (OBRIGATÓRIO @latest)
pnpm add next@latest react@latest react-dom@latest

# 3. Tailwind v4 + Plugin PostCSS (CRÍTICO)
pnpm add tailwindcss@latest
pnpm add -D @tailwindcss/postcss

# 4. React Compiler para Next.js 16 (OBRIGATÓRIO)
pnpm add -D babel-plugin-react-compiler

# 5. Utilitários e UI
pnpm add class-variance-authority clsx tailwind-merge lucide-react zod
pnpm add react-hook-form @hookform/resolvers
# Dica: centralize o setup do form num adapter próprio; telas importam do adapter, não da lib

# 6. shadcn/ui (opcional, instala sob demanda)
npx shadcn@canary init
```

## Princípios Fundamentais

### 1. SEMPRE Compila (TypeScript Strict)

```bash
# Verificar antes de commit
npx tsc --noEmit
```

Seu código TypeScript deve ser 100% type-safe. Sem `// @ts-ignore`, sem `any` não intencional, sem tipos implícitos.

### 2. SEMPRE Builda (pnpm build sem erros)

```bash
# Build deve passar SEMPRE
pnpm build

# Se falhar, conserte antes de apresentar
pnpm build 2>&1 | grep -i "error\|failed"
```

NUNCA apresente código que não builda. Se há warnings, verifique se são críticos.

### 3. SEMPRE com Error Handling

```typescript
// Error Boundary obrigatório
export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => console.error('App error:', error), [error]);
  return <div onClick={reset}>Erro. Clique para tentar novamente</div>;
}
```

Toda rota precisa de `error.tsx`, `loading.tsx` e `not-found.tsx` quando apropriado.

### 4. SEMPRE Validado (Zod em Server Actions)

```typescript
// Server Action com validação obrigatória
const schema = z.object({ email: z.string().email() });
const result = schema.safeParse(rawData);
if (!result.success) return { error: result.error };
```

Validação é defesa contra crashes. Use `safeParse`, nunca `parse`.

### 5. SEMPRE Mobile-First

```html
<!-- Começar pequeno, adicionar classes de breakpoint -->
<div class="text-sm sm:text-base md:text-lg lg:text-xl">
```

Desenvolva e teste em mobile PRIMEIRO. Responsividade não é opcional.

## Quando Consultar as References

- **setup-guide.md**: Antes de começar novo projeto. Contém configurações críticas de PostCSS, Tailwind v4, Next.js 16.
- **architecture-patterns.md**: Decidir entre Server/Client Components, estruturar rotas, organizar App Router.
- **component-patterns.md**: Criar componentes limpos com mobile-first, shadcn/ui, padrões reutilizáveis.
- **error-handling.md**: Implementar error boundaries, loading states, validação com Zod.
- **reliability-checklist.md**: Antes de deploy, verificar todos os itens do checklist.
- **common-problems.md**: Quando encontrar erro, procure por nome (ex: "Cannot apply unknown utility class").

## Breaking Changes Críticos (3 principais)

### 1. Tailwind CSS 3 → 4: Nova Sintaxe @import

**Antes (Tailwind v3):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Agora (Tailwind v4):**
```css
@import "tailwindcss";
```

PostCSS config OBRIGATÓRIO:
```javascript
// postcss.config.mjs
export default {
  plugins: { '@tailwindcss/postcss': {} }, // Use @tailwindcss/postcss, NÃO tailwindcss
};
```

**Impacto**: CSS não funciona sem `@tailwindcss/postcss` instalado e configurado.

### 2. Next.js 16: reactCompiler no Top-Level

**Antes (Next.js 15):**
```typescript
experimental: { reactCompiler: true }
```

**Agora (Next.js 16):**
```typescript
const nextConfig = {
  reactCompiler: true, // Direto, não em experimental
};
```

**Impacto**: Configuração experimental removida. Use `reactCompiler` diretamente.

### 3. PostCSS: @tailwindcss/postcss é Separado

**Antes**: Tailwind era o plugin direto de PostCSS.

**Agora**: Precisa instalar `@tailwindcss/postcss` como dependência de dev:

```bash
pnpm add -D @tailwindcss/postcss
```

**Impacto**: Sem este pacote, Tailwind CSS não processa nenhum estilo.

## Princípio de Versões

**Máxima Estabilidade**: Use ranges que permitem patch updates (seguro):
```json
{
  "next": "16.x",
  "react": "19.x",
  "tailwindcss": "4.x"
}
```

**NÃO Faça Isso** (travando patch versions):
```json
{
  "next": "16.0.3",
  "react": "19.0.0"
}
```

Versões patch são seguras. Minor e Major podem ter breaking changes. Use `pnpm outdated` regularmente.

## Estrutura de Projeto Recomendada

```
app/
├── (auth)/                 # Route groups
│   ├── login/page.tsx
│   └── layout.tsx
├── (dashboard)/
│   ├── page.tsx           # Server Component padrão
│   ├── _components/       # Privados da rota
│   ├── error.tsx          # Error boundary
│   ├── loading.tsx        # Loading state
│   └── layout.tsx
├── api/                   # Route Handlers (moderadamente)
├── actions/               # Server Actions centralizadas
├── layout.tsx
├── error.tsx              # Root error boundary
├── not-found.tsx          # Catch-all 404
└── page.tsx               # Home

components/
├── ui/                    # shadcn/ui (você customiza)
└── shared/                # Componentes reutilizáveis

lib/
├── db.ts                  # Database client
├── utils.ts               # Utilitários (cn, etc)
└── validations.ts         # Zod schemas
```

## Checklist de Confiabilidade

Antes de apresentar qualquer código:

- [ ] `pnpm build` passa sem erros
- [ ] `npx tsc --noEmit` sem erros de tipo
- [ ] `pnpm lint` sem avisos críticos
- [ ] error.tsx implementado nas rotas principais
- [ ] Server Actions com `safeParse` e try/catch
- [ ] Componentes têm tipos TypeScript completos
- [ ] Sem `// @ts-ignore` ou `any` não intencional
- [ ] Responsividade testada em mobile, tablet e desktop
- [ ] Loading e empty states implementados

## Exemplo Mínimo de Deploy-Ready

```typescript
// app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Minha App',
};

export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}

// app/page.tsx (Server Component padrão)
export default async function Home() {
  return <div className="p-4 md:p-8">Olá mundo!</div>;
}

// app/error.tsx (Error boundary obrigatório)
'use client';
export default function Error({ error, reset }) {
  return (
    <div onClick={reset}>
      Erro: {error.message}
    </div>
  );
}

// postcss.config.mjs (CRÍTICO)
export default {
  plugins: { '@tailwindcss/postcss': {} },
};

// next.config.ts (Next.js 16)
const nextConfig = {
  reactCompiler: true,
};
export default nextConfig;
```

## Filosofia: Sempre @latest, Sempre Confiável

1. **@latest é seguro**: Patches (16.0.x → 16.0.y) não quebram. Minors (16.x → 16.y) podem quebrar. Majors (16 → 17) quebram com certeza. Fique atualizado com minors ao menos.
2. **Documentação é garantia**: Se breaking change ocorrer, documentação está nos links de referência.
3. **Validação previne crashes**: Zod, TypeScript strict e error boundaries são seu seguro de vida.
4. **Build é verdade**: Se `pnpm build` passa, o código funciona em produção (na maioria dos casos).

---

**Consulte as references para detalhes completos sobre setup, padrões e troubleshooting.**

**Última atualização**: 2025-11-18 (vendored — stack é @latest; verifique as versões atuais ao usar)
**Próximas atualizações**: Quando houver major version change (Next.js 17, React 20, Tailwind 5)
