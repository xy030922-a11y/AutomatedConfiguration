#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Msys2Root = 'C:\msys64',
    [switch]$SkipUpdate,
    [switch]$AddToUserPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$bash = Join-Path $Msys2Root 'usr\bin\bash.exe'
$ucrt64Bin = Join-Path $Msys2Root 'ucrt64\bin'

if (-not (Test-Path -LiteralPath $bash -PathType Leaf)) {
    Write-Host "[ERROR] MSYS2 bash was not found at: $bash" -ForegroundColor Red
    Write-Host 'Install MSYS2 first, or pass its location with -Msys2Root.' -ForegroundColor Yellow
    exit 1
}

$env:CHERE_INVOKING = 'yes'
$env:MSYSTEM = 'UCRT64'

function Invoke-Msys2Command {
    param(
        [Parameter(Mandatory)]
        [string]$Command,

        [Parameter(Mandatory)]
        [string]$Description
    )

    Write-Host ''
    Write-Host ">>> $Description" -ForegroundColor Cyan
    & $bash -lc $Command | Out-Host
    $commandExitCode = $LASTEXITCODE

    if ($commandExitCode -ne 0) {
        throw "$Description failed with exit code $commandExitCode."
    }
}

try {
    if (-not $SkipUpdate) {
        Invoke-Msys2Command `
            -Description 'Updating MSYS2 (pass 1 of 2)' `
            -Command 'pacman --noconfirm -Syu'

        Invoke-Msys2Command `
            -Description 'Updating MSYS2 (pass 2 of 2)' `
            -Command 'pacman --noconfirm -Syu'
    }

    $packages = @(
        'mingw-w64-ucrt-x86_64-toolchain',
        'mingw-w64-ucrt-x86_64-cmake',
        'mingw-w64-ucrt-x86_64-ninja'
    )

    $packageList = $packages -join ' '
    Invoke-Msys2Command `
        -Description 'Installing the UCRT64 C++ toolchain' `
        -Command "pacman --noconfirm --needed -S $packageList"

    Invoke-Msys2Command `
        -Description 'Verifying installed tools' `
        -Command 'gcc --version | head -n 1 && g++ --version | head -n 1 && gdb --version | head -n 1 && cmake --version | head -n 1 && ninja --version'

    if ($AddToUserPath) {
        if (-not (Test-Path -LiteralPath $ucrt64Bin -PathType Container)) {
            throw "UCRT64 bin directory was not found at: $ucrt64Bin"
        }

        $normalizedBin = [IO.Path]::GetFullPath($ucrt64Bin).TrimEnd('\')
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        $pathEntries = @($userPath -split ';' | Where-Object { $_ })
        $alreadyPresent = $pathEntries | Where-Object {
            $_.TrimEnd('\') -eq $normalizedBin
        }

        if (-not $alreadyPresent) {
            $newUserPath = (@($normalizedBin) + $pathEntries) -join ';'
            [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
            Write-Host "Added to the user PATH: $normalizedBin" -ForegroundColor Green
        } else {
            Write-Host "Already in the user PATH: $normalizedBin" -ForegroundColor Yellow
        }
    }

    Write-Host ''
    Write-Host 'MSYS2 UCRT64 C++ toolchain installation completed.' -ForegroundColor Green
    Write-Host "Open the UCRT64 terminal with: $Msys2Root\ucrt64.exe"

    if (-not $AddToUserPath) {
        Write-Host 'Use -AddToUserPath if gcc and g++ must also be available in PowerShell or VS Code.' -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

exit 0
