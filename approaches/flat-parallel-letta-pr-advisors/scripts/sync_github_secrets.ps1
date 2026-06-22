param(
  [Parameter(Mandatory=$true)]
  [string]$Repo,

  [string]$CodingAgentsProject = "codingagents",
  [string]$CodingAgentsConfig = "dev"
)

$ErrorActionPreference = "Stop"

function Set-GitHubSecretFromDoppler {
  param(
    [Parameter(Mandatory=$true)][string]$SecretName,
    [Parameter(Mandatory=$true)][string]$DopplerProject,
    [Parameter(Mandatory=$true)][string]$DopplerConfig
  )

  $value = doppler secrets get $SecretName --project $DopplerProject --config $DopplerConfig --plain
  if (-not $value) { throw "Doppler secret $SecretName not found in $DopplerProject/$DopplerConfig" }

  # gh secret set reads from stdin; do not echo the value to terminal.
  $value | gh secret set $SecretName --repo $Repo
  Write-Host "Synced GitHub secret: $SecretName"
}

Set-GitHubSecretFromDoppler -SecretName "LETTA_API_KEY" -DopplerProject $CodingAgentsProject -DopplerConfig $CodingAgentsConfig

Write-Host "Set LETTA_BASE_URL separately once the K8s ingress URL exists:"
Write-Host "  gh secret set LETTA_BASE_URL --repo $Repo --body https://letta.yourdomain.com"
Write-Host "Set agent IDs after Stage 0 agent creation:"
Write-Host "  gh variable set LETTA_DEP_AGENT_ID --repo $Repo --body <dep-agent-id>"
Write-Host "  gh variable set LETTA_ARCH_AGENT_ID --repo $Repo --body <arch-agent-id>"