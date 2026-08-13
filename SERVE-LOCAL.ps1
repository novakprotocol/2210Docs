#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$DoNotOpenBrowser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Runtime = Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "IaTDocs\runtime\v0.08.2"

$python = $null
$prefix = @()
foreach ($candidate in @(
    @{ Name = "py"; Prefix = @("-3.11") },
    @{ Name = "py"; Prefix = @("-3") },
    @{ Name = "python"; Prefix = @() },
    @{ Name = "python3"; Prefix = @() }
)) {
    $cmd = Get-Command $candidate.Name -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    $probeArgs = [string[]]($candidate.Prefix + @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"))
    & $cmd.Source @probeArgs
    if ($LASTEXITCODE -eq 0) { $python = $cmd.Source; $prefix = [string[]]$candidate.Prefix; break }
}
if (-not $python) { throw "Python 3.11 or later is required." }

$separator = [IO.Path]::PathSeparator
$prior = $env:PYTHONPATH
try {
    $env:PYTHONPATH = (Join-Path $Root "src")
    if (Test-Path -LiteralPath $Runtime) { $env:PYTHONPATH += $separator + $Runtime }
    $probeArgs = [string[]]($prefix + @("-c", "import jinja2,mistune,markupsafe"))
    & $python @probeArgs
    if ($LASTEXITCODE -ne 0) {
        $venv = Join-Path $Root ".venv"
        if (-not (Test-Path -LiteralPath $venv)) {
            $venvArgs = [string[]]($prefix + @("-m", "venv", $venv))
            & $python @venvArgs
            if ($LASTEXITCODE -ne 0) { throw "Could not create the local Python environment." }
        }
        $python = Join-Path $venv "Scripts\python.exe"
        $prefix = @()
        & $python -m pip install --disable-pip-version-check --no-build-isolation -r (Join-Path $Root "requirements.txt")
        if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
        $env:PYTHONPATH = Join-Path $Root "src"
    }
    $serveCommand = @("-m", "iatdocs", "--repo", $Root, "serve", "--host", $HostName, "--port", [string]$Port)
    if (-not $DoNotOpenBrowser) { $serveCommand += "--open" }
    $serveArgs = [string[]]($prefix + $serveCommand)
    & $python @serveArgs
    if ($LASTEXITCODE -ne 0) { throw "Local server exited with code $LASTEXITCODE." }
}
finally { $env:PYTHONPATH = $prior }
