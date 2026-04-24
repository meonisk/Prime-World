<#
.SYNOPSIS
    First-run bootstrap for Prime-World: creates the runtime junctions the
    prebuilt PW_Game.exe expects.

.DESCRIPTION
    PW_Game.exe was built before the 2026 repo restructure and looks up data
    by the original SVN-era folder names. This script creates the junctions
    that bridge the new layout to those names:

      client/build/Data         -> assets/
      client/build/Localization -> localization/
      client/build/Profiles     -> profiles/
      assets/GameLogic          -> game-logic/
      assets/MiniGames          -> mini-games/
      assets/GFX_Textures       -> gfx-textures/
      assets/Server             -> server-data/
      assets/Dialog             -> dialogs/
      assets/SocialTest         -> social-test/

    It also performs a sanity check: a handful of large binaries used to live
    on Git LFS, and on a fresh clone they may still appear as 133-byte LFS
    pointer stubs if a previous setup left them behind. If so, the script
    points to `python tools/assets/fetch_assets.py --all`, which mirrors all
    heavy binaries from Google Drive (see tools/assets/manifest.json).

    Idempotent: safe to re-run. Refuses to overwrite real directories without
    -Force.

.PARAMETER Check
    Report state but do not modify anything. Exit 0 if everything is set up,
    1 if anything is missing or wrong.

.PARAMETER Force
    Recreate junctions even if they already point somewhere else.

.EXAMPLE
    pwsh tools/setup/setup.ps1
    Create junctions and warn about any missing large binaries.

.EXAMPLE
    pwsh tools/setup/setup.ps1 -Check
    Verify state. Exit code 0 = ready to launch, 1 = something needs fixing.
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

# ---------- helpers ----------

function Write-Step($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "    OK  $msg" -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "    !   $msg" -ForegroundColor Yellow }
function Write-Fail($msg)  { Write-Host "    X   $msg" -ForegroundColor Red }

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Test-Junction($path) {
    if (-not (Test-Path -LiteralPath $path)) { return $false }
    $item = Get-Item -Force -LiteralPath $path
    return [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Get-JunctionTarget($path) {
    $item = Get-Item -Force -LiteralPath $path
    return $item.Target | Select-Object -First 1
}

function Test-LfsPointer($path) {
    if (-not (Test-Path -LiteralPath $path)) { return $true }
    $len = (Get-Item -LiteralPath $path).Length
    if ($len -gt 1024) { return $false }
    $head = Get-Content -LiteralPath $path -TotalCount 1 -ErrorAction SilentlyContinue
    return $head -like 'version https://git-lfs.github.com/spec/v1*'
}

# ---------- phase 1: validate ----------

function Invoke-Validate($repoRoot) {
    Write-Step 'Validating environment'

    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot '.git'))) {
        throw "Not a git repository: $repoRoot"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'client\build\Bin\PW_Game.exe'))) {
        throw "client/build/Bin/PW_Game.exe not found. Are you in the Prime-World repo root?"
    }
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        throw "PowerShell 5.1+ required (detected $($PSVersionTable.PSVersion))."
    }
    if (-not (Get-Command 'git' -ErrorAction SilentlyContinue)) {
        throw "git is not in PATH. Install it and retry."
    }
    Write-Ok "repo at $repoRoot"
    Write-Ok "PowerShell $($PSVersionTable.PSVersion), git present"
}

# ---------- phase 2: junctions ----------

# Relative paths are resolved from repo root. Target is relative to the parent
# of the link (i.e. where mklink /J would be invoked).
$JunctionSpec = @(
    @{ Link = 'client\build\Data';         Target = '..\..\assets' },
    @{ Link = 'client\build\Localization'; Target = '..\..\localization' },
    @{ Link = 'client\build\Profiles';     Target = '..\..\profiles' },
    @{ Link = 'assets\GameLogic';          Target = 'game-logic' },
    @{ Link = 'assets\MiniGames';          Target = 'mini-games' },
    @{ Link = 'assets\GFX_Textures';       Target = 'gfx-textures' },
    @{ Link = 'assets\Server';             Target = 'server-data' },
    @{ Link = 'assets\Dialog';             Target = 'dialogs' },
    @{ Link = 'assets\SocialTest';         Target = 'social-test' }
)

function Resolve-ExpectedTarget($repoRoot, $linkRel, $targetRel) {
    $parent = Split-Path -Parent (Join-Path $repoRoot $linkRel)
    return (Resolve-Path (Join-Path $parent $targetRel) -ErrorAction SilentlyContinue).Path
}

