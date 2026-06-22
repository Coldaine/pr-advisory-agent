# QA Checklist

## Plan integrity

- [ ] Flat parallel architecture: two independent jobs, two independent agents.
- [ ] No orchestrator agent.
- [ ] No webhook sidecar / Flask listener.
- [ ] No custom `augmented_web_search.py`.
- [ ] No custom `osv_scan.py`.
- [ ] No custom `git_clone.py`.
- [ ] Firecrawl is retained via MCP, not removed.
- [ ] Exa is retained via MCP.
- [ ] `check_deps.py` includes WHY NOT LLM comments and deterministic registry calls.

## GitHub Actions

- [ ] `pull_request` triggers include `opened` and `synchronize`.
- [ ] Each Letta action step has a `prompt` input.
- [ ] Each Letta action step has `use_sticky_comment: "true"`.
- [ ] Permissions are `contents: read` and `pull-requests: write`; no `contents: write`.
- [ ] `fetch-depth: 0` is used.
- [ ] `osv-scanner` is installed with `go install` and GOPATH bin is added to `$GITHUB_PATH`.
- [ ] Dependency job uses cheaper model (`haiku`) or explicitly chosen low-cost model.
- [ ] Architecture job uses `auto` or deliberate stronger model.

## Doppler / secrets

- [ ] No real secrets in files.
- [ ] `.env.local` does not exist.
- [ ] `LETTA_API_KEY` is present in `codingagents/dev`.
- [ ] Exa and Firecrawl keys are present in `search_tools_and_browsers/dev`.
- [ ] Local commands use `doppler run`.
- [ ] GitHub secrets are synced from Doppler, not hand-maintained.
- [ ] K8s secrets come from External Secrets / Doppler, not checked manifests.

## K8s self-hosted server

- [ ] PostgreSQL/pgvector exists.
- [ ] `LETTA_MEMFS_SERVICE_URL=local` is set.
- [ ] `SECURE=true` and `LETTA_SERVER_PASSWORD` are set.
- [ ] Ingress is HTTPS.
- [ ] Docker image deprecation risk is accepted and tracked.

## Agent bootstrap

- [ ] Dependency Auditor agent created.
- [ ] Architectural Advisor agent created.
- [ ] Agent IDs saved as GitHub variables.
- [ ] Dependency skill installed for dependency agent.
- [ ] Architecture skill installed for architecture agent.
- [ ] Exa MCP connected.
- [ ] Firecrawl MCP connected.
- [ ] Sleep-time/reflection configured or documented as follow-up.