# Tratamento de Erros Next.js

Referência completa de tratamento de erros extraído da skill `nextjs-reliability`.

## Princípio Fundamental

**NUNCA apresentar código que possa quebrar. SEMPRE validar antes.**

## Checklist de Confiabilidade

Antes de apresentar qualquer código:

```bash
# 1. Verificar TypeScript
npx tsc --noEmit

# 2. Verificar build
npm run build

# 3. Verificar lint
npm run lint

# Todos devem passar sem erros!
```

## Error Boundaries (Obrigatório)

Error Boundaries capturam erros não tratados e exibem fallback UI.

### Root Error Boundary

```typescript
// app/error.tsx
'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function RootError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log para monitoramento (Sentry, LogRocket, etc)
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold">
            Algo deu errado
          </h2>
          <p className="text-sm text-muted-foreground mt-2">
            Desculpe, ocorreu um erro inesperado na aplicação.
          </p>
        </div>

        {/* Mostrar digest para debugging */}
        {error.digest && (
          <div className="bg-muted p-3 rounded text-xs text-muted-foreground font-mono">
            Código: {error.digest}
          </div>
        )}

        <Button
          onClick={reset}
          className="w-full sm:w-auto"
        >
          Tentar Novamente
        </Button>
      </div>
    </div>
  );
}
```

**Características:**
- ✅ Captura erros não tratados
- ✅ Log para monitoramento
- ✅ Botão "Tentar Novamente"
- ✅ Mostra digest para debugging

### Scoped Error Boundary

```typescript
// app/dashboard/error.tsx
'use client';

import { Button } from '@/components/ui/button';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="container py-8">
      <div className="rounded-lg border border-destructive bg-destructive/5 p-4 sm:p-6">
        <div className="flex gap-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              Erro no Dashboard
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              {error.message || 'Erro ao carregar dados do dashboard'}
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={reset}
            variant="outline"
            size="sm"
          >
            Tentar Novamente
          </Button>
          <Button
            variant="outline"
            size="sm"
            asChild
          >
            <a href="/dashboard">Voltar para Dashboard</a>
          </Button>
        </div>
      </div>
    </div>
  );
}
```

**Características:**
- ✅ Error boundary de escopo limitado
- ✅ Mensagem específica do contexto
- ✅ Alternativas de ação
- ✅ Design integrado

## Loading States (Obrigatório)

Loading skeletons melhoram UX enquanto dados carregam.

### Loading Skeleton Simples

```typescript
// app/dashboard/loading.tsx
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardLoading() {
  return (
    <div className="container py-4 md:py-8">
      {/* Header skeleton */}
      <div className="mb-8">
        <Skeleton className="h-10 w-48 mb-2" />
        <Skeleton className="h-4 w-64" />
      </div>

      {/* Cards skeleton */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-48 rounded-lg" />
        ))}
      </div>
    </div>
  );
}
```

### Loading com Elemento Visual

```typescript
// app/products/loading.tsx
import { Skeleton } from '@/components/ui/skeleton';

export default function ProductsLoading() {
  return (
    <div className="container py-4 md:py-8">
      {/* Header */}
      <div className="flex flex-col gap-4 mb-8 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>

      {/* Grid de produtos */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-4">
            {/* Imagem placeholder */}
            <Skeleton className="aspect-square rounded-lg" />
            {/* Título */}
            <Skeleton className="h-4 w-full" />
            {/* Descrição */}
            <Skeleton className="h-4 w-4/5" />
            {/* Preço + botão */}
            <div className="flex gap-2">
              <Skeleton className="h-8 flex-1" />
              <Skeleton className="h-8 w-12" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Componente Skeleton Reutilizável

```typescript
// components/ui/skeleton.tsx
import { cn } from '@/lib/utils';

