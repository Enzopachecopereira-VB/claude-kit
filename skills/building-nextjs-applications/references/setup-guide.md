# Guia Completo de Setup - Next.js 16 + Tailwind v4 + shadcn/ui

## Sumário
1. [Instalação Inicial](#instalação-inicial)
2. [Dependências Essenciais](#dependências-essenciais)
3. [Configurações Obrigatórias](#configurações-obrigatórias)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Checklist Pré-Deploy](#checklist-pré-deploy)

---

## Instalação Inicial

### Passo 1: Criar Projeto Next.js

```bash
npx create-next-app@latest nome-projeto \
  --typescript \
  --tailwind \
  --app \
  --src-dir=false \
  --import-alias "@/*"

cd nome-projeto
```

**Flags explicadas**:
- `--typescript`: Ativa TypeScript por padrão
- `--tailwind`: Instala Tailwind CSS
- `--app`: Usa App Router (não Pages Router)
- `--src-dir=false`: Coloca `app/` na raiz do projeto
- `--import-alias "@/*"`: Path alias para importações limpas

---

## Dependências Essenciais

### Passo 2: Instalar Dependências Core

```bash
# Atualizar para versões mais recentes
npm install next@latest react@latest react-dom@latest
```

### Passo 3: Instalar Tailwind v4 com Plugin PostCSS

**CRÍTICO**: Tailwind v4 requer o plugin PostCSS separado.

```bash
# Tailwind CSS v4 + plugin PostCSS (OBRIGATÓRIO)
npm install tailwindcss@latest
npm install -D @tailwindcss/postcss
```

**Por que?** No Tailwind v4, a arquitetura mudou. O `@tailwindcss/postcss` é um pacote separado que funciona como plugin PostCSS.

### Passo 4: Instalar React Compiler (OBRIGATÓRIO para Next.js 16)

```bash
npm install -D babel-plugin-react-compiler
```

### Passo 5: Instalar Utilitários para shadcn/ui

```bash
npm install class-variance-authority clsx tailwind-merge lucide-react
```

### Passo 6: Instalar shadcn/ui (Componentes)

```bash
npx shadcn@latest init
```

Quando perguntado, responda:
- **BaseColor**: Escolha a cor base (geralmente `slate`)
- **CSS Variables**: Responda `yes`
- **Dark Mode**: Responda `yes` se quiser dark mode

### Instalação Seletiva de Componentes

```bash
# Instalar apenas o necessário sob demanda
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add form
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

---

## Configurações Obrigatórias

### 3.1 Configurar PostCSS (CRÍTICO)

**Arquivo**: `postcss.config.mjs`

```javascript
// postcss.config.mjs
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {}, // IMPORTANTE: usar @tailwindcss/postcss, NÃO tailwindcss
  },
};

export default config;
```

**Por que `mjs`?** CommonJS pode causar problemas com módulos ES. Use `.mjs` para garantir ES modules.

**ERRO COMUM**:
```javascript
// ❌ ERRADO - Tailwind v4 vai falhar
plugins: {
  tailwindcss: {},
}

// ✅ CORRETO
plugins: {
  '@tailwindcss/postcss': {},
}
```

**Sintomas de erro**:
```
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin.
The PostCSS plugin has moved to a separate package (@tailwindcss/postcss)
```

### 3.2 Configurar Tailwind v4

**Arquivo**: `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class", // IMPORTANTE: string, não array ["class"]
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};

export default config;
```

**MUDANÇAS CRÍTICAS NO TAILWIND V4**:
- ❌ `darkMode: ["class"]` (array) → ✅ `darkMode: "class"` (string)
- ❌ NÃO usar `@tailwind directives` → ✅ Usar `@import "tailwindcss"`
- ❌ NÃO usar `@apply` com variáveis CSS → ✅ Usar CSS puro

### 3.3 Configurar Arquivo Global CSS (Sintaxe Tailwind v4)

**Arquivo**: `app/globals.css`

```css
/* app/globals.css */

/* ✅ NOVA sintaxe Tailwind v4 - IMPORTANTÍSSIMO */
@import "tailwindcss";

/* ❌ NUNCA fazer isso no v4
@tailwind base;
@tailwind components;
@tailwind utilities;
*/

/* Variáveis CSS para o tema */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  --muted: 210 40% 96%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --ring: 221.2 83.2% 53.3%;
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.3% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --ring: 212.7 26.8% 83.9%;
}

