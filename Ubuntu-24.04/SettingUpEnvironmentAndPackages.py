#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 Ubuntu 上自动安装 C++/Qt5/FFmpeg/MySQL 开发环境。
Automatically install a C++/Qt5/FFmpeg/MySQL development environment on Ubuntu.

适用范围 / Scope:
- 本脚本面向使用 APT 的 Ubuntu 系统，并在执行安装前显式核对发行版。
  This script targets APT-based Ubuntu systems and explicitly verifies the
  distribution before attempting installation.
- 包名以 Ubuntu 官方仓库为目标；脚本自身只启用官方 Universe 组件，不添加第三方
  PPA，也不下载或执行外部安装脚本。若主机原本配置了额外软件源，APT 的实际选源
  仍由该主机的仓库优先级决定，本脚本不会重写或固定来源。
  Package names target Ubuntu's official repositories. The script itself enables only
  official Universe, adds no third-party PPA, and downloads or executes no external
  installer script. If the host already has extra repositories, APT's configured
  priorities still select the actual source; this script neither rewrites nor pins it.

特性 / Features:
- 使用 Ubuntu 官方 APT 仓库，不添加第三方 PPA。
  Uses Ubuntu's official APT repositories; no third-party PPA is added.
- 安装 GCC、G++、CMake、GDB、Git、Ninja 和 pkg-config。
  Installs GCC, G++, CMake, GDB, Git, Ninja, and pkg-config.
- 安装仓库中的 Qt5，保证具备 Core、Widgets、Sql、Network 模块。
  Installs repository-provided Qt5 with Core, Widgets, Sql, and Network modules.
- 安装 nlohmann/json、FFmpeg 运行程序及主要开发库。
  Installs nlohmann/json, FFmpeg CLI tools, and major development libraries.
- 安装 MySQL Server、客户端开发库、Qt MySQL 驱动和 Connector/C++。
  Installs MySQL Server, client development files, Qt's MySQL driver, and Connector/C++.
- 不写入 ~/.bashrc、~/.profile、/etc/environment，也不修改 PATH。
  Does not write to ~/.bashrc, ~/.profile, /etc/environment, or modify PATH.

执行流程 / Execution flow:
1. 检查当前平台及 /etc/os-release，确认操作系统是 Ubuntu。
   Check the platform and /etc/os-release to confirm that the OS is Ubuntu.
2. 当前用户不是 root 时预先执行 sudo -v，尽早完成权限验证。
   When not running as root, invoke sudo -v early to validate privileges.
3. 为 APT 子进程构造非交互环境，刷新索引并启用 Universe。
   Build a noninteractive environment for APT subprocesses, refresh indexes,
   and enable Universe.
4. 使用 apt-cache 逐一确认包名可用，然后在一次 apt-get 调用中安装全部包。
   Check every package name with apt-cache, then install all packages in one
   apt-get invocation.
5. 检查命令、pkg-config 模块、头文件、Qt 插件及可查询的 MySQL 服务状态。
   Verify commands, pkg-config modules, headers, the Qt plugin, and the MySQL
   service state when it can be queried.

安全与退出状态 / Safety and exit status:
- --dry-run 只展示主要 APT/sudo 操作命令，不启动子进程、不查询 APT 元数据、
  不安装软件，也不执行安装后验证；因此成功预演不代表真实安装一定成功。
  --dry-run only displays the main APT/sudo operations: it starts no subprocess,
  queries no APT metadata, installs nothing, and skips post-install verification.
  A successful preview therefore does not guarantee that a real installation will succeed.
- --skip-update 仅跳过启用 Universe 之前的第一次 apt-get update；启用仓库后的
  第二次刷新仍会执行，以确保新仓库的索引可供后续包检查使用。
  --skip-update skips only the first apt-get update before Universe is enabled;
  the second refresh still runs so the newly enabled repository can be checked.
- 正常完成返回 0，脚本检测到错误返回 1，用户按 Ctrl+C 中断返回 130。
  Successful completion returns 0, a detected installation error returns 1,
  and a Ctrl+C interruption returns 130.

运行方法 / Usage:
    python3 SettingUpEnvironmentAndPackages.py

也可以先查看将执行的命令 / Preview commands without changing the system:
    python3 SettingUpEnvironmentAndPackages.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence


# C++ 基础工具链 / Core C++ toolchain
# - build-essential：安装编译 C/C++ 软件常用的元包依赖（包括 make 等）。
#   build-essential: pulls in the standard dependencies used to build C/C++ software,
#   including make and related essentials.
# - gcc、g++：分别提供 C 与 C++ 编译器；显式列出可让安装意图及验证对象更清晰。
#   gcc and g++: provide the C and C++ compilers; listing them explicitly makes the
#   intended tools and later verification targets clear.
# - cmake、ninja-build：提供生成构建系统和执行 Ninja 构建的工具。
#   cmake and ninja-build: generate build files and execute Ninja builds.
# - gdb、git：分别用于本地调试和版本控制；pkg-config 用于发现开发库。
#   gdb and git: support debugging and version control; pkg-config discovers
#   compiler/linker settings for installed development libraries.
TOOLCHAIN_PACKAGES: tuple[str, ...] = (
    "build-essential",
    "gcc",
    "g++",
    "cmake",
    "gdb",
    "git",
    "ninja-build",
    "pkg-config",
)

