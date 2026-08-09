# 已知问题 / Known Issues

> 审查日期：2026-08-09  
> Review date: 2026-08-09

本文记录 `AutomatedConfiguration` 仓库中**仍未修复**的问题、潜在风险和可移植性限制。代码中的注释只解释行为，不代表相关风险已经消除。

This document records **unresolved** defects, risks, and portability limitations in the `AutomatedConfiguration` repository. Comments in the source explain behavior; they do not mean that the associated risk has been fixed.

严重程度说明 / Severity levels:

- **高 / High**：可能稳定导致安装失败、配置丢失、隐私泄露或网络暴露，应优先处理。 / May consistently cause installation failure, configuration loss, privacy disclosure, or network exposure; address first.
- **中 / Medium**：在常见环境中可能导致误判、阻塞、重复操作或难以排障。 / May cause incorrect status, blocking behavior, repeated work, or difficult troubleshooting in common environments.
- **低 / Low**：主要影响兼容性、可维护性、文档准确性或特殊环境。 / Primarily affects compatibility, maintainability, documentation accuracy, or edge environments.

---

## 高优先级 / High priority

### AC-001：PotPlayer 快照包含敏感历史数据 / PotPlayer snapshot contains sensitive history

- **位置 / Location**：[Windows11/PotPlayerMini64.reg](./Windows11/PotPlayerMini64.reg)，`RememberFiles` 节以及固定路径值。 / The `RememberFiles` section and fixed-path values.
- **问题 / Problem**：文件保存了播放历史、媒体名称、Windows 用户名、桌面目录和绝对文件路径。 / The file stores playback history, media names, Windows usernames, desktop directories, and absolute file paths.
- **影响 / Impact**：一旦仓库被同步、共享或公开，个人使用记录和目录结构会随文件泄露；这些路径在其他计算机上通常也无效。 / If the repository is synchronized, shared, or made public, personal usage history and directory layout are disclosed; the paths are also generally invalid on another computer.
- **建议 / Recommendation**：提交或分享前删除 `RememberFiles`，将用户目录替换为无身份信息的占位路径，并重新检查 Git 历史中是否已有旧快照。 / Remove `RememberFiles` before committing or sharing, replace user directories with anonymous placeholder paths, and inspect Git history for earlier snapshots.
- **状态 / Status**：未修复；文件内已加入双语隐私警告。 / Open; bilingual privacy warnings have been added to the file.

### AC-002：PotPlayer 导入会先删除全部当前配置 / PotPlayer import deletes all current settings first

- **位置 / Location**：[Windows11/PotPlayerMini64.reg](./Windows11/PotPlayerMini64.reg) 开头的 `[-HKEY_CURRENT_USER\Software\Daum\PotPlayerMini64]`。 / The leading `[-HKEY_CURRENT_USER\Software\Daum\PotPlayerMini64]` directive.
- **问题 / Problem**：导入时会先删除整个当前用户键，再重建快照中列出的部分值。 / Importing first removes the entire per-user key and then recreates only values present in the snapshot.
- **影响 / Impact**：原有偏好、历史和快照未包含的子键会丢失；导入中断还可能留下不完整配置。 / Existing preferences, history, and subkeys absent from the snapshot are lost; an interrupted import may leave an incomplete configuration.
- **建议 / Recommendation**：仅在明确需要“全量重置”时保留删除指令；普通迁移应移除删除指令，并在 PotPlayer 关闭后先导出现有注册表键。 / Keep the deletion directive only for an intentional full reset; ordinary migration should omit it and export the current key while PotPlayer is closed.
- **状态 / Status**：未修复；文件内已加入双语破坏性操作警告。 / Open; a bilingual destructive-operation warning has been added.

### AC-003：两个 Winget 包 ID 当前无效 / Two Winget package IDs are currently invalid

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 中的 `VMware.WorkstationPro` 与 `Oray.SunloginClient`。 / `VMware.WorkstationPro` and `Oray.SunloginClient` in the package list.
- **问题 / Problem**：使用 `--exact --source winget` 查询时，两者均返回“找不到匹配包”。 / Exact queries against the `winget` source return “no package found” for both IDs.
- **影响 / Impact**：完整运行目前必然至少记录这两项失败，并最终返回退出码 `1`。 / A complete run currently always records at least these two failures and ultimately exits with code `1`.
- **建议 / Recommendation**：将 VMware 改为手动安装项；向日葵可核对并改用 Microsoft Store ID `XPDDRBQ2D1N7NJ`。 / Move VMware to the manual-install list; for Sunlogin, verify and use Microsoft Store ID `XPDDRBQ2D1N7NJ`.
- **状态 / Status**：未修复。 / Open.

### AC-004：NAT 代理步骤可能向局域网暴露代理 / NAT proxy steps may expose the proxy to the LAN