/* Reset e estilos base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  border-color: hsl(var(--border)); /* ✅ CSS puro, não @apply */
}

html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
}

/* ❌ NÃO FAZER ISSO - causará erro
* {
  @apply border-border;
}
*/

/* ✅ FAZER ISSO - CSS puro */
* {
  border-color: hsl(var(--border));
}

button {
  cursor: pointer;
}

input,
textarea,
select {
  font-family: inherit;
}

/* Remover setas de input number */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
```

**MUDANÇAS CRÍTICAS**:
- ✅ `@import "tailwindcss"` (nova sintaxe)
- ❌ Nunca usar `@tailwind base`, `@tailwind components`, `@tailwind utilities`
- ✅ CSS puro para border/cores
- ❌ Nunca usar `@apply` com classes que têm variáveis CSS

### 3.4 Configurar TypeScript

**Arquivo**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "noImplicitAny": false,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false,
    "strictNullChecks": false,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src", "app"],
  "exclude": ["node_modules"],
  "ts-node": {
    "compilerOptions": {
      "module": "commonjs"
    }
  }
}
```

### 3.5 Configurar Next.js 16

**Arquivo**: `next.config.ts`

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // React Compiler ativado nativamente (não é mais experimental)
  reactCompiler: true, // ✅ CORRETO no Next.js 16
  // ❌ NÃO usar: experimental: { reactCompiler: true }

  // Configuração de imagens remotas
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },

  // Turbopack habilitado por padrão
  // Nenhuma configuração adicional necessária

  // Você pode adicionar outras configurações aqui se necessário
};

export default nextConfig;
```

**MUDANÇAS DO NEXT.JS 16**:
- ✅ `reactCompiler: true` (agora é primeira classe)
- ❌ `experimental.reactCompiler: true` (removido)
- ✅ Turbopack habilitado por padrão

---

## Estrutura de Pastas

### 4.1 Estrutura App Router Recomendada

```
app/
├── _assets/                    # Assets privados
│   ├── fonts/
│   └── images/
├── (auth)/                     # Route group para autenticação
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx              # Layout compartilhado por auth routes
├── (dashboard)/                # Route group para dashboard
│   ├── _components/            # Componentes privados desta seção
│   │   ├── header.tsx
│   │   └── sidebar.tsx
│   ├── page.tsx                # /dashboard
│   ├── users/
│   │   ├── page.tsx            # /dashboard/users
│   │   ├── [id]/
│   │   │   └── page.tsx        # /dashboard/users/[id]
│   │   └── _components/        # Componentes privados de users
│   │       └── user-table.tsx
│   └── layout.tsx
├── api/                        # Route handlers (usar com moderação)
│   ├── auth/
│   │   └── route.ts
│   └── users/
│       └── route.ts
├── actions/                    # Server Actions centralizadas
│   ├── auth-actions.ts
│   ├── user-actions.ts
│   └── post-actions.ts
├── globals.css                 # Estilos globais (veja 3.3)
├── layout.tsx                  # Root layout
└── page.tsx                    # Home page (/)

components/
├── ui/                         # shadcn/ui components (copiar de lá)
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   ├── form.tsx
│   └── ...
└── shared/                     # Componentes reutilizáveis
    ├── header.tsx
    ├── footer.tsx
    ├── navbar.tsx
    └── ...

lib/
├── db.ts                       # Database client (Prisma/Drizzle/Supabase)
├── utils.ts                    # Funções utilitárias (cn, etc)
├── validations.ts              # Schemas Zod
└── constants.ts                # Constantes da aplicação

public/
├── images/
├── icons/
└── fonts/

