#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Silent,
    [switch]$SkipStore
)

$ErrorActionPreference = 'Continue'

function Test-Winget {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Error 'winget was not found. Install or update App Installer from Microsoft Store first.'
        exit 1
    }
}

function Install-WingetPackage {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Package
    )

    if ($SkipStore -and $Package.Source -eq 'msstore') {
        Write-Host "[SKIP] $($Package.Name) uses the msstore source and was skipped by -SkipStore." -ForegroundColor Yellow
        return 'Skipped'
    }

    $args = @(
        'install',
        '--id', $Package.Id,
        '--exact',
        '--source', $Package.Source,
        '--accept-package-agreements',
        '--accept-source-agreements'
    )

    if ($Silent -and -not $Package.NoSilent) {
        $args += '--silent'
    }

    Write-Host ""
    Write-Host ">>> Installing $($Package.Name) [$($Package.Id)]" -ForegroundColor Cyan
    & winget @args | Out-Host

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $($Package.Name)" -ForegroundColor Green
        return 'Succeeded'
    }

    Write-Host "[FAIL] $($Package.Name), exit code: $LASTEXITCODE" -ForegroundColor Red
    return 'Failed'
}

Test-Winget

$packages = @(
    @{ Name = '360 Zip'; Id = '360.360Zip'; Source = 'winget' },
    @{ Name = 'CMake'; Id = 'Kitware.CMake'; Source = 'winget' },
    @{ Name = 'DataGrip'; Id = 'JetBrains.DataGrip'; Source = 'winget' },
    @{ Name = 'DBeaver Community'; Id = 'DBeaver.DBeaver.Community'; Source = 'winget' },
    @{ Name = 'Everything'; Id = 'voidtools.Everything'; Source = 'winget' },
    @{ Name = 'Geek Uninstaller'; Id = 'GeekUninstaller.GeekUninstaller'; Source = 'winget' },
    @{ Name = 'FlClash'; Id = 'chen08209.FlClash'; Source = 'winget' },
    @{ Name = 'Git'; Id = 'Git.Git'; Source = 'winget' },
    @{ Name = 'Google Chrome'; Id = 'Google.Chrome'; Source = 'winget' },
    @{ Name = 'iVCam'; Id = 'e2eSoft.iVCam'; Source = 'winget' },
    @{ Name = 'Visual Studio Code'; Id = 'Microsoft.VisualStudioCode'; Source = 'winget' },
    @{ Name = 'Visual Studio Community'; Id = 'Microsoft.VisualStudio.Community'; Source = 'winget'; NoSilent = $true },
    @{ Name = 'MSYS2'; Id = 'MSYS2.MSYS2'; Source = 'winget' },
    @{ Name = 'PotPlayer'; Id = 'Daum.PotPlayer'; Source = 'winget' },
    @{ Name = 'QQ NT'; Id = 'Tencent.QQ.NT'; Source = 'winget' },
    @{ Name = 'QQ Music'; Id = 'Tencent.QQMusic'; Source = 'winget' },
    @{ Name = 'Steam'; Id = 'Valve.Steam'; Source = 'winget' },
    @{ Name = 'VMware Workstation Pro'; Id = 'VMware.WorkstationPro'; Source = 'winget' },
    @{ Name = 'WPS Office'; Id = 'Kingsoft.WPSOffice.CN'; Source = 'winget' },
    @{ Name = 'iQIYI'; Id = 'iQIYI.iQIYI'; Source = 'winget' },
    @{ Name = 'Youku'; Id = 'Youku.Youku'; Source = 'winget' },
    @{ Name = 'Tencent Video'; Id = 'Tencent.TencentVideo'; Source = 'winget' },
    @{ Name = 'Bilibili'; Id = 'Bilibili.Bilibili'; Source = 'winget' },
    @{ Name = 'Bilibili Livehime'; Id = 'Bilibili.Livehime'; Source = 'winget' },
    @{ Name = 'Feishu'; Id = 'ByteDance.Feishu'; Source = 'winget' },
    @{ Name = 'Battle.net'; Id = 'Blizzard.BattleNet'; Source = 'winget'; NoSilent = $true },
    @{ Name = 'Huorong Security'; Id = 'XPDNH1FMW7NB40'; Source = 'msstore' },
    @{ Name = 'AOMEI Partition Assistant'; Id = 'AOMEI.PartitionAssistant'; Source = 'winget' },
    @{ Name = 'Tuba Toolbox WinUI3'; Id = 'luolangaga.tubatools'; Source = 'winget' },
    @{ Name = 'WeChat'; Id = 'Tencent.WeChat'; Source = 'winget' },
    @{ Name = 'Sunlogin Client'; Id = 'Oray.SunloginClient'; Source = 'winget' },
    @{ Name = 'Thunder'; Id = 'Thunder.Thunder'; Source = 'winget' }
)

$manualPackages = @(
    @{ Name = 'AK Accelerator'; Reason = 'No stable winget package id was confirmed. Run: winget search "AK"' }
)

$failed = New-Object System.Collections.Generic.List[string]
$skipped = New-Object System.Collections.Generic.List[string]

$wslDistribution = 'Ubuntu-24.04'
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue

if (-not $wsl) {
    Write-Host "[FAIL] WSL 2, wsl.exe was not found." -ForegroundColor Red
    $failed.Add("WSL 2 [$wslDistribution]")
} else {
    $installedWslDistributions = @(
        & $wsl.Source --list --quiet 2>$null |
            ForEach-Object { ($_ -replace "`0", '').Trim() } |
            Where-Object { $_ }
    )

    if ($installedWslDistributions -contains $wslDistribution) {
        Write-Host "[SKIP] WSL 2 [$wslDistribution] is already installed." -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host ">>> Installing WSL 2 [$wslDistribution]" -ForegroundColor Cyan
        & $wsl.Source --install -d $wslDistribution --no-launch | Out-Host
        $wslExitCode = $LASTEXITCODE

        if ($wslExitCode -in @(0, 3010)) {
            Write-Host "[OK] WSL 2 [$wslDistribution]" -ForegroundColor Green
            Write-Host "[INFO] Restart Windows before launching Ubuntu for the first time." -ForegroundColor Yellow
        } else {
            Write-Host "[FAIL] WSL 2 [$wslDistribution], exit code: $wslExitCode" -ForegroundColor Red
            $failed.Add("WSL 2 [$wslDistribution]")
        }
    }
}

foreach ($package in $packages) {
    $installationResult = Install-WingetPackage -Package $package
    if ($installationResult -eq 'Skipped') {
        $skipped.Add("$($package.Name) [$($package.Id)]")
    } elseif ($installationResult -eq 'Failed') {
        $failed.Add("$($package.Name) [$($package.Id)]")
    }
}

Write-Host ""
Write-Host "========== Install result ==========" -ForegroundColor Cyan

if ($failed.Count -eq 0) {
    Write-Host "All attempted installations finished successfully." -ForegroundColor Green
} else {
    Write-Host "The following installations failed. Check them one by one:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
}

if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host "Skipped by request:" -ForegroundColor Yellow
    $skipped | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Manual check required:" -ForegroundColor Yellow
$manualPackages | ForEach-Object {
    Write-Host " - $($_.Name): $($_.Reason)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Examples:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\install-winget-apps.ps1"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\install-winget-apps.ps1 -Silent"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\install-winget-apps.ps1 -SkipStore"

if ($failed.Count -gt 0) {
    exit 1
}
