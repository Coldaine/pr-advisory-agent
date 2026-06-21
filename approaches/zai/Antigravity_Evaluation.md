# Plan 2 Evaluation: Self-Hosted Kubernetes

This document contains criticisms and actionable suggestions for **Plan 2** (`approaches/zai/Part1.txt` & `approaches/zai/Part2.txt`).

> **Reconciliation status:** This evaluation originally assumed a direct GitHub webhook receiver inside Kubernetes. `Plan2_Cluster_Baseline_Addendum.md` supersedes that architecture. The active Plan 2 baseline uses GitHub Actions as the trigger/execution surface and Kubernetes as the self-hosted Letta brain/state surface.

---

## 1. Technical Defects & Criticisms

### A. Blocking Webhook Handler & GitHub Timeout (Critical)
* **Issue**: The webhook listener (`webhook-handler.py`) triggers the Letta Agent synchronously:
  ```python
  r = requests.post(f"{LETTA_API_URL}/{AGENT_ID}/messages", json=agent_payload)
  ```
* **Criticism**: The Letta agent turn (cloning, running OSV-scanner, checking registry APIs, reasoning via LLM) takes between 1 to 3 minutes. However, **GitHub has a strict 10-second timeout on all webhook responses.** Because the request blocks, the connection will time out, causing GitHub to mark every PR webhook delivery as failed and trigger automatic retries. This creates infinite duplicate agent runs.

### B. Broken SemVer Comparisons in `check_deps.py`
* **Issue**: The script compares versions using direct string matching:
  ```python
  if latest_ver and latest_ver != current_ver:
  ```
* **Criticism**: In standard projects, dependencies in `package.json` are specified as semantic ranges (e.g. `"^4.18.2"`). A direct string comparison like `"4.19.0" != "^4.18.2"` or `"18.2.0" != "^18.2.0"` will evaluate to `True`, causing the agent to constant-flag false positive updates for packages that are fully up-to-date.
* **Lockfile Gap**: It only reads `package.json`, which does not contain the actual installed version ($X$) in the project. Without checking `package-lock.json` or `yarn.lock`, it cannot meet Requirement 4 ("you are using version X").

### C. Deprecated Docker Image & Missing Database
* **Issue**: The K8s deployment runs `letta/letta-server:latest` and mounts a PVC for storage.
* **Criticism**: The `letta/letta-server` image is deprecated. The active image is `letta/letta:latest`. Furthermore, Letta requires a PostgreSQL database with the `pgvector` extension to persist metadata and conversation states. Deploying just the server pod without a database sidecar or backend service will prevent the Letta server from starting.

### D. Blocking Tool Execution Bottleneck
* **Issue**: `check_deps.py` loops through dependencies and makes a synchronous HTTP request to the npm registry for each one.
* **Criticism**: For projects with dozens of dependencies, this synchronous serial network checking is slow and prone to hitting registry rate limits.

---

## 2. Actionable Suggestions for Plan 2 (Self-Hosted on Existing Cluster)

Since you already have a Kubernetes cluster running, implementing Plan 2 should reuse existing cluster primitives without building a custom CI receiver.

### A. Use the GitHub Actions + Self-Hosted Letta Split

The active implementation route is:

1. GitHub Actions triggers on `pull_request: [opened, synchronize]`.
2. `actions/checkout@v4` checks out the repository on the runner with enough history for diff analysis.
3. Runner-side steps install or expose deterministic tools such as `check_deps.py` and `osv-scanner`.
4. `letta-ai/letta-code-action@v0` connects to the self-hosted Letta server through `letta_base_url`.
5. Kubernetes hosts Letta Server, PostgreSQL/pgvector if required, MemFS/state, ingress/TLS, and cluster-side secrets.

Do not deploy a webhook receiver sidecar, queue, pod-local clone service, or tool-heavy custom Letta image in the first version.

### B. Keep the Real Code/Tool Fixes

1. **SemVer Range Resolution**: Update `check_deps.py` to use a Python library or ecosystem-native parser to correctly match ranges such as `^4.18.2` rather than using basic string inequality.
2. **Parse Lockfiles**: Update `check_deps.py` to read `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, or the relevant ecosystem lockfile to satisfy Requirement 4 ("you are using version X").
3. **Avoid Serial Registry Bottlenecks**: Batch or parallelize registry lookups where practical, and cache repeated package metadata during a single run.
4. **Quota Quality**: Architecture advice should produce up to 5 useful alternatives, not exactly 5 regardless of PR size.
