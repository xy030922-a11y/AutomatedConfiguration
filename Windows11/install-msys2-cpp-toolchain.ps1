# 本脚本在已安装的 MSYS2 中更新系统、安装 UCRT64 C++ 工具链并验证关键命令；它不会负责安装 MSYS2 本体。
# This script updates an existing MSYS2 installation, installs the UCRT64 C++ toolchain, and verifies key commands; it does not install MSYS2 itself.
# pacman 会修改 MSYS2 根目录；若该目录受保护，请使用具备相应写权限的 PowerShell。更新期间不要关闭终端。
# pacman modifies the MSYS2 root; use a PowerShell session with suitable write permission if that directory is protected, and do not close the terminal during updates.
# --needed 使工具链包安装可重复执行，但完整系统更新仍可能要求重启 MSYS2 进程后再运行第二阶段。
# --needed makes toolchain package installation repeatable, while a full system update may still require restarting MSYS2 processes before a later stage.
#Requires -Version 5.1
[CmdletBinding()]
param(
    # MSYS2 安装根目录；脚本据此解析 bash.exe、UCRT64 bin 和终端启动器路径。
    # MSYS2 installation root; the script derives bash.exe, UCRT64 bin, and terminal-launcher paths from it.
    [string]$Msys2Root = 'C:\msys64',

    # 跳过两轮 pacman -Syu，仅安装/验证工具链；仅在已确认 MSYS2 系统包为最新时使用。
    # Skip both pacman -Syu passes and only install/verify the toolchain; use this only when MSYS2 system packages are known to be current.
    [switch]$SkipUpdate,

    # 将 UCRT64\bin 持久化到当前用户 PATH 的最前端，使新开的 PowerShell/VS Code 能直接找到工具。
    # Persist UCRT64\bin at the front of the current user's PATH so newly opened PowerShell/VS Code sessions can find the tools directly.
    [switch]$AddToUserPath
)

# 严格模式捕获未初始化变量等脚本错误；Stop 让可终止错误进入统一的 catch 处理。
# Strict mode catches script errors such as uninitialized variables; Stop routes terminating errors into the common catch handler.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# 统一从根目录构造路径，避免在后续命令中重复拼接或依赖当前工作目录。
# Derive paths once from the root to avoid repeated concatenation and dependence on the current working directory.
$bash = Join-Path $Msys2Root 'usr\bin\bash.exe'
$ucrt64Bin = Join-Path $Msys2Root 'ucrt64\bin'

# bash.exe 是执行所有 pacman 和验证命令的硬性前置条件；只接受真实文件，不接受同名目录。
# bash.exe is a hard prerequisite for every pacman and verification command; require an actual file rather than a same-named directory.
if (-not (Test-Path -LiteralPath $bash -PathType Leaf)) {
    Write-Host "[ERROR] MSYS2 bash was not found at: $bash" -ForegroundColor Red
    Write-Host 'Install MSYS2 first, or pass its location with -Msys2Root.' -ForegroundColor Yellow
    # 退出码 1 表示前置条件失败，任何更新或安装命令都尚未执行。
    # Exit code 1 signals a prerequisite failure; no update or installation command has run.
    exit 1
}

# CHERE_INVOKING=yes 要求 MSYS2 shell 保留调用方当前目录；变量只影响本脚本进程及其子进程。
# CHERE_INVOKING=yes asks the MSYS2 shell to retain the caller's current directory; the variable affects only this process and its children.
$env:CHERE_INVOKING = 'yes'
# MSYSTEM=UCRT64 选择 UCRT64 子系统，使 shell 的 PATH 和包环境与所安装工具链一致。
# MSYSTEM=UCRT64 selects the UCRT64 subsystem so the shell PATH and package environment match the installed toolchain.
$env:MSYSTEM = 'UCRT64'

# 在同一个受控入口中运行 MSYS2 shell 命令、显示原始输出并把原生退出码转换为 PowerShell 异常。
# Run MSYS2 shell commands through one controlled entry point, show native output, and convert native exit codes into PowerShell exceptions.
function Invoke-Msys2Command {
    param(
        # 传给 bash -lc 的完整 shell 命令；本脚本只使用内部构造的固定命令，不接受交互式用户输入拼接。
        # Complete shell command passed to bash -lc; this script uses only internally constructed commands and does not concatenate interactive user input.
        [Parameter(Mandatory)]
        [string]$Command,

        # 面向控制台的步骤描述，同时用于失败异常消息，便于定位具体阶段。
        # Console-facing step description, also reused in failure exceptions to identify the exact stage.
        [Parameter(Mandatory)]
        [string]$Description
    )

    Write-Host ''
    Write-Host ">>> $Description" -ForegroundColor Cyan
    # -l 创建登录 shell，-c 执行指定命令；Out-Host 保留 pacman 和工具版本的实时输出。
    # -l creates a login shell and -c executes the supplied command; Out-Host preserves live pacman and tool-version output.
    & $bash -lc $Command | Out-Host
    # 立即保存 bash 退出码，避免后续 PowerShell 命令覆盖全局 $LASTEXITCODE。
    # Capture the bash exit code immediately so later PowerShell commands cannot overwrite global $LASTEXITCODE.
    $commandExitCode = $LASTEXITCODE

    # 非零状态转为异常，由外层 catch 统一输出错误并把整个脚本标记为失败。
    # Convert a nonzero status to an exception so the outer catch reports it consistently and marks the whole script as failed.
    if ($commandExitCode -ne 0) {
        throw "$Description failed with exit code $commandExitCode."
    }
}

