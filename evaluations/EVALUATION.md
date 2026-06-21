# PR Advisory Agent: Evaluation of Both Approaches

Supersedes `PLAN_EVALUATION.md`. That document contained several factual errors about the Letta Code GitHub Action's capabilities. This evaluation corrects them using the actual `action.yml`, official docs, and real-world usage from `letta-ai/letta-code`'s own CI.

---

## What's Being Evaluated

- **Plan 1** (`Plan1.txt`) — Standard/Cloud: GitHub Action + Letta Cloud, `check-deps.sh`, two skills, memory blocks + MemFS
- **Plan 2** (`ZAIPlan/Part1.txt` + `Part2.txt`) — Self-Hosted K8s: Letta server on Kubernetes with PVC, custom Docker image with tools, augmented web search

---

## Corrections to the Existing `PLAN_EVALUATION.md`

The existing evaluation made three claims that are factually wrong:

### 1. "`prompt` input is not supported" — WRONG

The `prompt` input IS a real, documented input in `action.yml`:

```yaml
prompt:
  description: "Instructions for Letta. Can be a direct prompt or custom template."
  required: false
  default: ""
```

Official docs list it as a trigger type: "Prompt: Set the `prompt` input for automated workflows."

Real-world proof: `letta-ai/letta-code` uses its own action with a multi-line `prompt:` to auto-review every PR (source: `.github/workflows/review.yml` in `letta-ai/letta-code`, commit `8e592387`):

```yaml
- uses: letta-ai/letta-code-action@daa80f29...
  with:
    model: auto
    prompt: |
      You are reviewing PR #${{ env.PR_NUMBER }} in ${{ github.repository }}.
      1. Read your review-knowledge.md memory file...
      2. Run `gh pr view $PR_NUMBER --json title,body,comments`...
```

Plan 1's use of `prompt:` is correct. The existing evaluation was wrong to flag it as unsupported.

### 2. "Triggering on every PR automatically won't work" — WRONG

The `prompt` input is specifically designed for automated workflows that bypass the `@letta-code` mention requirement. The action's prepare step checks for triggers including `prompt`. If `prompt` is set and a `pull_request` event fires, the agent runs automatically — no mention needed.

The real-world `review.yml` in `letta-ai/letta-code` proves this: it reviews every PR without requiring `@letta-code` mentions, using `prompt:` with `pull_request` events.

### 3. "Critical Workspace Context Isolation Gap" — WRONG PREMISE

The existing evaluation claimed that in Plan 2, the tools execute on the K8s pod and the repo checkout is on the GitHub runner, so the server can't access files. This misunderstands the architecture:

**How the GitHub Action actually works** (from `action.yml`):
1. The action installs the Letta Code CLI on the **GitHub runner** via `npm install -g @letta-ai/letta-code`
2. The CLI connects to the Letta API server via `LETTA_BASE_URL` (cloud or self-hosted)
3. Tool execution (bash, file reading, shell commands) happens **on the GitHub runner** where the CLI runs and where `actions/checkout` placed the repo
4. The Letta server handles LLM calls and memory persistence — it is the brain, not the hands

So `$REPO_PATH` points to the checked-out repo on the GitHub runner, and that's exactly where the CLI's tools execute. The self-hosted server doesn't need filesystem access to the repo.

**The real tool-access problem in Plan 2 is different** (see below): Plan 2 packages custom tools into the K8s Docker image, but the CLI runs on the GitHub runner. The tools need to be on the runner, not on the pod.

### 4. `letta_base_url` IS a real input — the existing evaluation missed this

```yaml
letta_base_url:
  description: "Letta API base URL (defaults to https://api.letta.com)"
  required: false
  default: ""
```

Plan 2's approach of pointing the action to a self-hosted server via `letta_base_url` IS supported. The existing evaluation didn't mention this input at all.

---

## Plan 1 Evaluation

### What Plan 1 Gets Right

1. **GitHub Action trigger design** — `pull_request: [opened, synchronize]` with a `prompt` input is a working pattern. The `prompt` input is real and designed for automated workflows. Letta themselves use this exact pattern.

