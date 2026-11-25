# Problemas Comuns - Next.js 16 Troubleshooting

Guia de troubleshooting para os problemas mais frequentes ao trabalhar com Next.js 16, React 19.2, Tailwind v4 e shadcn/ui.

---

## Problema: Tailwind CSS Não Está Sendo Aplicado

**Sintomas:**
- Componentes aparecem sem estilos
- Cores, bordas e espaçamento não são renderizados
- Classes Tailwind não têm efeito visual
- Browser dev tools mostra nenhuma estilização

**Causa:**
Arquivo `postcss.config.mjs` ausente ou configurado incorretamente. Tailwind v4 mudou completamente a arquitetura do PostCSS.

**Solução:**

1. Instale o plugin PostCSS correto:
```bash
npm install -D @tailwindcss/postcss
```

2. Crie `postcss.config.mjs` na raiz do projeto:
```javascript
// postcss.config.mjs
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {}, // IMPORTANTE: usar @tailwindcss/postcss
  },
};

export default config;
```

3. Verifique `app/globals.css` usa sintaxe v4:
```css
/* app/globals.css */
@import "tailwindcss"; /* Correto para v4 */
/* NÃO usar: @tailwind base, components, utilities */

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  /* ... CSS variables */
}

body {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}
```

4. Limpe cache e rebuild:
```bash
rm -rf .next node_modules/.cache
npm run build
```

5. Se persistir, verifique `tailwind.config.ts`:
```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
```

---

## Problema: Erro "@import com @tailwind Directives"

**Sintomas:**
```
Error: Cannot apply unknown utility class border-border
Error: It looks like you're trying to use `@tailwind` directives...
```

**Causa:**
Mistura de sintaxe Tailwind v3 (antiga) com v4 (nova). Ou uso de `@apply` com CSS variables que não é suportado.

**Solução:**

1. Remova `@tailwind` directives do CSS:
```css
/* ❌ ERRADO - v3 sintaxe */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ✅ CORRETO - v4 sintaxe */
@import "tailwindcss";
```

2. Não use `@apply` com classes customizadas:
```css
/* ❌ ERRADO */
* {
  @apply border-border;
}

/* ✅ CORRETO */
* {
  border-color: hsl(var(--border));
}
```

3. Se usar `@layer`, remova:
```css
/* ❌ ERRADO */
@layer components {
  .btn { @apply px-4 py-2; }
}

/* ✅ CORRETO - escrever CSS normal */
.btn {
  padding-left: 1rem;
  padding-right: 1rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
```

4. Rebuild:
```bash
npm run build
```

---

## Problema: PostCSS Config não é Reconhecido

**Sintomas:**
```
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin.
The PostCSS plugin has moved to a separate package...
```

**Causa:**
Usando `tailwindcss` como plugin ao invés de `@tailwindcss/postcss`.

**Solução:**

1. Instale o pacote correto:
```bash
npm install -D @tailwindcss/postcss
npm remove -D tailwindcss # se estava como dev dependency
```

2. Atualize `postcss.config.mjs`:
```javascript
const config = {
  plugins: {
    '@tailwindcss/postcss': {}, // ✅ CORRETO
    // tailwindcss: {}, // ❌ ERRADO
  },
};

export default config;
```

3. Certifique que `tailwindcss` está instalado como dependency:
```bash
npm install tailwindcss
```

4. Rebuild:
```bash
npm run build
```

---

## Problema: Next.js 16 reactCompiler Configuração Incorreta

**Sintomas:**
```
Error: Unrecognized key(s) in object: 'reactCompiler' at experimental
```

**Causa:**
No Next.js 16, `reactCompiler` não é mais experimental. Tentar usar `experimental.reactCompiler` causa erro.

**Solução:**

1. Atualize `next.config.ts`:
```typescript
// ❌ ERRADO - Next.js 15 e anterior
const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};

// ✅ CORRETO - Next.js 16
const nextConfig: NextConfig = {
  reactCompiler: true,
};

export default nextConfig;
```

2. Instale o Babel plugin se necessário:
```bash
npm install -D babel-plugin-react-compiler
```

3. Rebuild:
```bash
npm run build
```

---

