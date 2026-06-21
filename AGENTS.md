# AGENTS.md

This repository is a planning workspace for a PR advisory product.

## Product intent

The product reviews pull requests and posts advisory feedback about:
- dependency versions and upgrade opportunities
- security and vulnerability signals
- architecture alternatives and tradeoffs

The product should remain advisory unless the user explicitly decides otherwise.

## Decision status

No single implementation approach has been chosen yet.

Multiple approaches are intentionally active side by side under `approaches/`.
Do not treat any one folder as canonical unless the user explicitly says so.

## Repository structure

- `approaches/` contains active candidate approaches
- `evaluations/` contains cross-approach comparison material
- approach-specific evaluation notes may live beside the approach they evaluate

## Working rules for agents

- Keep the repository root neutral.
- Put approach-specific material inside `approaches/<approach-name>/`.
- Put cross-approach comparison documents inside `evaluations/`.
- If you update one approach, avoid silently merging its assumptions into the others.
- If you add comparison notes, be explicit about which approach each note references.
- If a future decision is made, record it in a dedicated decision document rather than implying it through file placement.
