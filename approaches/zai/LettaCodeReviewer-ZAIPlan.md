# Letta Code Reviewer: Plan 2 (Self-Hosted Kubernetes)

**Plan files:** `ZAIPlan/Part1.txt` + `Part2.txt`
**Reviewer:** Letta Code (agent-2a50ea69)
**Date:** 2026-06-21
**Sources:** `action.yml` from `letta-ai/letta-code-action@main`, official Letta docs, Docker Hub, `letta-ai/letta` `compose.yaml`, Docker docs

---

## Reconciliation Status After Plan 2 Addendum

`Plan2_Cluster_Baseline_Addendum.md` is now the governing baseline for Plan 2. Read the findings below as the original critique of the older Plan 2 draft, with this status:

| Original finding | Current status |
|:---|:---|
| Wrong Docker image, missing PostgreSQL/pgvector, missing MemFS env var, missing server auth, missing ingress/namespace material | Addressed in the current Part 1/Part 2 revision or captured as cluster facts to verify before final manifests |
| `contents: write` violates advisory-only | Addressed by the GitHub Actions workflow shape using `contents: read` and `pull-requests: write` |
| Missing `synchronize` trigger | Addressed by the GitHub Actions workflow trigger |
| Custom tools packaged in the Kubernetes image | Superseded by the addendum: tools belong on the GitHub runner or in the repo workspace |
| Webhook receiver / pod-local repository clone architecture | Superseded by the addendum: no custom webhook receiver in the baseline |
| Npm-only dependency coverage, shallow checkout, unverified commands, external API overhead | Still important implementation risks to verify before deployment |
| "Exactly 5" architecture advice quota | Corrected to "up to 5" viable alternatives |

## Critiques with Severity Grades

### CRITICAL — Would prevent the system from working

#### C1: Wrong Docker image name
**Severity: Critical**

Both Part 1 and Part 2 reference `letta/letta-server:latest` (Part 1) and `your-registry/letta-pr-advisor:latest` (Part 2, implying a custom build on top of `letta/letta-server`). This image does not exist on Docker Hub.

The real image is `letta/letta:latest`.
- Source: https://hub.docker.com/r/letta/letta
- Source: https://github.com/letta-ai/letta/blob/main/compose.yaml — uses `image: letta/letta:latest`

**Fix:** Replace all references to `letta/letta-server` with `letta/letta`.

---

#### C2: Missing PostgreSQL/pgvector dependency
**Severity: Critical**

The Letta server requires PostgreSQL with pgvector as its database backend. The official `compose.yaml` shows `letta_db` (pgvector) as a required service with a healthcheck. Plan 2's K8s manifests include only a Deployment, Service, and PVC for the Letta server — no database deployment, no database service, no database credentials.

Without PostgreSQL, the Letta server will fail to start. The first-launch Alembic migration creates ~42 tables and requires a working database connection.
- Source: `compose.yaml` in `letta-ai/letta` — `letta_db` service with `ankane/pgvector:v0.5.1`
- Source: RamNode deployment guide — "Wait for 'Database migration completed successfully'"

**Fix:** Add a PostgreSQL/pgvector StatefulSet or Deployment, Service, PVC, and Secret to the K8s manifests. Configure `LETTA_PG_URI` environment variable in the Letta server deployment.

---

#### C3: `contents: write` permission violates advisory-only requirement
**Severity: Critical**

The GitHub Action workflow in Plan 2 uses:
```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
```

Requirement #2 states: "Provides suggestions and does not modify code." `contents: write` allows the agent to push commits to the repository. This is a direct violation of the core advisory-only constraint.

Plan 1 correctly restricts to `contents: read` + `pull-requests: write`.

Note: The Letta Code action's own README and the real-world `review.yml` do use `contents: write` — but those are for a general coding agent that can make commits, not for an advisory-only agent. The permission must match the use case.

**Fix:** Change to:
```yaml
permissions:
  contents: read
  pull-requests: write
```

---

#### C4: Custom tools packaged in the wrong location
**Severity: Critical**

Plan 2's architecture says:
- "Containerize Tools: Create a custom Dockerfile that extends the Letta server image and includes `python3`, `pip`, `osv-scanner`, and your `check_deps.py` script"
- Skills reference: `Execute shell command: python3 /tools/check_deps.py $REPO_PATH`

But the Letta Code CLI runs on the **GitHub Action runner**, not on the Kubernetes pod. The `action.yml` shows the action installs the CLI on the runner (`npm install -g @letta-ai/letta-code`) and runs it there (`bun run .../src/runner/index.ts`). Tool execution (bash, file reading, shell commands) happens on the runner where the repo is checked out.

The `letta_base_url` input tells the CLI which API server to connect to for LLM calls and memory — it does NOT route tool execution to the remote server.

