# Dependency Audit Skill

## Purpose
Scan the entire repository for all dependencies and check their current versions
against the latest available versions. Flag security vulnerabilities and deprecated
packages.

## When to Activate
Activate this skill when reviewing any pull request.

## Instructions

1. Run `bash scripts/check-deps.sh` and capture the output.

2. Parse the output for each ecosystem. For each dependency found:
   - Identify the current version
   - Identify the latest available version
   - Determine the update type (patch / minor / major)
   - Check for known security vulnerabilities
   - Check for deprecation notices

3. Triage findings into priority order:
   - P0: Security vulnerabilities (CVEs, known exploits)
   - P1: Deprecated packages with recommended replacements
   - P2: Major version jumps (likely breaking changes)
   - P3: Minor version updates
   - P4: Patch updates

4. Format the output as the Dependency Audit section of the PR comment.

## Output Format

### Dependency Audit

#### 🔴 Critical (Security / Deprecated)
| Package | Current | Latest | Gap | Issue |
|---------|---------|--------|-----|-------|
| `package-name` | 1.0.0 | 2.0.0 | Major | CVE-XXXX / Deprecated: use `alternative` |

#### 🟡 Available Updates (Non-Critical)
| Package | Current | Latest | Gap | Notes |
|---------|---------|--------|-----|-------|

#### 🟢 Up to Date
X of Y dependencies are on their latest version.

<details>
<summary>Full dependency list</summary>
[Complete table with every dependency]
</details>

## Notes
- If the PR already addresses a flagged dependency, note that in the comment.
- If an ecosystem is not covered by the script, read the manifest file directly
  and query the registry API.
- Always prioritize security findings over version freshness.
