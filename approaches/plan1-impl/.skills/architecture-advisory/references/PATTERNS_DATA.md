# Data Access Patterns

## ORM (Object-Relational Mapping)
- **Examples**: Prisma, TypeORM, SQLAlchemy, Hibernate
- **Pros**: Rapid development, type safety, database agnostic
- **Cons**: Performance overhead, complex query generation ("magic")
- **When to use**: Standard CRUD apps, complex business logic in code

## Query Builders
- **Examples**: Knex, Kysely, PyPika
- **Pros**: More control than ORM, safer than raw SQL, flexible
- **Cons**: Still requires mapping to objects, steeper learning curve
- **When to use**: Apps needing complex joins or performance tuning

## Raw SQL
- **Pros**: Maximum performance, uses database-specific features
- **Cons**: Vulnerable to SQL injection if not careful, tedious to map
- **When to use**: Analytics, highly tuned endpoints, simple microservices
