# Padrões de Componentes Next.js

Referência completa de padrões de componentes extraído da skill `nextjs-modern-stack`.

## Princípios Fundamentais

### 1. Mobile-First Obrigatório

Todos os componentes DEVEM começar mobile. Use breakpoints Tailwind progressivamente:

- **sem prefixo**: mobile (< 640px)
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

```typescript
// ✅ CORRETO: Começa mobile, expande para cima
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// ❌ ERRADO: Começa em desktop
<div className="grid-cols-4 grid">
```

### 2. Server Components por Padrão

Use Server Components sempre. Client Components (`'use client'`) apenas para:

- Interatividade (onClick, onChange, etc)
- Hooks (useState, useEffect, useContext)
- Browser APIs (localStorage, geolocation)

```typescript
// ✅ CORRETO: Server Component (padrão)
export default async function UserList() {
  const users = await fetchUsers();
  return <div>{users.map(u => <p key={u.id}>{u.name}</p>)}</div>;
}

// ❌ ERRADO: Client Component desnecessário
'use client';
export function UserList({ users }) {
  return <div>{users.map(u => <p key={u.id}>{u.name}</p>)}</div>;
}
```

### 3. Performance por Padrão

- Sempre use `next/image` para imagens
- Use lazy loading quando apropriado
- Dynamic imports para código pesado
- Optimize fontes com `next/font`

## Padrões de Componentes

### 1. Server Component Simples

```typescript
// app/dashboard/page.tsx
import { db } from "@/lib/db";
import { UserTable } from "./_components/user-table";

export default async function DashboardPage() {
  // Fetch direto no componente
  const users = await db.user.findMany();

  return (
    <div className="container py-4 md:py-8">
      <h1 className="text-2xl md:text-3xl font-bold mb-4 md:mb-8">
        Dashboard
      </h1>
      <UserTable users={users} />
    </div>
  );
}
```

**Características:**
- ✅ Async component para fetch direto
- ✅ Sem states ou hooks
- ✅ Responsivo com classes mobile-first
- ✅ Props tipadas

### 2. Client Component com Interatividade

```typescript
// app/dashboard/_components/user-form.tsx
'use client';

import { createUser } from "@/app/actions/user-actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

export function UserForm() {
  const [isPending, setIsPending] = useState(false);

  async function handleSubmit(formData: FormData) {
    setIsPending(true);
    try {
      await createUser(formData);
    } finally {
      setIsPending(false);
    }
  }

  return (
    <form action={handleSubmit} className="flex flex-col gap-4 sm:flex-row">
      <Input
        name="name"
        placeholder="Nome do usuário"
        required
        className="flex-1"
        disabled={isPending}
      />
      <Button
        type="submit"
        disabled={isPending}
        className="w-full sm:w-auto"
      >
        {isPending ? "Criando..." : "Criar Usuário"}
      </Button>
    </form>
  );
}
```

**Características:**
- ✅ Usar `'use client'` apenas aqui
- ✅ Estados para UX (loading, pending)
- ✅ Server Action integrada
- ✅ Responsiva (flex-col em mobile, row em sm+)

### 3. Server Action Validada

```typescript
// app/actions/user-actions.ts
'use server';

import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { z } from "zod";

const createUserSchema = z.object({
  name: z.string().min(3, "Nome deve ter 3+ caracteres"),
  email: z.string().email("Email inválido"),
});

export async function createUser(formData: FormData) {
  try {
    const rawData = {
      name: formData.get("name"),
      email: formData.get("email"),
    };

    // Validação com Zod
    const validatedData = createUserSchema.parse(rawData);

    // Criar no banco
    await db.user.create({
      data: validatedData,
    });

    // Revalidar cache
    revalidatePath("/dashboard");

    return { success: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: error.errors[0].message
      };
    }
    return { success: false, error: "Erro ao criar usuário" };
  }
}
```

