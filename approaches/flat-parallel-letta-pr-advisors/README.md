# Flat Parallel Letta PR Advisors

This implementation package is the corrected ZAI-plan variant: two independent Letta Code agents triggered in parallel by GitHub Actions.

- **Dependency Auditor**: deterministic dependency inventory/version checks via `scripts/check_deps.py`, direct `osv-scanner` shell execution, Exa/Firecrawl MCP for changelog context.
- **Architectural Advisor**: reads the PR diff and surrounding code, uses Exa/Firecrawl MCP for architectural/library context, posts up to 5 viable alternatives.

No orchestrator. No webhook sidecar. No custom Firecrawl wrapper. No OSV wrapper. No git clone tool.

## Secret Posture

Doppler remains the source of truth for configuration and secrets:

- `LETTA_API_KEY` is stored in Doppler: `codingagents/dev`.
- Exa/Firecrawl keys are stored in Doppler: `search_tools_and_browsers/dev`.
- Local/bootstrap commands must use `doppler run`.
- Do not create `.env.local` with real secrets.
- GitHub Actions secrets are populated from Doppler via `scripts/sync_github_secrets.ps1`.

## Files

- `.github/workflows/reusable-pr-advisory.yml` — The root reusable entry point for external repositories.
- `scripts/check_deps.py` — deterministic registry checks with packaging/requests libraries.
- `scripts/sync_github_secrets.ps1` — Doppler-to-GitHub secret syncer script.
- `.skills/dependency-audit/SKILL.md` — dependency auditor instructions.
- `.skills/architecture-advisory/SKILL.md` — architecture advisor instructions.
- `k8s/` — baseline self-hosted Letta server manifests.
- `docs/runbooks/doppler.md` — Doppler-first secret handling and bootstrap commands.
- `docs/qa/QA_CHECKLIST.md` — validation checklist.
- `docs/qa/SELF_AUDIT.md` — review of plan integrity after rewrite.
- `tests/` — containing test package manifests (`package.json`, `requirements.txt`) to validate the dependency scanner output.

---

## Active Letta Agents

The agents have been successfully created on Letta Cloud (using the `letta/auto` model) and their IDs are mapped to the repository variables:

*   **Dependency Auditor** (ID: `agent-519c1c06-83b2-4900-94f1-ac100891b640`)
    *   System prompt is configured to enforce deterministic auditing and prevent code modification or direct PR approvals.
*   **Architectural Advisor** (ID: `agent-49f641aa-4043-4c7d-980a-1a100dea8cf5`)
    *   System prompt is configured to limit recommendations to a maximum of 5 viable alternatives, grounded in actual files/code.

---

## How to Call from External Repositories

Any external repository can call these agents using GitHub Actions by referencing the central reusable workflow.

### 1. Target Repo Workflow File
Create `.github/workflows/pr-advisory.yml` in the target repository with the following structure:

```yaml
name: PR Advisory Reviews
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr_advisory:
    uses: Coldaine/pr-advisory-agent/.github/workflows/reusable-pr-advisory.yml@main
    with:
      letta_dep_agent_id: ${{ vars.LETTA_DEP_AGENT_ID }}
      letta_arch_agent_id: ${{ vars.LETTA_ARCH_AGENT_ID }}
      # Defaults to Letta Cloud. If self-hosting, specify:
      # letta_base_url: 'https://letta.yourdomain.com'
    secrets:
      LETTA_API_KEY: ${{ secrets.LETTA_API_KEY }}
```

### 2. Required Permissions (Target Repo)
Verify the target repository allows the runner to write to pull requests. Ensure `Workflow permissions` under `Settings > Actions > General` is set to **"Read and write permissions"** or explicitly add the permissions block:
```yaml
permissions:
  contents: read
  pull-requests: write
```

### 3. Required Secrets & Variables (Target Repo)
Configure the following in the target repository's Settings:
*   **Repository Secret:**
    *   `LETTA_API_KEY`: API key to connect to the Letta server (Cloud or self-hosted).
*   **Repository Variables:**
    *   `LETTA_DEP_AGENT_ID`: The ID of the Dependency Auditor agent.
    *   `LETTA_ARCH_AGENT_ID`: The ID of the Architectural Advisor agent.

> [!NOTE]
> It is recommended to create a separate pair of Letta agents for each target repository to isolate their memory blocks and review histories.
