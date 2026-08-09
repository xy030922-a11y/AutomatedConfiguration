# Ubuntu 常用软件包 / Useful Ubuntu packages

本文命令应在 Ubuntu Bash 中执行。`sudo` 会以管理员权限修改系统级软件包，可能要求输入当前 Linux 用户密码；`apt install -y` 会自动确认安装提示，因此执行前应先检查软件包列表。APT 安装通常具有幂等性：重复运行会保留满足版本要求的已安装软件包，但仍可能根据当前仓库状态安装依赖或升级相关包。

Run these commands in Ubuntu Bash. `sudo` modifies system-wide packages with administrator privileges and may ask for the current Linux user's password. `apt install -y` automatically confirms installation prompts, so review each package list first. APT installation is generally idempotent: repeated runs keep installed packages that already satisfy the requested version, although dependencies or related packages may still be installed or upgraded according to current repository state.

所有安装命令都需要可用的 APT 软件源和网络连接；如果使用 WSL 代理，请先确认代理端口和协议与 `ProxyConfiguration.md` 中的配置一致。除非 APT 或系统明确提示，安装以下用户态工具通常不需要重启 Windows 或 WSL。

All installation commands require reachable APT repositories and network access. When using a WSL proxy, first verify that its port and protocol match the configuration in `ProxyConfiguration.md`. Installing these user-space tools normally does not require restarting Windows or WSL unless APT or the system explicitly says otherwise.

## 一、基础命令行工具 / 1. Basic command-line tools

以下命令一次安装常用终端工具。反斜杠 `\` 表示命令在下一行继续，复制时应保留每行末尾的反斜杠。

The following command installs common terminal utilities in one operation. A trailing backslash `\` continues the command on the next line; preserve each trailing backslash when copying it.

```bash
# 以管理员权限安装基础工具，并自动确认 APT 提示。/ Install basic tools as administrator and automatically confirm APT prompts.
sudo apt install -y \
    tree \
    curl \
    wget \
    git \
    vim \
    nano \
    less \
    tmux \
    man-db \
    bash-completion
```

| 软件包 / Package | 用途 / Purpose |
| --- | --- |
| `tree` | 树状显示目录结构。 / Display directory structures as a tree. |
| `curl` | 发送 HTTP/API 请求和下载文件。 / Send HTTP/API requests and download files. |
| `wget` | 下载文件或递归抓取资源。 / Download files or retrieve resources recursively. |
| `git` | 分布式版本控制。 / Distributed version control. |
| `vim` / `nano` | 在终端中编辑文本文件。 / Edit text files in a terminal. |
| `less` | 分页查看长文本，且不改动原文件。 / Page through long text without modifying the source file. |
| `tmux` | 管理终端会话，终端断开后会话中的程序仍可运行。 / Manage terminal sessions so programs can continue after disconnection. |
| `man-db` | 提供 `man` 手册查询基础设施。 / Provide the infrastructure used by `man` pages. |
| `bash-completion` | 提供 Bash 命令和参数补全。 / Provide Bash command and argument completion. |

---

## 二、文件、文本和搜索工具 / 2. File, text, and search tools

这组软件包会安装搜索、筛选、同步、磁盘分析和压缩工具。它们只提供命令，不会在安装时自动扫描或修改用户文件。

This group installs tools for searching, filtering, synchronization, disk analysis, and archives. Installation only provides the commands; it does not automatically scan or modify user files.

```bash
# 安装文件处理、搜索和归档工具。/ Install file-processing, search, and archive tools.
sudo apt install -y \
    jq \
    ripgrep \
    fd-find \
    fzf \
    bat \
    ncdu \
    rsync \
    zip \
    unzip \
    p7zip-full