- **位置 / Location**：[Ubuntu-24.04/ProxyConfiguration.md](./Ubuntu-24.04/ProxyConfiguration.md) 的 NAT、Allow LAN、监听地址和防火墙步骤。 / The NAT, Allow LAN, listen-address, and firewall instructions.
- **问题 / Problem**：文档要求扩大监听范围并开放端口，但没有要求把来源限制到 WSL 虚拟网段。 / The guide broadens the listener and opens a port without requiring the source to be restricted to the WSL virtual subnet.
- **影响 / Impact**：若代理监听 `0.0.0.0` 且防火墙规则允许任意来源，同一局域网中的其他设备可能使用该代理。 / If the proxy listens on `0.0.0.0` and the firewall rule allows any source, other LAN devices may use the proxy.
- **建议 / Recommendation**：优先使用镜像网络；必须使用 NAT 时，仅允许 WSL 虚拟网段访问，并确认代理软件支持来源限制和认证。 / Prefer mirrored networking; when NAT is required, allow only the WSL virtual subnet and verify that the proxy supports source restrictions and authentication.
- **状态 / Status**：未修复。 / Open.

---

## 中优先级 / Medium priority

### AC-005：WSL 检测只验证发行版名称 / WSL detection checks only the distribution name

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 的 WSL 检测和安装块。 / The WSL detection and installation block.
- **问题 / Problem**：脚本只检查是否存在名为 `Ubuntu-24.04` 的发行版，不验证列表命令退出码，也不确认其 VERSION 为 `2`。 / The script checks only for a distribution named `Ubuntu-24.04`; it does not validate the list-command exit code or confirm that VERSION is `2`.
- **影响 / Impact**：已有同名 WSL1 实例时会误报“WSL 2 已安装”；枚举失败时可能继续尝试安装。 / An existing WSL1 instance with that name is reported as “WSL 2 installed”; enumeration failure may trigger another install attempt.
- **建议 / Recommendation**：解析 `wsl --list --verbose`，分别处理“不存在、WSL1、WSL2、枚举失败”，并增加管理员权限检测和独立的 `-SkipWSL` 开关。 / Parse `wsl --list --verbose`, distinguish missing, WSL1, WSL2, and enumeration failure, and add an administrator check plus a separate `-SkipWSL` switch.
- **状态 / Status**：未修复。 / Open.

### AC-006：WSL 文档缺少 VERSION 异常修正步骤 / WSL documentation lacks a correction path for the wrong VERSION

- **位置 / Location**：[Ubuntu-24.04/AutomaticConfigurationSteps.md](./Ubuntu-24.04/AutomaticConfigurationSteps.md)。
- **问题 / Problem**：文档现已说明管理员 PowerShell、重启、首次启动和 VERSION 应为 `2`，但 VERSION 显示 `1` 时没有给出修正命令或转换前的数据备份提示。 / The guide now explains elevation, reboot, first launch, and that VERSION should be `2`, but it provides no corrective command or backup warning when VERSION is `1`.
- **影响 / Impact**：已有 WSL1 默认设置或旧发行版时，用户能识别结果不符合预期，却不知道如何安全转换到 WSL2。 / With an existing WSL1 default or older distribution, users can recognize the mismatch but are not told how to convert safely to WSL2.
- **建议 / Recommendation**：补充转换前备份提示和 `wsl --set-version Ubuntu-24.04 2`，并说明大型发行版转换可能耗时。 / Add a pre-conversion backup warning and `wsl --set-version Ubuntu-24.04 2`, noting that conversion of a large distribution may take time.
- **状态 / Status**：未修复。 / Open.

### AC-007：Windows 脚本和 Ubuntu 文档重复安装发行版 / Windows script and Ubuntu guide duplicate distribution installation

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 与 [Ubuntu-24.04/AutomaticConfigurationSteps.md](./Ubuntu-24.04/AutomaticConfigurationSteps.md)。
- **问题 / Problem**：两处都会执行 Ubuntu 24.04 安装，但仓库没有说明应选择哪一种入口。 / Both install Ubuntu 24.04, but the repository does not state which entry point should be used.
- **影响 / Impact**：用户按两套步骤执行时会遇到“发行版已存在”、重复下载或混乱的重启顺序。 / Following both paths can produce “distribution already exists,” duplicate downloads, or a confusing reboot sequence.
- **建议 / Recommendation**：确定一个主入口，另一个位置只引用主入口并说明已安装时如何跳过。 / Define one primary entry point; make the other location reference it and explain how to skip installation when already present.
- **状态 / Status**：未修复。 / Open.

### AC-008：APT 非交互和代理变量可能被 sudo 清除 / APT noninteractive and proxy variables may be removed by sudo

