# Checklist de Confiabilidade - Next.js

Verificação obrigatória antes de apresentar qualquer código. Use este checklist para garantir código robusto, confiável e à prova de falhas.

## Princípio Fundamental

**NUNCA apresentar código que possa quebrar. SEMPRE validar antes de entregar.**

---

## Verificações de TypeScript

- [ ] Rodar `npx tsc --noEmit` sem erros
- [ ] Rodar `npm run type-check` (se configurado)
- [ ] Todos os imports estão tipados corretamente
- [ ] Nenhum `any` implícito (revisar noImplicitAny)
- [ ] Props de componentes estão tipadas com TypeScript
- [ ] Retornos de funções estão explicitamente tipados
- [ ] Erros de type não ignorados com `@ts-ignore`

---

## Verificações de Build

- [ ] Rodar `npm run build` - **OBRIGATÓRIO**
- [ ] Build completa SEM erros
- [ ] Nenhum erro crítico no console
- [ ] Nenhum warning de build relacionado a código escrito
- [ ] Verificar se há warnings que podem virar erros em produção
- [ ] Testar: `npm run build && npm start`

---

## Verificações de Lint

- [ ] Rodar `npm run lint`
- [ ] Nenhum erro de linting
- [ ] Nenhum warning ignorado intencionalmente
- [ ] Código segue padrões de estilo do projeto
- [ ] Auto-fix com `npm run lint -- --fix` se necessário

---

## TypeScript Strict Compliance

- [ ] Null/undefined checks implementados
- [ ] Nenhuma tentativa de acessar propriedade em valor null
- [ ] Operador `?.` usado quando apropriado
- [ ] Validação de tipos parametrizados (generics)
- [ ] Type guards para union types
- [ ] Imports corretos de tipos (usar `import type` quando aplicável)
- [ ] Exports tipados corretamente

---

## Null Safety e Empty States

### Verificações de Null/Undefined

- [ ] Componentes tratam props null/undefined
- [ ] Nenhum acesso direto a propriedades sem verificação
- [ ] Usar optional chaining `?.` para segurança
- [ ] Usar nullish coalescing `??` para valores padrão
- [ ] Array methods têm fallback para arrays vazios

### Estados Vazios

- [ ] Listas vazias têm UI adequada
- [ ] Mensagens "nenhum resultado" exibidas corretamente
- [ ] Placeholders mostrados enquanto dados carregam
- [ ] Empty state é visível e bem formatado
- [ ] Sem erros quando dados não existem

---

## Error Boundaries

- [ ] Root error boundary criada em `app/error.tsx`
- [ ] Error boundaries em rotas com async operations
- [ ] Error component mostra mensagem significativa
- [ ] Botão "Tentar Novamente" ou reset em error boundaries
- [ ] Errors são logados no console
- [ ] Digest de erro (para monitoramento) capturado
- [ ] Layout não quebra quando erro ocorre

---

## Loading States

- [ ] `loading.tsx` criado em rotas com dados pesados
- [ ] Skeleton loaders ou spinners mostrados
- [ ] Loading state usa `Skeleton` component
- [ ] Tempo de carregamento é razoável
- [ ] Feedback visual claro de que algo está acontecendo
- [ ] Nenhum "flash" de conteúdo desatualizado
- [ ] Estado de carregamento matches layout final

---

## Validação com Zod

- [ ] Schema Zod definido para todos os forms
- [ ] Client-side validation com React Hook Form + Zod
- [ ] Server-side validation duplicada (nunca confiar apenas em client)
- [ ] Mensagens de erro customizadas em português
- [ ] `safeParse()` usado (retorna resultado, não lança erro)
- [ ] Validação de ambiente variables com Zod
- [ ] Types inferidos com `z.infer<typeof schema>`
- [ ] Validação de arrays e objetos complexos

---

## Server Actions com Error Handling

- [ ] Try/catch envolvendo toda lógica crítica
- [ ] Erros capturados e convertidos em response estruturada
- [ ] Nunca lançar erro diretamente (usar return com success: false)
- [ ] revalidatePath() chamado após mutação bem-sucedida
- [ ] Validação com Zod antes de usar dados
- [ ] ID/params validados antes de usar em queries
- [ ] Permissões/auth verificadas (if applicable)
- [ ] Console.error usado para logs do servidor

---

## Tratamento de Erros em Fetch

- [ ] Try/catch envolvendo fetch ou database calls
- [ ] Tratamento específico para diferentes tipos de erro
- [ ] Fallback para dados não encontrados (notFound() ou null)
- [ ] Timeout handling se aplicável
- [ ] Retry logic para operações críticas (if applicable)
- [ ] Connection errors tratados adequadamente

---

## Common Runtime Errors Prevention

- [ ] Nenhum acesso a `window` fora de client components
- [ ] Nenhum acesso a `process.env` em client components
- [ ] Dinâmic imports usados para código client-only
- [ ] Image URLs validadas antes de usar `next/image`
- [ ] Event handlers não lançam erros não capturados
- [ ] Async/await chains completas sem promessas flutuantes
- [ ] Nenhum `console.log` de dados sensíveis

---

## Form Validation Coverage

### Input Validation

- [ ] Campos obrigatórios marcados como `required`
- [ ] Tipos de input corretos (email, number, date, etc)
- [ ] Min/max length implementado
- [ ] Padrões (regex) validados com Zod
- [ ] Arquivo uploads têm limite de tamanho
- [ ] Inputs sanitizados de XSS

