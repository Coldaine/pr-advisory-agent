# Architecture Advisory Skill

## Purpose
Identify up to 5 alternative architectural approaches that the codebase could use
but currently doesn't. For each, provide specific pros and cons referencing
actual code.

## When to Activate
Activate this skill when reviewing any pull request.

## Instructions

1. Read the PR diff to understand what's changing.

2. Read the broader codebase context — not just the changed files. Read the
   surrounding modules, the entry points, the configuration, and the
   dependency structure.

3. Identify the architectural patterns currently in use:
   - API design (REST, GraphQL, gRPC, tRPC, etc.)
   - Data access (ORM, query builder, raw SQL, etc.)
   - State management (local state, global store, server state, etc.)
   - Authentication/authorization approach
   - Error handling patterns
   - Testing patterns
   - Deployment/infrastructure patterns

4. Identify up to 5 places where an alternative approach exists. Each
   alternative must be:
   - Specific to THIS codebase (reference actual files and code)
   - Genuinely viable (not a full rewrite unless the current approach is broken)
   - Something a senior engineer would actually consider

5. For each alternative, provide:
   - **Current approach**: what the codebase does now (reference the file/code)
   - **Alternative**: what could replace it
   - **Pros**: 2-3 specific, concrete benefits
   - **Cons**: 2-3 specific, concrete costs
   - **Effort estimate**: Low / Medium / High (with brief explanation)

6. If you have past review data in memory, check whether you've suggested
   this alternative before and the team ignored it. If so, either skip it
   or reframe it with new evidence.

## Output Format

### Architecture Advisory

Based on the changes in this PR and the surrounding codebase, here are up to 5
alternative architectural approaches to consider:

#### Alternative 1: [Name]
**Current**: [what the code does now — reference file:line]
**Alternative**: [what could replace it]
**Pros**:
- [specific benefit]
- [specific benefit]
**Cons**:
- [specific cost]
- [specific cost]
**Effort**: [Low/Medium/High] — [brief explanation]

#### Alternative 2: [Name]
...

## Quality Bar
- Each alternative must reference actual files or code patterns
- Pros and cons must be specific to this codebase, not generic advice
- If you cannot find 5 genuinely viable alternatives, provide fewer and
  explain why (don't pad with filler)
- If the PR touches only trivial changes (typo fix, config change), note
  that architecture analysis is not applicable and skip the section
