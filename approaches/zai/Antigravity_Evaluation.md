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

## 2. Actionable Suggestions for Plan 2 (Self-Hosted on Existing Cluster)

Since you already have a Kubernetes cluster running, implementing Plan 2 is simplified as you can reuse your existing database, Ingress controller, and secret management tools. Below is the recommended implementation route:

### A. Deploy a Combined Letta + Webhook Pod
Deploy both the Letta Server and your webhook receiver sidecar in a single K8s Pod. They can share a transient local directory (`/tmp/workspace`) using an `emptyDir` volume, resolving the context gap:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: letta-pr-advisor
  namespace: ai-agents
  labels:
    app: letta-pr-advisor
spec:
  containers:
    # Webhook Receiver Sidecar (Triggered by GitHub, starts agent asynchronously)
    - name: webhook-handler
      image: your-registry/letta-webhook-handler:latest
      ports:
        - containerPort: 5000
      env:
        - name: GITHUB_WEBHOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: pr-advisor-secrets
              key: github-webhook-secret
        - name: LETTA_API_KEY
          valueFrom:
            secretKeyRef:
              name: pr-advisor-secrets
              key: letta-api-key
      volumeMounts:
        - name: shared-workspace
          mountPath: /tmp/workspace

    # Letta Agent Server (Using active image and connecting to existing pgvector DB)
    - name: letta-server
      image: letta/letta:latest
      ports:
        - containerPort: 8283
      env:
        - name: DATABASE_URL
          value: "postgresql://user:password@postgres-service:5432/letta_db"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: pr-advisor-secrets
              key: anthropic-key
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: pr-advisor-secrets
              key: github-token
      volumeMounts:
        - name: shared-workspace
          mountPath: /tmp/workspace
        - name: memfs-data
          mountPath: /root/.letta

  volumes:
    - name: shared-workspace
      emptyDir: {}
    - name: memfs-data
      persistentVolumeClaim:
        claimName: letta-memfs-pvc
```

### B. Fix Logic and Webhook Timeout Issues
1. **Asynchronous Webhook Handling**: Modify `webhook-handler.py` to launch the agent turn in a background thread or queue, and immediately return a `202 Accepted` response to GitHub to prevent the 10-second webhook timeout.
2. **SemVer Range Resolution**: Update `check_deps.py` to use a python library (like `semver` or `packaging`) to correctly match version ranges (e.g. `^4.18.2`) rather than using basic string inequality.
3. **Parse Lockfiles**: Update `check_deps.py` to read `package-lock.json` or `yarn.lock` to satisfy Requirement 4 ("you are using version X").

