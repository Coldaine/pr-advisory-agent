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

# WHY NOT LLM? LLMs have a training cutoff date. If an LLM was trained
# in 2024, it physically cannot know about a security patch released yesterday.
# By using a Python script, we get real-time, deterministic data regardless
# of when the LLM was trained.

def check_npm(repo_path: str):
    """
    Reads package.json, queries the npm registry API for the absolute latest version.
    """
    dependencies = []
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
    # This loop forces a hard HTTP GET to the official npm registry.
    for name, current_version_spec in deps.items():
        try:
            r = requests.get(f"https://registry.npmjs.org/{name}/latest", timeout=5)
            r.raise_for_status()
            latest_version = r.json().get("version")

            # WHY NOT LLM? LLMs are bad at comparing semantic versions (semver).
            # They might think "4.10.0" is newer than "4.9.0" because 9 > 10.
            # Python exact matching removes hallucination and comparison errors here.
            if latest_version and latest_version not in current_version_spec:
                dependencies.append({
                    "ecosystem": "npm",
                    "name": name,
                    "current": current_version_spec,
                    "latest": latest_version,
                    "update_available": True
                })
        except requests.RequestException as e:
            # WHY NOT LLM? If the network is down, an LLM will often hallucinate a
            # version rather than admitting it failed to fetch it. This script fails
            # gracefully and reports the error to the LLM.
            dependencies.append({
                "ecosystem": "npm",
                "name": name,
                "error": f"Failed to fetch latest version: {str(e)}"
            })

    return dependencies

def check_pypi(repo_path: str):
    """
    Reads requirements.txt, queries the PyPI JSON API for the exact latest version.
    """
    dependencies = []
    req_path = Path(repo_path) / "requirements.txt"

    if not req_path.exists():
        return []

    try:
        with open(req_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [{"error": f"Failed to read requirements.txt: {str(e)}"}]

    # WHY NOT LLM? LLMs struggle to parse requirements.txt files because the syntax
    # is messy (e.g., `Django==4.2.0`, `requests>=2.31.0`, `# this is a comment`).
    # Python's exact parsing is deterministic and won't be confused by comments.
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "==" in line:
            parts = line.split("==")
            name = parts[0].strip()
            current_version = parts[1].strip()

            try:
                r = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=5)
                r.raise_for_status()
                latest_version = r.json().get("info", {}).get("version")

                if latest_version and latest_version != current_version:
                    dependencies.append({
                        "ecosystem": "pypi",
                        "name": name,
                        "current": current_version,
                        "latest": latest_version,
                        "update_available": True
                    })
            except requests.RequestException as e:
                dependencies.append({
                    "ecosystem": "pypi",
                    "name": name,
                    "error": f"Failed to fetch latest version: {str(e)}"
                })

    return dependencies

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 check_deps.py <repo_path>"}))
        sys.exit(1)

    repo = sys.argv[1]
    all_deps = {
        "npm": check_npm(repo),
        "pypi": check_pypi(repo)
    }

    # WHY NOT LLM? The LLM needs this data in a pristine, structured format.
    # If we returned raw text, the LLM might miss a package or hallucinate
    # a field. By printing strict JSON, the Letta agent can parse this directly
    # into its context window without any loss of fidelity.
    print(json.dumps(all_deps, indent=2))