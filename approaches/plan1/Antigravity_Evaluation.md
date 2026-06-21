# Plan 1 Evaluation: Standard / Letta Cloud

This document contains criticisms and actionable suggestions for **Plan 1** (`approaches/plan1/Plan1.txt`).

---

## 1. Technical Defects & Criticisms

### A. Redundant & Broken CLI Installation
* **Issue**: The workflow contains a manual installation step:
  ```yaml
  run: curl -fsSL https://letta.com/install.sh | bash
  ```
* **Criticism**: The official Letta Code CLI is installed via npm (`npm install -g @letta-ai/letta-code`), so this `curl` command will fail. Furthermore, the `letta-ai/letta-code-action` GitHub Action automatically installs the required CLI dependencies internally. Having a separate CLI installation step in the workflow is both incorrect and completely redundant.

### B. Incorrect GitHub Action Reference
* **Issue**: The workflow uses `uses: letta-ai/letta-code@v1`.
* **Criticism**: The official repository for the GitHub Action is named `letta-code-action`, not `letta-code`. Using the wrong name will cause the Action runner to crash instantly with a "Repository not found" error. The correct action name is:
  ```yaml
  uses: letta-ai/letta-code-action@v0
  ```

### C. Skill Auto-Discovery Path
* **Issue**: The plan places skills in `skills/dependency-audit/`.
* **Criticism**: Letta Code auto-discovers skills from a dot-prefixed `.skills/` directory (specifically `.skills/github-action/`), not a standard `skills/` directory. If stored in `skills/`, the agent will not automatically load these skill definitions during execution.

### D. Silent Scanning Failures
* **Issue**: The `check-deps.sh` script suppresses stderr and appends `|| true` to all scanner commands (e.g., `cargo outdated 2>/dev/null || true`).
* **Criticism**: If a scanner tool (like `cargo-outdated` or `pip-audit`) is missing from the runner environment, the script fails silently and outputs nothing. The agent will falsely conclude that the repository has zero outdated dependencies rather than warning that the scanner tool is missing.

### E. Runner Minutes Consumption
* **Issue**: Running dynamic audits for multiple ecosystems on the GitHub Actions runner.
* **Criticism**: Restoring dependencies and compiling helper tools (like `cargo-outdated`, which must be compiled from source via `cargo install`) on a clean runner environment takes several minutes per run, which will rapidly burn through your GitHub Actions free tier minutes.

---

## 2. Actionable Suggestions for Plan 1

1. **Fix Action Name and Version**: Change the step to use `uses: letta-ai/letta-code-action@v0`.
2. **Remove Redundant Installation**: Delete the `Install Letta Code` step entirely.
3. **Move Skills Path**: Relocate your custom skill files to `.skills/dependency-audit/` in your repository.
4. **Enable Sticky Comments**: Add `use_sticky_comment: "true"` to the Action inputs so the agent updates a single comment on each commit rather than posting a new comment, reducing PR noise.
5. **Handle Missing Scanners Gracefully**: Modify `check-deps.sh` to output warning markers when a tool is missing (e.g., `echo "cargo-outdated: tool missing"`) so the agent knows to fall back to manual manifest file parsing.
