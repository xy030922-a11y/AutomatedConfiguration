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
        return $true
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
        return $true
    }

    Write-Host "[FAIL] $($Package.Name), exit code: $LASTEXITCODE" -ForegroundColor Red
    return $false
}

Test-Winget

$packages = @(
    @{ Name = '360 Zip'; Id = '360.360Zip'; Source = 'winget' },
    @{ Name = 'CMake'; Id = 'Kitware.CMake'; Source = 'winget' },
    @{ Name = 'DataGrip'; Id = 'JetBrains.DataGrip'; Source = 'winget' },
    @{ Name = 'DBeaver Community'; Id = 'DBeaver.DBeaver.Community'; Source = 'winget' },
    @{ Name = 'Everything'; Id = 'voidtools.Everything'; Source = 'winget' },
    @{ Name = 'FlClash'; Id = 'chen08209.FlClash'; Source = 'winget' },
    @{ Name = 'Git'; Id = 'Git.Git'; Source = 'winget' },
    @{ Name = 'Google Chrome'; Id = 'Google.Chrome'; Source = 'winget' },
    @{ Name = 'iVCam'; Id = 'e2eSoft.iVCam'; Source = 'winget' },
    @{ Name = 'Visual Studio Code'; Id = 'Microsoft.VisualStudioCode'; Source = 'winget' },
    @{ Name = 'Visual Studio 2022 Community'; Id = 'Microsoft.VisualStudio.2022.Community'; Source = 'winget'; NoSilent = $true },
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

foreach ($package in $packages) {
    $ok = Install-WingetPackage -Package $package
    if (-not $ok) {
        $failed.Add("$($package.Name) [$($package.Id)]")
    }
}

Write-Host ""
Write-Host "========== Install result ==========" -ForegroundColor Cyan

if ($failed.Count -eq 0) {
    Write-Host "All winget packages finished successfully." -ForegroundColor Green
} else {
    Write-Host "The following packages failed. Check them one by one:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    exit 1
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