```

| 命令 / Command | 用途 / Purpose | 示例 / Example |
| --- | --- | --- |
| `jq` | 格式化、筛选和查询 JSON。 / Format, filter, and query JSON. | `cat data.json \| jq` |
| `rg` | 比 `grep -r` 更方便地递归搜索代码。 / Recursively search source code with a convenient interface. | `rg "TcpServer" src/` |
| `fdfind` | 更简单的 `find` 替代工具。 / A simpler alternative to `find`. | `fdfind CMakeLists` |
| `fzf` | 交互式模糊搜索。 / Interactive fuzzy search. | `history \| fzf` |
| `batcat` | 带语法高亮和分页功能的 `cat` 替代工具。 / A `cat` alternative with syntax highlighting and paging. | `batcat main.cpp` |
| `ncdu` | 交互式分析磁盘空间占用。 / Analyze disk usage interactively. | `ncdu ~` |
| `rsync` | 高效复制和同步文件或目录。 / Efficiently copy and synchronize files or directories. | `rsync -av src/ backup/` |
| `unzip` | 解压 ZIP 文件。 / Extract ZIP archives. | |
| `7z` | 处理 7z、ZIP 等压缩格式。 / Process 7z, ZIP, and other archive formats. | |

Ubuntu 中有两个特殊命令名 / Ubuntu exposes two commands under distribution-specific names：

以下内容只是命令名称，不需要执行；Debian/Ubuntu 使用这些名称是为了避免与其他软件包中的命令冲突。

The following lines are command names, not commands that must be run. Debian/Ubuntu uses these names to avoid conflicts with commands from other packages.

```bash
fdfind
batcat
```

可以在 `~/.bashrc` 中添加别名。别名只影响当前 Linux 用户的交互式 Bash，不需要管理员权限；在文件中重复添加同名行会产生重复定义，最后执行的定义生效。

Aliases can be added to `~/.bashrc`. They affect only the current Linux user's interactive Bash sessions and require no administrator privileges. Adding the same alias lines repeatedly creates duplicate definitions; the last definition executed takes effect.

```bash
# 将简短的 fd 命令映射到 Ubuntu 提供的 fdfind。/ Map the shorter fd name to Ubuntu's fdfind command.
alias fd='fdfind'
# 将简短的 bat 命令映射到 Ubuntu 提供的 batcat。/ Map the shorter bat name to Ubuntu's batcat command.
alias bat='batcat'
```

然后执行 / Then run：

`source` 会在当前 Shell 中重新执行整个 `.bashrc`，包括其中其他命令；如果配置文件中存在有副作用的内容，也会再次触发。

`source` re-executes the entire `.bashrc` in the current shell, including all other commands in it. Any entries with side effects run again.

```bash
# 不关闭终端，立即重新加载 Bash 配置。/ Reload the Bash configuration immediately without closing the terminal.
source ~/.bashrc
```

---

## 三、C/C++ 开发工具 / 3. C/C++ development tools

这组软件包包含编译器、构建系统、调试器、分析器和静态检查工具。安装会占用额外磁盘空间，但不会自动编译或修改现有项目。

This group contains compilers, build systems, debuggers, profilers, and static-analysis tools. Installation consumes additional disk space but does not automatically build or modify existing projects.

```bash
# 安装 C/C++ 构建、调试与代码检查工具。/ Install C/C++ build, debugging, and code-analysis tools.
sudo apt install -y \
    build-essential \
    cmake \
    ninja-build \
    gdb \
    valgrind \
    strace \
    ltrace \
    pkg-config \
    clang \
    clangd \
    clang-format \
    clang-tidy \
    shellcheck
```

| 软件包 / Package | 用途 / Purpose |
| --- | --- |
| `build-essential` | 安装 GCC、G++、Make 和标准开发文件。 / Install GCC, G++, Make, and standard development files. |
| `cmake` | 提供 CMake 构建系统。 / Provide the CMake build system. |
| `ninja-build` | 提供通常比 Make 更快的 Ninja 构建后端。 / Provide Ninja, a build backend that is often faster than Make. |
| `gdb` | 调试 C/C++ 程序。 / Debug C/C++ programs. |
| `valgrind` | 检查内存泄漏和非法内存访问。 / Detect memory leaks and invalid memory access. |
| `strace` | 跟踪进程的系统调用。 / Trace process system calls. |
| `ltrace` | 跟踪动态库函数调用。 / Trace dynamic-library function calls. |
| `pkg-config` | 查询第三方库头文件和链接参数。 / Query compiler and linker flags for third-party libraries. |
| `clang` | 提供 Clang C/C++ 编译器。 / Provide the Clang C/C++ compiler. |
| `clangd` | 为 VS Code 等编辑器提供 C/C++ 补全和跳转。 / Provide C/C++ completion and navigation for editors such as VS Code. |
| `clang-format` | 按规则格式化 C/C++ 代码。 / Format C/C++ code according to style rules. |
| `clang-tidy` | 对 C/C++ 源码执行静态检查。 / Perform static checks on C/C++ source code. |
| `shellcheck` | 检查 Shell 脚本中的常见问题。 / Detect common issues in shell scripts. |

`build-essential`、Git 等软件包可以直接从 Ubuntu 软件仓库安装。([Ubuntu 软件包查询][2])

Packages such as `build-essential` and Git can be installed directly from Ubuntu repositories. ([Ubuntu package search][2])

使用 Ninja 构建 CMake 项目 / Build a CMake project with Ninja：

在项目根目录运行以下命令。第一条会读取当前目录的 `CMakeLists.txt` 并在 `build` 目录生成 Ninja 构建文件；第二条执行编译。若 `build` 已存在，CMake 会复用并更新其中的配置，因此重复执行可能保留之前的缓存选项。

Run these commands from the project root. The first reads `CMakeLists.txt` from the current directory and generates Ninja build files in `build`; the second compiles the project. If `build` already exists, CMake reuses and updates its configuration, so repeated runs may preserve cached options.

```bash
# -S . 指定当前源码目录，-B build 指定独立构建目录，-G Ninja 选择生成器。/ Select the current source, an out-of-tree build directory, and the Ninja generator.
cmake -S . -B build -G Ninja
# 使用上一步生成的配置构建项目。/ Build the project with the configuration generated above.
cmake --build build
```

---

## 四、网络开发和排查工具 / 4. Networking and diagnostics tools

这组软件包可检查接口、路由、DNS、端口、连接和数据包。部分诊断命令需要 root 权限；扫描或抓包前应确认你有权操作目标网络和数据。

This group inspects interfaces, routes, DNS, ports, connections, and packets. Some diagnostic commands require root privileges. Before scanning or capturing traffic, confirm that you are authorized to work with the target network and data.

```bash
# 安装网络配置、连通性测试、扫描、转发和抓包工具。/ Install networking, connectivity, scanning, forwarding, and packet-capture tools.
sudo apt install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    dnsutils \
    traceroute \
    netcat-openbsd \
    nmap \
    lsof \
    socat \
    iperf3 \
    tcpdump
