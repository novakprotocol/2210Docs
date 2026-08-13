#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$HostName = "",
    [string]$Repository = "",
    [switch]$SkipMetrics,
    [switch]$SkipTests,
    [switch]$DoNotConfigurePages,
    [switch]$DoNotOpenPages
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = $PSScriptRoot
$EngineVersion = "v0.08.2"
$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$ReceiptRoot = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "IaTDocs-Publish-Receipts\$Timestamp"
$WorkRoot = Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "IaTDocs\publish\$Timestamp"
$LogPath = Join-Path $ReceiptRoot "publish.log"
New-Item -ItemType Directory -Force -Path $ReceiptRoot, $WorkRoot | Out-Null

function Log([string]$Message, [ConsoleColor]$Color = [ConsoleColor]::Gray) {
    $line = "[{0}] {1}" -f ((Get-Date).ToUniversalTime().ToString("HH:mm:ssZ")), $Message
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Need([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Required command is missing: $Name" }
    return $cmd.Source
}

function Run([string]$File, [string[]]$Args, [string]$Cwd = "", [switch]$AllowFailure, [switch]$Quiet) {
    $prior = Get-Location
    $priorEap = $ErrorActionPreference
    try {
        if ($Cwd) { Set-Location -LiteralPath $Cwd }
        if (-not $Quiet) { Log ("$ " + $File + " " + ($Args -join " ")) DarkGray }
        $ErrorActionPreference = "Continue"
        $text = & $File @Args 2>&1 | ForEach-Object { [string]$_ } | Out-String
        $code = $LASTEXITCODE
        $ErrorActionPreference = $priorEap
        if ($text.Trim() -and -not $Quiet) {
            foreach ($line in ($text.TrimEnd() -split "`r?`n")) { Log $line DarkGray }
        }
        if ($code -ne 0 -and -not $AllowFailure) {
            throw "Command failed with exit code ${code}: $File $($Args -join ' ')`n$text"
        }
        return [pscustomobject]@{ ExitCode = $code; Output = $text }
    }
    finally {
        $ErrorActionPreference = $priorEap
        Set-Location -LiteralPath $prior
    }
}

function Resolve-Python {
    $options = [System.Collections.Generic.List[object]]::new()
    if ($env:IATDOCS_PYTHON) { $options.Add([pscustomobject]@{ File = $env:IATDOCS_PYTHON; Prefix = [string[]]@(); Source = "IATDOCS_PYTHON" }) }
    $py = Get-Command "py" -ErrorAction SilentlyContinue
    if ($py) {
        foreach ($v in @("-3.13", "-3.12", "-3.11", "-3")) { $options.Add([pscustomobject]@{ File = $py.Source; Prefix = [string[]]@($v); Source = "py launcher $v" }) }
        $list = Run $py.Source @("-0p") -AllowFailure -Quiet
        if ($list.ExitCode -eq 0) {
            foreach ($line in ($list.Output -split "`r?`n")) {
                if ($line -match "([A-Za-z]:\\[^`"'<>|?*]+python(?:3)?\.exe)") { $options.Add([pscustomobject]@{ File = $Matches[1]; Prefix = [string[]]@(); Source = "py -0p" }) }
            }
        }
    }
    $roots = New-Object System.Collections.Generic.List[string]
    if ($env:LocalAppData) { $roots.Add((Join-Path $env:LocalAppData "Programs\Python")) | Out-Null }
    if ($env:ProgramFiles) { $roots.Add($env:ProgramFiles) | Out-Null }
    $programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    if ($programFilesX86) { $roots.Add($programFilesX86) | Out-Null }
    foreach ($base in $roots) {
        foreach ($dir in @("Python313", "Python312", "Python311")) {
            $path = Join-Path (Join-Path $base $dir) "python.exe"
            if (Test-Path -LiteralPath $path -PathType Leaf) { $options.Add([pscustomobject]@{ File = $path; Prefix = [string[]]@(); Source = "known install path" }) }
        }
    }
    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $options.Add([pscustomobject]@{ File = $cmd.Source; Prefix = [string[]]@(); Source = $name }) }
    }
    $seen = @{}
    foreach ($option in $options) {
        $key = ([string]$option.File) + "|" + (($option.Prefix) -join " ")
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        if (($option.File -notmatch "^(py|python|python3)$") -and -not (Test-Path -LiteralPath $option.File -PathType Leaf)) { continue }
        $probe = Run ([string]$option.File) ([string[]]$option.Prefix + @("-c", "import sys; print('.'.join(map(str,sys.version_info[:3])))")) -AllowFailure -Quiet
        if ($probe.ExitCode -ne 0) { continue }
        try { $version = [version]$probe.Output.Trim() } catch { continue }
        if ($version -ge [version]"3.11.0") { return [pscustomobject]@{ File = [string]$option.File; Prefix = [string[]]$option.Prefix; Version = $version.ToString(); Source = [string]$option.Source } }
    }
    throw "Python 3.11 or later is required. Set IATDOCS_PYTHON to the full python.exe path and rerun."
}

function Py([string[]]$Args, [switch]$AllowFailure, [switch]$Quiet) {
    return Run $script:Python.File ($script:Python.Prefix + $Args) $Root -AllowFailure:$AllowFailure -Quiet:$Quiet
}

function GhApi([string]$Method, [string]$Endpoint, $Body = $null, [switch]$AllowFailure, [switch]$Quiet) {
    $arguments = @("api", "--hostname", $script:Host, "-X", $Method, $Endpoint)
    $temp = $null
    try {
        if ($null -ne $Body) {
            $temp = Join-Path $WorkRoot ("body-" + [guid]::NewGuid().ToString("N") + ".json")
            $Body | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $temp -Encoding UTF8
            $arguments += @("--input", $temp)
        }
        return Run $script:Gh $arguments -AllowFailure:$AllowFailure -Quiet:$Quiet
    }
    finally {
        if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Force }
    }
}

