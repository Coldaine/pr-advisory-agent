# API Patterns

## REST
- **Pros**: Standardized, easy to cache, great tooling
- **Cons**: Over/under-fetching, multiple round trips
- **When to use**: Public APIs, simple CRUD, resource-heavy domains

## GraphQL
- **Pros**: Client-specified payloads, strong typing, single endpoint
- **Cons**: Caching is hard, N+1 query problems, complex to secure
- **When to use**: Complex related data, mobile clients, rapidly changing UI

## gRPC
- **Pros**: Extremely fast, strong contracts, bi-directional streaming
- **Cons**: Hard to debug (binary), requires client generation
- **When to use**: Microservice-to-microservice communication, high performance

## tRPC
- **Pros**: End-to-end type safety, no code generation, zero-schema
- **Cons**: TypeScript only, tightly couples client and server
- **When to use**: Monorepos (Next.js/React) with TypeScript full-stack
