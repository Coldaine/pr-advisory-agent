# Doppler Runbook

Doppler is the source of truth for secrets. Do not write real secrets to `.env`, `.env.local`, markdown, manifests, or checked-in files.

## Expected Doppler inventory to verify

- `codingagents/dev`
  - `LETTA_API_KEY` — present.
  - `GITHUB_TOKEN` — present, but GitHub Actions should normally use `${{ secrets.GITHUB_TOKEN }}` for PR comments.
- `search_tools_and_browsers/dev`
  - `EXA_API_KEY` — present.
  - `FIRECRAWL_API_KEY` — present.
  - `TAVILY_API_KEY` — present, available if needed.
- `ai-models/dev`
  - `OPENAI_API_KEY` — present.
- `databases/dev`
  - PostgreSQL-related credentials exist, but a dedicated self-hosted Letta DB password/URI should be created for this service rather than reusing unrelated DB credentials.

## Local bootstrap pattern

Use `doppler run`; do not create a local secret file.

```powershell
# Verify the Letta key exists without printing it
$d = doppler run --project codingagents --config dev -- powershell -NoProfile -Command '$env:LETTA_API_KEY -like "sk-let-*"'

# Run a Letta CLI/bootstrap command with the key injected only into process env
doppler run --project codingagents --config dev -- letta --help
```

If a command needs multiple Doppler projects, prefer a small wrapper script that fetches the minimum needed values and passes them directly to the process environment. Do not write a merged `.env` file.

## GitHub Actions pattern

The `letta-code-action` needs `letta_api_key` as an action input. The stable first implementation is:

1. Keep Doppler as source of truth.
2. Sync required values into GitHub repository secrets as deployment material:
   - `LETTA_API_KEY`
   - `LETTA_BASE_URL`
3. Store agent IDs as GitHub variables:
   - `LETTA_DEP_AGENT_ID`
   - `LETTA_ARCH_AGENT_ID`

Use `scripts/sync_github_secrets.ps1` to sync from Doppler to GitHub without printing values.

## K8s pattern

Preferred production pattern: External Secrets Operator + Doppler provider.

This implementation package includes `k8s/external-secrets.template.yaml` as a starting point. Fill in the Doppler token reference using a Kubernetes Secret or cluster-standard secret store. Do not put Doppler tokens directly in manifests.

## Secret names expected by manifests

`letta-secrets`:
- `letta-pg-uri`
- `letta-server-password`
- `openai-api-key`

`web-search-secrets`:
- `exa-api-key`
- `firecrawl-api-key`

GitHub repository secrets:
- `LETTA_API_KEY`
- `LETTA_BASE_URL`

GitHub repository variables:
- `LETTA_DEP_AGENT_ID`
- `LETTA_ARCH_AGENT_ID`