function Invoke-Junctions($repoRoot, [bool]$CheckOnly, [bool]$ForceRecreate) {
    Write-Step 'Runtime junctions'
    $missing = 0
    foreach ($j in $JunctionSpec) {
        $linkAbs     = Join-Path $repoRoot $j.Link
        $expectedAbs = Resolve-ExpectedTarget $repoRoot $j.Link $j.Target
        if (-not $expectedAbs) {
            Write-Warn2 "target does not exist: $($j.Link) -> $($j.Target)"
            $missing++
            continue
        }

        if (Test-Path -LiteralPath $linkAbs) {
            if (Test-Junction $linkAbs) {
                $currentTarget = Get-JunctionTarget $linkAbs
                if ($currentTarget -ieq $expectedAbs) {
                    Write-Ok "$($j.Link) -> $($j.Target)"
                    continue
                }
                if ($CheckOnly) {
                    Write-Fail "$($j.Link) points to $currentTarget (expected $expectedAbs)"
                    $missing++; continue
                }
                if (-not $ForceRecreate) {
                    Write-Fail "$($j.Link) points to $currentTarget (expected $expectedAbs). Re-run with -Force to fix."
                    $missing++; continue
                }
                cmd.exe /c "rmdir `"$linkAbs`"" | Out-Null
            } else {
                Write-Fail "$($j.Link) exists as a real directory. Refusing to delete."
                $missing++; continue
            }
        }

        if ($CheckOnly) {
            Write-Fail "$($j.Link) missing (should junction to $($j.Target))"
            $missing++; continue
        }

        cmd.exe /c "mklink /J `"$linkAbs`" `"$expectedAbs`"" | Out-Null
        if ($LASTEXITCODE -ne 0 -or -not (Test-Junction $linkAbs)) {
            Write-Fail "failed to create $($j.Link)"
            $missing++; continue
        }
        Write-Ok "created $($j.Link) -> $($j.Target)"
    }
    return $missing
}

# ---------- phase 3: warn about leftover LFS pointer stubs ----------

# These 11 files used to be tracked via Git LFS. They are now distributed via
# the Google Drive zip archives in tools/assets/manifest.json. On a fresh
# clone they should arrive as real binaries via fetch_assets.py.
# If they appear here as 133-byte stubs, an old git-lfs filter checked out
# the pointer text instead of the real content and the user needs to fetch
# the archives.
$ExpectedHeavyBinaries = @(
    'assets/audio/Asks_EN.fsb',
    'assets/audio/Asks_RU.fsb',
    'assets/audio/Music.fsb',
    'assets/test/Backs/_Breawer.dds',
    'client/flash-ui/library.fla',
    'client/flash-ui/main.fla',
    'vendor/CEF/libcef.dll',
    'vendor/Maya/2010/mkl_core.lib',
    'vendor/Maya/2011/mkl_core.lib',
    'vendor/Tamarin/Debug/Tamarin.lib',
    'vendor/Tamarin/Release/Tamarin.lib'
)

function Invoke-HeavyBinaryCheck($repoRoot) {
    Write-Step 'Checking heavy binaries (formerly LFS)'
    $stubs = @()
    foreach ($rel in $ExpectedHeavyBinaries) {
        $abs = Join-Path $repoRoot ($rel -replace '/', '\')
        if (Test-LfsPointer $abs) { $stubs += $rel }
    }

    if ($stubs.Count -eq 0) {
        Write-Ok 'all heavy binaries present'
        return 0
    }

    foreach ($s in $stubs) { Write-Fail "$s is a 133-byte LFS pointer stub" }
    Write-Host ''
    Write-Warn2 'These files are no longer distributed via Git LFS.'
    Write-Warn2 'Fetch them from Google Drive:'
    Write-Host '    python tools/assets/fetch_assets.py --all'
    Write-Host '    (or: --tag=assets --tag=vendor --tag=misc for the relevant subset)'
    return $stubs.Count
}

# ---------- main ----------

$repoRoot = Get-RepoRoot
Write-Host ''
Write-Host 'Prime-World setup' -ForegroundColor White
Write-Host ('-' * 60)

Invoke-Validate $repoRoot

$jMissing = Invoke-Junctions $repoRoot $Check $Force
$bMissing = Invoke-HeavyBinaryCheck $repoRoot

Write-Host ''
Write-Host ('-' * 60)
$total = $jMissing + $bMissing
if ($Check) {
    if ($total -eq 0) {
        Write-Host 'CHECK OK: setup is complete.' -ForegroundColor Green
        exit 0
    }
    Write-Host "CHECK FAILED: $total issue(s). Re-run without -Check (and/or run fetch_assets.py) to fix." -ForegroundColor Red
    exit 1
}
if ($total -eq 0) {
    Write-Host 'Setup complete. Launch client/build/Bin/PW_Game.exe.' -ForegroundColor Green
    exit 0
}
Write-Host "Setup finished with $total unresolved issue(s)." -ForegroundColor Red
exit 1
