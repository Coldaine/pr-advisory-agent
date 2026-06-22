# Flat Parallel Letta PR Advisors

This implementation package is the corrected ZAI-plan variant: two independent Letta Code agents triggered in parallel by GitHub Actions.

- **Dependency Auditor**: deterministic dependency inventory/version checks via `scripts/check_deps.py`, direct `osv-scanner` shell execution, Exa/Firecrawl MCP for changelog context.
- **Architectural Advisor**: reads the PR diff and surrounding code, uses Exa/Firecrawl MCP for architectural/library context, posts up to 5 viable alternatives.

No orchestrator. No webhook sidecar. No custom Firecrawl wrapper. No OSV wrapper. No git clone tool.

## Secret posture

Doppler is the source of truth.

- `LETTA_API_KEY` is stored in Doppler: `codingagents/dev`.
- Exa/Firecrawl keys are stored in Doppler: `search_tools_and_browsers/dev`.
- Local/bootstrap commands must use `doppler run`.
- Do not create `.env.local` with real secrets.
- GitHub Actions secrets should be populated from Doppler (or hydrated by a Doppler service token) rather than hand-entered.

## Files

- `.github/workflows/letta-pr-advisors.yml` — two parallel jobs, one per agent.
- `scripts/check_deps.py` — deterministic registry checks with WHY NOT LLM rationale.
- `.skills/dependency-audit/SKILL.md` — dependency auditor instructions.
- `.skills/architecture-advisory/SKILL.md` — architecture advisor instructions.
- `k8s/` — baseline self-hosted Letta server manifests.
- `docs/runbooks/doppler.md` — Doppler-first secret handling and bootstrap commands.
- `docs/qa/QA_CHECKLIST.md` — validation checklist.
- `docs/qa/SELF_AUDIT.md` — review of plan integrity after rewrite.
- `tests/` — containing test package manifests (`package.json`, `requirements.txt`) to validate the dependency scanner output.

## Current implementation status

Ready to start implementation work, but not ready to deploy until:

1. A self-hosted Letta server URL exists (`LETTA_BASE_URL`).
2. Two agents are created and IDs are stored as `LETTA_DEP_AGENT_ID` and `LETTA_ARCH_AGENT_ID`.
3. Exa and Firecrawl MCP servers are connected to the agents.
4. GitHub Actions can access `LETTA_API_KEY` and `LETTA_BASE_URL` from Doppler-backed secrets.
