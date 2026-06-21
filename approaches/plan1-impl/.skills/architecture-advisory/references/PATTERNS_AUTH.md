# Authentication / Authorization Patterns

## JWT (JSON Web Tokens)
- **Pros**: Stateless, scalable, works across domains
- **Cons**: Hard to revoke before expiration, payload visible
- **When to use**: Microservices, mobile apps, cross-domain auth

## Session Cookies
- **Pros**: Secure (HttpOnly), easy to revoke, built into browsers
- **Cons**: Requires server state, harder to scale, CSRF risks
- **When to use**: Traditional web applications, SSR frameworks

## OAuth 2.0 / OIDC
- **Pros**: Delegated auth, standardized, highly secure
- **Cons**: Complex flow, relies on third party
- **When to use**: Third-party integrations, enterprise SSO