try {
    $script:Git = Need "git"
    $script:Gh = Need "gh"
    $script:Python = Resolve-Python

    $doc = Get-Content -LiteralPath (Join-Path $Root "data\document.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    $script:Host = if ($HostName) { $HostName } else { [string]$doc.ghe_host }
    $fullName = if ($Repository) { $Repository } else { [string]$doc.source_repository }
    if (-not $script:Host -or -not $fullName -or $fullName -notmatch "^[^/]+/[^/]+$") {
        throw "Host or OWNER/REPOSITORY is not configured in data/document.json."
    }

    Log "Publishing $fullName on $script:Host with IaT Docs Engine $EngineVersion." Cyan
    Run $script:Gh @("auth", "status", "--hostname", $script:Host) | Out-Null
    Run $script:Gh @("auth", "setup-git", "--hostname", $script:Host) | Out-Null

    $dirtyBefore = (Run $script:Git @("-C", $Root, "status", "--porcelain") -Quiet).Output.Trim()
    if ($dirtyBefore) {
        throw "The main working tree has uncommitted changes. Commit or stash them before publishing."
    }

    $runtime = Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "IaTDocs\runtime\$EngineVersion"
    $priorPythonPath = $env:PYTHONPATH
    try {
        $separator = [IO.Path]::PathSeparator
        $env:PYTHONPATH = (Join-Path $Root "src")
        if (Test-Path -LiteralPath $runtime) { $env:PYTHONPATH += $separator + $runtime }
        $probe = Py @("-c", "import jinja2,mistune,markupsafe") -AllowFailure -Quiet
        if ($probe.ExitCode -ne 0) {
            $venv = Join-Path $Root ".venv"
            if (-not (Test-Path -LiteralPath $venv)) {
                Log "Creating local Python environment because the bootstrap runtime was not found." Yellow
                Py @("-m", "venv", $venv) | Out-Null
            }
            $venvPython = Join-Path $venv "Scripts\python.exe"
            if (-not (Test-Path -LiteralPath $venvPython)) { throw "Local Python environment is incomplete: $venv" }
            Run $venvPython @("-m", "pip", "install", "--disable-pip-version-check", "--no-build-isolation", "-r", (Join-Path $Root "requirements.txt")) $Root | Out-Null
            $script:Python = [pscustomobject]@{ File = $venvPython; Prefix = [string[]]@(); Version = "venv" }
            $env:PYTHONPATH = Join-Path $Root "src"
        }

        if (-not $SkipTests) {
            Py @("-m", "unittest", "discover", "-s", "tests", "-v") | Out-Null
        }

        if (-not $SkipMetrics) {
            Py @("-m", "iatdocs", "--repo", $Root, "metrics", "--apply") -AllowFailure | Out-Null
            $generated = @(
                "data/repository.json",
                "data/contributions.json",
                "work-ledger/contributions.json",
                "work-ledger/contributions.csv",
                "work-ledger/activity-events.csv"
            )
            $changed = (Run $script:Git (@("-C", $Root, "status", "--porcelain", "--") + $generated) -Quiet).Output.Trim()
            if ($changed) {
                Run $script:Git (@("-C", $Root, "add", "--") + $generated) | Out-Null
                Run $script:Git @("-C", $Root, "commit", "-m", "chore(iatdocs): refresh document intelligence") | Out-Null
                Run $script:Git @("-C", $Root, "push", "origin", "main") | Out-Null
                Log "Committed and pushed refreshed repository intelligence." Green
            }
        }

        Py @("-m", "iatdocs", "--repo", $Root, "doctor", "--json") | Out-Null
        Py @("-m", "iatdocs", "--repo", $Root, "build", "--strict") | Out-Null
        Py @("-m", "iatdocs", "--repo", $Root, "validate", "--built") | Out-Null
    }
    finally { $env:PYTHONPATH = $priorPythonPath }

    $site = Join-Path $Root "site"
    if (-not (Test-Path -LiteralPath (Join-Path $site "index.html"))) { throw "site/index.html was not generated." }
    $sourceCommit = (Run $script:Git @("-C", $Root, "rev-parse", "HEAD") -Quiet).Output.Trim()
    $publish = Join-Path $WorkRoot "gh-pages"
    New-Item -ItemType Directory -Force -Path $publish | Out-Null
    Get-ChildItem -LiteralPath $site -Force | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $publish -Recurse -Force }
    Set-Content -LiteralPath (Join-Path $publish "SOURCE-COMMIT.txt") -Value ($sourceCommit + "`n") -Encoding UTF8
    [ordered]@{
        schema_version = 1
        repository = $fullName
        host = $script:Host
        source_commit = $sourceCommit
        pages_branch = "gh-pages"
        engine_version = $EngineVersion
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $publish "PUBLISH-RECEIPT.json") -Encoding UTF8

    Run $script:Git @("-C", $publish, "init", "-b", "gh-pages") | Out-Null
    $name = (Run $script:Git @("-C", $Root, "config", "user.name") -Quiet).Output.Trim()
    $email = (Run $script:Git @("-C", $Root, "config", "user.email") -Quiet).Output.Trim()
    if (-not $name) { $name = "IaT Docs Publisher" }
    if (-not $email) { $email = "iatdocs-publisher@$script:Host" }
    Run $script:Git @("-C", $publish, "config", "user.name", $name) | Out-Null
    Run $script:Git @("-C", $publish, "config", "user.email", $email) | Out-Null
    Add-ExactPublishFiles -RepositoryPath $publish | Out-Null
    Run $script:Git @("-C", $publish, "commit", "-m", "Publish IaT Docs Pages from $sourceCommit") | Out-Null
    Run $script:Git @("-C", $publish, "remote", "add", "origin", "https://$script:Host/$fullName.git") | Out-Null
    Run $script:Git @("-C", $publish, "push", "--force", "origin", "gh-pages") | Out-Null
    Log "Published generated site to gh-pages." Green

    $pagesUrl = ""
    $pagesStatus = "not-configured"
    if (-not $DoNotConfigurePages) {
        $source = [ordered]@{ branch = "gh-pages"; path = "/" }
        $current = GhApi "GET" "repos/$fullName/pages" -AllowFailure -Quiet
        if ($current.ExitCode -eq 0) {
            $update = GhApi "PUT" "repos/$fullName/pages" ([ordered]@{ build_type = "legacy"; source = $source }) -AllowFailure
            if ($update.ExitCode -ne 0) { GhApi "PUT" "repos/$fullName/pages" ([ordered]@{ source = $source }) | Out-Null }
        }
        else {
            $create = GhApi "POST" "repos/$fullName/pages" ([ordered]@{ source = $source }) -AllowFailure
            if ($create.ExitCode -ne 0) { GhApi "POST" "repos/$fullName/pages" ([ordered]@{ build_type = "legacy"; source = $source }) | Out-Null }
        }
        GhApi "POST" "repos/$fullName/pages/builds" $null -AllowFailure -Quiet | Out-Null
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Seconds 10
            $state = GhApi "GET" "repos/$fullName/pages" $null -AllowFailure -Quiet
            if ($state.ExitCode -ne 0) { continue }
            $page = $state.Output | ConvertFrom-Json
            $pagesStatus = [string]$page.status
            $pagesUrl = [string]$page.html_url
            Log "Pages status: $pagesStatus" DarkCyan
            if ($pagesStatus -in @("built", "errored")) { break }
        }
        if ($pagesStatus -ne "built") { throw "Pages did not reach built status. Final status: $pagesStatus" }
        GhApi "PUT" "repos/$fullName/pages" ([ordered]@{ https_enforced = $true }) -AllowFailure -Quiet | Out-Null
    }

    [ordered]@{
        schema_version = 1
        status = "COMPLETE"
        repository = $fullName
        host = $script:Host
        source_commit = $sourceCommit
        pages_status = $pagesStatus
        pages_url = $pagesUrl
        receipt_directory = $ReceiptRoot
        completed_at = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $ReceiptRoot "PUBLISH-RESULT.json") -Encoding UTF8

    Log "Publication complete." Green
    if ($pagesUrl) {
        Log "Pages: $pagesUrl" White
        if (-not $DoNotOpenPages) { try { Start-Process $pagesUrl | Out-Null } catch {} }
    }
    Log "Receipts: $ReceiptRoot" White
}
catch {
    Log ("FAILED: " + $_.Exception.Message) Red
    throw
}
finally {
    if (Test-Path -LiteralPath $WorkRoot) { Remove-Item -LiteralPath $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
