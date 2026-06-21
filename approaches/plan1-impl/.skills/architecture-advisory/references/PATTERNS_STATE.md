# State Management Patterns

## Local State (React useState)
- **Pros**: Simple, localized, fast
- **Cons**: Prop drilling, hard to share across distant components
- **When to use**: Component-specific UI state (open/close, form input)

## Global Store (Redux, Zustand)
- **Pros**: Accessible anywhere, time-travel debugging, predictable
- **Cons**: Boilerplate, can become a dumping ground
- **When to use**: Complex client-side state (shopping cart, user session)

## Server State (React Query, SWR, Apollo)
- **Pros**: Built-in caching, background fetching, deduplication
- **Cons**: Paradigm shift from traditional stores
- **When to use**: Any data fetched from an API