## Problema: darkMode Configuration Error

**Sintomas:**
```
Type error: Object literal may only specify known properties,
and 'darkMode' does not exist in type 'Config'.
Ou classes dark: não são aplicadas.
```

**Causa:**
Usar `darkMode` como array (`["class"]`) ao invés de string (`"class"`).

**Solução:**

1. Atualize `tailwind.config.ts`:
```typescript
// ❌ ERRADO
const config: Config = {
  darkMode: ["class"], // Array causa tipo error
};

// ✅ CORRETO
const config: Config = {
  darkMode: "class", // String
};

export default config;
```

2. No layout raiz, adicione suporte a dark mode:
```typescript
// app/layout.tsx
'use client';

import { useEffect, useState } from 'react';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Detectar preferência do sistema
    const isDarkMode = window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches;
    setIsDark(isDarkMode);
  }, []);

  return (
    <html lang="pt-BR" className={isDark ? 'dark' : ''}>
      <body>{children}</body>
    </html>
  );
}
```

3. Rebuild:
```bash
npm run build
```

---

## Problema: Radix UI / shadcn/ui Componentes Não Funcionam

**Sintomas:**
- Componentes não renderizam
- Accordion não expande/colapsa
- Dropdown menu não abre
- Dialog não aparece
- Nenhum erro no console

**Causa:**
Context API mal implementado ou refs incorretas no componente.

**Solução:**

Exemplo com Accordion:

```typescript
// components/ui/accordion.tsx
'use client';

import React, { createContext, useState, useContext } from 'react';

// Contexto para accordion
const AccordionContext = createContext<{
  openItems: Set<string>;
  toggleItem: (value: string) => void;
}>({ openItems: new Set(), toggleItem: () => {} });

// Contexto para item específico
const AccordionItemContext = createContext<string>('');

export function Accordion({ children }: { children: React.ReactNode }) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggleItem = (value: string) => {
    const newItems = new Set(openItems);
    if (newItems.has(value)) {
      newItems.delete(value);
    } else {
      newItems.add(value);
    }
    setOpenItems(newItems);
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggleItem }}>
      <div className="border rounded-lg">
        {children}
      </div>
    </AccordionContext.Provider>
  );
}

export function AccordionItem({
  value,
  children,
}: {
  value: string;
  children: React.ReactNode;
}) {
  return (
    <AccordionItemContext.Provider value={value}>
      <div>{children}</div>
    </AccordionItemContext.Provider>
  );
}

export function AccordionTrigger({
  children,
}: {
  children: React.ReactNode;
}) {
  const { openItems, toggleItem } = useContext(AccordionContext);
  const itemValue = useContext(AccordionItemContext);
  const isOpen = openItems.has(itemValue);

  return (
    <button
      onClick={() => toggleItem(itemValue)}
      className="flex items-center justify-between w-full p-4 font-semibold"
    >
      {children}
      <span className="transform transition-transform">
        {isOpen ? '▼' : '▶'}
      </span>
    </button>
  );
}

export function AccordionContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const { openItems } = useContext(AccordionContext);
  const itemValue = useContext(AccordionItemContext);
  const isOpen = openItems.has(itemValue);

  if (!isOpen) return null;

  return (
    <div className="p-4 border-t bg-gray-50">
      {children}
    </div>
  );
}
```

Uso:

```typescript
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export function FAQ() {
  return (
    <Accordion>
      <AccordionItem value="item-1">
        <AccordionTrigger>O que é a Acme?</AccordionTrigger>
        <AccordionContent>
          A Acme é uma empresa fictícia usada neste exemplo.
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-2">
        <AccordionTrigger>Como entro em contato?</AccordionTrigger>
        <AccordionContent>
          Envie uma mensagem pelo formulário de contato.
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

---

## Problema: Build Falha com Erros Aleatórios

**Sintomas:**
- Build falha em produção mas funciona localmente
- Erros diferentes a cada build
- Cache está corrompido
- Arquivo não encontrado durante build

**Causa:**
Cache do Next.js ou node_modules corrompido.

**Solução:**

```bash
# 1. Limpar todos os caches
rm -rf .next
rm -rf node_modules/.cache
rm -rf dist

