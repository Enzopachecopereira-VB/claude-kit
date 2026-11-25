# Padrões de Arquitetura - Next.js 16 App Router

## Sumário
1. [Estrutura App Router](#estrutura-app-router)
2. [Server Components vs Client Components](#server-components-vs-client-components)
3. [Padrão de Layouts](#padrão-de-layouts)
4. [Route Groups](#route-groups)
5. [Server Actions](#server-actions)
6. [Data Fetching Patterns](#data-fetching-patterns)
7. [Parallel Routes](#parallel-routes)

---

## Estrutura App Router

### O Que é App Router?

O App Router (introduzido no Next.js 13) é o novo sistema de roteamento baseado em diretórios. Cada arquivo `page.tsx` dentro de `app/` se torna uma rota.

### Mapeamento de Arquivos para Rotas

```
app/
├── page.tsx                    → /
├── about/
│   └── page.tsx                → /about
├── blog/
│   ├── page.tsx                → /blog
│   └── [slug]/
│       └── page.tsx            → /blog/[slug]
└── api/
    └── users/
        └── route.ts            → GET/POST /api/users
```

### Segmentos Dinâmicos

```
app/
├── users/
│   └── [id]/
│       └── page.tsx            → /users/1, /users/2, etc

├── blog/
│   └── [...slug]/
│       └── page.tsx            → /blog/2024/01/artigo, /blog/tech
```

**Tipos de segmentos**:
- `[id]` - Um segmento dinâmico
- `[...slug]` - Catch-all (múltiplos segmentos)
- `[[...slug]]` - Opcional catch-all

---

## Server Components vs Client Components

### Por Que Importa?

O Next.js 16 tem uma filosofia clara:
- **Server Components por padrão** = performance, segurança, menor JS enviado
- **Client Components quando necessário** = interatividade, hooks, eventos do navegador

### Server Component (Padrão)

Um Server Component é renderizado apenas no servidor. Não tem acesso a hooks do React ou APIs do navegador.

```typescript
// app/users/page.tsx
import { db } from "@/lib/db";
import { UserCard } from "@/components/user-card";

// ✅ Nenhuma directive 'use client' = Server Component
export default async function UsersPage() {
  // ✅ Pode usar await diretamente
  const users = await db.user.findMany({
    orderBy: { createdAt: "desc" },
    take: 10,
  });

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Usuários</h1>

      {/* ✅ Renderizar lista é OK em Server Component */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {users.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>
    </div>
  );
}
```

**Benefícios**:
- ✅ Acesso direto ao banco de dados
- ✅ Sem exposição de credenciais ao cliente
- ✅ Menor JavaScript enviado ao navegador
- ✅ Melhor SEO (renderiza HTML completo)

**Limitações**:
- ❌ Não pode usar hooks (useState, useEffect, etc)
- ❌ Não pode usar eventos do navegador (onClick, onChange)
- ❌ Não pode usar browser APIs (localStorage, window, etc)

### Client Component (Quando Necessário)

Use `'use client'` apenas para componentes que precisam de interatividade.

```typescript
// app/users/_components/user-filter.tsx
'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// ✅ 'use client' permite usar hooks
export function UserFilter() {
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<string[]>([]);

  // ✅ Pode usar event handlers
  function handleAddFilter(filter: string) {
    setFilters([...filters, filter]);
  }

  function handleRemoveFilter(filter: string) {
    setFilters(filters.filter(f => f !== filter));
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Buscar usuários..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1"
        />
        <Button onClick={() => handleAddFilter(search)}>
          Adicionar Filtro
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((filter) => (
          <button
            key={filter}
            onClick={() => handleRemoveFilter(filter)}
            className="px-3 py-1 bg-blue-500 text-white rounded-full text-sm hover:bg-blue-600"
          >
            {filter} ×
          </button>
        ))}
      </div>
    </div>
  );
}
```

**Quando usar**:
- Quando precisar de `useState`, `useEffect`, `useContext`
- Para form inputs interativos
- Para modais, dropdowns, popovers
- Para animações com Framer Motion

### Padrão Recomendado: Composição Camadas

```typescript
// app/users/page.tsx (Server Component)
import { db } from "@/lib/db";
import { UserList } from "./_components/user-list";
import { UserFilter } from "./_components/user-filter";

export default async function UsersPage() {
  // ✅ Fetch no servidor
  const users = await db.user.findMany();

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-6">Usuários</h1>

      {/* ✅ Componente Client para filtros */}
      <UserFilter />

      {/* ✅ Componente Server para renderizar lista */}
      <UserList users={users} />
    </div>
  );
}
```

```typescript
// app/users/_components/user-list.tsx (Server Component)
import { User } from "@prisma/client";
import { UserCard } from "./user-card";

export function UserList({ users }: { users: User[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6">
      {users.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

```typescript
// app/users/_components/user-card.tsx (Server Component - sem interatividade)
import { User } from "@prisma/client";

export function UserCard({ user }: { user: User }) {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-semibold">{user.name}</h3>
      <p className="text-sm text-gray-600">{user.email}</p>
    </div>
  );
}
```

**Estrutura**:
- Parent (Server) → Fetch dados
- Middle Layer (Server) → Renderizar listas estáticas
- Interativo (Client) → Filtros, busca, formulários

---

## Padrão de Layouts

### Entendendo Layouts

Um `layout.tsx` é um componente que envolve todas as páginas dentro daquele segmento. É renderizado uma única vez e persiste entre mudanças de página.

### Root Layout

O layout raiz envolve toda a aplicação:

```typescript
// app/layout.tsx
import type { Metadata } from "next";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import "./globals.css";

export const metadata: Metadata = {
  title: "Minha App",
  description: "Descrição da aplicação",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <head>
        {/* Metadados automáticos */}
      </head>
      <body>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
```

### Layout Segmentado

Layouts em subdiretórios se aplicam apenas àquele segmento:

```
app/
├── layout.tsx                  # Applica a toda a app
├── (dashboard)/
│   ├── layout.tsx              # Applica apenas a /dashboard/*
│   ├── page.tsx                → /dashboard
│   ├── users/
│   │   └── page.tsx            → /dashboard/users
│   └── settings/
│       └── page.tsx            → /dashboard/settings
└── (auth)/
    ├── layout.tsx              # Applica apenas a /auth/*
    ├── login/
    │   └── page.tsx            → /login
    └── register/
        └── page.tsx            → /register
```

### Layout com Padrão Sidebar + Main

```typescript
// app/(dashboard)/layout.tsx
import { Sidebar } from "./_components/sidebar";
import { Header } from "./_components/header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      {/* Sidebar - renderizado uma única vez */}
      <Sidebar className="w-64 border-r" />

      <div className="flex-1 flex flex-col">
        {/* Header - renderizado uma única vez */}
        <Header className="border-b" />

        {/* Children muda conforme rota */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### Layout vs Template

- **Layout**: Persiste entre mudanças de página (melhor performance)
- **Template**: Remonta a cada mudança de página (para reset de state)

```typescript
// app/(dashboard)/template.tsx
'use client';

import { useEffect } from "react";

// ✅ Template remonta a cada página
export default function DashboardTemplate({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    console.log("Template remontado - nova página");
  }, []);

  return <div>{children}</div>;
}
```

---

## Route Groups

### O Que São Route Groups?

Route Groups permitem organizar rotas em grupos lógicos sem afetar a URL. Use `()` no nome do diretório.

### Exemplos Comuns

```
app/
├── (marketing)/                # Agrupa rotas públicas
│   ├── layout.tsx              # Layout diferente (navbar simples)
│   ├── page.tsx                → /
│   ├── about/
│   │   └── page.tsx            → /about
│   └── blog/
│       └── page.tsx            → /blog
├── (auth)/                     # Agrupa rotas de autenticação
│   ├── layout.tsx              # Layout diferente (centrado)
│   ├── login/
│   │   └── page.tsx            → /login
│   ├── register/
│   │   └── page.tsx            → /register
│   └── forgot-password/
│       └── page.tsx            → /forgot-password
└── (dashboard)/                # Agrupa rotas privadas
    ├── layout.tsx              # Layout diferente (com sidebar)
    ├── page.tsx                → /dashboard
    ├── users/
    │   └── page.tsx            → /dashboard/users
    └── settings/
        └── page.tsx            → /dashboard/settings
```

### Benefícios

- ✅ Layouts diferentes por seção
- ✅ Organizacao lógica sem afetar URLs
- ✅ Fácil de refatorar depois
- ✅ Cada layout pode ter seu próprio Metadata

### Exemplo: Marketing vs Dashboard

```typescript
// app/(marketing)/layout.tsx
import { MarketingHeader } from "@/components/marketing-header";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <MarketingHeader />
      {children}
    </>
  );
}
```

```typescript
// app/(dashboard)/layout.tsx
import { DashboardHeader } from "@/components/dashboard-header";
import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <DashboardHeader />
        {children}
      </div>
    </div>
  );
}
```

---

## Server Actions

### O Que São Server Actions?

Server Actions são funções assíncronas executadas **apenas no servidor**. Use-as para:
- Mutations (criar, atualizar, deletar)
- Validações com acesso ao banco
- Revalidar caches

### Declarar uma Server Action

```typescript
// app/actions/user-actions.ts
'use server';

import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { z } from "zod";

// ✅ Validação com Zod
const createUserSchema = z.object({
  name: z.string().min(3, "Mínimo 3 caracteres"),
  email: z.string().email("Email inválido"),
});

export async function createUser(formData: FormData) {
  // ✅ Parse e validação
  const rawData = {
    name: formData.get("name"),
    email: formData.get("email"),
  };

  try {
    const validatedData = createUserSchema.parse(rawData);

    // ✅ Seguro - credenciais do banco nunca vão ao cliente
    const user = await db.user.create({
      data: validatedData,
    });

    // ✅ Revalidar cache após mutation
    revalidatePath("/users");

    return { success: true, user };
  } catch (error) {
    return { success: false, error: "Dados inválidos" };
  }
}

export async function updateUser(id: string, formData: FormData) {
  const name = formData.get("name") as string;

  await db.user.update({
    where: { id },
    data: { name },
  });

  revalidatePath(`/users/${id}`);
}

export async function deleteUser(id: string) {
  await db.user.delete({ where: { id } });
  revalidatePath("/users");
}
```

### Usar em Server Component

```typescript
// app/users/new/page.tsx (Server Component)
import { createUser } from "@/app/actions/user-actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function NewUserPage() {
  return (
    <div className="max-w-md">
      <h1 className="text-2xl font-bold mb-6">Novo Usuário</h1>

      {/* ✅ action aponta para Server Action */}
      <form action={createUser} className="space-y-4">
        <div>
          <Label htmlFor="name">Nome</Label>
          <Input
            id="name"
            name="name"
            placeholder="João Silva"
            required
          />
        </div>

        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="joao@exemplo.com"
            required
          />
        </div>

        <Button type="submit" className="w-full">
          Criar Usuário
        </Button>
      </form>
    </div>
  );
}
```

### Usar em Client Component

```typescript
// app/users/_components/user-form.tsx (Client Component)
'use client';

import { createUser } from "@/app/actions/user-actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

export function UserForm() {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(formData: FormData) {
    setIsPending(true);
    setError("");

    try {
      // ✅ Chamar Server Action como função
      const result = await createUser(formData);

      if (!result.success) {
        setError(result.error);
      } else {
        // ✅ Limpar form após sucesso
        (formData as any).target?.reset?.();
      }
    } catch (err) {
      setError("Erro ao criar usuário");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <form action={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500">{error}</div>}

      <Input
        name="name"
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
        {isPending ? "Criando..." : "Criar"}
      </Button>
    </form>
  );
}
```

### Padrão com useFormStatus (React 19)

```typescript
'use client';

import { createUser } from "@/app/actions/user-actions";
import { useFormStatus } from "react-dom";
import { Button } from "@/components/ui/button";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" disabled={pending}>
      {pending ? "Salvando..." : "Salvar"}
    </Button>
  );
}

export function UserForm() {
  return (
    <form action={createUser} className="space-y-4">
      <input name="name" placeholder="Nome" required />
      <input name="email" type="email" placeholder="Email" required />

      {/* ✅ useFormStatus automático */}
      <SubmitButton />
    </form>
  );
}
```

---

## Data Fetching Patterns

### Pattern 1: Fetch no Server Component (Recomendado)

```typescript
// app/posts/page.tsx (Server Component)
import { fetchPosts } from "@/lib/api";
import { PostCard } from "@/components/post-card";

export default async function PostsPage() {
  // ✅ Fetch direto no componente
  const posts = await fetchPosts();

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

**Benefícios**:
- Renderiza HTML completo (melhor SEO)
- Sem estado intermediário de loading
- Credenciais seguras

### Pattern 2: Revalidação ISR (Incremental Static Regeneration)

```typescript
// app/products/page.tsx
import { getProducts } from "@/lib/db";

// ✅ Revalidar a cada 60 segundos
export const revalidate = 60;

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {products.map((product) => (
        <div key={product.id} className="p-4 border rounded-lg">
          <h3 className="font-semibold">{product.name}</h3>
          <p className="text-sm text-gray-600">{product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

**Opções**:
```typescript
export const revalidate = 0;        // Revalidar a cada request (Dynamic)
export const revalidate = 60;       // Revalidar a cada 60s (ISR)
export const revalidate = false;    // Never revalidate (Static)
```

### Pattern 3: Fetch com Error Boundary

```typescript
// app/users/page.tsx
import { getUsers } from "@/lib/db";
import { UserList } from "./_components/user-list";
import { ErrorBoundary } from "@/components/error-boundary";

export default async function UsersPage() {
  try {
    const users = await getUsers();

    return <UserList users={users} />;
  } catch (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h2 className="font-semibold text-red-800">Erro ao carregar usuários</h2>
        <p className="text-red-600">Tente recarregar a página</p>
      </div>
    );
  }
}
```

### Pattern 4: Suspense para Loading States

```typescript
// app/dashboard/page.tsx
import { Suspense } from "react";
import { UserStats } from "./_components/user-stats";
import { RecentActivity } from "./_components/recent-activity";
import { LoadingCards } from "./_components/loading-cards";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* ✅ Mostrar loading enquanto carrega */}
      <Suspense fallback={<LoadingCards count={3} />}>
        <UserStats />
      </Suspense>

      <Suspense fallback={<div>Carregando atividade...</div>}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```

### Pattern 5: Fetch com Parâmetros Dinâmicos

```typescript
// app/blog/[slug]/page.tsx
import { getPost } from "@/lib/db";
import { notFound } from "next/navigation";

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  // ✅ Fetch com parâmetro dinâmico
  const post = await getPost(slug);

  if (!post) {
    notFound(); // ✅ Retorna 404
  }

  return (
    <article className="max-w-2xl">
      <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
      <p className="text-gray-600 mb-6">{post.excerpt}</p>
      <div className="prose">{post.content}</div>
    </article>
  );
}
```

---

## Parallel Routes

### O Que São Parallel Routes?

Parallel Routes permitem renderizar múltiplos componentes na mesma página, cada um com seu próprio estado de carregamento e erros.

### Use Case: Dashboard com Tabs

```
app/
├── dashboard/
│   ├── @stats/
│   │   └── page.tsx            # Slot @stats
│   ├── @activity/
│   │   └── page.tsx            # Slot @activity
│   ├── layout.tsx              # Layout principal
│   └── page.tsx
```

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  stats,
  activity,
}: {
  children: React.ReactNode;
  stats: React.ReactNode;
  activity: React.ReactNode;
}) {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* ✅ Cada slot tem seu próprio estado */}
        <div>{stats}</div>
        <div>{activity}</div>
      </div>

      {children}
    </div>
  );
}
```

```typescript
// app/dashboard/@stats/page.tsx
import { getStats } from "@/lib/db";

export default async function StatsSlot() {
  const stats = await getStats();

  return (
    <div className="p-4 border rounded-lg">
      <h2 className="font-semibold mb-4">Estatísticas</h2>
      {/* Render stats */}
    </div>
  );
}
```

### Use Case: Modal em Parallel Route

```
app/
├── dashboard/
│   ├── @modal/
│   │   ├── (...)/     # Catch-all para modais
│   │   │   └── page.tsx
│   │   └── default.tsx # Quando não há modal
│   ├── layout.tsx
│   └── page.tsx
```

```typescript
// app/dashboard/@modal/default.tsx
// ✅ Renderizado quando não há modal ativo
export default function Default() {
  return null;
}
```

```typescript
// app/dashboard/@modal/(...)/page.tsx
'use client';

import { useRouter } from "next/navigation";
import { Dialog } from "@/components/ui/dialog";

export default function ModalPage() {
  const router = useRouter();

  return (
    <Dialog open onOpenChange={() => router.back()}>
      <div className="space-y-4">
        <h2 className="text-xl font-bold">Novo Item</h2>
        {/* Modal content */}
      </div>
    </Dialog>
  );
}
```

---

## Boas Práticas Resumidas

### Server Components (✅ Padrão)
- Fetch direto no componente
- Acesso seguro ao banco
- Renderizar listas estáticas
- Sem hooks React

### Client Components (❌ Exceção)
- Apenas para interatividade
- Formulários e filtros
- Modais e dropdowns
- Salvam state do usuário

### Server Actions
- Mutations e validações
- Sempre em arquivos separados
- Começam com `'use server'`
- Retornam erro ou sucesso

### Data Fetching
- Suspense para loading states
- Revalidate para cache
- Error boundaries para erros
- Parâmetros dinâmicos com await params

### Layouts
- Root layout para toda app
- Segmentados para seções
- Persiste entre páginas
- Templates remontam cada página

---

## Checklist de Componente

Antes de criar qualquer componente, pergunte-se:

- [ ] Precisa de interatividade? NÃO → Server Component
- [ ] Usa hooks (useState, useEffect)? SIM → Client Component
- [ ] É uma lista estática? SIM → Server Component
- [ ] É um formulário? SIM → Client Component
- [ ] Busca dados? SIM → Server Component (async)
- [ ] Mostra loading? SIM → Suspense no parent
- [ ] Altera dados? SIM → Server Action
- [ ] É responsivo? SIM → Mobile-first Tailwind

Seguindo esse guia você terá uma arquitetura escalável, performática e simples.
