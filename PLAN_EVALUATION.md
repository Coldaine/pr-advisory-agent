# PR Advisory Agent: Plan Evaluation & Gap Analysis

This document evaluates the two proposed implementation plans for the **PR Advisory Agent**:
1. **Plan 1 (Standard / Letta Cloud)** (from `Plan1.txt`)
2. **Plan 2 (Self-Hosted Kubernetes)** (from `ZAIPlan/Part1.txt` & `Part2.txt`)

---

## Part A: Plan 1 (Standard/Cloud) Evaluation

### 1. Letta Code CLI Installation Discrepancy
* **Gap:** The plan specifies installing Letta Code CLI via:
  ```bash
  curl -fsSL https://letta.com/install.sh | bash
  ```
* **Analysis:** Letta Code CLI is a Node.js-based application requiring Node.js 18+. The official CLI installation is performed via npm:
  ```bash
  npm install -g @letta-ai/letta-code
  ```
  Using `curl` will likely result in a HTTP 404 or execute an unsupported script.

### 2. GitHub Action Name & Versioning
* **Gap:** The workflow uses `uses: letta-ai/letta-code@v1`.
* **Analysis:** The official GitHub integration repository is named `letta-code-action`, not `letta-code`. The correct name to use is:
  ```yaml
  uses: letta-ai/letta-code-action@v0
  ```

### 3. Unsupported `prompt` Input in GitHub Action
* **Gap:** The workflow configures a multi-line `prompt` parameter under the `with:` section.
* **Analysis:** The `letta-ai/letta-code-action` does not support a custom `prompt` input in its `action.yml`. Instead, the action is designed to be reactive to comments containing mentions of `@letta-code` (using `issue_comment` or `pull_request_review_comment` events), parsing the prompt directly from the comment body. Providing `prompt` under `with:` will be ignored or cause validation errors.

### 4. Triggering on Every PR Automatically
* **Gap:** The plan states: *"The agent fires automatically on every PR without needing a `@letta-code` mention."*
* **Analysis:** The `letta-ai/letta-code-action` relies on comment triggers (e.g. `@letta-code` mentions) or label/assignment events to process requests. Simply running the action on a clean `pull_request` event will not automatically run the agent or post a comment, because there is no incoming comment message to trigger the agent's turn. 
* **Recommendation:** If you want the agent to review every PR automatically, either:
  1. Use a script block in the workflow to call the Letta CLI directly (e.g., `letta run --prompt "..."`), or
  2. Configure the action to trigger when the PR is opened/synchronized, and write a custom step in your workflow that programmatically creates a comment mentioning `@letta-code` to kick off the agent.

### 5. Execution Environment & Tool Dependencies in `check-deps.sh`
* **Gap:** The script `check-deps.sh` invokes various ecosystem-specific utilities (`cargo outdated`, `pip-audit`, `npm outdated`) that are not pre-installed in standard GitHub runners or require pre-restoring dependencies.
* **Recommendation:** Pre-install required tooling in the workflow runner environment or have the script fallback gracefully to manual manifest parsing.

---

## Part B: Plan 2 (Kubernetes Self-Hosted) Evaluation

### 1. The Remote Workspace Context Isolation Gap (Critical)
* **Gap:** In Plan 2, the Letta Server runs inside a Kubernetes cluster, and tools are executed in that container context:
  ```markdown
  Execute shell command: python3 /tools/check_deps.py $REPO_PATH
  ```
  However, the repository checkout (`actions/checkout@v4`) occurs on the **GitHub Action runner** environment.
* **Analysis:** Because the codebase is checked out on the transient GitHub Action runner, the remote self-hosted server running in Kubernetes does **not** have access to the source code files by default. The path `$REPO_PATH` will point to a non-existent or empty folder in the K8s container.
* **Recommendation:** To resolve this:
  - The tool execution must be routed to run *locally* on the GitHub runner instead of on the remote Kubernetes pod, or
  - The custom tools must clone the repository directly inside the Kubernetes pod using a scoped GitHub token before performing the analysis.

### 2. Ingress & API Security Scopes
* **Gap:** Exposing your Letta Server externally via Ingress (`letta.yourdomain.com`) exposes the agent creation, modification, and execution API endpoints.
* **Analysis:** If the server Ingress is publicly accessible, you must enforce API key validation on all endpoints to prevent malicious actors from triggering executions or calling the agent's shell tools. Ensure that Letta's authentication server features are enabled and configured with robust credentials.

---

## Part C: Comparative Analysis

| Dimension | Plan 1: Standard/Cloud | Plan 2: Kubernetes Self-Hosted |
| :--- | :--- | :--- |
| **Hosting & Infrastructure** | Managed Cloud (Letta SaaS) or Local Runner | Self-hosted K8s Deployment, PVC, and Service |
| **Data Ownership** | Stored on Letta Cloud servers | 100% on your own infrastructure (PVC/MemFS) |
| **Execution Environment** | Clean host environment in GitHub runner | Custom Docker image on Kubernetes pod |
| **Setup Speed** | Faster setup (minimal manifest files) | Requires Docker builds, Ingress setup, and K8s configuration |
| **Custom Tool Overhead** | Installed dynamically during action run | Pre-baked in Docker image (faster runner startups) |
| **Web Search Capability** | Standard web search tools | Enhanced integrations (Exa + Tavily + Firecrawl) |

### Pros & Cons Summary

#### Plan 1 (Standard/Cloud)
* **Pros:** Quick implementation, low operational maintenance, simple YAML workflow structure.
* **Cons:** Dependency on third-party SaaS hosting for state; installation of CLI tools (like `pip-audit`) adds startup overhead on every PR run.

#### Plan 2 (Kubernetes Self-Hosted)
* **Pros:** Complete control over memory directories (MemFS) and security policies; pre-baked tools speed up run times; advanced scrapers (Firecrawl) yield richer changelog context.
* **Cons:** High infrastructure management overhead; critical execution context gap (server container has no default access to the runner workspace files).

---

## Recommendation
If **data privacy and self-hosting** are your highest priorities, **Plan 2 (Kubernetes)** is the superior architectural route, provided you resolve the **workspace file transfer gap** (e.g., having the container clone the repo dynamically). If **developer velocity and low maintenance** are the primary goals, start with **Plan 1 (Standard/Cloud)** and migrate to self-hosted K8s once the agent core logic is finalized.
