---
name: architecture-advisory
description: Review PR architecture using actual diff/code context and Exa/Firecrawl MCP; provide up to 5 viable alternatives with concrete pros/cons.
---

# Architecture Advisory Skill

## When to use

Use this skill for every pull request reviewed by the Architectural Advisor agent.

## Core rule

Give specific, code-grounded alternatives. Provide up to 5 viable alternatives, not exactly 5 filler items.

## Workflow

1. Inspect the diff:
   ```bash
   git fetch origin <base-branch> --depth=1 || true
   git diff origin/<base-branch>...HEAD
   ```

2. Read surrounding code, not just changed files:
   - entry points;
   - config files;
   - adjacent modules;
   - dependency and framework patterns;
   - tests where relevant.

3. Use Exa MCP for architectural/library context.

4. Use Firecrawl MCP to scrape specific docs pages when deeper library/framework details are needed.

5. Check MemFS `patterns/` for repo-specific lessons from prior reviews.

6. Post one advisory PR comment. For each viable alternative include:
   - **Current:** actual file/code reference.
   - **Alternative:** concrete approach.
   - **Pros:** 2-3 specific benefits.
   - **Cons:** 2-3 specific costs or risks.
   - **Effort:** Low / Medium / High.

7. Update memory:
   - `team-patterns` memory block with what was suggested;
   - architecture history/pattern block with recurring choices;
   - MemFS `history/pr-<number>.md` with concise review summary.

## Quality bar

- Every finding must reference actual files/code.
- If fewer than 5 alternatives are useful, provide fewer and say why.
- Do not provide generic pattern catalogs.
- Do not suggest full rewrites unless the current approach is genuinely broken.
- Do not repeat suggestions the team has consistently ignored unless there is new evidence.

## Anti-patterns

- Do not modify code.
- Do not approve PRs.
- Do not write custom Exa/Firecrawl wrappers.
- Do not pad with boilerplate.