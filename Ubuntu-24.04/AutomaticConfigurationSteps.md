# 安装 Ubuntu 24.04 LTS（WSL 2）/ Install Ubuntu 24.04 LTS on WSL 2

综合兼容性和稳定性，安装 **Ubuntu 24.04 LTS** 最合适。

For a balance of compatibility and stability, **Ubuntu 24.04 LTS** is the recommended distribution here.

以下命令应在 **Windows PowerShell** 中运行，而不是在 Ubuntu Shell 中运行。建议使用管理员权限打开 PowerShell；命令需要联网下载 WSL 更新和 Ubuntu 发行版，并会更改 Windows 的 WSL/虚拟化相关组件。开始前请保存其他 WSL 发行版中尚未保存的工作。

Run the following commands in **Windows PowerShell**, not in an Ubuntu shell. Opening PowerShell as an administrator is recommended. The commands require Internet access to download WSL updates and the Ubuntu distribution, and they can change WSL/virtualization components in Windows. Save any unsaved work in other WSL distributions before starting.

```powershell
# 将 Windows 上的 WSL 组件更新到可用的新版本。/ Update the WSL components on Windows to the latest available version.
wsl --update
# 下载并安装名为 Ubuntu-24.04 的发行版。/ Download and install the distribution named Ubuntu-24.04.
wsl --install -d Ubuntu-24.04
```

`wsl --update` 通常可以安全地重复执行；已经安装目标发行版时，再次执行安装命令可能报告该发行版已存在，而不是创建同名副本。根据 Windows 和 WSL 当前状态，安装程序可能要求重启。若出现重启提示，请先重启 Windows，再继续首次启动 Ubuntu；首次启动通常还会要求创建 Linux 用户名和密码。

`wsl --update` is generally safe to run repeatedly. If the target distribution is already installed, running the install command again may report that it already exists rather than create a duplicate. Depending on the current Windows and WSL state, a Windows restart may be required. If prompted, restart Windows before continuing with the first Ubuntu launch; the first launch normally asks you to create a Linux username and password.

安装完成后检查 / Verify the installation：

仍在 Windows PowerShell 中运行以下只读命令。列表中的 `NAME` 应包含 `Ubuntu-24.04`，`VERSION` 应显示 `2`；星号表示当前默认发行版。

Run this read-only command in Windows PowerShell. The `NAME` column should include `Ubuntu-24.04`, and `VERSION` should show `2`; an asterisk marks the current default distribution.

```powershell
# 列出已安装发行版、运行状态和 WSL 版本。/ List installed distributions, their state, and their WSL version.
wsl -l -v
```

进入 Ubuntu 后检查版本 / Verify the Ubuntu release inside Ubuntu：

打开已安装的 Ubuntu 终端后运行以下命令。它只读取发行版标识文件，不需要 `sudo`，也不会修改系统。

Open the installed Ubuntu terminal and run the following command. It only reads the distribution identification file, requires no `sudo`, and does not modify the system.

```bash
# 显示 Ubuntu 发行版名称、版本和代号。/ Display the Ubuntu distribution name, version, and codename.
cat /etc/os-release
```

预计显示 / Expected entry：

```text
VERSION="24.04.x LTS (Noble Numbat)"
```

补丁版本 `x` 会随 Ubuntu 更新而变化，只要主版本为 `24.04 LTS` 即符合本文档目标。

The patch component represented by `x` changes as Ubuntu is updated; a main release of `24.04 LTS` satisfies the target of this guide.
