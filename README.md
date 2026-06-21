# PR Advisory Agent

This repository is a planning workspace for a product that reviews pull requests and posts advisory feedback.

The product goal is stable:
- analyze dependencies and version drift
- flag security-relevant issues
- suggest architecture alternatives with pros and cons
- stay advisory rather than modifying product code

The implementation approach is not settled yet.

We are intentionally keeping multiple active approaches side by side while we compare tradeoffs.

## Repository layout

- `approaches/` - active candidate approaches
- `approaches/plan1/Plan1.txt` - simpler Letta Code-first approach
- `approaches/zai/Part1.txt` - ZAI blueprint overview
- `approaches/zai/Part2.txt` - ZAI implementation details
- `evaluations/EVALUATION.md` - cross-approach analysis and comparison notes
- `AGENTS.md` - instructions for coding agents working in this repo

## Current decision status

No single approach is canonical yet.

If you are reviewing or extending this repo, treat each approach folder as an active candidate unless a later decision document says otherwise.
