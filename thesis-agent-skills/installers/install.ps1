[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidateSet('controller','worker','reviewer')][string]$Profile,
  [Parameter(Mandatory)][string]$Target,
  [string]$Python = 'python',
  [switch]$DryRun,
  [switch]$Execute,
  [switch]$Force,
  [switch]$AllowGlobal
)
$ErrorActionPreference = 'Stop'
$installArgs = @((Join-Path $PSScriptRoot 'install.py'), '--profile', $Profile, '--target', $Target)
if ($DryRun) { $installArgs += '--dry-run' }
if ($Execute) { $installArgs += '--execute' }
if ($Force) { $installArgs += '--force' }
if ($AllowGlobal) { $installArgs += '--allow-global' }
& $Python @installArgs
exit $LASTEXITCODE
