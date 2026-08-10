# 本脚本通过 winget 批量安装应用，并单独配置 WSL 2/Ubuntu；仅在已确认接受这些系统级更改时运行。
# This script installs applications in bulk through winget and configures WSL 2/Ubuntu separately; run it only after accepting these system-level changes.
# 建议从管理员 PowerShell 启动：某些安装程序、WSL 可选功能和机器级写入会触发 UAC 或需要提升权限。
# An elevated PowerShell session is recommended because some installers, WSL optional features, and machine-wide writes may require elevation or trigger UAC.
# winget 对已安装包通常会跳过或升级，但各安装器行为不同；重新运行前仍应检查上一次失败或待重启状态。
# winget usually skips or upgrades installed packages, but installer behavior varies; check previous failures and pending-restart state before rerunning.
#Requires -Version 5.1
[CmdletBinding()]
param(
    # 请求支持静默安装的包使用 winget --silent；标记为 NoSilent 的包仍保持交互式安装。
    # Requests winget --silent for packages that support it; packages marked NoSilent remain interactive.
    [switch]$Silent,

    # 跳过 Microsoft Store 源中的包；跳过项会单独统计，不会被当作成功安装。
    # Skips packages from the Microsoft Store source; skipped entries are tracked separately and are not counted as successful installs.
    [switch]$SkipStore
)

# 单个包失败后继续处理后续包，最终再用汇总和进程退出码报告整体结果。
# Continue processing later packages after an individual failure, then report the aggregate result through the summary and process exit code.
$ErrorActionPreference = 'Continue'

# 在任何安装开始前确认 winget 可调用，避免产生一串相同的“命令不存在”错误。
# Confirm that winget is callable before any installation starts, avoiding a cascade of identical command-not-found errors.
function Test-Winget {
    # SilentlyContinue 仅抑制探测阶段的错误；未找到命令时由下面的分支给出明确错误并返回 1。
    # SilentlyContinue suppresses only discovery-time errors; the branch below emits a clear error and returns 1 when the command is absent.
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Error 'winget was not found. Install or update App Installer from Microsoft Store first.'
        # 退出码 1 表示前置条件失败，调用脚本的终端或自动化工具可据此判定未执行安装。
        # Exit code 1 signals a prerequisite failure so the calling shell or automation can detect that installation did not run.
        exit 1
    }
}

# 安装一个清单项并返回 Succeeded、Skipped 或 Failed；调用方负责累计状态，而不是在此函数中终止整个批次。
# Install one manifest entry and return Succeeded, Skipped, or Failed; the caller aggregates status instead of terminating the whole batch here.
function Install-WingetPackage {
    param(
        # 每个哈希表至少提供 Name、Id、Source；可选 NoSilent 用于必须交互的安装器。
        # Each hashtable supplies at least Name, Id, and Source; optional NoSilent identifies installers that must remain interactive.
        [Parameter(Mandatory)]
        [hashtable]$Package
    )

    # -SkipStore 只影响 Source=msstore 的条目；在调用 winget 前返回可区分的 Skipped 状态。
    # -SkipStore affects only entries whose Source is msstore; return a distinct Skipped state before invoking winget.
    if ($SkipStore -and $Package.Source -eq 'msstore') {
        Write-Host "[SKIP] $($Package.Name) uses the msstore source and was skipped by -SkipStore." -ForegroundColor Yellow
        return 'Skipped'
    }

    # 使用精确包 ID 和固定源，避免同名搜索匹配到其他发布者；同时预先接受源与包协议以减少批处理阻塞。
    # Use an exact package ID and pinned source to avoid matching another publisher by name; pre-accept source and package agreements to reduce batch blocking.
    $args = @(
        'install',
        '--id', $Package.Id,
        '--exact',
        '--source', $Package.Source,
        '--accept-package-agreements',
        '--accept-source-agreements'
    )

    # 只有请求 -Silent 且包未声明 NoSilent 时才附加 --silent；该标志仍取决于安装器自身是否正确实现静默模式。
    # Append --silent only when -Silent was requested and the package does not declare NoSilent; actual silence still depends on installer support.
    if ($Silent -and -not $Package.NoSilent) {
        $args += '--silent'
    }

    Write-Host ""
    Write-Host ">>> Installing $($Package.Name) [$($Package.Id)]" -ForegroundColor Cyan
    # & 调用原生命令，@args 逐项传参以保留参数边界；Out-Host 让 winget 的实时输出继续显示给用户。
    # & invokes the native command, @args preserves argument boundaries, and Out-Host keeps winget's live output visible to the user.
    & winget @args | Out-Host

    # $LASTEXITCODE 是刚执行的 winget 进程退出码；0 为成功，其他值统一记为失败并留待最终汇总。
    # $LASTEXITCODE is the exit code from the winget process just run; zero is success, while every other value is recorded for the final failure summary.
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $($Package.Name)" -ForegroundColor Green
        return 'Succeeded'
    }

    Write-Host "[FAIL] $($Package.Name), exit code: $LASTEXITCODE" -ForegroundColor Red
    return 'Failed'
}

# 前置条件通过后才构造并处理安装清单。
# Build and process the installation manifest only after the prerequisite check succeeds.
Test-Winget

# 静态清单固定显示名称、winget 包 ID 和来源；包 ID 或来源可能随仓库更新而失效，应定期重新验证。
# The static manifest pins display name, winget package ID, and source; IDs or sources can become stale as repositories change and should be revalidated periodically.
# NoSilent=$true 表示即使传入 -Silent 也不附加 --silent，以保留该安装器所需的用户交互。
# NoSilent=$true prevents --silent from being added even when -Silent is passed, preserving interaction required by that installer.
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
    @{ Name = 'OBS Studio'; Id = 'OBSProject.OBSStudio'; Source = 'winget' },
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