**Características:**
- ✅ Validação com Zod
- ✅ Error handling robusto
- ✅ Revalidação automática
- ✅ Retorno estruturado

### 4. Card Componente UI

```typescript
// components/ui/card.tsx
import { cn } from "@/lib/utils";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card text-card-foreground shadow-sm",
        className
      )}
      {...props}
    />
  );
}

// Uso
<Card className="p-4 sm:p-6">
  <h3 className="text-lg font-semibold">Título</h3>
  <p className="text-sm text-muted-foreground mt-2">Descrição</p>
</Card>
```

**Características:**
- ✅ Props tipadas
- ✅ Merge de classes com `cn()`
- ✅ Spread props para flexibilidade
- ✅ Styling baseado em tema

## Padrões Mobile-First

### 1. Container Responsivo

```typescript
// Sempre usar container com padding responsivo
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  {/* Conteúdo */}
</div>

// Ou com max-width
<div className="container max-w-4xl mx-auto px-4">
  {/* Conteúdo */}
</div>
```

### 2. Grid Responsivo

```typescript
// ✅ CORRETO: Começa 1 coluna, expande
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  {items.map(item => (
    <Card key={item.id} />
  ))}
</div>

// Variação com diferentes gaps
<div className="grid grid-cols-1 gap-3 sm:gap-4 md:grid-cols-2 lg:gap-6 lg:grid-cols-3">
  {/* Conteúdo */}
</div>
```

### 3. Tipografia Responsiva

```typescript
// Títulos
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
  Título Principal
</h1>

// Subtítulos
<h2 className="text-xl sm:text-2xl md:text-3xl font-semibold">
  Subtítulo
</h2>

// Body text
<p className="text-sm sm:text-base md:text-lg leading-relaxed">
  Parágrafo com texto responsivo
</p>
```

### 4. Espaçamento Responsivo

```typescript
// Padding responsivo
<div className="p-4 sm:p-6 md:p-8 lg:p-10">
  {/* Conteúdo */}
</div>

// Margin responsivo
<div className="mb-4 sm:mb-6 md:mb-8 lg:mb-10">
  {/* Conteúdo */}
</div>

// Space between items
<div className="space-y-3 sm:space-y-4 md:space-y-6">
  {/* Items com espaçamento responsivo */}
</div>
```

### 5. Flex Direction Responsivo

```typescript
// ✅ CORRETO: Coluna em mobile, row em maior
<div className="flex flex-col gap-4 sm:items-center sm:justify-between md:flex-row">
  <h2 className="text-xl font-semibold">Título</h2>
  <Button>Ação</Button>
</div>

// Header/Footer com conteúdo responsivo
<div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
  <div>
    <h1 className="text-2xl font-bold">Logo</h1>
    <p className="text-sm text-muted-foreground">Subtítulo</p>
  </div>
  <nav className="flex gap-4">
    {/* Nav items */}
  </nav>
</div>
```

## Composição shadcn/ui + Radix UI

### Button Variants

```typescript
// components/ui/button.tsx
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // Variants customizados
        success: "bg-green-500 text-white hover:bg-green-600",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        xl: "h-12 rounded-md px-10 text-base",
        icon: "h-9 w-9",
        "icon-sm": "h-7 w-7",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "ghost" | "link" | "success";
  size?: "default" | "sm" | "lg" | "xl" | "icon" | "icon-sm";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? "Carregando..." : children}
    </button>
  )
);
Button.displayName = "Button";
```

### Dialog Component

```typescript
// components/ui/dialog.tsx
'use client';

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, ...props }, ref) => (
  <DialogPortal>
    <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    />
    <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
      <X className="h-4 w-4" />
    </DialogPrimitive.Close>
  </DialogPortal>
));
DialogContent.displayName = DialogPrimitive.Content.displayName;
```

**Características:**
- ✅ Composição de Radix UI primitives
- ✅ Animações integradas
- ✅ Acessibilidade automática
- ✅ Customizável via className