```

| 命令 / Command | 用途 / Purpose |
| --- | --- |
| `ip` | 查看网卡、IP 和路由。 / Inspect interfaces, IP addresses, and routes. |
| `ss` | 查看 TCP/UDP 端口与连接。 / Inspect TCP/UDP sockets and connections. |
| `ping` | 测试 IP 网络连通性与延迟。 / Test IP reachability and latency. |
| `ifconfig` / `netstat` | 提供传统网络查询命令。 / Provide traditional network inspection commands. |
| `dig` / `nslookup` | 查询 DNS 记录。 / Query DNS records. |
| `traceroute` | 查看到目标的网络路径。 / Trace the network path to a destination. |
| `nc` | 测试 TCP/UDP 客户端与服务端。 / Test TCP/UDP clients and servers. |
| `nmap` | 扫描主机和端口。 / Scan hosts and ports. |
| `lsof` | 查看占用文件或端口的进程。 / Identify processes using files or ports. |
| `socat` | 转发、创建和调试套接字连接。 / Forward, create, and debug socket connections. |
| `iperf3` | 测试网络吞吐量。 / Measure network throughput. |
| `tcpdump` | 抓取和检查网络数据包。 / Capture and inspect network packets. |

常见用法 / Common usage：

下面命令分别为只读查询、主动连接、临时监听和抓包操作。`nc -l 8080` 会占用本机 TCP 8080 端口并持续等待连接，使用 `Ctrl+C` 结束；`tcpdump` 会持续输出捕获结果，且可能显示敏感网络内容，同样使用 `Ctrl+C` 停止。

The commands below include read-only queries, an active connection, a temporary listener, and packet capture. `nc -l 8080` occupies local TCP port 8080 and waits for connections until stopped with `Ctrl+C`. `tcpdump` continuously displays captured traffic, which may contain sensitive network data, and is also stopped with `Ctrl+C`.

```bash
# 查看监听端口；-l 仅显示监听套接字，-n 不解析名称，-t 显示 TCP，-p 显示进程。/ Show listening TCP sockets numerically with process information.
ss -lntp

# 查看占用 8080 端口的进程；读取所有进程信息可能需要 sudo。/ Identify the process using port 8080; sudo may be needed to inspect every process.
sudo lsof -i :8080

# 主动连接本机 TCP 8080 服务；连接会一直保持到任一端关闭。/ Connect to a local TCP service on port 8080 until either side closes it.
nc 127.0.0.1 8080

# 在所有默认可用地址上临时监听 TCP 8080；Ctrl+C 停止。/ Temporarily listen on TCP port 8080 on the default available addresses; stop with Ctrl+C.
nc -l 8080

# 在所有接口抓取与 8080 端口有关的数据包；需要 root 权限。/ Capture packets involving port 8080 on all interfaces; root privileges are required.
sudo tcpdump -i any port 8080
```

---

## 五、系统监控和进程管理 / 5. System monitoring and process management

这些工具读取 CPU、内存、磁盘、网络和进程信息。交互式工具通常用 `q` 或其界面提示退出；查询命令本身不会更改系统，但在交互式进程管理器中结束进程属于有副作用的操作。

These tools read CPU, memory, disk, network, and process information. Interactive tools usually exit with `q` or the key shown in their interface. Query commands do not modify the system, but terminating a process from an interactive process manager is a state-changing operation.

```bash
# 安装交互式监控器和基础系统统计工具。/ Install interactive monitors and basic system-statistics tools.
sudo apt install -y \
    htop \
    btop \
    sysstat \
    iotop \
    procps
