# Plan 2 Evaluation: Self-Hosted Kubernetes

This document contains criticisms and actionable suggestions for **Plan 2** (`approaches/zai/Part1.txt` & `approaches/zai/Part2.txt`).

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

## 2. Actionable Suggestions for Plan 2

1. **Implement Asynchronous Webhook Handling**: Modify `webhook-handler.py` to trigger the Letta Agent in a background thread or asynchronous task queue, and return a `202 Accepted` response immediately to GitHub to avoid the 10-second timeout.
2. **Utilize a Proper SemVer Parser**: Use the `semver` or `packaging` Python libraries in `check_deps.py` to properly evaluate semantic range compatibility rather than using simple string inequalities.
3. **Parse Lockfiles**: Update `check_deps.py` to parse `package-lock.json`, `yarn.lock`, or python lockfiles to resolve the true installed package versions.
4. **Deploy Database Sidecar**: Add a PostgreSQL with `pgvector` service and deployment to your Kubernetes manifests to act as the Letta database backend.
5. **Secure the Ingress**: Configure basic authentication or API key verification on your exposed Letta API endpoint to ensure unauthorized users cannot call your agent's shell tools.
