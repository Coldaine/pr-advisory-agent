---
name: dependency-audit
description: Deterministically audit dependency versions and vulnerabilities for PRs using check_deps.py, direct osv-scanner shell execution, and Exa/Firecrawl MCP for changelog context.
---

# Dependency Audit Skill

## When to use

Use this skill for every pull request reviewed by the Dependency Auditor agent.

## Core rule

Do not guess package versions from model memory. Use deterministic tools for live version and vulnerability data.

## Workflow

1. Run:
   ```bash
   python3 scripts/check_deps.py .
   ```
   Capture and inspect the JSON output.

2. Locate lockfiles and run `osv-scanner` directly. Do not call a wrapper script.
   Supported lockfiles to try:
   - `package-lock.json`
   - `yarn.lock`
   - `pnpm-lock.yaml`
   - `poetry.lock`
   - `requirements.txt`
   - `Cargo.lock`
   - `go.sum`
   - `Gemfile.lock`

   Example:
   ```bash
   osv-scanner --lockfile package-lock.json --format json
   ```

3. Use Exa MCP for changelog and breaking-change context:
   - `<package_name> changelog <latest_version>`
   - `<package_name> migration guide <current_version> to <latest_version>`

4. Use Firecrawl MCP to scrape specific changelog/docs pages when Exa finds a relevant source that needs deeper reading.

5. Post one advisory PR comment with:
   - summary of critical/high findings first;
   - dependency table: `Package | Current | Latest | Security Risk | Breaking Changes`;
   - collapsed full output only when useful.

6. Update memory:
   - `dependency-tracking` memory block with repeated or resolved dependency flags;
   - `team-patterns` memory block when a pattern emerges;
   - MemFS `history/pr-<number>.md` with concise review summary.

## Priority order

- P0: Known vulnerability / active exploit / CVE affecting current version.
- P1: Deprecated or abandoned dependency with recommended replacement.
- P2: Major version jump with meaningful security/maintenance benefit.
- P3: Minor update with clear benefit.
- P4: Patch update or freshness-only note.

## Anti-patterns

- Do not hallucinate latest versions.
- Do not write custom wrappers for Exa, Firecrawl, or OSV.
- Do not modify code.
- Do not approve PRs.
- Do not pad the comment with low-value freshness noise.