# 2. Limpar npm cache
npm cache clean --force

# 3. Reinstalar dependencies
rm package-lock.json
npm install

# 4. Rebuild
npm run build

# 5. Se ainda falhar, check TypeScript
npx tsc --noEmit

# 6. Se ainda falhar, check lint
npm run lint
```

Se build continua falhando:

```bash
# Verificar se há espaço em disco
df -h

# Verificar arquivo específico
ls -la .next/

# Aumentar verbosidade
npm run build -- --debug
```

---

## Problema: TypeScript Errors Aleatórios

**Sintomas:**
```
error TS2307: Cannot find module '@/components/Button'
error TS2304: Cannot find name 'React'
error TS1005: ',' expected
```

**Causa:**
Path alias incorreto ou tsconfig.json fora de sync.

**Solução:**

1. Verifique `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "strict": false,
    "noImplicitAny": false,
    "strictNullChecks": false
  }
}
```

2. Verificar se diretório exists:
```bash
ls -la src/components/Button.tsx
```

3. Reconstruir cache:
```bash
npx tsc --noEmit
```

4. Se usa IDE, restart TypeScript server:
   - VSCode: `Cmd+Shift+P` > "TypeScript: Restart TS Server"

---

## Problema: Imagens não Carregam com next/image

**Sintomas:**
- Imagens não aparecem no browser
- Error no console sobre `remotePatterns`
- Placeholder visível mas imagem não carrega

**Causa:**
Remote image URL não autorizada ou formato inválido.

**Solução:**

1. Configure `next.config.ts`:
```typescript
// next.config.ts
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      {
        protocol: 'https',
        hostname: '**.example.com', // Wildcard
      },
    ],
  },
};

export default nextConfig;
```

2. Use corretamente em componentes:
```typescript
import Image from 'next/image';

export function ProductImage() {
  return (
    <Image
      src="https://images.unsplash.com/photo-123.jpg"
      alt="Descrição da imagem"
      width={400}
      height={300}
      priority={false}
    />
  );
}
```

3. Para imagens locais, use:
```typescript
import localImage from '@/public/images/product.jpg';

export function LocalImage() {
  return (
    <Image
      src={localImage}
      alt="Descrição"
      priority={false}
    />
  );
}
```

4. Rebuild:
```bash
npm run build
```

---

## Problema: Form Submission Não Funciona

**Sintomas:**
- Botão click não dispara action
- Form não valida
- Dados não são salvos
- Nenhum feedback visual

**Causa:**
Server Action não configurada ou Form não usa corretamente.

**Solução:**

1. Configure Server Action:
```typescript
// app/actions/user-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(3, 'Nome muito curto'),
  email: z.string().email('Email inválido'),
});

export async function createUser(formData: FormData) {
  try {
    const rawData = {
      name: formData.get('name'),
      email: formData.get('email'),
    };

    const validatedData = createUserSchema.safeParse(rawData);

    if (!validatedData.success) {
      return {
        success: false,
        error: validatedData.error.errors[0]?.message || 'Dados inválidos',
      };
    }

    await db.user.create({
      data: validatedData.data,
    });

    revalidatePath('/users');

    return { success: true };
  } catch (error) {
    console.error('Error creating user:', error);
    return {
      success: false,
      error: 'Erro ao criar usuário',
    };
  }
}
```

2. Use em Form (Server Component):
```typescript
// app/users/new/page.tsx
import { createUser } from '@/app/actions/user-actions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function NewUserPage() {
  return (
    <form action={createUser} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Nome</Label>
        <Input
          id="name"
          name="name"
          type="text"
          placeholder="Digite o nome"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="seu@email.com"
          required
        />
      </div>

      <Button type="submit">Criar Usuário</Button>
    </form>
  );
}
```

3. Ou use com Client Component e FormData:
```typescript
// app/users/_components/user-form.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createUser } from '@/app/actions/user-actions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export function UserForm() {
  const [isPending, setIsPending] = useState(false);
  const router = useRouter();

  async function handleSubmit(formData: FormData) {
    setIsPending(true);

    try {
      const result = await createUser(formData);

      if (!result.success) {
        toast.error(result.error);
        return;
      }

      toast.success('Usuário criado com sucesso');
      router.push('/users');
    } catch (error) {
      toast.error('Erro ao criar usuário');
      console.error(error);
    } finally {
      setIsPending(false);
    }
  }

  return (
    <form action={handleSubmit} className="space-y-4">
      <Input
        name="name"
        type="text"
        placeholder="Nome"
        required
        disabled={isPending}
      />
      <Input
        name="email"
        type="email"
        placeholder="Email"
        required
        disabled={isPending}
      />
      <Button type="submit" disabled={isPending}>
        {isPending ? 'Criando...' : 'Criar'}
      </Button>
    </form>
  );
}
```

---

## Problema: Componentes Compartilhados Quebram em Rotas Diferentes

**Sintomas:**
- Header funciona em uma página mas não em outra
- Props muda entre rotas
- Estado não persiste entre páginas
- Componente renderiza differently

**Causa:**
Componente assume contexto específico ou está hard-coded para rota particular.

**Solução:**

1. Componentes compartilhados devem ser genéricos:
```typescript
// ❌ ERRADO - hard-coded para dashboard
export function Header() {
  return (
    <header>
      <h1>Dashboard</h1>
      {/* Assume estar no dashboard */}
    </header>
  );
}

