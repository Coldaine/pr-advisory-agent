#!/usr/bin/env python3
"""
check_deps.py: Scans a repository for dependencies, queries official
registries for the latest versions, and returns structured JSON.

[Agent Note]: I wrote this script to handle mechanical extraction of dependency versions.
Why Python? I switched from the original Bash script plan because parsing PyPI requirements.txt
and handling API pagination/errors is much more robust in Python. This ensures we don't crash
the GitHub Action on bad JSON.
"""
import json
import sys
import requests
from pathlib import Path
import urllib.parse
import re
from packaging.requirements import Requirement
from concurrent.futures import ThreadPoolExecutor

# WHY NOT LLM? LLMs have a training cutoff date. If an LLM was trained
# in 2024, it physically cannot know about a security patch released yesterday.
# By using a Python script, we get real-time, deterministic data regardless
# of when the LLM was trained.

def parse_semver(version_str: str):
    """
    Parses a version string into a tuple of integers for clean semantic comparison.
    Handles major.minor.patch, major.minor, and major releases.
    """
    # Extract only digits and dots/hyphens for basic semver parsing
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return tuple(map(int, match.groups()))
    
    # Try 2-digit semver (e.g. 4.17)
    match = re.search(r'(\d+)\.(\d+)', version_str)
    if match:
        return (int(match.group(1)), int(match.group(2)), 0)
    
    # Try 1-digit semver (e.g. 4)
    match = re.search(r'(\d+)', version_str)
    if match:
        return (int(match.group(1)), 0, 0)
        
    return (0, 0, 0)

def is_newer(current_spec: str, latest_version: str) -> bool:
    """
    Determines if the latest registry version is newer than the current version or spec range.
    Strips prefix range specifiers (e.g. ^, ~, >=, v) to establish a clean base version.
    """
    if not latest_version:
        return False
        
    # Strip common non-version characters to find the baseline version
    # e.g., ^4.17.1 -> 4.17.1, >=2.3.0 -> 2.3.0, v1.0.0 -> 1.0.0
    current_clean = re.sub(r'^[^\d]*', '', current_spec)
    
    current_parsed = parse_semver(current_clean)
    latest_parsed = parse_semver(latest_version)
    
    return latest_parsed > current_parsed

def is_safe_package_name(name: str, ecosystem: str) -> bool:
    """
    Validates the package name to prevent arbitrary path traversal or URL manipulation (SSRF).
    """
    if not isinstance(name, str):
        return False
    if ecosystem == "npm":
        # Allow scoped npm packages e.g. @types/node, @babel/core
        # Safe characters: alphanumeric, dashes, dots, underscores, and single slash for scope.
        return bool(re.match(r'^(?:@[a-zA-Z0-9_.-]+/)?(?:[a-zA-Z0-9_.-]+)$', name))
    elif ecosystem == "pypi":
        # PyPI package names. Safe characters: alphanumeric, dashes, dots, underscores.
        return bool(re.match(r'^[a-zA-Z0-9_.-]+$', name))
    return False

def fetch_npm_latest(name: str, current_spec: str):
    """
    Fetches the latest version of a package from the npm registry.
    """
    if not is_safe_package_name(name, "npm"):
        return {
            "ecosystem": "npm",
            "name": name,
            "error": f"Invalid package name format: {name}"
        }
    try:
        encoded_name = urllib.parse.quote(name, safe='@')
        r = requests.get(f"https://registry.npmjs.org/{encoded_name}/latest", timeout=5)
        r.raise_for_status()
        latest_version = r.json().get("version")
        
        if latest_version and is_newer(current_spec, latest_version):
            return {
                "ecosystem": "npm",
                "name": name,
                "current": current_spec,
                "latest": latest_version,
                "update_available": True
            }
    except requests.RequestException as e:
        return {
            "ecosystem": "npm",
            "name": name,
            "error": f"Failed to fetch latest version: {str(e)}"
        }
    return None

def check_npm(repo_path: str):
    """
    Reads package.json and queries npm registry in parallel.
    """
    pkg_json_path = Path(repo_path) / "package.json"

    # WHY NOT LLM? LLMs cannot reliably read and parse raw JSON files from the
    # filesystem without complex tool wrappers. They also tend to "remember"
    # package.json contents from their training data instead of reading the actual file.
    if not pkg_json_path.exists():
        return []

    try:
        with open(pkg_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # We only care about actual dependencies, not devDependencies for this check.
            deps = data.get("dependencies", {})
    except Exception as e:
        return [{"error": f"Failed to parse package.json: {str(e)}"}]

    # WHY NOT LLM? An LLM might try to guess the latest version of "express" based on
    # its training data. It might output "4.18.0" when the actual latest is "4.19.2".
    # This loop forces parallel HTTP GET requests to the official npm registry.
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_npm_latest, name, spec) for name, spec in deps.items()]
        results = [f.result() for f in futures]

    return [r for r in results if r is not None]

def fetch_pypi_latest(name: str, current_version: str):
    """
    Fetches the latest version of a package from the PyPI JSON API.
    """
    if not is_safe_package_name(name, "pypi"):
        return {
            "ecosystem": "pypi",
            "name": name,
            "error": f"Invalid package name format: {name}"
        }
    try:
        r = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=5)
        r.raise_for_status()
        latest_version = r.json().get("info", {}).get("version")
        
        if latest_version and is_newer(current_version, latest_version):
            return {
                "ecosystem": "pypi",
                "name": name,
                "current": current_version,
                "latest": latest_version,
                "update_available": True
            }
    except requests.RequestException as e:
        return {
            "ecosystem": "pypi",
            "name": name,
            "error": f"Failed to fetch latest version: {str(e)}"
        }
    return None

def check_pypi(repo_path: str):
    """
    Reads requirements.txt and queries PyPI JSON API in parallel.
    """
    req_path = Path(repo_path) / "requirements.txt"

    if not req_path.exists():
        return []

    try:
        with open(req_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [{"error": f"Failed to read requirements.txt: {str(e)}"}]

    # Gather PyPI dependency names and pinned versions (package==1.0.0)
    pypi_deps = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Strip inline comments
        if "#" in line:
            line = line.split("#")[0].strip()
        if not line:
            continue

        try:
            req = Requirement(line)
            name = req.name
            specs = list(req.specifier)
            if specs:
                current_version = specs[0].version
                pypi_deps.append((name, current_version))
        except Exception:
            # Fallback to simple == split
            if "==" in line:
                parts = line.split("==")
                name = parts[0].strip()
                current_version = parts[1].strip()
                pypi_deps.append((name, current_version))

    # Run queries in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_pypi_latest, name, curr_ver) for name, curr_ver in pypi_deps]
        results = [f.result() for f in futures]

    return [r for r in results if r is not None]

if __name__ == "__main__":
    # The script expects the repository path as the first argument.
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 check_deps.py <repo_path>"}))
        sys.exit(1)

    repo = sys.argv[1]

    # Aggregate all ecosystems.
    all_deps = {
        "npm": check_npm(repo),
        "pypi": check_pypi(repo)
    }

    # WHY NOT LLM? The LLM needs this data in a pristine, structured format.
    # If we returned raw text, the LLM might miss a package or hallucinate
    # a field. By printing strict JSON, the Letta agent can parse this directly
    # into its context window without any loss of fidelity.
    print(json.dumps(all_deps, indent=2))