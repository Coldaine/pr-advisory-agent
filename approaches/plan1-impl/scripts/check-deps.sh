#!/bin/bash
# scripts/check-deps.sh
# Dependency checking script invoked by the PR Advisory Agent.
# Runs native package manager commands for every ecosystem in the repo.
# The agent interprets the output — this script just gathers data.

set -e

echo "=== Dependency Version Check ==="
echo ""

# Node.js / npm
if [ -f "package.json" ]; then
  echo "--- npm ---"
  npm outdated --json 2>/dev/null || true
  echo ""
fi

# Python / pip
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.cfg" ]; then
  echo "--- pip ---"
  pip list --outdated --format=json 2>/dev/null || true
  echo ""
fi

# Python audit (if pip-audit is installed)
if command -v pip-audit &> /dev/null; then
  echo "--- pip-audit ---"
  pip-audit --format json 2>/dev/null || true
  echo ""
fi

# Rust / cargo
if [ -f "Cargo.toml" ]; then
  echo "--- cargo ---"
  cargo outdated --format json 2>/dev/null || true
  echo ""
fi

# Go
if [ -f "go.mod" ]; then
  echo "--- go ---"
  go list -m -u all 2>/dev/null || true
  echo ""
fi

# Ruby / bundler
if [ -f "Gemfile" ]; then
  echo "--- bundler ---"
  bundle outdated 2>/dev/null || true
  echo ""
fi

# .NET
if ls *.csproj 1>/dev/null 2>&1; then
  echo "--- dotnet ---"
  dotnet list package --outdated 2>/dev/null || true
  echo ""
fi

# npm audit (if package-lock.json exists)
if [ -f "package-lock.json" ]; then
  echo "--- npm-audit ---"
  npm audit --json 2>/dev/null || true
  echo ""
fi

echo "=== End Dependency Check ==="
