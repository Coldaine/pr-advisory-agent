# Ecosystem Reference

## Supported Ecosystems

### Node.js / JavaScript / TypeScript
- Manifest files: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- Check command: `npm outdated --json`
- List command: `npm ls --all --json`
- Audit command: `npm audit --json`
- Registry: https://registry.npmjs.org

### Python
- Manifest files: `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `setup.cfg`
- Check command: `pip list --outdated --format=json`
- Audit command: `pip-audit --format json`
- Registry: https://pypi.org/pypi/{package}/json

### Rust
- Manifest files: `Cargo.toml`, `Cargo.lock`
- Check command: `cargo outdated --format json`
- Registry: https://crates.io/api/v1/crates/{package}

### Go
- Manifest files: `go.mod`, `go.sum`
- Check command: `go list -m -u all`
- Registry: https://proxy.golang.org/{module}/@latest

### Ruby
- Manifest files: `Gemfile`, `Gemfile.lock`
- Check command: `bundle outdated`
- Registry: https://rubygems.org/api/v1/gems/{gem}.json

### Java / Kotlin
- Manifest files: `pom.xml`, `build.gradle`, `build.gradle.kts`
- Registry: https://search.maven.org/solrsearch/select

### .NET
- Manifest files: `*.csproj`, `packages.config`
- Check command: `dotnet list package --outdated`
- Registry: https://api.nuget.org/v3-flatcontainer/{package}/index.json

### Docker
- Manifest files: `Dockerfile`, `docker-compose.yml`
- Check: Base image tags (e.g., `python:3.11-slim` → check for newer tags)

## Adding New Ecosystems
If the agent encounters a manifest file not listed above:
1. Read the manifest file directly using file-reading tools
2. Parse the dependency list (the agent understands the file format)
3. Query the relevant registry API for latest versions
4. Report findings in the standard format
