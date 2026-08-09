#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 Ubuntu 上自动安装 C++/Qt5/FFmpeg/MySQL 开发环境。
Automatically install a C++/Qt5/FFmpeg/MySQL development environment on Ubuntu.

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

# qtbase5-dev 提供 Qt5Core、Qt5Widgets、Qt5Sql 和 Qt5Network 的头文件与库。
# qtbase5-dev provides headers and libraries for Qt5Core, Qt5Widgets,
# Qt5Sql, and Qt5Network.
QT5_PACKAGES: tuple[str, ...] = (
    "qtbase5-dev",
    "qtbase5-dev-tools",
    "qt5-qmake",
    "qtchooser",
    "libqt5sql5-mysql",
)

# 现代 C++ JSON 头文件库 / Modern C++ JSON header-only library
JSON_PACKAGES: tuple[str, ...] = (
    "nlohmann-json3-dev",
)

# FFmpeg 命令行工具和常用开发模块 / FFmpeg CLI and common development modules
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

# MySQL 服务端、C/C++ 开发包及 Qt SQL MySQL 插件。
# MySQL server, C/C++ development packages, and Qt SQL MySQL plugin.
MYSQL_PACKAGES: tuple[str, ...] = (
    "mysql-server",
    "mysql-client",
    "default-libmysqlclient-dev",
    "libmysqlcppconn-dev",
)

# 汇总所有软件包，便于统一检查并通过一次 apt-get 调用完成安装。
# Collect all packages so they can be validated and installed in one apt-get call.
ALL_PACKAGES: tuple[str, ...] = (
    *TOOLCHAIN_PACKAGES,
    *QT5_PACKAGES,
    *JSON_PACKAGES,
    *FFMPEG_PACKAGES,
    *MYSQL_PACKAGES,
)

NOT_DETECTED = "未检测到 / not detected"


class InstallError(RuntimeError):
    """安装失败时抛出的异常。 / Raised when installation fails."""


def print_command(command: Sequence[str]) -> None:
    """以可复制形式打印命令。 / Print a command in copyable shell form."""
    print("+ " + shlex.join(command), flush=True)


