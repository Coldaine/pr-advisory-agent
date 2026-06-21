# Letta Code Reviewer: Plan 1 (Standard/Cloud)

**Plan file:** `Plan1.txt`
**Reviewer:** Letta Code (agent-2a50ea69)
**Date:** 2026-06-21
**Sources:** `action.yml` from `letta-ai/letta-code-action@main`, official Letta docs, real-world `review.yml` from `letta-ai/letta-code` repo

---

## Reconciliation Status After Plan Correction

The main plan in `approaches/plan1/Plan1.txt` has been corrected against the findings below:

| Original finding | Current status |
|:---|:---|
| Wrong GitHub Action reference | Corrected to `letta-ai/letta-code-action@v0` |
| Wrong/redundant CLI installation step | Removed from the workflow; optional local setup uses `npm install -g @letta-ai/letta-code` |
| Non-dot `skills/` directory | Corrected to `.skills/` for custom skill examples |
| Missing sticky comment configuration | Corrected with `use_sticky_comment: "true"` |
| Missing model configuration | Corrected with `model: auto` |
| `agent_id` stored as a secret | Corrected to `vars.LETTA_AGENT_ID` |
| Silent scanner failures | Addressed in the agent configuration by requiring missing-tool disclosure and manifest fallback |
| Forced "exactly 5" architecture findings | Corrected to "up to 5" viable alternatives |

Remaining validation items: verify the current Letta agent creation CLI/API flow and sleep-time/self-evaluation command names before implementation.

## Critiques with Severity Grades

### CRITICAL — Would prevent the system from working

#### C1: Wrong GitHub Action reference
**Severity: Critical**

The workflow uses `uses: letta-ai/letta-code@v1`. This repository/action does not exist. The correct action is `letta-ai/letta-code-action@v0`.

- Source: https://github.com/letta-ai/letta-code-action
- The real-world `review.yml` in `letta-ai/letta-code` pins a specific commit hash: `letta-ai/letta-code-action@daa80f29e345315623ff759f5ecf5018946bbc15`

**Fix:** Change to `uses: letta-ai/letta-code-action@v0` (or pin to a specific commit).

---

#### C2: Wrong CLI installation command
**Severity: Critical**

The plan specifies:
```bash
curl -fsSL https://letta.com/install.sh | bash
```

This URL does not serve a Letta Code installer. The official installation is:
```bash
npm install -g @letta-ai/letta-code
```
Requires Node.js 18+.

- Source: https://docs.letta.com/letta-code/cli/

**Additionally:** The GitHub Action installs the CLI itself. The `action.yml` includes a step that runs `npm install -g @letta-ai/letta-code` if no `path_to_letta_executable` is provided. The plan's separate "Install Letta Code" step is both wrong AND redundant — it should be removed entirely.

**Fix:** Remove the `Install Letta Code` step from the workflow. The action handles CLI installation internally.

---

### HIGH — Significant issue causing failures or security problems

#### H1: Skills directory path mismatch
**Severity: High**

The plan places skills in `skills/dependency-audit/` and `skills/architecture-advisory/`. However, the GitHub Action installs its built-in skill to `.skills/github-action/SKILL.md` (dot-prefixed). Letta Code discovers skills from `.skills/`, not `skills/`.

- Source: `action.yml` step "Setup GitHub Action Skill": `mkdir -p .skills/github-action`

If skills are placed in `skills/` (without the dot prefix), the Letta Code CLI may not auto-discover them. The agent would run without the dependency-audit and architecture-advisory skills loaded, defeating the core purpose.

**Fix:** Use `.skills/dependency-audit/` and `.skills/architecture-advisory/` instead of `skills/`.

---

#### H2: Missing `use_sticky_comment` configuration
**Severity: High**

Without `use_sticky_comment: "true"`, the action may create a new tracking comment on every `synchronize` event. The plan triggers on `[opened, synchronize]`, meaning every push to a PR would generate a new comment. For a PR advisory agent that posts a single comprehensive review, this would clutter the PR with duplicate comments.

The real-world `review.yml` from `letta-ai/letta-code` uses `tracking_comment: "false"` and `track_progress: ""` to control comment behavior.

**Fix:** Add `use_sticky_comment: "true"` to the `with:` block, or configure `track_progress` and `tracking_comment` appropriately.

---

#### H3: `letta agent create` command may not exist in this form
**Severity: High**

The plan specifies:
```bash
letta agent create --name "PR Advisory Agent"
```

The official CLI docs show agent creation via `letta --new-agent --personality tutorial`. The `letta agent create` subcommand syntax is not documented. If this command doesn't exist, the agent setup step fails before any review work begins.

- Source: https://docs.letta.com/letta-code/cli/ — shows `letta --new-agent` not `letta agent create`

**Fix:** Verify the correct agent creation command. Use `letta --new-agent` or create the agent via the Letta API/SDK. Alternatively, let the GitHub Action auto-discover/create an agent (if `agent_id` is not provided, the action finds or creates one automatically per `action.yml`).