# 所有可执行阶段共用一个 try/catch，确保 PowerShell 错误和显式 throw 都产生一致的退出码。
# Wrap all executable stages in one try/catch so PowerShell errors and explicit throws produce a consistent exit code.
try {
    # 默认执行两轮完整更新，以覆盖核心组件升级后第二轮仍待更新的包；-SkipUpdate 会跳过整个分支。
    # Run two full update passes by default to cover packages still pending after core-component upgrades; -SkipUpdate bypasses this entire branch.
    # --noconfirm 自动回答 pacman 提示，适合批处理但不会提供逐项确认机会；运行前应确保无其他 pacman 进程占用数据库。
    # --noconfirm answers pacman prompts automatically, which suits batch use but removes per-package confirmation; ensure no other pacman process holds the database first.
    if (-not $SkipUpdate) {
        Invoke-Msys2Command `
            -Description 'Updating MSYS2 (pass 1 of 2)' `
            -Command 'pacman --noconfirm -Syu'

        Invoke-Msys2Command `
            -Description 'Updating MSYS2 (pass 2 of 2)' `
            -Command 'pacman --noconfirm -Syu'
    }

    # 元包提供 UCRT64 GCC/G++/GDB 等完整工具链，并显式补充 CMake 与 Ninja 构建工具。
    # The metapackage supplies the full UCRT64 GCC/G++/GDB toolchain, with CMake and Ninja added explicitly as build tools.
    $packages = @(
        'mingw-w64-ucrt-x86_64-toolchain',
        'mingw-w64-ucrt-x86_64-cmake',
        'mingw-w64-ucrt-x86_64-ninja'
    )

    # pacman 在 bash 中需要空格分隔的包名；包名均来自上面的静态内部清单。
    # pacman expects space-separated package names in bash; every name comes from the static internal manifest above.
    $packageList = $packages -join ' '
    # --needed 跳过已为最新版本的目标包，使重复运行不会无意义地重新安装它们。
    # --needed skips target packages already at the current version, avoiding unnecessary reinstalls on repeated runs.
    Invoke-Msys2Command `
        -Description 'Installing the UCRT64 C++ toolchain' `
        -Command "pacman --noconfirm --needed -S $packageList"

    # 通过逐个运行版本命令验证 PATH 解析与可执行性；&& 会在首个失败处停止并让 bash 返回非零状态。
    # Verify PATH resolution and executability by running each version command; && stops at the first failure and makes bash return a nonzero status.
    Invoke-Msys2Command `
        -Description 'Verifying installed tools' `
        -Command 'gcc --version | head -n 1 && g++ --version | head -n 1 && gdb --version | head -n 1 && cmake --version | head -n 1 && ninja --version'

    # PATH 修改是显式可选操作；不传 -AddToUserPath 时，工具仅保证在 MSYS2 UCRT64 shell 中可用。
    # PATH modification is explicitly opt-in; without -AddToUserPath, tools are guaranteed only inside the MSYS2 UCRT64 shell.
    if ($AddToUserPath) {
        # 写入 PATH 前再次验证目标目录存在，避免持久化一个尚未创建或拼错的路径。
        # Validate the target directory again before writing PATH to avoid persisting a missing or mistyped location.
        if (-not (Test-Path -LiteralPath $ucrt64Bin -PathType Container)) {
            throw "UCRT64 bin directory was not found at: $ucrt64Bin"
        }

        # 规范为绝对路径并去掉尾随反斜杠，以便与用户 PATH 中不同书写形式进行稳定比较。
        # Normalize to an absolute path and trim the trailing backslash for stable comparison with alternate spellings in the user PATH.
        $normalizedBin = [IO.Path]::GetFullPath($ucrt64Bin).TrimEnd('\')
        # 只读取当前用户作用域，不改写系统 PATH；空条目在比较和重组时被移除。
        # Read only the current-user scope and do not rewrite machine PATH; empty entries are removed during comparison and reconstruction.
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        $pathEntries = @($userPath -split ';' | Where-Object { $_ })
        # 通过去除尾随反斜杠进行精确文本匹配，避免相同路径被重复追加。
        # Compare exact path text after trimming trailing backslashes to avoid appending the same path twice.
        $alreadyPresent = $pathEntries | Where-Object {
            $_.TrimEnd('\') -eq $normalizedBin
        }

        if (-not $alreadyPresent) {
            # 将 UCRT64 bin 放在最前面会优先解析其中的同名程序；更改只对之后新启动的进程自动生效。
            # Prepending UCRT64 bin gives its same-named executables resolution priority; the change is automatically visible only to newly started processes.
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

    # 未选择 PATH 持久化时给出提示，但不把该选择视为安装失败。
    # When PATH persistence was not selected, show guidance without treating that choice as an installation failure.
    if (-not $AddToUserPath) {
        Write-Host 'Use -AddToUserPath if gcc and g++ must also be available in PowerShell or VS Code.' -ForegroundColor Yellow
    }
} catch {
    # 捕获阶段错误并返回 1；异常消息保留失败步骤及其原生命令退出码（若可用）。
    # Catch stage errors and return 1; the exception message retains the failed step and its native-command exit code when available.
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 只有全部更新、安装、验证及可选 PATH 操作完成后才显式返回成功退出码 0。
# Explicitly return success exit code 0 only after all updates, installation, verification, and optional PATH work have completed.
exit 0