### Error Messages

- [ ] Erro de validação exibido inline com campo
- [ ] Mensagens em português e descritivas
- [ ] Indicação visual clara do erro
- [ ] Erro desaparece quando usuário corrige
- [ ] Estado de erro não quebra form submit

### Form State

- [ ] isSubmitting/isPending controla loading
- [ ] Botão submit desabilitado durante processamento
- [ ] Form não pode ser resubmetido durante processamento
- [ ] Estado é limpo após sucesso/erro
- [ ] Feedback visual (toast, alert) após resultado

---

## Database/API Integration

- [ ] Queries têm WHERE conditions (nunca delete/update all)
- [ ] IDs validados antes de usar em queries
- [ ] Limite de resultados implementado (pagination)
- [ ] Erros de banco tratados (unique constraints, etc)
- [ ] Timestamps (createdAt, updatedAt) configurados
- [ ] Soft deletes considerados onde apropriado
- [ ] Nenhum N+1 query problem

---

## Component Safety

- [ ] Props interface completa e tipada
- [ ] Componente renderiza com dados mínimos
- [ ] Componente renderiza com dados null
- [ ] Componente renderiza com dados vazio
- [ ] Componente renderiza com erro
- [ ] Sem lógica condicional complexa
- [ ] Children componentes validam props passadas

---

## API Routes / Server Handlers

- [ ] HTTP method validation (POST, GET, etc)
- [ ] CORS configurado se necessário
- [ ] Rate limiting considerado
- [ ] Input validation em request body
- [ ] Response status codes apropriados
- [ ] Error response formatado consistentemente
- [ ] Nenhuma credential/secret exposta em resposta

---

## Browser Compatibility

- [ ] Código usa ES2020+ (conforme tsconfig)
- [ ] Nenhum polyfill necessário não providenciado
- [ ] LocalStorage/SessionStorage verificam se disponível
- [ ] Mobile viewport configurado
- [ ] Touch events funcionam (if applicable)
- [ ] Keyboard navigation funciona

---

## Performance & Bundle

- [ ] Lazy loading implementado onde apropriado
- [ ] Code splitting automático via dynamic imports
- [ ] Nenhuma dependência gigante desnecessária
- [ ] Tree shaking habilitado
- [ ] Imagens otimizadas (next/image)
- [ ] Fontes carregadas otimamente (next/font)

---

## Accessibility (A11y)

- [ ] Semantic HTML usado (button, form, main, etc)
- [ ] Labels associados com inputs
- [ ] Alt text em imagens
- [ ] aria-labels onde necessário
- [ ] Color contrast adequado
- [ ] Keyboard navigation funciona
- [ ] Fotos não são único meio de comunicação

---

## Security Basics

- [ ] Nenhuma credencial hardcoded
- [ ] Environment variables sensíveis nunca expostas
- [ ] User input escapado/sanitizado
- [ ] CSRF protection se aplicável
- [ ] Validação server-side (não apenas client)
- [ ] Nenhuma execução dinâmica de código
- [ ] Dependencies sem vulnerabilidades conhecidas

---

## Environment Variables

- [ ] Todas variáveis necessárias documentadas
- [ ] `.env.example` atualizado
- [ ] Variáveis `NEXT_PUBLIC_*` apenas para dados públicos
- [ ] Validação com Zod em runtime
- [ ] Erro claro se variável falta em produção
- [ ] Nenhuma variável sensível em `NEXT_PUBLIC_*`

---

## Testing de Fluxo

- [ ] Fluxo happy path funciona (usuario faz algo normal)
- [ ] Fluxo error path funciona (network down, API error, etc)
- [ ] Fluxo edge case considerado (empty data, muito data, etc)
- [ ] Alterações não quebram features existentes
- [ ] Manual testing em navegador funciona
- [ ] Mobile testing em device real (or emulator)

---

## Checklist Final Pré-Deploy

Antes de fazer deploy QUALQUER código:

- [ ] Build completa: `npm run build` ✅
- [ ] TypeScript limpo: `npx tsc --noEmit` ✅
- [ ] Lint passa: `npm run lint` ✅
- [ ] Error boundaries cobertas
- [ ] Loading states implementados
- [ ] Not found handlers criados
- [ ] Try/catch em operações críticas
- [ ] Zod validation em forms
- [ ] Null checks em componentes
- [ ] Empty states tratados
- [ ] Toast/feedback de ações
- [ ] Sem console.errors
- [ ] Sem warnings do build
- [ ] Mobile responsivo testado
- [ ] Acessibilidade básica OK
- [ ] Environment vars configuradas

---

## Comandos de Verificação Rápida

```bash
# Verificação completa
npm run build && npm run lint && npx tsc --noEmit

# Apenas build
npm run build

# Apenas TypeScript
npx tsc --noEmit

# Apenas lint
npm run lint -- --fix
```

---

## Resumo de Princípios

1. **Simples é melhor**: Código simples tem menos bugs
2. **Validado sempre**: Input validation salva vidas
3. **Com tratamento de erros**: Try/catch é seu amigo
4. **Null-safe**: Verificar null/undefined previne crashes
5. **Testado**: Build + tipos + lint antes de apresentar

**Lembre-se**: Código robusto = Usuários felizes = Sem 3AM calls