.env.local                       # Variáveis de ambiente (NÃO commitar)
.env.example                    # Exemplo de variáveis (commitar)
```

### 4.2 Componentes Privados com Underscore

Use `_components` para componentes privados de uma rota:

```
app/
├── users/
│   ├── page.tsx               # Pode importar de _components
│   ├── [id]/page.tsx          # Pode importar de ../_components
│   └── _components/
│       ├── user-form.tsx
│       └── user-table.tsx     # NÃO aparecem em rotas
```

---

## Checklist Pré-Deploy

Antes de fazer deploy ou compartilhar o projeto, verifique:

- [ ] **postcss.config.mjs** criado com `@tailwindcss/postcss`
  ```bash
  ls postcss.config.mjs
  ```

- [ ] **app/globals.css** usa `@import "tailwindcss"` (não `@tailwind`)
  ```bash
  grep "@import \"tailwindcss\"" app/globals.css
  ```

- [ ] **next.config.ts** tem `reactCompiler: true` (não `experimental`)
  ```bash
  grep "reactCompiler: true" next.config.ts
  ```

- [ ] **tailwind.config.ts** tem `darkMode: "class"` (não array)
  ```bash
  grep "darkMode: \"class\"" tailwind.config.ts
  ```

- [ ] **Nenhum `@apply` com classes customizadas** no CSS
  ```bash
  grep -r "@apply border-" app/
  ```

- [ ] **babel-plugin-react-compiler instalado**
  ```bash
  npm ls babel-plugin-react-compiler
  ```

- [ ] **Build completa sem erros**
  ```bash
  npm run build
  ```

- [ ] **ESLint passa sem erros**
  ```bash
  npm run lint
  ```

---

## Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Iniciar servidor de produção
npm start

# Adicionar componente shadcn
npx shadcn@latest add [component-name]

# Linting e formatação
npm run lint
npm run lint -- --fix

# Limpar cache (quando houver problemas)
rm -rf .next node_modules/.cache
npm run build
```

---

## Problemas Comuns e Soluções

### CSS não está sendo aplicado

**Sintomas**: Componentes aparecem sem estilos, cores ou espaçamento.

**Causas**:
1. `postcss.config.mjs` ausente ou incorreto
2. Tailwind não importado em `globals.css`
3. `@tailwindcss/postcss` não instalado

**Solução**:
```bash
# 1. Instalar o plugin
npm install -D @tailwindcss/postcss

# 2. Verificar postcss.config.mjs
cat postcss.config.mjs

# 3. Verificar globals.css começa com @import "tailwindcss"
head -1 app/globals.css

# 4. Limpar cache e rebuild
rm -rf .next node_modules/.cache
npm run build
```

### Erro: "Cannot apply unknown utility class border-border"

**Sintomas**:
```
Error: Unknown utility class "border-border"
```

**Causa**: Tailwind v4 não suporta `@apply` com classes que usam CSS variables.

**Solução**: Substituir `@apply` por CSS puro:
```css
/* ❌ ERRADO */
* { @apply border-border; }

/* ✅ CORRETO */
* { border-color: hsl(var(--border)); }
```

### Erro: "trying to use tailwindcss directly as PostCSS plugin"

**Sintomas**:
```
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin.
The PostCSS plugin has moved to a separate package...
```

**Solução**: Atualizar `postcss.config.mjs`:
```javascript
const config = {
  plugins: {
    '@tailwindcss/postcss': {}, // ✅ CORRETO
    // tailwindcss: {}, ❌ ERRADO
  },
};
export default config;
```

### Erro: "reactCompiler at experimental"

**Sintomas**:
```
Error: Unrecognized key(s) in object: 'reactCompiler' at experimental
```

**Causa**: Next.js 16 não usa mais `experimental.reactCompiler`.

**Solução**: Atualizar `next.config.ts`:
```typescript
const nextConfig: NextConfig = {
  reactCompiler: true, // ✅ CORRETO
  // experimental: { reactCompiler: true }, ❌ ERRADO
};
```

### darkMode não funciona

**Sintomas**: Classes `dark:` não são aplicadas.

**Causa**: `darkMode` configurado como array ao invés de string.

**Solução**: Verificar `tailwind.config.ts`:
```typescript
const config: Config = {
  darkMode: "class", // ✅ CORRETO - string
  // darkMode: ["class"], ❌ ERRADO - array
};
```

---

## Resumo Final

### Passos Essenciais (1-2 minutos)

1. **Criar projeto**:
   ```bash
   npx create-next-app@latest nome-projeto --typescript --tailwind --app --src-dir=false --import-alias "@/*"
   ```

2. **Instalar dependências**:
   ```bash
   npm install next@latest react@latest react-dom@latest
   npm install -D @tailwindcss/postcss babel-plugin-react-compiler
   npm install class-variance-authority clsx tailwind-merge lucide-react
   npx shadcn@latest init
   ```

3. **Criar postcss.config.mjs** (cópia colada)

4. **Atualizar app/globals.css** com `@import "tailwindcss"`

5. **Atualizar next.config.ts** com `reactCompiler: true`

6. **Build e testar**:
   ```bash
   npm run build
   npm run dev
   ```

Pronto! Projeto Next.js 16 moderno configurado corretamente.
