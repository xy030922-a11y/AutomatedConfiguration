# Ubuntu / WSL 自动配置资料

本目录收集了在 Windows Subsystem for Linux（WSL）中准备 Ubuntu 开发环境时使用的说明文档和自动安装脚本，主要面向 C++、Qt5、FFmpeg 与 MySQL 开发。

This directory contains guides and an installation script for preparing an Ubuntu development environment under Windows Subsystem for Linux (WSL), primarily for C++, Qt5, FFmpeg, and MySQL development.

## 文件说明 / File overview

| 文件 / File | 用途 / Purpose |
| --- | --- |
| [`AutomaticConfigurationSteps.md`](./AutomaticConfigurationSteps.md) | 说明如何更新 WSL、安装 Ubuntu 24.04 LTS，并检查 WSL 与 Ubuntu 版本。 / Explains how to update WSL, install Ubuntu 24.04 LTS, and verify the WSL and Ubuntu versions. |
| [`ProxyConfiguration.md`](./ProxyConfiguration.md) | 介绍 WSL 镜像网络、自动代理、手动代理、NAT 网络和 APT 代理的配置方法。 / Covers mirrored networking, automatic and manual proxies, NAT mode, and APT proxy configuration for WSL. |
| [`SettingUpEnvironmentAndPackages.py`](./SettingUpEnvironmentAndPackages.py) | 自动启用 Ubuntu 官方 Universe 仓库，安装并验证 C++ 工具链、Qt5、nlohmann/json、FFmpeg 和 MySQL 开发组件。 / Enables Ubuntu's official Universe repository, then installs and verifies the C++ toolchain, Qt5, nlohmann/json, FFmpeg, and MySQL development components. |
| [`SomePackages.md`](./SomePackages.md) | 汇总常用命令行、文件搜索、C/C++ 开发、网络排查和系统监控工具，并附安装命令与示例。 / Lists useful CLI, file-search, C/C++, networking, and system-monitoring tools with installation commands and examples. |
| [`gitConfiguration.md`](./gitConfiguration.md) | 说明如何设置和检查 Git 用户名、邮箱，以及如何选择全局或仅当前仓库配置。 / Explains how to set and verify a Git username and email globally or for the current repository only. |
| [`README.md`](./README.md) | 当前目录的总览、建议使用顺序和脚本运行方法。 / Provides this directory overview, the recommended workflow, and script usage. |

## 建议使用顺序 / Recommended workflow

1. 按照 `AutomaticConfigurationSteps.md` 安装并确认 WSL 与 Ubuntu 版本。 / Install WSL and verify the Ubuntu version with `AutomaticConfigurationSteps.md`.
2. 如果 Ubuntu 无法直接联网，按照 `ProxyConfiguration.md` 配置代理。 / If Ubuntu cannot access the network directly, configure a proxy with `ProxyConfiguration.md`.
3. 先预演自动安装脚本，确认命令符合预期。 / Preview the installer first and review its commands.

   ```bash
   python3 SettingUpEnvironmentAndPackages.py --dry-run
   ```

4. 确认无误后执行安装；脚本需要 root 权限，非 root 用户会通过 `sudo` 提权。 / Run the installation after reviewing it; the script uses `sudo` when not run as root.

   ```bash
   python3 SettingUpEnvironmentAndPackages.py
   ```

5. 根据需要从 `SomePackages.md` 安装额外工具，并使用 `gitConfiguration.md` 配置 Git。 / Install optional tools from `SomePackages.md`, then configure Git with `gitConfiguration.md`.

如果已经手动刷新过 APT 索引，可使用 `--skip-update` 跳过脚本开头的第一次 `apt-get update`；脚本仍会在启用 Universe 仓库后刷新一次索引。

If the APT index was refreshed manually, use `--skip-update` to skip the first `apt-get update`; the script still refreshes the index once after enabling Universe.

## 使用提示 / Notes

- 自动安装脚本仅针对 Ubuntu 编写，并使用 Ubuntu 官方 APT 仓库。 / The installer targets Ubuntu and uses only official Ubuntu APT repositories.
- 安装会更改系统软件包，并包含 MySQL Server；建议先执行 `--dry-run`。 / Installation changes system packages and includes MySQL Server, so running `--dry-run` first is recommended.
- 脚本不会修改 `PATH`、`~/.bashrc`、`~/.profile` 或 `/etc/environment`。 / The script does not modify `PATH`, `~/.bashrc`, `~/.profile`, or `/etc/environment`.
- 文档中的代理端口、Git 用户名和邮箱均为示例，请替换为实际值。 / Proxy ports, Git usernames, and email addresses shown in the guides are examples; replace them with actual values.