```

| 命令 / Command | 用途 / Purpose |
| --- | --- |
| `htop` | 交互式查看和管理进程。 / Inspect and manage processes interactively. |
| `btop` | 直观显示 CPU、内存、磁盘和网络状态。 / Present CPU, memory, disk, and network status visually. |
| `iostat` | 查看 CPU 与块设备 I/O 统计。 / Report CPU and block-device I/O statistics. |
| `iotop` | 查看各进程的磁盘读写。 / Inspect disk I/O by process. |
| `ps` / `top` / `free` | 提供基础进程与内存状态。 / Provide basic process and memory status. |

例如 / Examples：

```bash
# 启动交互式进程查看器。/ Start the interactive process viewer.
htop
# 启动交互式综合资源监控器。/ Start the interactive resource monitor.
btop
# 以便于阅读的单位显示内存和交换空间。/ Display memory and swap usage in human-readable units.
free -h
# 以便于阅读的单位显示文件系统空间。/ Display filesystem usage in human-readable units.
df -h
# 每秒持续显示扩展 CPU 和设备 I/O 统计；Ctrl+C 停止。/ Continuously report extended CPU and device I/O statistics every second; stop with Ctrl+C.
iostat -xz 1
```

`htop` 当前仍在 Ubuntu 官方软件包索引中。([Ubuntu 软件包查询][3])

`htop` remains available in Ubuntu's official package index. ([Ubuntu package search][3])

---

## 六、我建议你直接安装的组合 / 6. Suggested combined installation

这套比较适合你现在的开发环境，不会安装太多冷门工具。

This selection is suitable for the current development environment without adding too many niche tools.

第一条命令刷新软件包索引，不会安装或升级软件包；第二条命令合并安装前述常用工具与 APT 信任/仓库管理基础组件。两条命令都需要联网和管理员权限，`-y` 会自动确认安装计划。重复运行通常只会刷新索引并确认软件包状态，但仓库内容变化时可能安装新依赖或更新相关包。

The first command refreshes package indexes without installing or upgrading packages. The second installs a combined set of the tools above plus basic APT trust and repository-management components. Both require network access and administrator privileges, and `-y` automatically confirms the installation plan. Repeated runs normally refresh indexes and confirm package state, but repository changes may cause new dependencies or related package updates to be installed.

```bash
# 从已配置的软件源下载最新软件包索引。/ Download current package indexes from configured repositories.
sudo apt update

# 一次安装建议的开发、搜索、网络、监控和仓库管理工具。/ Install the suggested development, search, networking, monitoring, and repository-management tools in one operation.
sudo apt install -y \
    tree curl wget git vim less tmux bash-completion \
    jq ripgrep fd-find fzf bat ncdu rsync unzip p7zip-full \
    build-essential cmake ninja-build gdb valgrind \
    strace ltrace pkg-config clangd clang-format clang-tidy shellcheck \
    iproute2 iputils-ping net-tools dnsutils traceroute \
    netcat-openbsd nmap lsof socat iperf3 tcpdump \
    htop btop sysstat iotop \
    ca-certificates gnupg software-properties-common
```

安装完成后配置别名 / Configure aliases after installation：

以下 here-document 会把内容**追加**到当前用户的 `~/.bashrc`。`>>` 不检查已有内容，每次重复执行都会再次添加同一组注释和别名；虽然 Bash 通常采用最后一条同名别名，但文件会不断增长。该操作不需要 `sudo`，也不会影响其他 Linux 用户。

The following here-document **appends** content to the current user's `~/.bashrc`. The `>>` operator does not check existing content, so every repeated run adds the same comment and aliases again. Although Bash normally uses the last definition of a repeated alias, the file keeps growing. This operation requires no `sudo` and does not affect other Linux users.

```bash
# 把 EOF 之前的文字原样追加到 .bashrc；单引号可禁止变量和命令展开。/ Append the text through EOF literally to .bashrc; quoting EOF prevents variable and command expansion.
cat >> ~/.bashrc <<'EOF'

# 现代命令别名；每行只影响交互式 Bash。/ Modern command aliases; each line affects interactive Bash only.
alias fd='fdfind'
alias bat='batcat'
alias ll='ls -alF'
alias la='ls -A'
alias grep='grep --color=auto'
EOF

# 在当前 Shell 中重新执行完整 .bashrc，使别名立即生效。/ Re-execute the entire .bashrc in the current shell so the aliases take effect immediately.
source ~/.bashrc
```
