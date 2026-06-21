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

1. Inspect the diff with `git diff origin/<base-branch>...HEAD`.
2. Read surrounding code, not just changed files.
3. Use Exa MCP for architectural/library context.
4. Use Firecrawl MCP to scrape specific docs pages when deeper details are needed.
5. Check MemFS `patterns/` for repo-specific lessons from prior reviews.
6. Post one advisory PR comment with viable alternatives only.
7. Update `team-patterns` and MemFS `history/pr-<number>.md`.

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