2. **Advisory-only enforcement via token scope** — `pull-requests: write` + `contents: read` is correct. The agent can post comments but cannot push code. This is the right security boundary.

3. **Agent-driven dependency scanning** — `check-deps.sh` covers 7+ ecosystems (npm, pip, cargo, go, ruby, .NET, npm audit). The script is a data-gathering helper; the agent interprets output. This is the right division of labor.

4. **Memory architecture** — Memory blocks (always in context, agent-editable) + MemFS (git-tracked, on-demand) + dream subagents (automatic reflection) is the real Letta model. The three mechanisms coexist and serve different purposes.

5. **Per-PR isolation with shared learning** — Each PR gets its own conversation with shared memory blocks. This is correct per the Conversations API.

6. **Two-skill structure** — `dependency-audit` and `architecture-advisory` are appropriately scoped. Skills with reference documents and progressive disclosure match the skill model.

7. **Security model** — Read-only `advisory-config` block, scoped `GITHUB_TOKEN`, prompt injection mitigation via token scope, MemFS git-tracked for auditability. This is well-reasoned.

### What Plan 1 Gets Wrong

1. **CLI installation command** — `curl -fsSL https://letta.com/install.sh | bash` is wrong. The official installation is `npm install -g @letta-ai/letta-code` (requires Node.js 18+).
   - Source: https://docs.letta.com/letta-code/cli/
   - Note: The GitHub Action handles CLI installation itself via `npm install -g @letta-ai/letta-code` inside the action. The workflow should NOT have a separate install step. Plan 1's `Install Letta Code` step is both wrong and redundant.

2. **GitHub Action name and version** — `letta-ai/letta-code@v1` is wrong. The correct action is `letta-ai/letta-code-action@v0`.
   - Source: https://github.com/letta-ai/letta-code-action

3. **Redundant CLI install step** — The action installs the CLI itself (see `action.yml` step "Install Base Action Dependencies"). Plan 1's workflow has a separate `Install Letta Code` step that would fail (wrong URL) and is unnecessary even if it worked.

4. **Missing `agent_id` in workflow** — Plan 1 references `secrets.LETTA_AGENT_ID` but the agent creation step (`letta agent create`) returns an agent_id that needs to be stored. The workflow should either use `agent_id` to pin a specific agent or let the action auto-discover/create one. The real-world usage pins `agent_id` to a specific agent.

5. **Missing action configuration inputs** — The action supports `track_progress`, `use_sticky_comment`, `model`, and other inputs that matter for a PR advisory workflow. Plan 1 doesn't configure any of these. For a single-comment advisory agent, you'd want `use_sticky_comment: "true"` to update one comment rather than posting new ones each push.

6. **Skills directory path** — Plan 1 uses `skills/` but the action installs its built-in skill to `.skills/github-action/SKILL.md`. Letta Code discovers skills from `.skills/` (dot-prefixed), not `skills/`. Plan 1's `skills/dependency-audit/` directory might not be auto-discovered.
   - Source: `action.yml` step "Setup GitHub Action Skill" creates `.skills/github-action/`

7. **`letta agent create` command** — The CLI docs show `letta --new-agent` not `letta agent create --name "..."`. The agent creation flow may work differently than described.

8. **`check-deps.sh` tool availability** — `cargo outdated`, `pip-audit`, `bundle outdated` are not pre-installed on GitHub runners. The script uses `|| true` to suppress errors, so missing tools produce no output for that ecosystem — the agent would need to fall back to manual manifest parsing. This is a graceful degradation but should be documented as expected behavior.

9. **Unverified Letta commands** — `/sleeptime`, `/palace` are referenced but not confirmed in the CLI command list. Known commands include `/compact`, `/reflect`, `/remember`, `/context`, `/doctor`, `/init`, `/clear`, `/new`, `/connect`, `/login`. The `/sleeptime` command may exist (docs mention it in the context of dream agents) but should be verified before relying on it.

10. **"36.8% performance improvement" claim** — The skill learning performance figure is cited from Letta research but without a verifiable source. It may be real, but the plan presents it as established fact without citation to a specific paper or benchmark.

### Plan 1 Verdict