# 无可靠 winget ID 的软件不会自动安装；它们仅在批次结束时作为人工检查项显示。
# Software without a reliable winget ID is not installed automatically; it is displayed only as a manual-review item after the batch.
$manualPackages = @(
    @{ Name = 'AK Accelerator'; Reason = 'No stable winget package id was confirmed. Run: winget search "AK"' }
)

# 使用强类型列表分别累计失败和按请求跳过的项目，防止跳过项被误计为成功或失败。
# Use strongly typed lists to aggregate failures and requested skips separately, preventing skipped entries from being counted as successes or failures.
$failed = New-Object System.Collections.Generic.List[string]
$skipped = New-Object System.Collections.Generic.List[string]

# 发行版名称同时用于存在性检测与 wsl --install；这里的检测只确认名称存在，并不验证其 VERSION 列是否确为 WSL 2。
# The distribution name is used for both presence detection and wsl --install; this check confirms only the name and does not verify that its VERSION column is actually WSL 2.
$wslDistribution = 'Ubuntu-24.04'
# 通过 Get-Command 获取解析后的 wsl.exe 路径，后续使用 Source 可避免别名或同名函数干扰。
# Resolve wsl.exe through Get-Command so later use of Source avoids interference from aliases or same-named functions.
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue

# 缺少 wsl.exe 时不立即终止，以便 winget 应用仍可继续安装；该项加入失败清单后最终返回失败退出码。
# When wsl.exe is absent, do not terminate immediately so winget applications can still be processed; record the item and return a failing exit code at the end.
if (-not $wsl) {
    Write-Host "[FAIL] WSL 2, wsl.exe was not found." -ForegroundColor Red
    $failed.Add("WSL 2 [$wslDistribution]")
} else {
    # wsl --list --quiet 仅获取发行版名称；移除潜在 NUL 字符并清理空白/空行后再做精确包含判断。
    # wsl --list --quiet retrieves distribution names only; remove possible NUL characters and trim whitespace/blank lines before exact containment testing.
    # 2>$null 只隐藏探测命令的标准错误；后续安装命令的输出仍会正常展示。
    # 2>$null hides only standard error from this discovery command; output from the later installation command remains visible.
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
        # wsl --install 可能启用 Windows 可选功能并要求管理员权限；--no-launch 延迟首次启动和 Linux 用户创建。
        # wsl --install may enable Windows optional features and require elevation; --no-launch postpones first launch and Linux-user creation.
        & $wsl.Source --install -d $wslDistribution --no-launch | Out-Host
        # 立即保存原生命令退出码，避免后续 PowerShell 命令覆盖 $LASTEXITCODE。
        # Save the native exit code immediately so later PowerShell commands cannot overwrite $LASTEXITCODE.
        $wslExitCode = $LASTEXITCODE

        # 0 表示完成，3010 表示成功但需要重启；两者均视为安装成功，并明确提示首次启动前重启 Windows。
        # Zero means completed, while 3010 means successful with restart required; both count as success and prompt for a Windows restart before first launch.
        if ($wslExitCode -in @(0, 3010)) {
            Write-Host "[OK] WSL 2 [$wslDistribution]" -ForegroundColor Green
            Write-Host "[INFO] Restart Windows before launching Ubuntu for the first time." -ForegroundColor Yellow
        } else {
            Write-Host "[FAIL] WSL 2 [$wslDistribution], exit code: $wslExitCode" -ForegroundColor Red
            $failed.Add("WSL 2 [$wslDistribution]")
        }
    }
}

# 顺序处理清单，确保控制台输出与清单顺序一致；单项失败不会阻止后续包尝试安装。
# Process the manifest sequentially so console output follows manifest order; one failure does not prevent later package attempts.
foreach ($package in $packages) {
    $installationResult = Install-WingetPackage -Package $package
    # 只累计需要在最终报告中展示的 Skipped 和 Failed；Succeeded 无需额外存储。
    # Aggregate only Skipped and Failed for the final report; Succeeded requires no additional storage.
    if ($installationResult -eq 'Skipped') {
        $skipped.Add("$($package.Name) [$($package.Id)]")
    } elseif ($installationResult -eq 'Failed') {
        $failed.Add("$($package.Name) [$($package.Id)]")
    }
}

Write-Host ""
Write-Host "========== Install result ==========" -ForegroundColor Cyan

# “全部成功”仅描述实际尝试的安装；按 -SkipStore 跳过的项目在下一节独立列出。
# “All successful” describes only attempted installations; items skipped through -SkipStore are listed separately below.
if ($failed.Count -eq 0) {
    Write-Host "All attempted installations finished successfully." -ForegroundColor Green
} else {
    Write-Host "The following installations failed. Check them one by one:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
}

# 跳过清单仅在非空时输出，既保留可审计性，也不把用户主动跳过误报为错误。
# Print the skipped list only when nonempty, preserving auditability without reporting intentional skips as errors.
if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host "Skipped by request:" -ForegroundColor Yellow
    $skipped | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}

# 人工检查提示必须先于最终失败退出执行，因此即使自动安装存在失败也始终可见。
# Manual-review guidance must run before the final failing exit so it remains visible even when automated installations fail.
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

# 任一 WSL 或 winget 安装失败时返回 1；没有失败时脚本自然结束并向调用方表示成功。
# Return 1 when any WSL or winget installation failed; with no failures, the script ends naturally and reports success to its caller.
if ($failed.Count -gt 0) {
    exit 1
}
