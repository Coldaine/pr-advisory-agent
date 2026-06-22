# Integration Guide: Calling PR Advisory Agents from External Repositories

This guide explains how to configure other repositories to utilize the PR Advisory Agents defined in `Coldaine/pr-advisory-agent` via a reusable GitHub Actions workflow.

## Phase 1: Central Repository Configuration (`Coldaine/pr-advisory-agent`)

### Reusable Workflow Integration
The core logic resides in `.github/workflows/reusable-pr-advisory.yml`, which uses `on: workflow_call` to allow external triggering.

### Access Control Settings
- **Public Repository:** External public and private repositories can reference the reusable workflow directly.
- **Private Repository:** Navigate to **Settings > Actions > General > Access**. Select "Accessible from repositories in the same organization" or configure cross-repository sharing.

## Phase 2: Target Repository Configuration (The Calling Repo)

### Workflow Definition
Create `.github/workflows/pr-advisory.yml` in the root of your repository:

```yaml
name: PR Advisory Reviews
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr_advisory:
    # Reference the reusable workflow in the central repository
    uses: Coldaine/pr-advisory-agent/.github/workflows/reusable-pr-advisory.yml@main
    with:
      # Pass the agent IDs configured for this repository
      letta_dep_agent_id: ${{ vars.LETTA_DEP_AGENT_ID }}
      letta_arch_agent_id: ${{ vars.LETTA_ARCH_AGENT_ID }}
      # Pass the URL of the self-hosted Letta server, or omit/set to Letta Cloud
      letta_base_url: 'https://api.letta.com'
    secrets:
      # Pass the API key secret to authenticate with the Letta server
      LETTA_API_KEY: ${{ secrets.LETTA_API_KEY }}
```

### Repository Permissions Configuration
The workflow requires write permissions to post comments on PRs.
Navigate to **Settings > Actions > General > Workflow permissions** and select **"Read and write permissions"**, or explicitly set them in the job:

```yaml
permissions:
  contents: read
  pull-requests: write
```

### Secrets and Variables Setup
Navigate to **Settings > Secrets and variables > Actions**:

**Repository Secrets:**
- `LETTA_API_KEY`: Your Letta server API key.

**Repository Variables:**
- `LETTA_DEP_AGENT_ID`: The ID of the Dependency Auditor agent.
- `LETTA_ARCH_AGENT_ID`: The ID of the Architectural Advisor agent.

## Phase 3: Letta Server & Agent Provisioning

### Agent Instance Strategies
- **Isolated History (Recommended):** Create a new pair of agents for each target repository to keep review history and memory clean.
- **Shared History:** Reuse agent IDs across repositories (memory will be shared).

### Exa/Firecrawl MCP Setup
Ensure target agents have Exa and Firecrawl MCP servers connected for live data retrieval.

### Self-Hosted Letta Infrastructure
If using self-hosted Letta (see `k8s/`), ensure the ingress URL is publicly accessible.

## Phase 4: Verification and Testing

1. Create a draft pull request in the target repository.
2. Verify the workflow:
   - Checks out the target repository.
   - Checks out `Coldaine/pr-advisory-agent` to a temporary directory.
   - Sets up `.skills/` and `check_deps.py`.
   - Runs `letta-code-action`.
   - Posts an advisory comment to the PR.
