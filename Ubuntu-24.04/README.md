# Ubuntu / WSL 自动配置资料

本目录收集了在 Windows Subsystem for Linux（WSL）中准备 Ubuntu 开发环境时使用的说明文档和自动安装脚本，主要面向 C++、Qt5、FFmpeg 与 MySQL 开发。

This directory contains guides and an installation script for preparing an Ubuntu development environment under Windows Subsystem for Linux (WSL), primarily for C++, Qt5, FFmpeg, and MySQL development.

文档中的命令分别面向 Windows PowerShell 或 Ubuntu Bash；请按照各段说明选择终端。带有 `sudo` 的命令会修改 Ubuntu 系统级配置或软件包，运行前可能要求输入当前 Linux 用户密码。

Commands in these guides target either Windows PowerShell or Ubuntu Bash; use the shell named in each section. Commands prefixed with `sudo` modify system-wide Ubuntu configuration or packages and may ask for the current Linux user's password.

## 文件说明 / File overview

| 文件 / File | 用途 / Purpose |
| --- | --- |
| [`AutomaticConfigurationSteps.md`](./AutomaticConfigurationSteps.md) | 说明如何更新 WSL、安装 Ubuntu 24.04 LTS，并检查 WSL 与 Ubuntu 版本。 / Explains how to update WSL, install Ubuntu 24.04 LTS, and verify the WSL and Ubuntu versions. |
| [`ProxyConfiguration.md`](./ProxyConfiguration.md) | 介绍 WSL 镜像网络、自动代理、手动代理、NAT 网络和 APT 代理的配置方法。 / Covers mirrored networking, automatic and manual proxies, NAT mode, and APT proxy configuration for WSL. |
| [`SettingUpEnvironmentAndPackages.py`](./SettingUpEnvironmentAndPackages.py) | 自动启用 Ubuntu 官方 Universe 仓库，安装并验证 C++ 工具链、Qt5、nlohmann/json、FFmpeg 和 MySQL 开发组件。 / Enables Ubuntu's official Universe repository, then installs and verifies the C++ toolchain, Qt5, nlohmann/json, FFmpeg, and MySQL development components. |
| [`SomePackages.md`](./SomePackages.md) | 汇总常用命令行、文件搜索、C/C++ 开发、网络排查和系统监控工具，并附安装命令与示例。 / Lists useful CLI, file-search, C/C++, networking, and system-monitoring tools with installation commands and examples. |
| [`gitConfiguration.md`](./gitConfiguration.md) | 说明如何设置和检查 Git 用户名、邮箱，以及如何选择全局或仅当前仓库配置。 / Explains how to set and verify a Git username and email globally or for the current repository only. |
| [`KnownIssues.md`](../KnownIssues.md) | 记录仓库中尚未修复的问题、风险、影响和建议处理方式。 / Records unresolved repository issues, risks, impact, and recommended remediation. |
| [`README.md`](./README.md) | 当前目录的总览、建议使用顺序和脚本运行方法。 / Provides this directory overview, the recommended workflow, and script usage. |

## 建议使用顺序 / Recommended workflow

1. 按照 `AutomaticConfigurationSteps.md` 安装并确认 WSL 与 Ubuntu 版本。 / Install WSL and verify the Ubuntu version with `AutomaticConfigurationSteps.md`.
2. 如果 Ubuntu 无法直接联网，按照 `ProxyConfiguration.md` 配置代理。 / If Ubuntu cannot access the network directly, configure a proxy with `ProxyConfiguration.md`.
3. 先预演自动安装脚本，确认命令符合预期。 / Preview the installer first and review its commands.

   `--dry-run` 只打印脚本计划执行的命令，不修改 APT 仓库、索引、软件包或服务；应在 Ubuntu 终端中从本目录执行。 / `--dry-run` only prints the commands the script plans to run and does not modify APT repositories, indexes, packages, or services; run it from this directory in an Ubuntu terminal.

   ```bash
   # 预览操作，不修改系统。/ Preview the operations without changing the system.
   python3 SettingUpEnvironmentAndPackages.py --dry-run
   ```

4. 确认无误后执行安装；脚本需要 root 权限，非 root 用户会通过 `sudo` 提权。 / Run the installation after reviewing it; the script uses `sudo` when not run as root.

   实际运行会联网刷新 APT 索引、启用 Ubuntu Universe 仓库、安装开发包并检查结果。请保持网络稳定，并留意 `sudo` 密码提示和 APT 输出；脚本成功返回 `0`，安装或验证失败返回非零状态。 / A real run refreshes APT indexes over the network, enables Ubuntu's Universe repository, installs development packages, and verifies the result. Keep the network available and watch for the `sudo` password prompt and APT output; the script returns `0` on success and a nonzero status on installation or verification failure.

   ```bash
   # 执行实际安装，会修改 Ubuntu 系统。/ Perform the real installation, which modifies the Ubuntu system.
   python3 SettingUpEnvironmentAndPackages.py
   ```

5. 根据需要从 `SomePackages.md` 安装额外工具，并使用 `gitConfiguration.md` 配置 Git。 / Install optional tools from `SomePackages.md`, then configure Git with `gitConfiguration.md`.

如果已经手动刷新过 APT 索引，可使用 `--skip-update` 跳过脚本开头的第一次 `apt-get update`；脚本仍会在启用 Universe 仓库后刷新一次索引。

If the APT index was refreshed manually, use `--skip-update` to skip the first `apt-get update`; the script still refreshes the index once after enabling Universe.

`--skip-update` 只改变第一次索引刷新是否执行，不代表整个安装离线运行。重复运行脚本通常会让 APT 确认已安装的软件包，并再次执行仓库准备和验证；它不会为同一个 APT 软件包创建重复副本。

`--skip-update` changes only whether the initial index refresh runs; it does not make the overall installation offline. Re-running the script generally makes APT confirm already-installed packages and repeats repository preparation and verification; it does not create duplicate copies of the same APT package.

## 使用提示 / Notes

- 自动安装脚本仅针对 Ubuntu 编写，并使用 Ubuntu 官方 APT 仓库。 / The installer targets Ubuntu and uses only official Ubuntu APT repositories.
- 安装会更改系统软件包，并包含 MySQL Server；建议先执行 `--dry-run`。 / Installation changes system packages and includes MySQL Server, so running `--dry-run` first is recommended.
- 安装所需时间和磁盘空间取决于已有软件包、镜像速度与网络情况；中途强制关闭终端可能留下未完成的 APT/dpkg 操作。 / Required time and disk space depend on existing packages, mirror speed, and network conditions; forcibly closing the terminal mid-run may leave an unfinished APT/dpkg operation.
- 安装 MySQL Server 后可能启动系统服务；WSL 未启用 systemd 时，服务状态与普通 Ubuntu 主机可能不同。 / Installing MySQL Server may start a system service; when systemd is not enabled in WSL, service state may differ from a regular Ubuntu host.
- 脚本不会修改 `PATH`、`~/.bashrc`、`~/.profile` 或 `/etc/environment`。 / The script does not modify `PATH`, `~/.bashrc`, `~/.profile`, or `/etc/environment`.
- 文档中的代理端口、Git 用户名和邮箱均为示例，请替换为实际值。 / Proxy ports, Git usernames, and email addresses shown in the guides are examples; replace them with actual values.
- 除非文档明确要求重启 Windows 或关闭 WSL，否则 APT 软件包安装本身通常不要求重启；若系统工具给出重启提示，应以实际提示为准。 / Unless a guide explicitly asks for a Windows restart or WSL shutdown, installing APT packages normally does not itself require a restart; follow any restart prompt actually shown by system tools.