// ✅ CORRETO - genérico, reutilizável
type HeaderProps = {
  title: string;
  subtitle?: string;
};

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-3xl font-bold">{title}</h1>
      {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
    </header>
  );
}
```

2. Use em diferentes contextos:
```typescript
// app/dashboard/page.tsx
import { Header } from '@/components/shared/header';

export default function DashboardPage() {
  return (
    <div>
      <Header
        title="Dashboard"
        subtitle="Bem-vindo de volta"
      />
      {/* ... */}
    </div>
  );
}

// app/products/page.tsx
import { Header } from '@/components/shared/header';

export default function ProductsPage() {
  return (
    <div>
      <Header
        title="Produtos"
        subtitle="Gerencie seus produtos"
      />
      {/* ... */}
    </div>
  );
}
```

3. Para contextos específicos, use providers:
```typescript
// app/providers.tsx
'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      {children}
    </ThemeProvider>
  );
}

// app/layout.tsx
import { Providers } from './providers';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## Problema: Environment Variables Não Carregam

**Sintomas:**
```
Error: DATABASE_URL is undefined
process.env.NEXT_PUBLIC_API_URL é null/undefined
Variáveis mudam entre dev e prod
```

**Causa:**
Arquivo `.env.local` falta ou variáveis não são carregadas em build time.

**Solução:**

1. Crie `.env.local` na raiz:
```bash
# .env.local
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
NEXT_PUBLIC_API_URL="https://api.example.com"
```

2. Valide em runtime:
```typescript
// lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url('DATABASE_URL deve ser uma URL válida'),
  NEXT_PUBLIC_API_URL: z.string().url('API_URL deve ser uma URL válida'),
});

export const env = envSchema.parse({
  DATABASE_URL: process.env.DATABASE_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});
```

3. Use no código:
```typescript
import { env } from '@/lib/env';

export async function fetchData() {
  const response = await fetch(`${env.NEXT_PUBLIC_API_URL}/data`);
  return response.json();
}
```

4. Adicione `.env.local` ao `.gitignore`:
```bash
# .gitignore
.env.local
.env.*.local
```

5. Crie `.env.example` para documentar:
```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
NEXT_PUBLIC_API_URL=https://api.example.com
```

---

## Resumo de Verificações Rápidas

Quando algo quebrar, execute nesta ordem:

1. **Build error?** → `npm run build`
2. **TypeScript error?** → `npx tsc --noEmit`
3. **Lint error?** → `npm run lint`
4. **CSS não funciona?** → Verifique `postcss.config.mjs`
5. **Componente não funciona?** → Verifique Context API
6. **Form não funciona?** → Verifique Server Action
7. **Imagens não aparecem?** → Verifique `remotePatterns`
8. **Variáveis indefinidas?** → Verifique `.env.local`

**Última opção**:
```bash
rm -rf .next node_modules/.cache
npm run build
```
