## 一、基础命令行工具

```bash
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

| 软件包               | 用途                 |
| ----------------- | ------------------ |
| `tree`            | 树状显示目录结构           |
| `curl`            | HTTP/API 请求、下载文件   |
| `wget`            | 下载文件或递归抓取资源        |
| `git`             | 版本控制               |
| `vim` / `nano`    | 终端文本编辑             |
| `less`            | 分页查看长文本            |
| `tmux`            | 终端会话管理，断开终端后程序仍可运行 |
| `man-db`          | 提供 `man` 手册        |
| `bash-completion` | Bash 命令和参数补全       |

---

## 二、文件、文本和搜索工具

```bash
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

| 命令       | 用途                   | 示例                       |
| -------- | -------------------- | ------------------------ |
| `jq`     | 格式化、查询 JSON          | `cat data.json \| jq`    |
| `rg`     | 比 `grep -r` 更方便地搜索代码 | `rg "TcpServer" src/`    |
| `fdfind` | 更简单的 `find` 替代工具     | `fdfind CMakeLists`      |
| `fzf`    | 交互式模糊搜索              | `history \| fzf`         |
| `batcat` | 带语法高亮的 `cat`         | `batcat main.cpp`        |
| `ncdu`   | 分析磁盘空间占用             | `ncdu ~`                 |
| `rsync`  | 高效复制和同步目录            | `rsync -av src/ backup/` |
| `unzip`  | 解压 ZIP               |                          |
| `7z`     | 处理 7z、ZIP 等压缩格式      |                          |

Ubuntu 中有两个特殊命令名：

```bash
fdfind
batcat
```

可以在 `~/.bashrc` 中添加别名：

```bash
alias fd='fdfind'
alias bat='batcat'
```

然后执行：

```bash
source ~/.bashrc
```

---

## 三、C/C++ 开发工具

```bash
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

| 软件包               | 用途                      |
| ----------------- | ----------------------- |
| `build-essential` | 安装 GCC、G++、Make 和标准开发文件 |
| `cmake`           | CMake 构建系统              |
| `ninja-build`     | 比 Make 更快的构建后端          |
| `gdb`             | C/C++ 调试器               |
| `valgrind`        | 检查内存泄漏和非法内存访问           |
| `strace`          | 跟踪系统调用                  |
| `ltrace`          | 跟踪动态库函数调用               |
| `pkg-config`      | 查找第三方库头文件和链接参数          |
| `clang`           | Clang 编译器               |
| `clangd`          | VSCode C/C++ 代码补全和跳转    |
| `clang-format`    | 格式化 C/C++ 代码            |
| `clang-tidy`      | 静态代码检查                  |
| `shellcheck`      | 检查 Shell 脚本问题           |

`build-essential`、Git 等软件包可以直接从 Ubuntu 软件仓库安装。([Ubuntu 软件包查询][2])

使用 Ninja 构建 CMake 项目：

```bash
cmake -S . -B build -G Ninja
cmake --build build
```

---

## 四、网络开发和排查工具

```bash
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

| 命令                     | 用途                |
| ---------------------- | ----------------- |
| `ip`                   | 查看网卡、IP、路由        |
| `ss`                   | 查看 TCP/UDP 端口和连接  |
| `ping`                 | 测试网络连通性           |
| `ifconfig` / `netstat` | 传统网络命令            |
| `dig` / `nslookup`     | DNS 查询            |
| `traceroute`           | 查看网络路径            |
| `nc`                   | TCP/UDP 客户端和服务端测试 |
| `nmap`                 | 端口扫描              |
| `lsof`                 | 查看哪个进程占用了文件或端口    |
| `socat`                | 转发、创建和调试套接字连接     |
| `iperf3`               | 测试网络吞吐量           |
| `tcpdump`              | 抓取网络数据包           |

常见用法：

```bash
# 查看监听端口
ss -lntp

# 查看 8080 端口被谁占用
sudo lsof -i :8080

# 连接 TCP 服务端
nc 127.0.0.1 8080

# 临时启动 TCP 服务端
nc -l 8080

# 抓取 8080 端口数据包
sudo tcpdump -i any port 8080
```

---

## 五、系统监控和进程管理

```bash
sudo apt install -y \
    htop \
    btop \
    sysstat \
    iotop \
    procps
```

| 命令                    | 用途                  |
| --------------------- | ------------------- |
| `htop`                | 交互式进程管理             |
| `btop`                | 更直观地查看 CPU、内存、磁盘和网络 |
| `iostat`              | 查看 CPU 和磁盘 I/O      |
| `iotop`               | 查看进程磁盘读写            |
| `ps` / `top` / `free` | 基础系统状态命令            |

例如：

```bash
htop
btop
free -h
df -h
iostat -xz 1
```

`htop` 当前仍在 Ubuntu 官方软件包索引中。([Ubuntu 软件包查询][3])

---

## 六、我建议你直接安装的组合

这套比较适合你现在的开发环境，不会安装太多冷门工具：

```bash
sudo apt update

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

安装完成后配置别名：

```bash
cat >> ~/.bashrc <<'EOF'

# Modern command aliases
alias fd='fdfind'
alias bat='batcat'
alias ll='ls -alF'
alias la='ls -A'
alias grep='grep --color=auto'
EOF

source ~/.bashrc
```