- **位置 / Location**：[Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 的 `apt_environment()`、`get_privilege_prefix()` 和以 `sudo` 开头的 APT 命令。 / `apt_environment()`, `get_privilege_prefix()`, and APT commands prefixed with `sudo`.
- **问题 / Problem**：变量设置在 `sudo` 的父进程环境中；Ubuntu 默认 `env_reset` 通常不会把所有变量传给提权后的 `apt-get`。 / Variables are set in the parent environment of `sudo`; Ubuntu's default `env_reset` generally does not pass every variable to the elevated `apt-get` process.
- **影响 / Impact**：安装可能出现交互提示，或在必须依赖代理时无法访问 APT 仓库。 / Installation may prompt interactively or fail to reach APT repositories when a proxy is required.
- **建议 / Recommendation**：在 `sudo` 后显式设置 `DEBIAN_FRONTEND`、`APT_LISTCHANGES_FRONTEND`，并仅白名单保留所需代理变量。 / Set `DEBIAN_FRONTEND` and `APT_LISTCHANGES_FRONTEND` explicitly after `sudo`, and preserve only the required proxy variables through a whitelist.
- **状态 / Status**：未修复。 / Open.

### AC-009：Git 代理示例包含无效键且缺少撤销步骤 / Git proxy example contains an unused key and no rollback

- **位置 / Location**：[gitConfiguration.md](./gitConfiguration.md) 的全局代理章节。 / The global proxy section.
- **问题 / Problem**：Git 使用 `http.proxy` 处理 HTTP(S) 传输；`https.proxy` 会被保存为任意配置键，但 Git 的 HTTP 传输不会读取它。文档也没有提供查看和 `--unset` 命令。 / Git uses `http.proxy` for HTTP(S) transport; `https.proxy` is stored as an arbitrary key but is not read by Git's HTTP transport. The guide also omits inspection and `--unset` commands.
- **影响 / Impact**：用户可能误以为 HTTPS 代理已通过第二个键配置；代理软件停止后，全局代理仍会使 Git 网络操作失败。 / Users may believe the second key configures HTTPS; when the proxy application stops, the persistent global proxy can break Git network operations.
- **建议 / Recommendation**：仅设置 `http.proxy`，并补充 `--get http.proxy` 与 `--unset http.proxy`。 / Set only `http.proxy`, and document `--get http.proxy` and `--unset http.proxy`.
- **状态 / Status**：未修复。 / Open.

### AC-010：Git 身份示例相互矛盾 / Git identity examples are inconsistent

- **位置 / Location**：[gitConfiguration.md](./gitConfiguration.md)。
- **问题 / Problem**：可复制命令使用不完整邮箱 `y@`，预期输出却显示 `example@gmail.com`。 / The copyable command uses the incomplete email `y@`, while the expected output shows `example@gmail.com`.
- **影响 / Impact**：提交可能记录错误身份，并无法与托管平台账户正确关联。 / Commits may record the wrong identity and fail to associate with the intended hosting account.
- **建议 / Recommendation**：所有示例统一使用明显的保留示例地址，例如 `user@example.com`。 / Use one clearly reserved example address such as `user@example.com` throughout.
- **状态 / Status**：未修复。 / Open.

### AC-011：Markdown 存在断链和未定义引用 / Markdown contains broken and undefined links

- **位置 / Location**：[Ubuntu-24.04/README.md](./Ubuntu-24.04/README.md) 对 Git 文档的链接，以及 [Ubuntu-24.04/SomePackages.md](./Ubuntu-24.04/SomePackages.md) 的 `[2]`、`[3]` 引用。 / The Git-document link in the README and references `[2]` and `[3]` in `SomePackages.md`.
- **问题 / Problem**：Git 文档已位于仓库根目录，但 README 仍按同目录引用，且表格说明遗漏了该文档现在包含的全局代理内容；`SomePackages.md` 的两个参考编号也没有定义。 / The Git guide is now at the repository root, but the README still references it as a sibling and its table description omits the guide's global-proxy content; two numbered references in `SomePackages.md` also have no definitions.
- **影响 / Impact**：渲染后的链接无法打开，读者无法访问来源或目标文档，并可能漏看代理配置的持久影响。 / Rendered links do not open, preventing readers from reaching sources or the target guide, and the persistent proxy configuration may be overlooked.
- **建议 / Recommendation**：README 使用 `../gitConfiguration.md` 并更新用途说明，同时补齐或删除未定义引用。 / Use `../gitConfiguration.md` in the README, update its purpose text, and define or remove the unresolved references.
- **状态 / Status**：未修复。 / Open.

### AC-012：永久代理缺少 no_proxy 和持久撤销说明 / Persistent proxy lacks no_proxy and persistent rollback guidance

- **位置 / Location**：[Ubuntu-24.04/ProxyConfiguration.md](./Ubuntu-24.04/ProxyConfiguration.md) 的 `~/.bashrc` 示例。 / The `~/.bashrc` examples.
- **问题 / Problem**：示例永久设置代理但未设置 `no_proxy/NO_PROXY`；临时 `unset` 不会删除 `.bashrc` 中的设置。 / The example persists proxy variables without `no_proxy/NO_PROXY`; a temporary `unset` does not remove settings from `.bashrc`.
- **影响 / Impact**：本地开发服务可能被错误发送到代理；打开新终端后被取消的代理会再次生效。 / Local development services may be sent to the proxy, and a proxy unset in one shell returns in every new shell.
- **建议 / Recommendation**：加入 localhost/loopback 的 `no_proxy`，并说明如何从 `.bashrc` 删除或注释代理块。 / Add `no_proxy` for localhost and loopback addresses, and explain how to remove or comment out the proxy block in `.bashrc`.
- **状态 / Status**：未修复。 / Open.

### AC-013：三种代理协议仍共用同一示例端口 / Three proxy protocols still share one example port

- **位置 / Location**：[Ubuntu-24.04/ProxyConfiguration.md](./Ubuntu-24.04/ProxyConfiguration.md) 的 `all_proxy=socks5h://...` 示例和端口说明。 / The `all_proxy=socks5h://...` examples and port guidance.
- **问题 / Problem**：文档现已提醒端口必须支持 URL 声明的协议，但 HTTP、HTTPS CONNECT 和 SOCKS5 示例仍统一使用 `7890`；只有混合端口才同时兼容这些写法。 / The guide now warns that the port must support the declared scheme, but the HTTP, HTTPS CONNECT, and SOCKS5 examples still all use `7890`; only a mixed port supports all of these forms at once.
- **影响 / Impact**：读取 `all_proxy` 的工具可能连接失败，而 HTTP/HTTPS 工具仍表现正常，增加排障难度。 / Tools that read `all_proxy` may fail while HTTP/HTTPS tools continue working, making diagnosis confusing.
- **建议 / Recommendation**：明确区分 HTTP、SOCKS 和混合端口，并为各协议提供独立变量示例。 / Clearly distinguish HTTP, SOCKS, and mixed ports and provide separate variable examples for each protocol.
- **状态 / Status**：未修复。 / Open.

### AC-014：Winget 的 Silent 模式并非完全无人值守 / Winget Silent mode is not fully unattended

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 的 `$Silent` 处理以及 Visual Studio、Battle.net 的 `NoSilent` 标记。 / `$Silent` handling and the `NoSilent` flags for Visual Studio and Battle.net.
- **问题 / Problem**：这些项目即使传入 `-Silent` 仍可能打开 UI；脚本也没有统一添加 `--disable-interactivity`，WSL、UAC 和认证提示不受该开关完全控制。 / These items may still open a UI when `-Silent` is supplied; the script does not consistently add `--disable-interactivity`, and WSL, UAC, and authentication prompts are not fully controlled by the switch.
- **影响 / Impact**：无人值守运行可能阻塞并等待用户输入。 / An unattended run may block while waiting for user input.
- **建议 / Recommendation**：将“静默安装”和“禁止交互”拆成独立策略，对不支持静默的包明确跳过或要求交互运行。 / Separate “silent installer” and “no interaction” policies, and explicitly skip or require interactive execution for packages that do not support silent mode.
- **状态 / Status**：未修复。 / Open.

### AC-015：Winget 成功判断和源健康检查过于简单 / Winget success and source-health checks are too simple

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 的 `Test-Winget()` 和 `$LASTEXITCODE` 判断。 / `Test-Winget()` and `$LASTEXITCODE` handling.
- **问题 / Problem**：脚本只确认命令可解析，并只把退出码 `0` 当成功；它不区分需要重启、已安装、无升级、源异常或进程无法启动。 / The script only confirms that the command resolves and treats only exit code `0` as success; it does not distinguish reboot required, already installed, no upgrade, source failure, or process launch failure.
- **影响 / Impact**：最终汇总可能误报成功或失败，重复运行也可能意外转为升级。 / The final summary may report incorrect success or failure, and repeated runs may unexpectedly perform upgrades.
- **建议 / Recommendation**：预检源、捕获启动异常、保存每项退出码，并按 WinGet 结果类型分类。 / Validate sources, catch launch exceptions, retain each exit code, and classify documented WinGet outcomes.
- **状态 / Status**：未修复。 / Open.

### AC-016：MSYS2 更新范围大且 PATH 可能遮蔽工具 / MSYS2 update is broad and PATH may shadow tools

- **位置 / Location**：[Windows11/install-msys2-cpp-toolchain.ps1](./Windows11/install-msys2-cpp-toolchain.ps1)。
- **问题 / Problem**：脚本用 `--noconfirm` 连续执行两次完整 `pacman -Syu`，并可把 `ucrt64\bin` 放到用户 PATH 最前面。 / The script performs two full `pacman -Syu` updates with `--noconfirm` and can prepend `ucrt64\bin` to the user PATH.
- **影响 / Impact**：已有定制环境可能发生包替换或兼容性变化；PATH 前置可能遮蔽 Windows 版 CMake、编译器或同名 DLL。 / A customized environment may undergo package replacements or compatibility changes; prepending PATH may shadow Windows CMake, compilers, or same-named DLLs.
- **建议 / Recommendation**：在文档中明确全量升级范围，提供确认模式，并优先通过 MSYS2/UCRT64 专用终端使用工具链。 / Document the full-update scope, provide a confirmation mode, and prefer using the toolchain through the dedicated MSYS2/UCRT64 terminal.
- **状态 / Status**：未修复。 / Open.

### AC-017：Windows 两个安装脚本没有编排关系 / Windows installers are not orchestrated

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 与 [Windows11/install-msys2-cpp-toolchain.ps1](./Windows11/install-msys2-cpp-toolchain.ps1)。
- **问题 / Problem**：第一个脚本只安装 MSYS2 本体，不会调用第二个工具链脚本，也没有统一入口说明执行顺序。 / The first script installs only MSYS2 itself; it does not call the toolchain script, and there is no single entry point documenting execution order.
- **影响 / Impact**：用户可能误以为 C++ 工具链已经完整安装；前一个脚本的无关失败还可能阻止外部编排继续。 / Users may believe the C++ toolchain is complete; unrelated failures in the first script may also prevent an external orchestrator from continuing.
- **建议 / Recommendation**：新增 Windows README 或总控脚本，明确“安装 MSYS2 → 重开/更新 → 安装 UCRT64 工具链”的顺序和失败策略。 / Add a Windows README or orchestrator documenting “install MSYS2 → reopen/update → install the UCRT64 toolchain” and the failure policy.
- **状态 / Status**：未修复。 / Open.

### AC-018：Git 全局代理示例在 WSL NAT 模式下地址错误 / Git global proxy example uses the wrong address in WSL NAT mode

- **位置 / Location**：[gitConfiguration.md](./gitConfiguration.md) 的 `127.0.0.1:7890` 全局代理示例，以及 [Ubuntu-24.04/README.md](./Ubuntu-24.04/README.md) 将该文档纳入 WSL 工作流的位置。 / The `127.0.0.1:7890` global-proxy example in `gitConfiguration.md` and its use from the WSL workflow in the Ubuntu README.
- **问题 / Problem**：回环地址适用于 Windows Git 和 WSL 镜像网络；在默认 NAT 网络中，WSL 内的 `127.0.0.1` 指向 Linux 虚拟机自身，而不是 Windows 上的代理程序。 / Loopback works for Git on Windows and for WSL mirrored networking; under the default NAT network, `127.0.0.1` inside WSL refers to the Linux VM itself rather than the proxy application on Windows.
- **影响 / Impact**：同一配置可能让 Windows Git 正常联网，却让 WSL Git 稳定连接失败。 / The same configuration can work for Git on Windows while consistently failing for Git inside WSL.
- **建议 / Recommendation**：分别提供 Windows、WSL 镜像网络和 WSL NAT 示例；NAT 模式复用 `ProxyConfiguration.md` 中探测 Windows 主机地址的方法，并先验证对应端口。 / Provide separate examples for Windows, WSL mirrored networking, and WSL NAT; in NAT mode, reuse the Windows-host discovery method from `ProxyConfiguration.md` and validate the selected port first.
- **状态 / Status**：未修复。 / Open.

### AC-019：APT 示例使用范围过宽的 `sudo -E` / APT example uses overly broad `sudo -E`

- **位置 / Location**：[Ubuntu-24.04/ProxyConfiguration.md](./Ubuntu-24.04/ProxyConfiguration.md) 的 `sudo -E apt update` 示例。 / The `sudo -E apt update` example.
- **问题 / Problem**：若 `sudoers` 允许，`-E` 会尝试保留整个调用环境，而不仅是 APT 所需的代理变量；文档虽说明能否保留受策略控制，但没有限制保留范围。 / When permitted by `sudoers`, `-E` attempts to preserve the caller's entire environment rather than only the proxy variables APT needs; the guide notes the policy dependency but does not narrow the retained scope.
- **影响 / Impact**：访问令牌、调试开关或其他不应进入提权进程的变量可能被带入 root 环境，同时不同主机仍可能因策略拒绝而表现不一致。 / Access tokens, debug flags, or other variables that should not enter an elevated process may be passed into the root environment, while policy differences can still make behavior inconsistent across hosts.
- **建议 / Recommendation**：显式传递白名单变量，例如在 `sudo` 后使用受控的 `env http_proxy=... https_proxy=...`，或为 APT 创建权限受控的 `Acquire::*::Proxy` 配置。 / Pass an explicit variable allowlist, for example with controlled `env http_proxy=... https_proxy=...` arguments after `sudo`, or create a permission-controlled APT `Acquire::*::Proxy` configuration.
- **状态 / Status**：未修复。 / Open.

### AC-020：MySQL 服务状态可能未验证却仍报告整体成功 / MySQL service state may remain unchecked while overall verification succeeds

- **位置 / Location**：[Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 的 `systemctl is-active mysql` 验证分支。 / The `systemctl is-active mysql` verification branch.
- **问题 / Problem**：`systemctl` 不存在时脚本完全跳过服务检查；命令存在但没有输出时只打印提示，不把“无法验证”与“已验证并运行”区分为不同结果。 / When `systemctl` is absent, the script skips the service check entirely; when the command exists but returns no output, it prints a notice without distinguishing “not verified” from “verified and running” in the final result.
- **影响 / Impact**：开发文件均存在但 MySQL 服务未启动或不可管理时，脚本仍可能以退出码 `0` 结束。 / If development files exist but the MySQL service is not started or cannot be managed, the script may still finish with exit code `0`.
- **建议 / Recommendation**：明确输出 `active`、`inactive/failed`、`not checked` 三态，并提供可选严格模式；在未启用 systemd 的 WSL 中同时说明如何手动启动和验证 MySQL。 / Report explicit `active`, `inactive/failed`, and `not checked` states and offer an optional strict mode; for WSL without systemd, document how to start and verify MySQL manually.
- **状态 / Status**：未修复。 / Open.

---

## 低优先级 / Low priority

### AC-021：PotPlayer 快照依赖原机器硬件和显示布局 / PotPlayer snapshot depends on the source hardware and display layout

- **位置 / Location**：[Windows11/PotPlayerMini64.reg](./Windows11/PotPlayerMini64.reg) 的 Dialog、Positions、Settings 和 SimpleOpen 节。 / The Dialog, Positions, Settings, and SimpleOpen sections.
- **问题 / Problem**：窗口坐标、尺寸、Quick Sync 等硬件选项以及路径均来自导出机器。 / Window coordinates, sizes, hardware options such as Quick Sync, and paths all come from the source machine.
- **影响 / Impact**：不同分辨率或硬件上可能出现窗口越界、硬件加速不可用和路径失效。 / Different displays or hardware may produce off-screen windows, unavailable hardware acceleration, and invalid paths.
- **建议 / Recommendation**：只保留真正需要迁移的通用设置，删除设备、坐标、历史和固定路径值。 / Retain only portable settings and remove device, coordinate, history, and fixed-path values.
- **状态 / Status**：未修复。 / Open.

### AC-022：注册表头与编码组合兼容性有限 / Registry header and encoding combination has limited compatibility

- **位置 / Location**：[Windows11/PotPlayerMini64.reg](./Windows11/PotPlayerMini64.reg) 文件头。
- **问题 / Problem**：文件使用 UTF-16 LE BOM，但头部仍为旧式 `REGEDIT4`。 / The file uses a UTF-16 LE BOM while retaining the legacy `REGEDIT4` header.
- **影响 / Impact**：Windows Regedit 通常能够处理，但第三方或严格解析器可能拒绝或错误读取。 / Windows Regedit commonly handles it, but third-party or strict parsers may reject or misread it.
- **建议 / Recommendation**：验证目标环境后考虑统一为 `Windows Registry Editor Version 5.00` 与 UTF-16 LE。 / After testing the target environment, consider standardizing on `Windows Registry Editor Version 5.00` with UTF-16 LE.
- **状态 / Status**：未修复。 / Open.

### AC-023：Python 脚本未限定 Ubuntu 24.04 / Python script does not enforce Ubuntu 24.04

- **位置 / Location**：[Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 的系统检查。 / The system-validation logic.
- **问题 / Problem**：脚本只验证 `ID=ubuntu`，任何 Ubuntu 版本都会在包名验证之前执行仓库准备操作。 / The script checks only `ID=ubuntu`; any Ubuntu release proceeds with repository preparation before package-name validation.
- **影响 / Impact**：在未测试版本上运行时，包名、服务行为和验证路径可能不同。 / On an untested release, package names, service behavior, and verification paths may differ.
- **建议 / Recommendation**：若只支持 Noble，应在任何变更前要求 `VERSION_ID=24.04`；否则明确支持矩阵并按版本维护包组。 / If only Noble is supported, require `VERSION_ID=24.04` before any mutation; otherwise document a support matrix and maintain version-specific package groups.
- **状态 / Status**：未修复。 / Open.

### AC-024：Python 对“官方仓库”的描述过强 / Python claim about “official repositories” is too strong

- **位置 / Location**：[Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 顶部说明及 [Ubuntu-24.04/README.md](./Ubuntu-24.04/README.md)。
- **问题 / Problem**：脚本不会新增第三方 PPA，但 APT 仍会使用系统中已经配置的全部软件源。 / The script does not add third-party PPAs, but APT still uses every source already configured on the system.
- **影响 / Impact**：不能保证最终软件包全部来自 Ubuntu 官方仓库。 / It cannot guarantee that every installed package originates from an official Ubuntu repository.
- **建议 / Recommendation**：将措辞改为“脚本不会添加第三方仓库”，或增加软件源审计和来源限制。 / Change the wording to “the script does not add third-party repositories,” or add source auditing and origin restrictions.
- **状态 / Status**：未修复。 / Open.

### AC-025：部分 Markdown 命令不具备重复执行保护 / Some Markdown commands are not repeat-safe

- **位置 / Location**：[Ubuntu-24.04/SomePackages.md](./Ubuntu-24.04/SomePackages.md) 的 `cat >> ~/.bashrc` 示例。 / The `cat >> ~/.bashrc` example.
- **问题 / Problem**：每次执行都会再次追加同一组别名。 / Every execution appends the same aliases again.
- **影响 / Impact**：`.bashrc` 会持续累积重复块，增加维护和排障成本。 / `.bashrc` accumulates duplicate blocks, increasing maintenance and troubleshooting cost.
- **建议 / Recommendation**：使用带唯一标记的配置块、先检测别名，或指导用户手动编辑。 / Use a uniquely marked block, detect aliases first, or instruct the user to edit manually.
- **状态 / Status**：未修复。 / Open.

### AC-026：微信包仍指向旧版分支 / WeChat package still targets the legacy branch

- **位置 / Location**：[Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 中的 `Tencent.WeChat`。
- **问题 / Problem**：该 ID 当前解析到 3.x 分支；新版 4.x 使用独立 ID `Tencent.WeChat.Universal`。 / This ID currently resolves to the 3.x branch; the newer 4.x branch uses the separate ID `Tencent.WeChat.Universal`.
- **影响 / Impact**：安装可以成功，但可能不是用户预期的新版产品。 / Installation succeeds but may not produce the newer product the user expects.
- **建议 / Recommendation**：明确目标分支并在切换前核对数据迁移、兼容性和发布者信息。 / Choose the intended branch explicitly and verify data migration, compatibility, and publisher information before switching.
- **状态 / Status**：未修复。 / Open.

### AC-027：Dry-run 不验证真实 APT 包可用性 / Dry-run does not validate actual APT package availability

- **位置 / Location**：[Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 的 `package_is_available()` 与 `--dry-run` 流程。 / `package_is_available()` and the `--dry-run` path.
- **问题 / Problem**：预演模式直接把每个包视为可用，不运行 `apt-cache show`；因此它只预览命令，不验证当前软件源是否真的包含这些包。 / Dry-run treats every package as available and does not run `apt-cache show`; it previews commands but does not prove that configured repositories contain the packages.
- **影响 / Impact**：软件源、发行版版本或包名发生变化时，预演仍会成功，实际安装才会发现缺包。 / If repositories, Ubuntu versions, or package names change, preview still succeeds and the missing package is discovered only during a real run.
- **建议 / Recommendation**：保留纯预演模式，同时增加一个只读的 `--validate-packages` 模式，允许刷新前提满足时查询 APT 元数据但不安装。 / Keep the pure preview mode and add a read-only `--validate-packages` mode that queries APT metadata without installing when prerequisites are available.
- **状态 / Status**：未修复。 / Open.

### AC-028：Ubuntu README 缺少进入仓库目录的具体命令 / Ubuntu README lacks a concrete command for entering the repository directory

- **位置 / Location**：[Ubuntu-24.04/README.md](./Ubuntu-24.04/README.md) 的 Python 脚本运行步骤。 / The Python-script execution steps.
- **问题 / Problem**：文档只要求“从本目录执行”，没有说明如何从 Ubuntu 默认主目录进入位于 Windows Desktop 的仓库；常见路径需要经过 `/mnt/c/Users/<Windows-user>/...`。 / The guide says only to run “from this directory” and does not explain how to reach a repository stored on the Windows Desktop from Ubuntu's default home directory; the common path goes through `/mnt/c/Users/<Windows-user>/...`.
- **影响 / Impact**：在新打开的 Ubuntu 终端中直接复制 `python3 SettingUpEnvironmentAndPackages.py` 会得到“文件不存在”。 / Copying `python3 SettingUpEnvironmentAndPackages.py` directly into a newly opened Ubuntu terminal produces “file not found.”
- **建议 / Recommendation**：提供带占位用户名的 `cd /mnt/c/Users/<Windows-user>/Desktop/AutomatedConfiguration/Ubuntu-24.04` 示例，并提醒含空格路径需要加引号。 / Provide a `cd /mnt/c/Users/<Windows-user>/Desktop/AutomatedConfiguration/Ubuntu-24.04` example with a placeholder username and note that paths containing spaces need quoting.
- **状态 / Status**：未修复。 / Open.

### AC-029：`.wslconfig` 示例没有提醒合并既有设置 / `.wslconfig` example does not warn users to merge existing settings

- **位置 / Location**：[Ubuntu-24.04/ProxyConfiguration.md](./Ubuntu-24.04/ProxyConfiguration.md) 的 `[wsl2]` 配置块。 / The `[wsl2]` configuration block.
- **问题 / Problem**：文档要求写入完整示例，但没有先检查、备份并合并现有 `.wslconfig`；该文件还可能包含内存、处理器、交换文件或其他全局 WSL 设置。 / The guide asks users to write the complete example without first checking, backing up, and merging an existing `.wslconfig`, which may also contain memory, processor, swap-file, or other global WSL settings.
- **影响 / Impact**：用示例整体替换文件可能悄然丢失原有资源限制和网络配置。 / Replacing the whole file with the example can silently remove existing resource limits and networking settings.
- **建议 / Recommendation**：先备份文件，只合并缺少的键，并保证最终只有一个 `[wsl2]` 节；修改后再执行 `wsl --shutdown`。 / Back up the file, merge only missing keys, and keep a single `[wsl2]` section before running `wsl --shutdown`.
- **状态 / Status**：未修复。 / Open.

### AC-030：独立 APT 示例依赖未说明的索引与 Universe 前置条件 / Standalone APT examples rely on undocumented index and Universe prerequisites

- **位置 / Location**：[Ubuntu-24.04/SomePackages.md](./Ubuntu-24.04/SomePackages.md) 前半部分的各个独立 `apt install` 代码块。 / The standalone `apt install` blocks in the first part of the package guide.
- **问题 / Problem**：组合安装段落会执行 `apt update`，但独立段落没有说明软件包索引必须已刷新，且 `bat`、`fd-find`、`btop` 等包依赖 Ubuntu Universe 已启用。 / The combined-install section runs `apt update`, but the standalone sections do not state that package indexes must already be refreshed, and packages such as `bat`, `fd-find`, and `btop` depend on Ubuntu Universe being enabled.
- **影响 / Impact**：在全新或最小化 Ubuntu 上单独复制某一段时，可能出现“无法定位软件包”，即使包名本身正确。 / Copying one section on a fresh or minimal Ubuntu system can produce “unable to locate package” even when the package name is correct.
- **建议 / Recommendation**：在文件开头增加统一前置步骤，或让每个可独立复制的安装段落明确引用 `sudo apt update` 与 Universe 启用步骤。 / Add one shared prerequisite section at the beginning, or make every independently copyable install block explicitly reference `sudo apt update` and the Universe-enablement step.
- **状态 / Status**：未修复。 / Open.

---

## 已修复并保留回归检查 / Resolved and retained for regression checks

以下项目不再属于开放问题，但后续修改应避免回归。

The following items are no longer open, but future changes should avoid reintroducing them.

### RES-001：Python 验证失败曾返回成功码 / Python verification failures previously returned success

- [Ubuntu-24.04/SettingUpEnvironmentAndPackages.py](./Ubuntu-24.04/SettingUpEnvironmentAndPackages.py) 现在会累计缺失组件并抛出 `InstallError`，入口最终返回 `1`。 / The script now accumulates missing components, raises `InstallError`, and ultimately returns `1`.

### RES-002：SkipStore 曾被计为成功且手动提醒不可达 / SkipStore was counted as success and manual guidance was unreachable

- [Windows11/install-winget-apps.ps1](./Windows11/install-winget-apps.ps1) 现在区分 `Succeeded`、`Skipped`、`Failed`，并在最终失败退出前显示 AK Accelerator 手动提醒。 / The script now distinguishes `Succeeded`, `Skipped`, and `Failed`, and prints the AK Accelerator manual guidance before the final failure exit.

---

## 维护要求 / Maintenance requirements

- 修复问题后，应更新对应状态，并保留验证方法或回归测试说明。 / When an issue is fixed, update its status and retain the verification method or regression-test notes.
- 软件包 ID、版本、WSL 命令和外部链接具有时效性，应定期重新核验。 / Package IDs, versions, WSL commands, and external links are time-sensitive and should be revalidated periodically.
- 不要在问题文档中复制真实用户名、媒体标题、访问令牌或其他敏感值。 / Do not copy real usernames, media titles, access tokens, or other sensitive values into this issue document.