The architecture is sound and close to a working design. The GitHub Action integration pattern is correct in concept (proven by Letta's own real-world usage). The main errors are mechanical: wrong install command, wrong action name, redundant install step, missing action configuration inputs, and skills directory path. All fixable without changing the design.

---

## Plan 2 Evaluation

### What Plan 2 Gets Right

1. **Self-hosted server via `letta_base_url`** — This IS supported by the action. You can point the CLI to a self-hosted Letta server. The architectural approach is valid in principle.

2. **Persistent MemFS on PVC** — Using a PVC to persist MemFS across pod restarts is a reasonable K8s pattern for stateful workloads.

3. **OSV-Scanner for vulnerability scanning** — OSV-Scanner is a real Google tool and a legitimate addition to the dependency audit pipeline.

4. **Augmented web search concept** — Combining Exa (semantic), Tavily (general), and Firecrawl (scrape) for changelog research is a reasonable tool design, though it adds significant complexity.

### What Plan 2 Gets Wrong

1. **Wrong Docker image name** — `letta/letta-server:latest` does not exist. The real image is `letta/letta:latest`.
   - Source: https://hub.docker.com/r/letta/letta
   - Also, `your-registry/letta-pr-advisor:latest` implies building a custom image on top of a non-existent base.

2. **Missing PostgreSQL/pgvector dependency** — The Letta server requires PostgreSQL with pgvector as its database backend. Plan 2's K8s manifests only include a Deployment, Service, and PVC for the Letta server itself — no database deployment. The official `compose.yaml` shows `letta_db` (pgvector) as a required dependency.
   - Source: https://github.com/letta-ai/letta/blob/main/compose.yaml

3. **Docker image is deprecated** — Official docs state: "The Docker image is no longer an actively maintained or supported Letta product surface. If you want to use local models or OpenAI-compatible local providers, use Letta Code local mode instead."
   - Source: https://docs.letta.com/guides/docker/
   - Building a production system on a deprecated image is risky.

4. **`contents: write` permission contradicts advisory-only** — Plan 2's GitHub Action uses:
   ```yaml
   permissions:
     contents: write    # ← allows code pushes
     issues: write
     pull-requests: write
   ```
   The requirement is "advisory only, does not modify code." `contents: write` allows the agent to push commits. Plan 1 correctly restricts to `contents: read`. This is a direct violation of Requirement #2.

5. **Missing `[synchronize]` trigger** — Plan 2 only triggers on `pull_request: [opened]`. Plan 1 includes `[opened, synchronize]`. Without `synchronize`, the agent won't re-review when new commits are pushed to an existing PR.

6. **Custom tools are on the wrong machine** — Plan 2 says "Containerize Tools: Create a custom Dockerfile that extends the Letta server image and includes `python3`, `pip`, `osv-scanner`, and your `check_deps.py`." But the Letta Code CLI runs on the **GitHub runner**, not on the K8s pod. The tools are packaged into the K8s Docker image, but the CLI calls tools on the runner where it's running. The agent would try to run `python3 /tools/check_deps.py $REPO_PATH` and find no `/tools/check_deps.py` on the runner.
   - The fix would be to install the tools on the GitHub runner during the workflow (before the action step), not in the K8s image. But Plan 2 doesn't describe this.

7. **`check_deps.py` only covers npm** — Plan 2's `check_deps.py` only implements `check_npm()` with a comment "# Add check_pypi, check_go_mod, etc. as needed". Plan 1's `check-deps.sh` covers 7+ ecosystems out of the box. This is a significant coverage gap.

8. **`fetch-depth: 1` (shallow checkout)** — Plan 2 uses `fetch-depth: 1` while Plan 1 uses `fetch-depth: 0`. Shallow checkout may miss git history that the agent needs for architecture analysis (e.g., commit patterns, blame context).

9. **MemFS does not "replace" memory blocks** — Plan 2 says "MemFS (git-backed filesystem) stored on a Kubernetes Persistent Volume (PVC). Replaces legacy memory blocks." This is incorrect. MemFS and memory blocks coexist in the Letta architecture. Memory blocks are editable segments of the system prompt (always in context). MemFS is the filesystem projection for structured files. They serve different purposes.
   - Source: My own system prompt documents both mechanisms coexisting.

10. **Missing MemFS environment variable** — To enable MemFS on a Docker server, you need `LETTA_MEMFS_SERVICE_URL=local`. Plan 2's deployment manifest doesn't include this environment variable. MemFS won't work without it.
    - Source: https://docs.letta.com/guides/docker/

11. **Missing server security configuration** — No `SECURE=true` or `LETTA_SERVER_PASSWORD` set. The server would be unauthenticated if exposed via Ingress.
    - Source: https://docs.letta.com/guides/docker/

12. **Missing namespace and secret manifests** — The deployment references `namespace: ai-agents` and secrets `letta-secrets` / `web-search-secrets` but provides no Namespace or Secret manifests. These would need to be created separately.

13. **K8s manifests have no Ingress** — Plan 2 mentions setting up Ingress in Stage 1 but provides no Ingress manifest. The ADE requires HTTPS for remote connections, so you'd need TLS termination.

14. **Augmented web search adds 3 external API dependencies** — Exa, Tavily, and Firecrawl each require API keys and network access. This is significant operational overhead for a dependency checker that could mostly use package registry APIs (which Plan 1 does).

15. **`/memfs enable`, `/sleeptime enable`, `/skill create` commands unverified** — These commands are presented as CLI commands but may not exist in this form. The CLI uses slash commands like `/init`, `/new`, `/model` — not `/memfs enable`.

### Plan 2 Verdict

The self-hosting concept is architecturally valid (`letta_base_url` is real), but the execution is deeply flawed: wrong Docker image, missing database dependency, deprecated infrastructure, security violations (`contents: write`), tools on the wrong machine, missing trigger events, and incomplete manifests. The plan would require substantial rework before it could be deployed.

---

## Code Quality & Implementation Defects Analysis

Beyond high-level architectural gaps, the actual code scripts and prompts provided in the plans contain several critical logic errors and code quality issues:

### 1. `check_deps.py` Logic & Performance Defects (Plan 2)
* **Naive String Matching for SemVer**:
  ```python
  if latest_ver and latest_ver != current_ver:
  ```
  In `package.json`, `current_ver` contains semantic ranges (e.g., `"^4.18.2"` or `"~1.0.0"`). Doing a direct string inequality check against the latest version (`"4.18.2" != "^4.18.2"`) will produce constant false positives. It flags packages as outdated even when they are fully up-to-date.
* **Lack of Lockfile Resolution**:
  Scanning `package.json` only gives the defined *range*, not the actual *installed* version ($X$) required by Requirement 4 ("you are using version X"). The script must parse `package-lock.json` or `yarn.lock` to report the true installed version.
* **Sequential Requests Bottleneck**:
  The script performs a synchronous `requests.get` call inside a `for` loop for every single dependency. A standard repository with 100+ dependencies will block the script for minutes, potentially hitting registry rate limits and timing out the entire run.

### 2. `webhook-handler.py` Blocking & Timeout Defect (Plan 2 / Plan 3)
* **Webhook Timeout**:
  ```python
  r = requests.post(f"{LETTA_API_URL}/{AGENT_ID}/messages", json=agent_payload, headers=headers)
  return jsonify({"status": "triggered"})
  ```
  This is a blocking HTTP request. Because the Letta Agent's review turn takes 1–3 minutes (cloning, dependency checking, web searches, and LLM generation), this webhook call will hang. GitHub has a strict **10-second webhook timeout**. This blocking call will cause GitHub to log all webhook deliveries as failed and trigger repeated retries, leading to execution loops.
  * **Fix**: The handler must trigger the agent *asynchronously* (e.g., using a background thread, queue, or an async run endpoint) and return a `202 Accepted` response to GitHub immediately.

### 3. `check-deps.sh` Silent Failure Defect (Plan 1)
* **Swallowed Diagnostics**:
  ```bash
  cargo outdated --format json 2>/dev/null || true
  ```
  By redirecting `stderr` to `/dev/null` and appending `|| true`, the script swallows all errors. If a tool like `cargo-outdated` is missing or fails, the script returns an empty string instead of alerting the agent that the scan environment is incomplete. The agent will falsely assume there are zero dependencies or updates.

### 4. Prompt Engineering & Suggestion Quota Defect (Plan 1 & Plan 2)
* **Forced Suggestion Quota**:
  The prompts state: *"Identify exactly 5 places where an alternative architectural approach could be used..."*
  Forcing a strict count of exactly 5 alternatives means that for minor PRs (e.g., config changes or simple typo fixes) the agent is forced to hallucinate or pad the review with low-quality, generic "filler" recommendations. This degrades review trust and introduces developer noise.
  * **Fix**: The prompt should instruct the agent to find *up to* 5 viable alternatives, allowing it to skip the section or offer fewer if the PR is small or the code is already well-architected.

---

## Correcting the GitHub Runner Anti-Pattern in Plan 2 (Self-Hosted K8s)

### The Hybrid Anti-Pattern in Plan 2's Original Form
In its original form, Plan 2 proposed using a **GitHub Actions runner** in combination with the self-hosted Letta Server. This creates a convoluted hybrid loop:
1. GitHub triggers the Actions runner.
2. The runner checks out code, installs the Letta CLI, and calls the remote K8s Server.
3. The K8s Server processes the prompt, but executes terminal/file tools *back* on the GitHub Actions runner where the CLI is running.
4. This requires you to install and maintain all dependency audit tools (`pip-audit`, `cargo-outdated`, etc.) on the runner machine anyway.

### The Corrected Plan 2: Native Self-Hosted Webhooks
To resolve this anti-pattern and eliminate the GitHub Actions runner entirely, Plan 2 must be implemented as a fully native, event-driven architecture inside Kubernetes:
* **Trigger**: A direct GitHub Webhook sends `pull_request` payloads (e.g. `opened`, `synchronize`) directly to your Kubernetes cluster Ingress.
* **Cloning**: A webhook handler sidecar triggers the Letta Agent. The agent's first step is to run a local `git_clone` tool to clone the target PR branch into `/tmp/workspace` inside the Kubernetes pod container.
* **Analysis**: The audit and architecture skills run directly against the cloned repo in the pod container (where tools like `osv-scanner` are pre-baked in the Docker image).
* **Delivery**: The agent posts the comment directly to the PR via the GitHub API, deletes `/tmp/workspace`, and updates its MemFS memory.

---

## Comparative Analysis (Plan 1 vs. Plan 2 Corrected)

| Dimension | Plan 1: Standard/Cloud | Plan 2: Self-Hosted K8s (Corrected) |
|:---|:---|:---|
| **GitHub Action Runner** | Yes (runs Letta CLI & tools) | **No** (bypassed completely via webhooks) |
| **Trigger Mechanism** | GitHub Action Workflow | Direct GitHub Webhook to Ingress |
| **Tool Execution Location** | GitHub Action Runner | Kubernetes Pod Container |
| **Workspace Context** | Local checkout on runner | Cloned dynamically to `/tmp/workspace` |
| **Advisory-only enforcement** | Correct (`contents: read` only) | Correct (Restricted API/token scopes) |
| **Ecosystem Tools** | Restored/Installed on runner | Pre-baked in Custom K8s Docker Image |
| **Infrastructure Overhead** | None (managed cloud) | High (PostgreSQL, PVC, Ingress, webhook handler) |
| **Data Ownership** | Stored on Letta Cloud | 100% on PVC |

---

## Recommendation

Based on this evaluation:

1. **If self-hosting is a requirement**: 
   * **Proceed with Plan 2 (Kubernetes)**, but implement it using the **corrected runner-less webhook pattern** instead of the hybrid runner model. This ensures all tool execution and repository scanning are kept entirely secure inside your Kubernetes container, solving the workspace context gap.
2. **If developer velocity is the primary goal**:
   * **Proceed with Plan 1 (Standard/Cloud)**. Apply the CLI installation and Action version name corrections listed in Part A. This is the fastest path to a working agent, and you can easily migrate the custom skills and prompts to Kubernetes (Plan 2) later.