## TypeScript Props Typing

### 1. Props Simples

```typescript
interface HeaderProps {
  title: string;
  subtitle?: string;
  isActive: boolean;
  onClose?: () => void;
}

export function Header({ title, subtitle, isActive, onClose }: HeaderProps) {
  return (
    <div>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
      {onClose && <button onClick={onClose}>Fechar</button>}
    </div>
  );
}
```

### 2. Props com HTML Attributes

```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "outlined";
  loading?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "default", loading, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border p-4",
        {
          "shadow-lg": variant === "elevated",
          "border-2": variant === "outlined",
        },
        className
      )}
      {...props}
    />
  )
);
Card.displayName = "Card";
```

### 3. Props com Children

```typescript
interface ModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Modal({ open, title, onClose, children, footer }: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">{title}</h2>
        <div className="mb-6">{children}</div>
        <div className="flex gap-2 justify-end">
          {footer}
          <button onClick={onClose} className="px-4 py-2">
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Quando Usar "use client"

```typescript
// ✅ USAR 'use client' para:

// 1. Interatividade com eventos
'use client';
export function SearchInput() {
  const [query, setQuery] = useState('');
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}

// 2. Hooks (useState, useEffect, etc)
'use client';
import { useState, useEffect } from 'react';
export function Timer() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setCount(c => c + 1), 1000);
    return () => clearInterval(timer);
  }, []);
  return <div>{count}s</div>;
}

// 3. Browser APIs
'use client';
import { useEffect } from 'react';
export function Geolocation() {
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(...);
  }, []);
}

// ❌ NÃO usar 'use client' para:

// 1. Apenas renderização
export function UserCard({ user }) {
  return <div>{user.name}</div>;
}

// 2. Server Actions
import { deleteUser } from '@/app/actions/user-actions';
export function UserRow({ user }) {
  return (
    <form action={() => deleteUser(user.id)}>
      <button type="submit">Deletar</button>
    </form>
  );
}

// 3. Componentes estáticos
export function Footer() {
  return <footer>© 2025</footer>;
}
```

## Responsividade em Profundidade

### Média Query Customizada

```typescript
// tailwind.config.ts
const config: Config = {
  theme: {
    extend: {
      screens: {
        xs: "320px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },
    },
  },
};
```

### Padrões Comuns

```typescript
// Navbar responsivo
<nav className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
  <div className="text-xl font-bold">Logo</div>
  <ul className="flex flex-col gap-2 sm:flex-row sm:gap-4">
    <li><a href="/">Home</a></li>
    <li><a href="/about">Sobre</a></li>
  </ul>
</nav>

// Form responsivo
<form className="space-y-4 sm:space-y-6">
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
    <input placeholder="Primeiro nome" />
    <input placeholder="Sobrenome" />
  </div>
  <textarea placeholder="Mensagem" className="w-full" />
  <button className="w-full sm:w-auto">Enviar</button>
</form>

// Lista com sidebar
<div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
  <aside className="lg:col-span-1">
    {/* Sidebar */}
  </aside>
  <main className="lg:col-span-3">
    {/* Conteúdo */}
  </main>
</div>
```

## Acessibilidade (ARIA + Semantic HTML)

```typescript
// ✅ Semantic HTML
export function MainContent() {
  return (
    <main className="container py-8">
      <header className="mb-8">
        <h1>Título Principal</h1>
        <nav aria-label="navegação principal">
          <ul role="list">
            <li><a href="/">Home</a></li>
            <li><a href="/about">Sobre</a></li>
          </ul>
        </nav>
      </header>
      <section>
        <h2>Seção 1</h2>
        <article>
          <h3>Artigo 1</h3>
          <p>Conteúdo</p>
        </article>
      </section>
      <footer>Rodapé</footer>
    </main>
  );
}

// Componente acessível com ARIA
interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning';
}

