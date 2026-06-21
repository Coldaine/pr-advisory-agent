# AGENTS.md

This file is for coding agents working in this repository.

## What this repo is for

This repo is about designing a PR advisory product.

The intended product reviews pull requests and posts advisory feedback about:
- dependency versions and upgrade opportunities
- security and vulnerability signals
- architecture alternatives and tradeoffs

The product should remain advisory unless the user explicitly decides otherwise.

## Current repo status

We have not chosen a single implementation approach yet.

Multiple approaches are intentionally active side by side under `approaches/`.
Do not treat any one folder as the source of truth unless the user explicitly says so.

Cross-approach analysis belongs under `evaluations/`.

## Working rules for agents

- Keep the repository root neutral.
- Put approach-specific material inside `approaches/<approach-name>/`.
- Put comparison or scoring documents inside `evaluations/`.
- If you update one approach, avoid silently merging its assumptions into the others.
- If you add comparison notes, be explicit about which approach each note references.
- If a future decision is made, record it in a dedicated decision document rather than implying it through file placement.