So `python3 /tools/check_deps.py` would execute on the GitHub runner, where `/tools/check_deps.py` does not exist (it's in the K8s Docker image). The dependency audit would fail completely.

- Source: `action.yml` — CLI installed and run on the GitHub runner; `LETTA_BASE_URL` is passed as an env var to the CLI, not as a tool execution endpoint

**Fix:** Install custom tools on the GitHub runner in a pre-action workflow step:
```yaml
steps:
  - uses: actions/checkout@v4
  - name: Install custom tools
    run: |
      pip install pip-audit osv-scanner
      # Copy check_deps.py into the workspace
  - uses: letta-ai/letta-code-action@v0
    with:
      letta_base_url: ${{ secrets.LETTA_BASE_URL }}
      ...
```

---

### HIGH — Significant issue causing failures or security problems

#### H1: Docker image is deprecated
**Severity: High**

Official Letta docs state: "The Docker image is no longer an actively maintained or supported Letta product surface. If you want to use local models or OpenAI-compatible local providers, use Letta Code local mode instead."
- Source: https://docs.letta.com/guides/docker/

Building a production system on a deprecated image means no security patches, no bug fixes, and no updates. The plan does not acknowledge this deprecation.

**Fix:** Either accept the deprecation risk and document it, or pivot to Letta Code local mode (`letta --backend local`) running on a machine that's accessible to the GitHub Action runner (e.g., via Tailscale).

---

#### H2: Missing `[synchronize]` trigger
**Severity: High**

Plan 2 only triggers on `pull_request: [opened]`. When a developer pushes new commits to an existing PR, the agent will not re-run. Plan 1 includes `[opened, synchronize]`.

Requirement #1 says "Comments on every single PR" with verification: "Push a new commit to the PR. The agent comments again." Plan 2 fails this verification.

**Fix:** Add `synchronize` to the trigger types:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
```

---

#### H3: Missing MemFS environment variable
**Severity: High**

To enable MemFS on a Docker-based Letta server, you must set `LETTA_MEMFS_SERVICE_URL=local`. Plan 2's deployment manifest does not include this environment variable. Without it, MemFS is not enabled, and the entire memory persistence architecture (the PVC-backed git repository) is non-functional.

- Source: https://docs.letta.com/guides/docker/ — "To enable MemFS (the git-backed memory filesystem) on your Docker server, set `LETTA_MEMFS_SERVICE_URL=local`"

**Fix:** Add `LETTA_MEMFS_SERVICE_URL=local` to the Letta server deployment's environment variables.

---

#### H4: Missing server authentication
**Severity: High**

Plan 2 mentions setting up Ingress to expose the Letta server externally (e.g., `letta.yourdomain.com`), but provides no authentication configuration. The Letta Docker docs specify:
- `SECURE=true` — enables password protection
- `LETTA_SERVER_PASSWORD=yourpassword` — sets the server password

Without authentication, anyone who can reach the Ingress endpoint has full access to the Letta API — creating agents, running tools, accessing memory, and executing shell commands.

- Source: https://docs.letta.com/guides/docker/

**Fix:** Add `SECURE=true` and `LETTA_SERVER_PASSWORD` (from a K8s Secret) to the deployment environment. Configure the GitHub Action to pass the password via an additional secret.

---

#### H5: MemFS does not "replace" memory blocks
**Severity: High**

Plan 2 states: "MemFS (git-backed filesystem) stored on a Kubernetes Persistent Volume (PVC). Replaces legacy memory blocks."

This is architecturally incorrect. MemFS and memory blocks are complementary mechanisms that coexist in the Letta architecture:
- **Memory blocks** are editable segments of the system prompt, always loaded into context, agent-editable. They are the agent's always-visible working memory.
- **MemFS** is the filesystem projection of memory to a git-tracked directory. It stores structured files (skills, reference docs, logs) that are loaded on demand.

The plan's claim that MemFS "replaces" memory blocks means the agent configuration would be missing the always-in-context memory blocks that drive behavior (like the `advisory-config` read-only block from Plan 1). Without memory blocks, the agent has no always-visible instructions or pattern tracking.

**Fix:** Remove the "replaces legacy memory blocks" claim. Configure both memory blocks (for always-in-context directives and pattern tracking) AND MemFS (for structured file storage) as complementary systems.

---

### MEDIUM — Degrades quality or requires workarounds

#### M1: `check_deps.py` only covers npm
**Severity: Medium**

Plan 2's `check_deps.py` only implements `check_npm()` with a comment "# Add check_pypi, check_go_mod, etc. as needed". Plan 1's `check-deps.sh` covers 7+ ecosystems (npm, pip, cargo, go, ruby, .NET, npm audit) out of the box.

For a PR advisory agent whose primary function is dependency analysis, covering only one ecosystem is a significant coverage gap. The plan doesn't acknowledge this limitation.

**Fix:** Implement at minimum the same ecosystem coverage as Plan 1's `check-deps.sh`, or document that only npm is supported in the initial version.

---

#### M2: `fetch-depth: 1` (shallow checkout)
**Severity: Medium**

Plan 2 uses `fetch-depth: 1` while Plan 1 uses `fetch-depth: 0`. Shallow checkout gets only the latest commit. If the agent needs git history for architecture analysis (commit patterns, blame, branch history), it won't have access. The official docs example also uses `fetch-depth: 1`, so this may be intentional — but for architecture advisory that reads broader codebase context, full history could be valuable.

**Fix:** Document the tradeoff. Use `fetch-depth: 0` if the agent should access git history, or keep `fetch-depth: 1` if only the current file state matters.

---

#### M3: Missing namespace and secret manifests
**Severity: Medium**

The deployment references `namespace: ai-agents` and secrets `letta-secrets` and `web-search-secrets`, but provides no Namespace manifest and no Secret manifests. These would need to be created separately, but the plan doesn't mention this.

**Fix:** Add Namespace, Secret, and any required RBAC manifests, or document that they must be pre-created.

---

#### M4: Missing Ingress manifest
**Severity: Medium**

Plan 2's Stage 1 says "Configure Ingress: Set up an Ingress route with TLS" but provides no Ingress manifest. The ADE requires HTTPS for remote connections, so TLS termination is mandatory. Without Ingress, the server is only accessible within the cluster.

**Fix:** Add an Ingress manifest with TLS configuration, or document that Ingress is out of scope for the plan.

---

#### M5: Unverified CLI commands (`/memfs enable`, `/sleeptime enable`, `/skill create`)
**Severity: Medium**

Plan 2 references several slash commands that are not confirmed in official docs:
- `/memfs enable` — not documented; MemFS is enabled via environment variable, not a CLI command
- `/sleeptime enable` / `/sleeptime trigger compaction` — mentioned in docs context but not in CLI command reference
- `/skill create dependency-audit` — not documented; skills are typically created as files in `.skills/`

**Fix:** Replace `/memfs enable` with `LETTA_MEMFS_SERVICE_URL=local` environment variable. Verify `/sleeptime` exists. Create skills as files in `.skills/` directory instead of using `/skill create`.

---

#### M6: Three external API dependencies for web search
**Severity: Medium**

The `augmented_web_search.py` tool requires API keys for Exa, Tavily, and Firecrawl — three additional paid services. Plan 1 queries package registries directly (npm registry, PyPI, crates.io) which are free and don't require API keys.

For dependency version checking, package registries are the authoritative source. Web search adds changelog context but at significant cost and complexity. The plan doesn't justify why three search providers are needed for a dependency checker.

**Fix:** Start with direct package registry queries (free, authoritative). Add web search later if changelog/migration context proves valuable. Drop Firecrawl unless scraping specific changelog pages is a confirmed need.

---

### LOW — Minor inaccuracy or improvement opportunity

#### L1: `mountPath: /root/.letta` assumes root user
**Severity: Low**

The deployment mounts the PVC at `/root/.letta`, assuming the container runs as root. If the Letta Docker image runs as a non-root user, this path won't work. The official `compose.yaml` mounts to `./data/letta:/root/.letta` but also has commented-out alternatives.

**Fix:** Verify the container user in the `letta/letta` image and adjust the mount path accordingly.

---

#### L2: GitHub API rate limit note is inaccurate
**Severity: Low**

Plan 2 says "If you process >1000 PRs/hour, you may hit limits." The actual GitHub Actions `GITHUB_TOKEN` rate limit for PRs is 5,000 requests/hour per repo. 1000 PRs/hour is an unrealistic volume for any team, making this note misleading.

**Fix:** Remove or correct the rate limit note. The real concern is the Letta API rate limit, not GitHub's.

---

#### L3: Typo in Part 2 system prompt
**Severity: Low**

Part 2's system prompt includes: `*Instruc: This is injected at the agent creation level via the Letta CLI or SDK.*`

This appears to be a truncated "Instructions:" label.

**Fix:** Complete the word to "Instructions:" or remove the label.

---

## Summary

| Severity | Count | Issues |
|:---|:---|:---|
| Critical | 4 | Wrong Docker image, missing database, security violation (contents: write), tools on wrong machine |
| High | 5 | Deprecated image, missing synchronize trigger, missing MemFS env var, missing auth, incorrect MemFS/blocks architecture |
| Medium | 6 | npm-only coverage, shallow checkout, missing manifests, unverified commands, external API overhead, missing Ingress |
| Low | 3 | Root user assumption, inaccurate rate limit note, typo |

**Overall assessment:** Plan 2 has structural failures across every layer — wrong Docker image, missing database dependency, security permission violation, tools deployed to the wrong machine, deprecated infrastructure, and architectural misunderstandings about how MemFS and memory blocks relate. Unlike Plan 1 (which has mechanical errors with a sound design), Plan 2's design itself is broken in ways that require a rewrite, not just fixes. The self-hosting concept via `letta_base_url` is valid, but the execution fails on nearly every implementation detail.