# Qt5 开发环境 / Qt5 development environment:
# - qtbase5-dev 提供 Qt5Core、Qt5Widgets、Qt5Sql 和 Qt5Network 的头文件与库；
#   qtbase5-dev-tools 补充 moc、uic、rcc 等 Qt 构建期工具。
#   qtbase5-dev provides headers and libraries for Qt5Core, Qt5Widgets, Qt5Sql,
#   and Qt5Network; qtbase5-dev-tools adds build-time utilities such as moc, uic,
#   and rcc.
# - qt5-qmake 提供 qmake；qtchooser 在并存多个 Qt 版本时帮助选择工具链。
#   qt5-qmake provides qmake; qtchooser helps select a toolchain when multiple Qt
#   versions coexist.
# - libqt5sql5-mysql 是 Qt SQL 访问 MySQL 所需的运行时数据库驱动插件；它虽不
#   提供独立命令，但会在安装验证中通过插件文件进行检查。
#   libqt5sql5-mysql is the runtime database driver used by Qt SQL to access MySQL.
#   It has no standalone command, so verification checks its plugin file instead.
QT5_PACKAGES: tuple[str, ...] = (
    "qtbase5-dev",
    "qtbase5-dev-tools",
    "qt5-qmake",
    "qtchooser",
    "libqt5sql5-mysql",
)

# 现代 C++ JSON 头文件库：安装后预期存在 /usr/include/nlohmann/json.hpp。
# Modern C++ header-only JSON library; installation is expected to provide
# /usr/include/nlohmann/json.hpp.
JSON_PACKAGES: tuple[str, ...] = (
    "nlohmann-json3-dev",
)

# FFmpeg 命令行工具和常用开发模块 / FFmpeg CLI and common development modules:
# - ffmpeg 提供命令行程序，既用于媒体处理，也作为安装后的版本检查入口。
#   ffmpeg provides the CLI used for media processing and for post-install version checks.
# - libavcodec/libavformat/libavutil 分别覆盖编解码、封装格式和基础工具 API。
#   libavcodec/libavformat/libavutil cover codec, container-format, and utility APIs.
# - libavfilter/libavdevice 提供滤镜图和设备输入输出 API。
#   libavfilter/libavdevice provide filter-graph and device I/O APIs.
# - libswscale/libswresample 提供图像缩放/像素格式转换和音频重采样 API。
#   libswscale/libswresample provide image scaling/pixel conversion and audio resampling.
# 每个 -dev 包都应安装可由 pkg-config 发现的模块；验证阶段会逐项检查。
# Every -dev package should expose a pkg-config module, checked individually later.
FFMPEG_PACKAGES: tuple[str, ...] = (
    "ffmpeg",
    "libavcodec-dev",
    "libavformat-dev",
    "libavutil-dev",
    "libavfilter-dev",
    "libavdevice-dev",
    "libswscale-dev",
    "libswresample-dev",
)

# MySQL 服务端与开发接口 / MySQL server and development interfaces:
# - mysql-server 安装数据库服务；mysql-client 提供 mysql 命令行客户端。
#   mysql-server installs the database service; mysql-client provides the mysql CLI.
# - default-libmysqlclient-dev 提供当前 Ubuntu 默认 MySQL/MariaDB 兼容 C API 的
#   头文件和链接库；libmysqlcppconn-dev 提供 MySQL Connector/C++ 开发文件。
#   default-libmysqlclient-dev supplies headers and libraries for Ubuntu's default
#   MySQL/MariaDB-compatible C API; libmysqlcppconn-dev supplies Connector/C++ files.
# Qt 的 MySQL 插件在 QT5_PACKAGES 中列出，避免重复；服务状态和 Connector/C++
# 头文件会在安装后分别检查。
# The Qt MySQL plugin is listed under QT5_PACKAGES to avoid duplication; service
# status and the Connector/C++ header are checked separately after installation.
MYSQL_PACKAGES: tuple[str, ...] = (
    "mysql-server",
    "mysql-client",
    "default-libmysqlclient-dev",
    "libmysqlcppconn-dev",
)

# 按功能分组定义后再汇总为不可变元组，既保留可读性，也保证预检查清单和实际
# 安装清单来自同一个数据源，避免两者因手工维护而产生偏差。
# Define packages by function and then combine them into one immutable tuple. This
# keeps the list readable and ensures preflight validation and installation consume
# the same source of truth instead of drifting apart through manual maintenance.
ALL_PACKAGES: tuple[str, ...] = (
    *TOOLCHAIN_PACKAGES,
    *QT5_PACKAGES,
    *JSON_PACKAGES,
    *FFMPEG_PACKAGES,
    *MYSQL_PACKAGES,
)

# 版本探测失败时使用统一的双语哨兵文本；验证逻辑也据此把命令加入失败清单。
# Shared bilingual sentinel for failed version detection; verification uses this exact
# value to decide whether a command belongs in the failure list.
NOT_DETECTED = "未检测到 / not detected"


class InstallError(RuntimeError):
    """
    表示可预期、可向用户说明的安装或环境错误。
    Represent an expected installation or environment error suitable for users.

    外部命令失败、平台不受支持、包不可用及安装后验证失败都会转换成该异常；
    main() 统一捕获后将消息写入标准错误并返回退出码 1，从而避免显示 Python
    回溯，同时保留明确的自动化失败信号。
    External-command failures, unsupported platforms, unavailable packages, and
    post-install verification failures are converted to this exception. main()
    catches it, writes the message to stderr, and returns exit code 1, avoiding a
    Python traceback while preserving an unambiguous automation failure signal.
    """