export function Toast({ message, type }: ToastProps) {
  return (
    <div
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      className={cn(
        "p-4 rounded-lg",
        {
          "bg-green-100 text-green-800": type === 'success',
          "bg-red-100 text-red-800": type === 'error',
          "bg-yellow-100 text-yellow-800": type === 'warning',
        }
      )}
    >
      {message}
    </div>
  );
}

// Form com labels acessíveis
export function LoginForm() {
  const emailId = useId();
  const passwordId = useId();

  return (
    <form className="space-y-4">
      <div>
        <label htmlFor={emailId} className="block text-sm font-medium">
          Email
        </label>
        <input
          id={emailId}
          type="email"
          required
          aria-required="true"
        />
      </div>
      <div>
        <label htmlFor={passwordId} className="block text-sm font-medium">
          Senha
        </label>
        <input
          id={passwordId}
          type="password"
          required
          aria-required="true"
        />
      </div>
      <button type="submit">Entrar</button>
    </form>
  );
}
```

## Performance - Lazy Loading e Dynamic Imports

```typescript
// Dynamic import de componente pesado
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("./heavy-chart"), {
  loading: () => <div className="h-96 bg-gray-200 animate-pulse" />,
});

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <HeavyChart />
    </div>
  );
}

// Lazy image
import Image from "next/image";

export function ProductCard({ product }) {
  return (
    <Card>
      <Image
        src={product.image}
        alt={product.name}
        width={300}
        height={300}
        loading="lazy"
        quality={75}
      />
      <h3>{product.name}</h3>
    </Card>
  );
}

// Suspense com fallback
import { Suspense } from 'react';

export default function Page() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <SlowComponent />
    </Suspense>
  );
}
```

## Exemplo Completo: Página de Produtos

```typescript
// app/products/page.tsx
import { db } from "@/lib/db";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AddProductForm } from "./_components/add-product-form";
import Link from "next/link";

export default async function ProductsPage() {
  const products = await db.product.findMany({
    orderBy: { createdAt: "desc" },
  });

  return (
    <div className="container py-4 md:py-8">
      {/* Header */}
      <div className="flex flex-col gap-4 mb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Produtos</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Gerenciar produtos da loja
          </p>
        </div>
        <Button asChild>
          <Link href="/products/new">Novo Produto</Link>
        </Button>
      </div>

      {/* Produtos Grid */}
      {products.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-muted-foreground">Nenhum produto encontrado</p>
          <Button asChild className="mt-4">
            <Link href="/products/new">Criar Primeiro Produto</Link>
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product) => (
            <Card key={product.id} className="p-4 sm:p-6 hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-2 line-clamp-2">
                {product.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {product.description}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold">
                  R$ {product.price.toFixed(2)}
                </span>
                <Button asChild variant="outline" size="sm">
                  <Link href={`/products/${product.id}`}>Ver</Link>
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Checklist de Componente

Antes de criar/entregar qualquer componente, verificar:

- [ ] **Server Component?** É Server Component por padrão?
- [ ] **Client Component?** Usa `'use client'` apenas se necessário (hooks/eventos)?
- [ ] **Mobile-first?** Classes começam sem breakpoint?
- [ ] **Responsivo?** Testado em todos breakpoints (sm, md, lg, xl)?
- [ ] **Imagens?** Usa `next/image` para imagens?
- [ ] **TypeScript?** Props tipadas corretamente?
- [ ] **Validação?** Usa Zod para formulários?
- [ ] **Acessível?** Tem aria-labels, semantic HTML?
- [ ] **Performance?** Lazy loading se necessário?
- [ ] **Código limpo?** Sem comentários óbvios, DRY?
- [ ] **Builds?** `npm run build` passa sem erros?

## Recursos Adicionais

- Tailwind CSS: https://tailwindcss.com/docs
- shadcn/ui: https://ui.shadcn.com
- Radix UI: https://www.radix-ui.com
- React: https://react.dev
- Next.js: https://nextjs.org/docs
