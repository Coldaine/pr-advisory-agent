# Cross-Repository Usage

## Setup in a Target Repository

### 1. Create the Workflow File

Add `.github/workflows/pr-advisory.yml` to your repository:

```yaml
name: PR Advisory Reviews
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr_advisory:
    uses: Coldaine/pr-advisory-agent/.github/workflows/reusable-pr-advisory.yml@main
    with:
      letta_dep_agent_id: ${{ vars.LETTA_DEP_AGENT_ID }}
      letta_arch_agent_id: ${{ vars.LETTA_ARCH_AGENT_ID }}
      letta_base_url: 'https://api.letta.com'
      base_branch: 'main'
    secrets:
      LETTA_API_KEY: ${{ secrets.LETTA_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Configure Workflow Permissions

In your repository: `Settings > Actions > General > Workflow permissions`
Select **Read and write permissions**, or add the following to the job:

```yaml
permissions:
  contents: read
  pull-requests: write
```

### 3. Set Up Secrets and Variables

In `Settings > Secrets and variables > Actions`:

**Variables tab:**
- `LETTA_DEP_AGENT_ID` — The ID of your Dependency Auditor agent
- `LETTA_ARCH_AGENT_ID` — The ID of your Architectural Advisor agent

**Secrets tab:**
- `LETTA_API_KEY` — API key for your Letta server instance

## Letta Agent Provisioning

Each target repository should have its own pair of Letta agents (isolated history) so that review memory and MemFS state are not shared across repositories.

Ensure your agents have Exa and Firecrawl MCP servers connected for changelog and documentation context retrieval.

## Base Branch

The `base_branch` input controls which branch is compared against for PR diff analysis. Set this to the default branch of your repository (e.g., `main`, `develop`, `master`).