def print_command(command: Sequence[str]) -> None:
    """
    以 shell 可复制形式打印即将处理的命令，并立即刷新输出。
    Print the command in copyable shell form and flush output immediately.

    shlex.join 会对含空格或特殊字符的参数进行引用；前导 ``+`` 让真实执行与
    dry-run 预览使用相同且容易识别的日志格式。
    shlex.join quotes arguments containing spaces or shell metacharacters. The
    leading ``+`` gives real execution and dry-run previews the same recognizable
    log format.
    """
    print("+ " + shlex.join(command), flush=True)


def run_command(
    command: Sequence[str],
    *,
    dry_run: bool,
    env: Mapping[str, str] | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """
    统一记录并运行外部命令，或在 dry-run 中返回模拟成功结果。
    Log and run an external command, or return simulated success in dry-run mode.

    参数 / Parameters:
    - ``command``：已分词的参数序列，不经过 shell 解释，降低注入和转义风险。
      ``command``: a tokenized argument sequence, never interpreted by a shell,
      reducing injection and quoting risks.
    - ``dry_run``：为 True 时仅打印命令，不检查程序是否存在，也不使用 ``env``。
      ``dry_run``: when True, only prints; executable existence is not checked and
      ``env`` is not consumed.
    - ``env``：完整的子进程环境映射；传入时会复制，调用方的映射不会被修改。
      ``env``: complete subprocess environment mapping; copied before use so the
      caller's mapping is not mutated.
    - ``capture_output``：仅在调用方需要分析 stdout/stderr 时建立管道；其余命令
      继承终端，APT 进度和 sudo 提示可直接显示给用户。
      ``capture_output``: creates pipes only when stdout/stderr must be inspected;
      otherwise the terminal is inherited so APT progress and sudo prompts remain visible.
    - ``check``：为 True 时把非零状态交给异常转换；为 False 时返回原始状态，供
      包探测等“非零也是有效查询结果”的调用方自行判断。
      ``check``: converts nonzero status into an exception when True; when False,
      returns the status for probes where a nonzero result is meaningful.

    FileNotFoundError 和启用 ``check`` 后的 CalledProcessError 会包装成 InstallError。
    捕获输出时，失败消息同时附带 stdout/stderr，便于定位 APT 或工具错误。
    FileNotFoundError and, with ``check`` enabled, CalledProcessError are wrapped as
    InstallError. Captured stdout/stderr are appended to failures for diagnosis.
    """
    print_command(command)

    # 预演模式在任何命令查找、权限检查或环境传递之前短路，并构造 returncode=0 的
    # CompletedProcess。因此它适合审阅流程，但不会发现 sudo/APT/网络/包可用性问题。
    # Dry-run short-circuits before command lookup, privilege checks, or environment
    # propagation and constructs a CompletedProcess with returncode=0. It is useful for
    # reviewing the workflow but cannot expose sudo/APT/network/package-availability issues.
    if dry_run:
        return subprocess.CompletedProcess(command, 0, "", "")

    try:
        # shell=False 是 subprocess.run 的默认行为；这里传入参数列表而非命令字符串，
        # 不会经过 shell 展开。仅在调用方需要检查输出时创建管道，否则继承当前终端。
        # subprocess.run defaults to shell=False. Passing an argument list avoids shell
        # expansion. Pipes are created only when output inspection is requested; all other
        # commands inherit the current terminal.
        return subprocess.run(
            list(command),
            check=check,
            text=True,
            env=dict(env) if env is not None else None,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
        )
    except FileNotFoundError as exc:
        raise InstallError(f"找不到命令 / Command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = ""
        if capture_output:
            detail = f"\nstdout:\n{exc.stdout or ''}\nstderr:\n{exc.stderr or ''}"
        raise InstallError(
            f"命令执行失败（退出码 {exc.returncode}）/ Command failed "
            f"(exit code {exc.returncode}): {shlex.join(command)}{detail}"
        ) from exc


def read_os_release() -> dict[str, str]:
    """
    读取并解析 /etc/os-release 中简单的 ``KEY=VALUE`` 记录。
    Read and parse simple ``KEY=VALUE`` records from /etc/os-release.

    空行、注释和不含等号的行会被忽略；值两端的空白及双引号会被移除。返回值
    至少供发行版 ID、版本号、代号和可读名称检测使用。文件不存在时无法安全
    确认平台，因此直接抛出 InstallError。
    Blank lines, comments, and lines without ``=`` are ignored; surrounding whitespace
    and double quotes are removed from values. The result supplies the distribution ID,
    version, codename, and display name used by platform checks. A missing file prevents
    safe identification of the platform and therefore raises InstallError.
    """
    os_release = Path("/etc/os-release")
    if not os_release.is_file():
        raise InstallError(
            "未找到 /etc/os-release，无法确认当前系统是 Ubuntu。 / "
            "/etc/os-release was not found; cannot verify that this system is Ubuntu."
        )

    result: dict[str, str] = {}
    for raw_line in os_release.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # 每行只按第一个等号分隔，保留值中可能存在的后续等号。
        # Split only on the first equals sign so any additional equals signs remain in the value.
        # 空行、注释及不含键值分隔符的非标准行不会参与结果。
        # Blank lines, comments, and nonstandard lines without a key/value separator are omitted.
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def ensure_supported_system() -> dict[str, str]:
    """
    确认内核平台为 Linux 且发行版 ID 为 Ubuntu，并返回系统元数据。
    Confirm a Linux platform with Ubuntu as its distribution ID and return OS metadata.

    检查分两层进行：platform.system() 可快速排除 Windows/macOS，随后读取
    /etc/os-release 防止在其他 Linux 发行版上误用 Ubuntu 包名。版本与代号只
    用于日志展示，当前逻辑并未限定某个 Ubuntu 版本。
    Validation has two layers: platform.system() quickly rejects Windows/macOS, then
    /etc/os-release prevents Ubuntu package names from being used on another Linux
    distribution. Version and codename are logged only; no specific Ubuntu release is
    currently enforced.
    """
    if platform.system() != "Linux":
        raise InstallError("该脚本只能在 Linux/Ubuntu 下运行。 / Ubuntu Linux is required.")

    info = read_os_release()
    if info.get("ID", "").lower() != "ubuntu":
        pretty_name = info.get("PRETTY_NAME", "unknown Linux distribution")
        raise InstallError(
            f"检测到 {pretty_name}；该脚本只针对 Ubuntu APT 包进行测试。 / "
            f"Detected {pretty_name}; this script is tested only with Ubuntu APT packages."
        )

    version = info.get("VERSION_ID", "unknown")
    codename = info.get("VERSION_CODENAME", "unknown")
    print(f"检测到 Ubuntu {version} ({codename}) / Detected Ubuntu {version} ({codename})")
    return info


def get_privilege_prefix(*, dry_run: bool) -> list[str]:
    """
    返回特权命令所需前缀：root 用户为空列表，普通用户为 ``["sudo"]``。
    Return the privileged-command prefix: empty for root, ``["sudo"]`` otherwise.

    非 root 情况下必须能在 PATH 中找到 sudo，并在真实执行前调用 ``sudo -v``
    缓存/刷新凭据。这样可在下载或安装开始前暴露权限问题。dry-run 中同一调用
    只会打印，不会弹出密码提示，也不能证明真实运行时拥有 sudo 权限。
    For a non-root user, sudo must be present in PATH and ``sudo -v`` refreshes/caches
    credentials before real work begins, surfacing permission problems before downloads
    or installation. In dry-run the same call is only printed: it prompts for no password
    and does not prove that sudo will be available during a real run.
    """
    if os.geteuid() == 0:
        return []

    if shutil.which("sudo") is None:
        raise InstallError(
            "当前不是 root，且系统未安装 sudo。请先安装 sudo 或使用 root 运行。 / "
            "The current user is not root and sudo is unavailable; install sudo or run as root."
        )

    # 提前验证 sudo，避免安装中途才首次要求密码；后续命令仍各自带 sudo 前缀，
    # 因而即使凭据缓存策略较短，也会遵守系统自身的 sudo 认证规则。
    # Validate sudo early instead of first prompting halfway through installation. Later
    # commands still carry their own sudo prefix and therefore follow the host's normal
    # authentication policy even when its credential-cache timeout is short.
    run_command(["sudo", "-v"], dry_run=dry_run)
    return ["sudo"]


def apt_environment() -> dict[str, str]:
    """
    从当前环境副本构造用于 APT 相关子进程的非交互环境。
    Build a noninteractive environment for APT-related subprocesses from a copy.

    ``DEBIAN_FRONTEND=noninteractive`` 要求 Debian 配置脚本避免交互式界面；
    ``APT_LISTCHANGES_FRONTEND=none`` 禁止 apt-listchanges 打开交互前端。保留当前
    环境的其余内容，意味着代理、区域设置和 PATH 等已有配置也会传给子进程。
    ``DEBIAN_FRONTEND=noninteractive`` asks Debian package configuration to avoid an
    interactive UI; ``APT_LISTCHANGES_FRONTEND=none`` disables the apt-listchanges
    interactive frontend. Copying the current environment also retains configured proxy,
    locale, PATH, and related settings for the child process.

    注意：这里不会修改系统或用户的永久环境变量。
    Note: this does not modify permanent system or user environment variables.

    当命令经 sudo 执行时，环境首先传给 sudo；sudo 是否继续向 apt-get 保留这些
    变量取决于本机 sudoers 的 env_reset/env_keep 策略。此函数本身不修改 sudoers。
    When a command runs through sudo, this environment first reaches sudo. Whether sudo
    preserves these variables for apt-get depends on the host's sudoers env_reset/env_keep
    policy. This function does not modify sudoers.
    """
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    env["APT_LISTCHANGES_FRONTEND"] = "none"
    return env


def enable_universe(
    privilege_prefix: Sequence[str], *, dry_run: bool, env: Mapping[str, str]
) -> None:
    """
    安装仓库管理工具，并以幂等方式启用 Ubuntu 官方 Universe 组件。
    Install repository-management tooling and idempotently enable official Universe.

    ``software-properties-common`` 提供 ``add-apt-repository``；随后使用 ``-y``
    启用 Universe。已启用时再次调用通常不会重复添加有效条目。索引刷新不在本
    函数内完成，而由 main() 在返回后统一执行，确保新组件的包元数据可查询。
    ``software-properties-common`` supplies ``add-apt-repository``; ``-y`` then enables
    Universe. Re-running it when already enabled normally does not duplicate an active
    entry. Index refresh is intentionally handled by main() after this function returns,
    ensuring metadata from the newly enabled component can be queried.

    ``env`` 与 ``dry_run`` 原样传给统一命令执行器；因此预演只显示这两条命令。
    ``env`` and ``dry_run`` are forwarded unchanged to the common command runner, so a
    preview merely displays both commands.
    """
    run_command(
        [*privilege_prefix, "apt-get", "install", "-y", "software-properties-common"],
        dry_run=dry_run,
        env=env,
    )
    run_command(
        [*privilege_prefix, "add-apt-repository", "-y", "universe"],
        dry_run=dry_run,
        env=env,
    )


def package_is_available(package: str, *, dry_run: bool) -> bool:
    """
    查询当前 APT 索引是否能为指定包返回至少一个版本说明。
    Query whether current APT indexes expose at least one version record for a package.

    真实运行调用 ``apt-cache show --no-all-versions``，并同时要求退出码为 0 且
    stdout 非空。命令使用 ``check=False``，因为“包不存在”的非零状态是查询结果，
    不是需要立即转换为异常的执行故障。该检查依赖最近一次 apt-get update 获得的
    本地元数据，并不验证下载服务器在安装时一定可达。
    Real execution invokes ``apt-cache show --no-all-versions`` and requires both a zero
    status and nonempty stdout. ``check=False`` is intentional because a nonzero status
    for an absent package is a query result, not an execution failure to raise immediately.
    The check relies on local metadata from apt-get update and does not guarantee that the
    download server will remain reachable during installation.
    """
    # 预演模式将任意包视为可用，不查询本机仓库元数据，以便在 Ubuntu/WSL 中安全
    # 审阅后续安装命令；因此该返回值仅用于维持预览流程，不能视为可用性证据。
    # Dry-run treats every package as available and skips local metadata queries so the
    # later install command can be safely reviewed. This return value only keeps the preview
    # flowing and must not be interpreted as evidence that a package actually exists.
    if dry_run:
        return True

    result = run_command(
        ["apt-cache", "show", "--no-all-versions", package],
        dry_run=False,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def ensure_packages_available(packages: Iterable[str], *, dry_run: bool) -> None:
    """
    在安装前逐一验证包名，并将所有不可用项合并成一个错误。
    Validate every package name before installation and combine all misses into one error.

    列表推导会完整检查传入集合，而不是遇到第一个缺失项就停止，便于一次修正
    所有仓库/包名问题。只要存在不可用包便抛出 InstallError，所以真正的
    apt-get install 尚未开始，不会由本脚本造成“已装一部分目标包”的状态。
    The comprehension checks the entire iterable instead of stopping at the first miss,
    allowing all repository/name problems to be fixed together. Any unavailable package
    raises InstallError before this script starts apt-get install, avoiding a script-created
    partial target installation at this preflight stage.
    """
    unavailable = [pkg for pkg in packages if not package_is_available(pkg, dry_run=dry_run)]
    if unavailable:
        joined = ", ".join(unavailable)
        raise InstallError(
            "以下包在当前 Ubuntu 仓库中不可用 / Packages unavailable in the current "
            f"Ubuntu repositories: {joined}"
        )


def install_packages(
    packages: Sequence[str],
    privilege_prefix: Sequence[str],
    *,
    dry_run: bool,
    env: Mapping[str, str],
) -> None:
    """
    使用单次面向无人值守执行的 apt-get 调用安装已通过预检查的完整包序列。
    Install the complete prevalidated package sequence in one apt-get call designed
    for unattended use.

    ``-y`` 自动确认 APT 提示，``--install-recommends`` 明确包含 Ubuntu 推荐依赖；
    包名作为独立参数传递，不进行 shell 拼接。所有包置于同一命令中，使 APT 可以
    整体解析依赖关系。网络、锁冲突、dpkg 配置或磁盘空间导致的非零状态会由
    run_command 转换为 InstallError。
    ``-y`` confirms APT prompts and ``--install-recommends`` explicitly includes Ubuntu's
    recommended dependencies. Package names are separate arguments rather than shell text.
    One command lets APT resolve the dependency set as a whole. Nonzero status from network,
    lock, dpkg-configuration, or disk-space failures becomes InstallError via run_command.

    是否真正无交互还取决于 apt_environment() 中的变量能否通过本机 sudoers 策略
    传递给 apt-get；``-y`` 只自动确认常规 APT 问题，并不能替代所有 debconf 前端设置。
    Fully unattended behavior still depends on the variables from apt_environment() surviving
    the host's sudoers policy. ``-y`` answers normal APT confirmations but does not replace all
    debconf frontend settings.
    """
    command = [
        *privilege_prefix,
        "apt-get",
        "install",
        "-y",
        "--install-recommends",
        *packages,
    ]
    run_command(command, dry_run=dry_run, env=env)


def first_existing_command(candidates: Sequence[str]) -> str | None:
    """
    按候选顺序返回 PATH 中首个可执行命令的解析路径，否则返回 None。
    Return the resolved path of the first executable found in PATH, or None.

    顺序具有优先级语义：验证 Qt 时优先采用常见的 ``qmake``，仅在找不到时尝试
    ``qmake-qt5``，以兼容不同 Ubuntu/Qt 打包方式。
    Candidate order defines preference: Qt verification tries the conventional ``qmake``
    first and falls back to ``qmake-qt5`` for Ubuntu/Qt packaging variations.
    """
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def get_first_line(command: Sequence[str]) -> str:
    """
    运行版本探测命令，并返回合并输出中的第一条非空结果行。
    Run a version probe and return the first line of its combined output.

    stderr 合并到 stdout，可兼容把版本信息写往任一流的工具。命令不存在、退出
    状态非零或成功但无输出时返回统一的 NOT_DETECTED。此辅助函数只在安装后验证
    中调用，故不使用 dry-run 命令执行器，也不会抛出 InstallError 中断剩余检查。
    stderr is merged into stdout to support tools that report versions on either stream.
    A missing command, nonzero status, or empty successful output returns NOT_DETECTED.
    This helper is used only during post-install verification, so it bypasses the dry-run
    runner and does not raise InstallError before the remaining checks can be collected.
    """
    try:
        result = subprocess.run(
            list(command),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return NOT_DETECTED

    lines = result.stdout.strip().splitlines()
    return lines[0] if lines else NOT_DETECTED


def pkg_config_has(module: str) -> bool:
    """
    静默检查 pkg-config 是否能解析指定开发模块。
    Silently check whether pkg-config can resolve a development module.

    如果 pkg-config 本身不在 PATH 中立即返回 False；否则使用 ``--exists``，丢弃
    两个输出流并以退出码判断。该检查验证模块元数据的可发现性，不会编译或链接
    示例程序，因此不能覆盖 ABI、编译器选项或运行时加载问题。
    Return False immediately when pkg-config is absent from PATH. Otherwise ``--exists``
    is used with both streams discarded and the status code decides the result. This tests
    metadata discoverability, not compilation or linking, so ABI, compiler-option, and
    runtime-loading problems remain outside its scope.
    """
    if shutil.which("pkg-config") is None:
        return False
    return subprocess.run(
        ["pkg-config", "--exists", module],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def verify_installation(*, dry_run: bool) -> None:
    """
    汇总验证主要命令、开发模块、头文件、Qt 插件和 MySQL 服务状态。
    Aggregate checks for key commands, development modules, headers, the Qt plugin,
    and MySQL service state.

    验证采用“尽量检查完再报告”的策略：每个失败项加入 ``verification_failures``，
    最后去重并一次抛出 InstallError。这既给交互用户完整摘要，也确保自动化调用在
    任一必需组件缺失时收到失败退出码。检查范围包括：
    Verification follows a collect-then-report strategy: each miss is appended to
    ``verification_failures`` and the final list is deduplicated before one InstallError
    is raised. Interactive users receive a complete summary, while automation receives a
    failure status whenever a required component is missing. Coverage includes:

    - GCC/G++/CMake/GDB/Git/FFmpeg/MySQL 客户端版本命令；
      GCC/G++/CMake/GDB/Git/FFmpeg/MySQL-client version commands;
    - qmake 返回的 Qt 版本，以及 Qt5/FFmpeg 的 pkg-config 模块；
      the Qt version returned by qmake and Qt5/FFmpeg pkg-config modules;
    - nlohmann/json、Connector/C++ 头文件和 Qt MySQL 驱动插件的预期路径；
      expected paths for nlohmann/json, Connector/C++, and the Qt MySQL driver;
    - 可使用 systemctl 时 MySQL 服务是否为 ``active``。
      whether MySQL is ``active`` when systemctl can be used.

    dry-run 会在任何探测前返回，因为预演并未安装软件；运行这些检查只会反映预演
    前主机的旧状态，容易造成误导。该验证确认关键制品存在且可发现，但不是完整的
    编译、数据库连接或媒体处理集成测试。
    dry-run returns before any probe because no software was installed; probing would only
    describe the host's pre-preview state and would be misleading. Verification confirms
    key artifacts are present and discoverable, but it is not a full compile, database-
    connection, or media-processing integration test.
    """
    # 预演不读取当前安装状态，也不会因当前主机缺少目标组件而失败；它仅确认脚本
    # 能生成预期命令并保持系统不变。
    # Preview mode reads no installation state and does not fail merely because the current
    # host lacks target components; it confirms command generation while leaving the host unchanged.
    if dry_run:
        print("\nDry-run 完成：系统未发生更改。 / Dry run completed; no changes were made.")
        return

    print("\n========== 安装验证 / Installation verification ==========")
    verification_failures: list[str] = []

    # 读取各工具版本输出的第一行，既确认命令可执行，也提供简洁摘要。版本号本身
    # 不与最低版本阈值比较，因此这里只验证“已安装且能启动”。
    # Read the first version-output line to confirm each command starts and to provide a concise
    # summary. No minimum-version threshold is compared; this verifies presence/executability only.
    checks = (
        ("GCC", ["gcc", "--version"]),
        ("G++", ["g++", "--version"]),
        ("CMake", ["cmake", "--version"]),
        ("GDB", ["gdb", "--version"]),
        ("Git", ["git", "--version"]),
        ("FFmpeg", ["ffmpeg", "-version"]),
        ("MySQL client", ["mysql", "--version"]),
    )
    for name, command in checks:
        version = get_first_line(command)
        print(f"{name}: {version}")
        if version == NOT_DETECTED:
            verification_failures.append(name)

    # 不同 Ubuntu 版本可能使用 qmake 或 qmake-qt5 作为命令名。找到命令后通过
    # ``-query QT_VERSION`` 读取 Qt 自报版本；路径会一并打印以便识别实际工具链。
    # Ubuntu releases may expose qmake or qmake-qt5. Once found, ``-query QT_VERSION``
    # obtains Qt's reported version and the resolved path identifies the selected toolchain.
    qmake = first_existing_command(("qmake", "qmake-qt5"))
    if qmake:
        qt_version = get_first_line([qmake, "-query", "QT_VERSION"])
        print(f"Qt: {qt_version} ({qmake})")
        if qt_version == NOT_DETECTED:
            verification_failures.append("Qt qmake")
    else:
        print("Qt: 未检测到 qmake / qmake not detected")
        verification_failures.append("Qt qmake")

    # pkg-config 检查确认构建系统能够发现所需 Qt 和 FFmpeg 开发模块。所有缺失项
    # 按模块名记录，避免只显示笼统的“Qt/FFmpeg 失败”。
    # pkg-config checks confirm build systems can discover the required Qt and FFmpeg modules.
    # Each missing module is recorded by name instead of reporting only a generic framework failure.
    qt_modules = ("Qt5Core", "Qt5Widgets", "Qt5Sql", "Qt5Network")
    ffmpeg_modules = (
        "libavcodec",
        "libavformat",
        "libavutil",
        "libavfilter",
        "libavdevice",
        "libswscale",
        "libswresample",
    )

    missing_qt = [module for module in qt_modules if not pkg_config_has(module)]
    missing_ffmpeg = [module for module in ffmpeg_modules if not pkg_config_has(module)]
    verification_failures.extend(f"Qt pkg-config: {module}" for module in missing_qt)
    verification_failures.extend(f"FFmpeg pkg-config: {module}" for module in missing_ffmpeg)

    print(
        "Qt pkg-config 模块 / Qt pkg-config modules: "
        + ("全部可用 / all available" if not missing_qt else "缺少 / missing: " + ", ".join(missing_qt))
    )
    print(
        "FFmpeg pkg-config 模块 / FFmpeg pkg-config modules: "
        + (
            "全部可用 / all available"
            if not missing_ffmpeg
            else "缺少 / missing: " + ", ".join(missing_ffmpeg)
        )
    )

    # 头文件和插件检查覆盖没有独立可执行命令/pkg-config 项的库组件。JSON 与
    # Connector/C++ 使用明确路径；Qt 插件则在 /usr/lib 的架构子目录中使用 glob，
    # 兼容 x86_64-linux-gnu、aarch64-linux-gnu 等多架构目录名称。
    # Header/plugin checks cover components without a standalone executable or dedicated
    # pkg-config entry. JSON and Connector/C++ use known paths; the Qt plugin is globbed under
    # /usr/lib architecture directories to accommodate names such as x86_64- or aarch64-linux-gnu.
    json_header = Path("/usr/include/nlohmann/json.hpp")
    connector_header = Path("/usr/include/mysql_driver.h")
    qt_mysql_plugin_candidates = tuple(Path("/usr/lib").glob("*/qt5/plugins/sqldrivers/libqsqlmysql.so"))

    if not json_header.is_file():
        verification_failures.append("nlohmann/json header")
    if not connector_header.is_file():
        verification_failures.append("MySQL Connector/C++ header")
    if not qt_mysql_plugin_candidates:
        verification_failures.append("Qt MySQL driver")

    print(
        "nlohmann/json: "
        + (str(json_header) if json_header.is_file() else "未找到头文件 / header not found")
    )
    print(
        "MySQL Connector/C++: "
        + (str(connector_header) if connector_header.is_file() else "未找到头文件 / header not found")
    )
    print(
        "Qt MySQL driver: "
        + (
            str(qt_mysql_plugin_candidates[0])
            if qt_mysql_plugin_candidates
            else "未找到插件 / plugin not found"
        )
    )

    # systemctl 在未启用 systemd 的 WSL 实例中可能不存在或无法返回状态。命令存在
    # 且明确返回状态时，只有 ``active`` 通过；inactive/failed 等状态进入失败清单。
    # 若没有输出则只提示无法查询，不把 WSL 的 systemd 配置差异误判成安装缺失。
    # systemctl may be absent or unable to report status when WSL runs without systemd. When
    # it exists and reports a state, only ``active`` passes; inactive/failed states are failures.
    # Empty output produces a query warning rather than treating WSL's systemd setup as a missing install.
    if shutil.which("systemctl"):
        mysql_result = subprocess.run(
            ["systemctl", "is-active", "mysql"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        mysql_state = mysql_result.stdout.strip()
        if mysql_state:
            print(f"MySQL service: {mysql_state}")
            if mysql_state != "active":
                verification_failures.append(f"MySQL service ({mysql_state})")
        else:
            print(
                "MySQL service: 无法通过 systemctl 检测（WSL 中可能未启用 systemd） / "
                "could not query systemctl (systemd may be disabled in WSL)"
            )

    # dict.fromkeys 在保留首次出现顺序的同时去重，使错误稳定且避免同一根因重复显示。
    # dict.fromkeys deduplicates while preserving first-seen order, keeping diagnostics stable
    # and preventing the same underlying miss from being printed repeatedly.
    if verification_failures:
        details = ", ".join(dict.fromkeys(verification_failures))
        raise InstallError(
            "安装验证失败，以下组件不可用 / Installation verification failed; "
            f"the following components are unavailable: {details}"
        )

    print("\n安装完成。脚本未修改 PATH、.bashrc、.profile 或 /etc/environment。")
    print("Installation completed without modifying PATH or shell environment files.")


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行选项并返回 argparse 命名空间。
    Parse command-line options and return an argparse namespace.

    ``--dry-run`` 控制所有会修改仓库或安装软件的统一执行路径，并让安装验证提前
    返回；``--skip-update`` 只控制 main() 中首次索引刷新。argparse 自行处理
    ``--help``、未知参数及其标准退出行为，因而这些情况发生在 main() 的异常处理前。
    ``--dry-run`` controls every repository-mutating or package-installing command path and
    causes verification to return early. ``--skip-update`` controls only the first index
    refresh in main(). argparse handles ``--help``, unknown arguments, and their standard
    exits before main() enters its installation-error handling block.
    """
    parser = argparse.ArgumentParser(
        description=(
            "在 Ubuntu 上安装 C++/Qt5/FFmpeg/MySQL 开发环境。 / "
            "Install a C++/Qt5/FFmpeg/MySQL development environment on Ubuntu."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示命令，不修改系统 / print commands without changing the system",
    )
    parser.add_argument(
        "--skip-update",
        action="store_true",
        help="跳过第一次 apt-get update / skip the initial apt-get update",
    )
    return parser.parse_args()


def main() -> int:
    """
    编排平台检查、仓库准备、包预检查、安装及安装后验证。
    Orchestrate platform checks, repository preparation, package preflight,
    installation, and post-install verification.

    返回值专为 shell/CI 调用设计 / Return values are designed for shell/CI callers:
    - ``0``：流程完整成功，或 dry-run 已安全生成全部命令。
      ``0``: the full workflow succeeded, or dry-run safely generated all commands.
    - ``1``：InstallError 表示受支持的失败路径，例如平台错误、命令失败、包不可用
      或验证缺失；错误详情写入 stderr。
      ``1``: InstallError represents a handled failure such as an unsupported platform,
      failed command, unavailable package, or missing verification target; details go to stderr.
    - ``130``：捕获 KeyboardInterrupt，遵循常见的 128 + SIGINT(2) 约定。
      ``130``: KeyboardInterrupt, following the conventional 128 + SIGINT(2) status.

    未预期的编程错误不会被宽泛捕获，因而仍会显示回溯，避免把脚本缺陷伪装成
    普通安装错误。
    Unexpected programming errors are not broadly caught, so they retain a traceback rather
    than being disguised as ordinary installation failures.
    """
    args = parse_arguments()

    try:
        ensure_supported_system()
        privilege_prefix = get_privilege_prefix(dry_run=args.dry_run)
        env = apt_environment()

        # 默认先刷新现有索引，再安装 add-apt-repository 所需工具并启用 Universe。
        # --skip-update 仅省略第一次刷新；无论该选项如何，Universe 操作之后都再次
        # update，以便 apt-cache 和安装阶段看到新启用组件中的最新元数据。
        # By default, refresh existing indexes before installing repository tooling and enabling
        # Universe. --skip-update omits only that first refresh. An update always follows the
        # Universe operation so apt-cache and installation can see metadata from the new component.
        print("\n========== 准备 Ubuntu 官方仓库 / Preparing official repositories ==========")
        if not args.skip_update:
            run_command(
                [*privilege_prefix, "apt-get", "update"],
                dry_run=args.dry_run,
                env=env,
            )

        enable_universe(privilege_prefix, dry_run=args.dry_run, env=env)
        run_command(
            [*privilege_prefix, "apt-get", "update"],
            dry_run=args.dry_run,
            env=env,
        )

        # 在开始安装前一次性检查所有包名，避免安装到一半才发现某个名称不属于当前
        # Ubuntu 版本/已启用组件。dry-run 中这些查询按设计短路为“可用”。
        # Validate every package name before installation so a name absent from the current
        # Ubuntu release/enabled components is found before installation. These probes
        # intentionally short-circuit to “available” during dry-run.
        print("\n========== 检查软件包 / Checking packages ==========")
        ensure_packages_available(ALL_PACKAGES, dry_run=args.dry_run)

        print("\n========== 安装开发环境 / Installing development environment ==========")
        install_packages(
            ALL_PACKAGES,
            privilege_prefix,
            dry_run=args.dry_run,
            env=env,
        )

        # 真实安装后执行制品/服务验证；dry-run 在 verify_installation 内打印安全完成
        # 消息并立即返回。只有所有必需检查通过后，main 才返回成功状态 0。
        # After a real install, verify artifacts and service state. In dry-run,
        # verify_installation prints a safe-completion message and returns immediately. main
        # reaches success status 0 only after all required real-install checks have passed.
        verify_installation(dry_run=args.dry_run)
        return 0

    # Ctrl+C 与可预期安装错误使用不同退出码，便于调用脚本区分“用户取消”和“执行失败”。
    # Ctrl+C and handled installation errors use distinct statuses so callers can distinguish
    # user cancellation from an execution failure.
    except KeyboardInterrupt:
        print("\n用户取消安装。 / Installation cancelled by user.", file=sys.stderr)
        return 130
    except InstallError as exc:
        print(f"\n错误 / Error: {exc}", file=sys.stderr)
        return 1


# 通过 SystemExit 将 main() 的整数状态原样交给操作系统；模块被导入时不会自动执行。
# SystemExit forwards main()'s integer status to the OS; importing the module performs no run.
if __name__ == "__main__":
    raise SystemExit(main())
