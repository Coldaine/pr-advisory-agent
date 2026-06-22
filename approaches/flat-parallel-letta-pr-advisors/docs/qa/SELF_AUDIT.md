# Self-Audit: Rewrite Integrity

## Result

The rewrite preserved the intended architecture and restored the pieces that were incorrectly removed.

## What was preserved

- Firecrawl remains first-class, but as an MCP server rather than a Python wrapper.
- Exa remains first-class, also via MCP.
- The dependency scanner remains deterministic and includes the WHY NOT LLM rationale.
- The system remains flat and parallel: two jobs, two agents, no orchestrator.
- The agents remain advisory-only.
- Letta Code built-ins are used where available.

## What was intentionally removed

- `augmented_web_search.py` custom wrapper — removed because MCP exists.
- `osv_scan.py` wrapper — removed because the agent can run `osv-scanner` directly.
- `git_clone.py` — removed because `actions/checkout` already provides the repo on the runner.
- Webhook sidecar — removed because GitHub Actions is the right execution surface for repo tools.
- Orchestrator agent — removed because independent specialized agents are simpler and faster.

## What still needs verification

- Exact Letta SDK/API call shape for programmatic agent creation and memory block creation.
- Exact MCP connection mechanism for Exa and Firecrawl on the selected self-hosted Letta server version.
- Whether `letta/letta:latest` self-hosted server accepts the same `LETTA_API_KEY` semantics as Letta Cloud through `letta-code-action` when `letta_base_url` is set.
- Per-agent MemFS isolation semantics on a shared self-hosted server.

## Potential weak spot

The GitHub Action currently references GitHub Secrets for `LETTA_API_KEY` and `LETTA_BASE_URL`. Doppler remains the source of truth, but GitHub still needs those values synced or hydrated. If the target posture is zero mirrored secrets in GitHub, the workflow needs a Doppler service token and an action-input hydration pattern validated against GitHub Actions expression timing.