def run_command(
    command: Sequence[str],
    *,
    dry_run: bool,
    env: Mapping[str, str] | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """运行外部命令。 / Run an external command."""
    print_command(command)

    # 预演模式只打印命令，并返回一个模拟的成功结果，不启动任何子进程。
    # Dry-run mode only prints the command and returns a simulated successful result.
    if dry_run:
        return subprocess.CompletedProcess(command, 0, "", "")

    try:
        # 仅在调用方需要检查输出时创建管道，否则让命令直接使用当前终端。
        # Create pipes only when the caller needs the output; otherwise inherit the terminal.
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
    """读取 /etc/os-release。 / Read /etc/os-release."""
    os_release = Path("/etc/os-release")
    if not os_release.is_file():
        raise InstallError(
            "未找到 /etc/os-release，无法确认当前系统是 Ubuntu。 / "
            "/etc/os-release was not found; cannot verify that this system is Ubuntu."
        )

    result: dict[str, str] = {}
    for raw_line in os_release.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # 忽略空行、注释及不含键值分隔符的非标准行。
        # Ignore blank lines, comments, and nonstandard lines without a key/value separator.
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def ensure_supported_system() -> dict[str, str]:
    """确认脚本运行于 Ubuntu。 / Ensure that the script is running on Ubuntu."""
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
    """返回 root 命令前缀。 / Return the prefix used for privileged commands."""
    if os.geteuid() == 0:
        return []

    if shutil.which("sudo") is None:
        raise InstallError(
            "当前不是 root，且系统未安装 sudo。请先安装 sudo 或使用 root 运行。 / "
            "The current user is not root and sudo is unavailable; install sudo or run as root."
        )

    # 提前验证 sudo，避免安装中途才要求密码。
    # Validate sudo early so installation does not fail halfway through.
    run_command(["sudo", "-v"], dry_run=dry_run)
    return ["sudo"]


def apt_environment() -> dict[str, str]:
    """
    创建仅对 apt 子进程生效的环境变量。
    Create environment variables that apply only to apt subprocesses.

    注意：这里不会修改系统或用户的永久环境变量。
    Note: this does not modify permanent system or user environment variables.
    """
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    env["APT_LISTCHANGES_FRONTEND"] = "none"
    return env


def enable_universe(
    privilege_prefix: Sequence[str], *, dry_run: bool, env: Mapping[str, str]
) -> None:
    """启用 Ubuntu Universe 官方仓库。 / Enable Ubuntu's official Universe repository."""
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
    """检查 APT 是否能找到包。 / Check whether APT can find a package."""
    # 预演模式不查询本机仓库元数据，以便在非 Ubuntu 主机上审阅命令。
    # Skip local repository queries in dry-run mode so commands can be reviewed elsewhere.
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
    """安装前检查全部包名。 / Validate all package names before installation."""
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
    """通过 apt-get 安装软件包。 / Install packages through apt-get."""
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
    """返回第一个存在的命令。 / Return the first command found in PATH."""
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def get_first_line(command: Sequence[str]) -> str:
    """读取命令输出的第一行。 / Read the first line of command output."""
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
    """检查 pkg-config 模块是否存在。 / Check whether a pkg-config module exists."""
    if shutil.which("pkg-config") is None:
        return False
    return subprocess.run(
        ["pkg-config", "--exists", module],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def verify_installation(*, dry_run: bool) -> None:
    """验证主要命令、头文件和模块。 / Verify key commands, headers, and modules."""
    if dry_run:
        print("\nDry-run 完成：系统未发生更改。 / Dry run completed; no changes were made.")
        return

    print("\n========== 安装验证 / Installation verification ==========")
    verification_failures: list[str] = []

    # 读取各工具版本输出的第一行，提供简洁的安装结果摘要。
    # Read the first version-output line from each tool for a concise installation summary.
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

    # 不同 Ubuntu 版本可能使用 qmake 或 qmake-qt5 作为命令名。
    # Ubuntu releases may expose the command as either qmake or qmake-qt5.
    qmake = first_existing_command(("qmake", "qmake-qt5"))
    if qmake:
        qt_version = get_first_line([qmake, "-query", "QT_VERSION"])
        print(f"Qt: {qt_version} ({qmake})")
        if qt_version == NOT_DETECTED:
            verification_failures.append("Qt qmake")
    else:
        print("Qt: 未检测到 qmake / qmake not detected")
        verification_failures.append("Qt qmake")

    # pkg-config 检查可确认编译器能够发现所需 Qt 和 FFmpeg 开发模块。
    # pkg-config checks confirm that the compiler can discover the required development modules.
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

    # 头文件和插件检查用于覆盖没有独立可执行命令的库组件。
    # Header and plugin checks cover library components that have no standalone executable.
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

    # systemctl 在未启用 systemd 的 WSL 实例中可能不存在或无法返回状态。
    # systemctl may be absent or unable to report status when WSL runs without systemd.
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

    if verification_failures:
        details = ", ".join(dict.fromkeys(verification_failures))
        raise InstallError(
            "安装验证失败，以下组件不可用 / Installation verification failed; "
            f"the following components are unavailable: {details}"
        )

    print("\n安装完成。脚本未修改 PATH、.bashrc、.profile 或 /etc/environment。")
    print("Installation completed without modifying PATH or shell environment files.")


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数。 / Parse command-line arguments."""
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
    """程序入口。 / Program entry point."""
    args = parse_arguments()

    try:
        ensure_supported_system()
        privilege_prefix = get_privilege_prefix(dry_run=args.dry_run)
        env = apt_environment()

        # 先刷新索引并启用官方 Universe 仓库，以覆盖脚本所需的软件包。
        # Refresh package indexes and enable the official Universe repository first.
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

        # 在开始安装前一次性检查所有包名，避免安装到一半才发现缺失项。
        # Validate every package name before installation to avoid a partial setup.
        print("\n========== 检查软件包 / Checking packages ==========")
        ensure_packages_available(ALL_PACKAGES, dry_run=args.dry_run)

        print("\n========== 安装开发环境 / Installing development environment ==========")
        install_packages(
            ALL_PACKAGES,
            privilege_prefix,
            dry_run=args.dry_run,
            env=env,
        )

        verify_installation(dry_run=args.dry_run)
        return 0

    except KeyboardInterrupt:
        print("\n用户取消安装。 / Installation cancelled by user.", file=sys.stderr)
        return 130
    except InstallError as exc:
        print(f"\n错误 / Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