---

### MEDIUM — Degrades quality or requires workarounds

#### M1: `check-deps.sh` tools not available on GitHub runner
**Severity: Medium**

The script invokes `cargo outdated`, `pip-audit`, `bundle outdated`, `dotnet list package --outdated` — none of which are pre-installed on standard GitHub `ubuntu-latest` runners. The script uses `2>/dev/null || true` to suppress errors, so missing tools silently produce no output for that ecosystem.

This isn't broken (graceful degradation), but it means the agent silently misses ecosystems. The agent should be instructed to fall back to manual manifest parsing when a tool produces no output, and the plan should document which ecosystems will work out-of-the-box vs. which need pre-installation.

**Fix:** Either pre-install tools in a workflow step before the action, or explicitly document that ecosystems without pre-installed tools will rely on the agent's manual manifest parsing fallback.

---

#### M2: Missing `model` configuration in workflow
**Severity: Medium**

The plan's workflow doesn't set a `model` input. The action defaults to `opus` (the most expensive model). For a PR advisory agent that runs on every PR, this could be costly. The plan's AGENT-CONFIG.md discusses multi-model routing (haiku for triage, opus for architecture, sonnet for formatting) but the workflow doesn't implement any of it.

The real-world `review.yml` uses `model: auto`.

**Fix:** Set `model: auto` or a specific cheaper model for routine dependency checks. Consider whether opus-level reasoning is needed for every PR.

---

#### M3: `agent_id` stored as secret but should be a variable
**Severity: Medium**

The workflow uses `${{ secrets.LETTA_AGENT_ID }}`. GitHub secrets are designed for sensitive values. An agent ID is not sensitive — it's a public identifier. It should be stored as a repository variable (`vars.LETTA_AGENT_ID`) or hardcoded in the workflow. Plan 2's workflow correctly uses `${{ vars.LETTA_AGENT_ID }}`.

**Fix:** Use `vars.LETTA_AGENT_ID` instead of `secrets.LETTA_AGENT_ID`.

---

#### M4: Unverified Letta CLI commands
**Severity: Medium**

The plan references several CLI commands/slash commands that are not confirmed in official docs:
- `/sleeptime` — mentioned in docs context for dream agents but not in the CLI command reference
- `/palace` — not found in any official source
- `letta agent get <agent-id>` — not documented

Known confirmed commands: `/init`, `/new`, `/resume`, `/agent`, `/model`, `/connect`, `/login`, `/compact`, `/reflect`, `/remember`, `/context`, `/doctor`, `/clear`.

**Fix:** Verify each command exists before relying on it. Use `/reflect` or background reflection agents (confirmed in the system prompt) instead of `/sleeptime` if the latter can't be verified. Use the Letta API or desktop app instead of `/palace` for memory inspection.

---

### LOW — Minor inaccuracy or improvement opportunity

#### L1: "36.8% performance improvement" claim lacks citation
**Severity: Low**

The plan cites a "36.8% relative improvement (15.7% absolute)" for skill learning as established fact. While this may come from Letta research, no specific paper, benchmark, or URL is cited. The claim could be real but is presented without verifiable provenance.

**Fix:** Add a citation to the specific research paper or blog post, or soften the claim to "Letta reports measurable improvements from skill learning."

---

#### L2: `fetch-depth: 0` may be unnecessary
**Severity: Low**

The plan uses `fetch-depth: 0` (full git history). For dependency auditing, only the current file state matters. For architecture analysis, full git history could help (commit patterns, blame context) but may significantly increase checkout time for large repos. This is a reasonable choice but should be a conscious decision, not a default.

**Fix:** Document why full history is needed, or use `fetch-depth: 1` if git history isn't actually used by the agent.

---

#### L3: Plan includes "Beyond Requirements" marketing content
**Severity: Low**

The final ~500 lines of `Plan1.txt` are essentially a Letta Code sales pitch — listing 12 features that go "above and beyond" the requirements with phrases like "This is the biggest one, and it's not in your requirements at all" and "No other agent framework gives you this." This adds no implementation value and inflates the document.

**Fix:** Remove or separate the marketing content from the technical plan.

---

## Summary

| Severity | Count | Issues |
|:---|:---|:---|
| Critical | 2 | Wrong action reference, wrong CLI install (redundant step) |
| High | 3 | Skills path mismatch, missing sticky comment config, unverified agent create command |
| Medium | 4 | Missing runner tools, no model config, agent_id as secret, unverified CLI commands |
| Low | 3 | Uncited performance claim, unnecessary fetch-depth, marketing content |

**Overall assessment:** The architecture is sound and close to working. The critical issues are mechanical (wrong names/URLs) and easy to fix. The high issues would cause real problems at runtime (skills not loading, comment spam, agent creation failure). The medium and low issues are quality/polish concerns. No fundamental design errors — just implementation mistakes that need correction before deployment.