export function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-muted',
        className
      )}
      {...props}
    />
  );
}
```

## Not Found Pages (Obrigatório)

Criar `not-found.tsx` em rotas dinâmicas.

### 404 em Rota Dinâmica

```typescript
// app/products/[id]/not-found.tsx
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function ProductNotFound() {
  return (
    <div className="container flex min-h-[400px] items-center justify-center">
      <div className="text-center space-y-6 max-w-md">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold mb-2">
            404 - Produto Não Encontrado
          </h2>
          <p className="text-muted-foreground">
            O produto que você procura não existe ou foi removido.
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
          <Button variant="outline" asChild>
            <Link href="/products">Ver Todos os Produtos</Link>
          </Button>
          <Button asChild>
            <Link href="/">Voltar à Home</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### 404 Global com Metadata

```typescript
// app/not-found.tsx
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export const metadata = {
  title: 'Página não encontrada',
  description: 'A página que você procura não existe.',
};

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="text-center space-y-6">
        <div>
          <h1 className="text-6xl md:text-8xl font-bold">404</h1>
          <h2 className="text-2xl font-semibold mt-4">
            Página Não Encontrada
          </h2>
          <p className="text-muted-foreground mt-2 max-w-md mx-auto">
            Desculpe, a página que você está procurando não existe ou foi movida.
          </p>
        </div>

        <Button asChild>
          <Link href="/">Voltar à Home</Link>
        </Button>
      </div>
    </div>
  );
}
```

**Características:**
- ✅ Diferenciado de error.tsx
- ✅ Metadata configurada
- ✅ Navegação clara

## Server Actions com Tratamento de Erros

### Padrão Básico

```typescript
// app/actions/product-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';
import { z } from 'zod';

// Schema de validação
const createProductSchema = z.object({
  name: z.string().min(3, 'Nome deve ter 3+ caracteres').max(100),
  description: z.string().min(10, 'Descrição deve ter 10+ caracteres'),
  price: z.number().positive('Preço deve ser positivo'),
  category: z.enum(['electronics', 'clothing', 'books']),
});

// Return type estruturado
type ActionResult<T> = {
  success: true;
  data: T;
} | {
  success: false;
  error: string;
};

export async function createProduct(
  formData: FormData
): Promise<ActionResult<{ id: string }>> {
  try {
    // Extrair dados do form
    const rawData = {
      name: formData.get('name'),
      description: formData.get('description'),
      price: Number(formData.get('price')),
      category: formData.get('category'),
    };

    // Validar com Zod
    const validatedData = createProductSchema.safeParse(rawData);

    if (!validatedData.success) {
      const firstError = validatedData.error.errors[0];
      return {
        success: false,
        error: firstError?.message || 'Dados inválidos',
      };
    }

    // Criar no banco
    const product = await db.product.create({
      data: validatedData.data,
    });

    // Revalidar cache
    revalidatePath('/products');

    return {
      success: true,
      data: { id: product.id },
    };
  } catch (error) {
    console.error('Error creating product:', error);
    return {
      success: false,
      error: 'Erro ao criar produto. Tente novamente.',
    };
  }
}
```

### Delete com Confirmação

```typescript
// app/actions/product-actions.ts
export async function deleteProduct(
  id: string
): Promise<ActionResult<null>> {
  try {
    // Validar ID
    if (!id || typeof id !== 'string' || id.trim().length === 0) {
      return { success: false, error: 'ID inválido' };
    }

    // Verificar se existe
    const product = await db.product.findUnique({
      where: { id },
    });

    if (!product) {
      return { success: false, error: 'Produto não encontrado' };
    }

    // Deletar
    await db.product.delete({ where: { id } });

    // Revalidar
    revalidatePath('/products');

    return { success: true, data: null };
  } catch (error) {
    console.error('Error deleting product:', error);
    return {
      success: false,
      error: 'Erro ao deletar produto',
    };
  }
}
```

## Client Component com Error Handling

```typescript
// app/products/_components/delete-button.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { deleteProduct } from '@/app/actions/product-actions';
import { toast } from 'sonner';

interface DeleteButtonProps {
  productId: string;
  onDeleted?: () => void;
}

export function DeleteButton({ productId, onDeleted }: DeleteButtonProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  async function handleDelete() {
    // Confirmar ação
    if (!confirm('Tem certeza que deseja deletar este produto?')) {
      return;
    }

    setIsDeleting(true);

    try {
      const result = await deleteProduct(productId);

      // Verificar resultado
      if (!result.success) {
        toast.error(result.error);
        return;
      }

      // Sucesso
      toast.success('Produto deletado com sucesso');
      onDeleted?.();
      router.push('/products');
      router.refresh();
    } catch (error) {
      // Erro não esperado
      toast.error('Erro inesperado. Tente novamente.');
      console.error('Delete error:', error);
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <Button
      variant="destructive"
      onClick={handleDelete}
      disabled={isDeleting}
      size="sm"
    >
      {isDeleting ? (
        <>
          <span className="animate-spin mr-2">⏳</span>
          Deletando...
        </>
      ) : (
        'Deletar Produto'
      )}
    </Button>
  );
}
```

**Características:**
- ✅ Confirmação antes de deletar
- ✅ Try/catch com feedback
- ✅ Loading state visual
- ✅ Toast notifications
- ✅ Router refresh

## Validação com Zod

### Schemas Simples e Diretos

```typescript
// lib/validations.ts
import { z } from 'zod';

// Produto
export const productSchema = z.object({
  name: z
    .string()
    .min(3, 'Nome deve ter no mínimo 3 caracteres')
    .max(100, 'Nome não pode ter mais de 100 caracteres'),
  description: z
    .string()
    .min(10, 'Descrição muito curta')
    .max(500, 'Descrição muito longa'),
  price: z
    .number()
    .positive('Preço deve ser maior que zero')
    .finite(),
  category: z.enum(['electronics', 'clothing', 'books'], {
    errorMap: () => ({ message: 'Categoria inválida' }),
  }),
  image: z
    .string()
    .url('URL de imagem inválida'),
});

export type ProductFormData = z.infer<typeof productSchema>;

// Usuário
export const userSchema = z.object({
  name: z.string().min(3).max(100),
  email: z.string().email('Email inválido'),
  age: z
    .number()
    .int()
    .min(18, 'Deve ter 18 anos ou mais'),
});

export type UserFormData = z.infer<typeof userSchema>;

// Login
export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z
    .string()
    .min(8, 'Senha deve ter 8+ caracteres'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
```

### Validação em Server Actions

```typescript
'use server';

import { productSchema } from '@/lib/validations';

export async function createProduct(formData: FormData) {
  const rawData = {
    name: formData.get('name'),
    description: formData.get('description'),
    price: Number(formData.get('price')),
    category: formData.get('category'),
    image: formData.get('image'),
  };

  // safeParse não lança exceção
  const validation = productSchema.safeParse(rawData);

  if (!validation.success) {
    return {
      success: false,
      errors: validation.error.flatten().fieldErrors,
    };
  }

  // validation.data é tipado e validado
  const product = await db.product.create({
    data: validation.data,
  });

  return { success: true, data: product };
}
```

## Server Components com Tratamento de Erros

### Fetch com Tratamento

```typescript
// app/products/[id]/page.tsx
import { notFound } from 'next/navigation';
import { db } from '@/lib/db';
import { ProductDetail } from './_components/product-detail';

type PageProps = {
  params: { id: string };
};

// Função separada para fetch
async function getProduct(id: string) {
  try {
    // Validar entrada
    if (!id || typeof id !== 'string') {
      console.warn('Invalid product ID:', id);
      return null;
    }

    // Fetch com timeout implícito
    const product = await db.product.findUnique({
      where: { id },
      include: {
        reviews: true,
        seller: {
          select: { id: true, name: true },
        },
      },
    });

    return product;
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
}

export default async function ProductPage({ params }: PageProps) {
  const product = await getProduct(params.id);

  // Redirecionar para not-found se não encontrado
  if (!product) {
    notFound();
  }

  return (
    <div className="container py-4 md:py-8">
      <ProductDetail product={product} />
    </div>
  );
}

// Metadata com error handling
export async function generateMetadata({ params }: PageProps) {
  const product = await getProduct(params.id);

  if (!product) {
    return {
      title: 'Produto não encontrado',
      description: 'O produto que você procura não existe.',
    };
  }

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.image],
    },
  };
}
```

## Null/Undefined Safety

### Type Guards

```typescript
// ❌ NUNCA fazer isso
function ProductCard({ product }) {
  return <div>{product.name}</div>; // Pode quebrar!
}

// ✅ SEMPRE fazer isso
type Product = {
  id: string;
  name: string;
  price: number;
};

interface ProductCardProps {
  product: Product | null;
}

export function ProductCard({ product }: ProductCardProps) {
  if (!product) {
    return (
      <div className="p-4 border rounded text-center">
        <p className="text-muted-foreground text-sm">
          Produto indisponível
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded">
      <h3 className="font-semibold">{product.name}</h3>
      <p className="text-sm text-muted-foreground">
        R$ {product.price.toFixed(2)}
      </p>
    </div>
  );
}
```

### Optional Chaining

```typescript
// Seguro com optional chaining
function UserProfile({ user }: UserProfileProps) {
  return (
    <div>
      <h1>{user?.name || 'Usuário Anônimo'}</h1>
      <p>{user?.email}</p>
      <div>Seguidores: {user?.followers?.length ?? 0}</div>
    </div>
  );
}
```

## Empty States

```typescript
// Sempre lidar com arrays vazios
export default async function ProductsPage() {
  const products = await db.product.findMany();

  return (
    <div className="container py-4 md:py-8">
      {products.length === 0 ? (
        // Empty state
        <div className="text-center py-12 sm:py-16">
          <h2 className="text-lg font-semibold mb-2">
            Nenhum produto encontrado
          </h2>
          <p className="text-muted-foreground mb-6">
            Comece criando um novo produto
          </p>
          <Button asChild>
            <Link href="/products/new">Criar Produto</Link>
          </Button>
        </div>
      ) : (
        // Grid com produtos
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
```

## Form Validation (Client + Server)

```typescript
// app/products/new/_components/product-form.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { productSchema, type ProductFormData } from '@/lib/validations';
import { createProduct } from '@/app/actions/product-actions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

export function ProductForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    mode: 'onChange', // Validar ao mudar
  });

  async function onSubmit(data: ProductFormData) {
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        formData.append(key, String(value));
      });

      const result = await createProduct(formData);

      if (!result.success) {
        toast.error(result.error);
        return;
      }

      toast.success('Produto criado com sucesso');
      reset();
      router.push(`/products/${result.data.id}`);
    } catch (error) {
      toast.error('Erro inesperado. Tente novamente.');
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Nome */}
      <div className="space-y-2">
        <Label htmlFor="name">Nome do Produto</Label>
        <Input
          id="name"
          {...register('name')}
          placeholder="Ex: iPhone 15 Pro"
          disabled={isSubmitting}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      {/* Descrição */}
      <div className="space-y-2">
        <Label htmlFor="description">Descrição</Label>
        <Textarea
          id="description"
          {...register('description')}
          placeholder="Descreva o produto em detalhes"
          disabled={isSubmitting}
          rows={4}
        />
        {errors.description && (
          <p className="text-sm text-destructive">
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Preço */}
      <div className="space-y-2">
        <Label htmlFor="price">Preço (R$)</Label>
        <Input
          id="price"
          type="number"
          step="0.01"
          min="0"
          {...register('price', { valueAsNumber: true })}
          placeholder="0.00"
          disabled={isSubmitting}
        />
        {errors.price && (
          <p className="text-sm text-destructive">{errors.price.message}</p>
        )}
      </div>

      {/* Categoria */}
      <div className="space-y-2">
        <Label htmlFor="category">Categoria</Label>
        <select
          id="category"
          {...register('category')}
          disabled={isSubmitting}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="">Selecione uma categoria</option>
          <option value="electronics">Eletrônicos</option>
          <option value="clothing">Roupas</option>
          <option value="books">Livros</option>
        </select>
        {errors.category && (
          <p className="text-sm text-destructive">
            {errors.category.message}
          </p>
        )}
      </div>

      {/* Submit */}
      <Button
        type="submit"
        disabled={isSubmitting || !isValid}
        className="w-full sm:w-auto"
      >
        {isSubmitting ? 'Criando...' : 'Criar Produto'}
      </Button>
    </form>
  );
}
```

**Características:**
- ✅ Validação client-side com React Hook Form
- ✅ Schema Zod para type safety
- ✅ Server Action para validação server-side
- ✅ Feedback de erro por campo
- ✅ Loading state
- ✅ Reset após sucesso

## Environment Variables

```typescript
// Verificar variáveis obrigatórias no boot
if (!process.env.DATABASE_URL) {
  throw new Error(
    'DATABASE_URL não configurada. Adicione em .env.local'
  );
}

if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_URL não configurada. Adicione em .env.local'
  );
}

export const config = {
  databaseUrl: process.env.DATABASE_URL,
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
};
```

## Toast Notifications

### Instalação

```bash
npm install sonner
```

### Configuração

```typescript
// app/layout.tsx
import { Toaster } from 'sonner';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        <Toaster
          position="top-right"
          richColors
          theme="light"
          expand
        />
      </body>
    </html>
  );
}
```

### Uso em Componentes

```typescript
'use client';

import { toast } from 'sonner';

// Sucesso
toast.success('Operação realizada com sucesso');

// Erro
toast.error('Ocorreu um erro. Tente novamente.');

// Informação
toast.info('Sua alteração foi salva');

// Aviso
toast.warning('Ação irreversível');

// Custom
toast.custom((t) => (
  <div className="p-4 bg-white rounded border">
    <h3>Título</h3>
    <p>Mensagem customizada</p>
  </div>
));

// Promise (para operações assíncronas)
toast.promise(
  fetchData(),
  {
    loading: 'Carregando...',
    success: 'Dados carregados',
    error: 'Erro ao carregar',
  }
);
```

## Checklist Final de Confiabilidade

Antes de apresentar código, SEMPRE verificar:

- [ ] **Build Completo**: `npm run build` passa sem erros?
- [ ] **TypeScript**: `npx tsc --noEmit` sem erros?
- [ ] **Lint**: `npm run lint` passa?
- [ ] **Error Boundaries**: `error.tsx` nas rotas principais?
- [ ] **Loading States**: `loading.tsx` onde apropriado?
- [ ] **Not Found**: `not-found.tsx` em rotas dinâmicas?
- [ ] **Server Actions**: Try/catch com error handling?
- [ ] **Validação**: Zod em todos os forms?
- [ ] **Null Checks**: Props e dados verificados?
- [ ] **Empty States**: Arrays vazios tratados?
- [ ] **Toast Notifications**: Feedback de ações?
- [ ] **Environment Variables**: Validadas?
- [ ] **Types**: Props e returns tipados?
- [ ] **Logs**: Console.error em catch blocks?

## Padrão de Verificação Rápida

```bash
# Executar antes de apresentar
npm run build && npm run lint && npx tsc --noEmit

# Deve completar sem erros!
```

## Try/Catch Guidelines

```typescript
// ✅ BOM: Específico e com logging
try {
  const product = await db.product.findUnique({ where: { id } });
  if (!product) {
    return { success: false, error: 'Produto não encontrado' };
  }
  return { success: true, data: product };
} catch (error) {
  console.error('Database error:', error);
  return { success: false, error: 'Erro ao buscar produto' };
}

// ❌ RUIM: Genérico e sem logging
try {
  // código
} catch (e) {
  // ignorar ou falhar silenciosamente
}

// ❌ RUIM: Lançar erro diretamente
try {
  const user = await getUser();
} catch (error) {
  throw error; // Propagar sem tratamento
}
```

## Recursos Adicionais

- Zod Docs: https://zod.dev
- Sonner: https://sonner.emilkowal.ski
- React Hook Form: https://react-hook-form.com
- Next.js Error Handling: https://nextjs.org/docs/app/building-your-application/routing/error-handling
- TypeScript Handbook: https://www.typescriptlang.org/docs

## Resumo

Código confiável = Simples + Validado + Com tratamento de erros

**SEMPRE:**
- ✅ Build antes de apresentar
- ✅ Try/catch em operações críticas
- ✅ Validação com Zod
- ✅ Error boundaries
- ✅ Loading e empty states
- ✅ Toast para feedback
- ✅ Type safety completa
- ✅ Null/undefined checks
