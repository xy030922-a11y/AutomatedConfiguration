# WSL 代理配置 / WSL proxy configuration

你是在 Windows 上运行代理软件，再让 WSL Ubuntu 复用它。建议优先使用 **WSL 镜像网络 + 自动代理**。

This guide assumes that the proxy application runs on Windows and WSL Ubuntu reuses it. **WSL mirrored networking with automatic proxy discovery** is the preferred approach.

文中的 `127.0.0.1:7890`、`${WIN_HOST}:7890` 都是示例。执行前应在 FlClash、Clash、v2rayN 或其他代理软件中确认实际监听地址、端口和协议。HTTP 代理 URL 必须指向 HTTP 或混合端口；`socks5h://` URL 必须指向支持 SOCKS5 的端口。

Every `127.0.0.1:7890` or `${WIN_HOST}:7890` value in this guide is an example. Before running the commands, verify the actual listening address, port, and protocol in FlClash, Clash, v2rayN, or the proxy application in use. An HTTP proxy URL must use an HTTP or mixed port, while a `socks5h://` URL must use a port that supports SOCKS5.

## 方法一：镜像网络模式，推荐 / Method 1: Mirrored networking (recommended)

适用于 **Windows 11 22H2 及以上版本**。镜像网络允许 WSL 直接通过 `127.0.0.1` 访问 Windows 上运行的代理，并且对 VPN、DNS 的兼容性更好。([Microsoft Learn][1])

This method applies to **Windows 11 version 22H2 or later**. Mirrored networking lets WSL reach a proxy running on Windows through `127.0.0.1` and generally improves compatibility with VPNs and DNS. ([Microsoft Learn][1])

### 1. 更新 WSL / Update WSL

在 Windows PowerShell 中执行以下命令，而不是在 Ubuntu Shell 中执行。更新操作需要联网，并可能触发 UAC 或要求管理员权限；版本查询是只读操作。

Run the following commands in Windows PowerShell, not in the Ubuntu shell. Updating requires Internet access and may trigger UAC or require administrator privileges; the version query is read-only.

```powershell
# 更新 WSL 运行时和相关组件。/ Update the WSL runtime and related components.
wsl --update
# 显示当前 WSL 及内核等组件的版本。/ Display the current WSL, kernel, and related component versions.
wsl --version
```

重复运行 `wsl --update` 会再次检查更新，通常不会重复安装相同版本。

Re-running `wsl --update` checks for updates again and normally does not reinstall the same version.

### 2. 编辑 `.wslconfig` / Edit `.wslconfig`

在 Windows PowerShell 中执行。`$env:USERPROFILE` 指向当前 Windows 用户的配置目录；该文件会影响此用户启动的所有 WSL 2 发行版，而不只 Ubuntu 24.04。

Run this in Windows PowerShell. `$env:USERPROFILE` points to the current Windows user's profile directory. The file affects every WSL 2 distribution started by this user, not only Ubuntu 24.04.

```powershell
# 用记事本打开或新建用户级 WSL 配置文件。/ Open or create the per-user WSL configuration file in Notepad.
notepad $env:USERPROFILE\.wslconfig
```

写入以下配置。`networkingMode=mirrored` 启用镜像网络；`dnsTunneling=true` 让 DNS 查询经由 Windows；`autoProxy=true` 尝试把 Windows HTTP 代理信息导入 WSL；`firewall=true` 让 WSL 网络流量受 Windows/Hyper-V 防火墙规则约束。

Write the following configuration. `networkingMode=mirrored` enables mirrored networking; `dnsTunneling=true` sends DNS queries through Windows; `autoProxy=true` attempts to import Windows HTTP proxy information into WSL; and `firewall=true` keeps WSL traffic subject to Windows/Hyper-V firewall rules.

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
firewall=true
```

保存后执行以下命令。它会立即终止所有正在运行的 WSL 发行版及其中的进程，以便下次启动时重新加载 `.wslconfig`；请先保存编辑器、终端任务和服务中的未保存数据。

After saving, run the following command. It immediately stops all running WSL distributions and their processes so `.wslconfig` is reloaded on the next start. Save unsaved work in editors, terminal jobs, and services first.

```powershell
# 关闭整个 WSL 虚拟机；下次打开 Ubuntu 时自动重启。/ Shut down the WSL VM; it restarts automatically when Ubuntu is opened again.
wsl --shutdown
```

然后重新打开 Ubuntu。修改 `.wslconfig` 后重复执行 `wsl --shutdown` 是安全的，但每次都会中止当时运行的 WSL 进程。

Then reopen Ubuntu. Re-running `wsl --shutdown` after changing `.wslconfig` is safe, but every run terminates the WSL processes active at that time.

`autoProxy=true` 会让 WSL 使用 Windows 的 HTTP 代理信息；因此你的 FlClash、Clash、v2rayN 等软件需要先开启 **系统代理**。([Microsoft Learn][2])

`autoProxy=true` lets WSL consume Windows HTTP proxy information, so **system proxy** mode must first be enabled in FlClash, Clash, v2rayN, or the corresponding proxy application. ([Microsoft Learn][2])

### 3. 检查代理是否自动导入 / Check whether the proxy was imported

在重新打开的 Ubuntu Shell 中运行。该命令只读取当前进程环境，并以不区分大小写的方式筛选名称中包含 `proxy` 的变量。

Run this in the reopened Ubuntu shell. It only reads the current process environment and filters variable names containing `proxy` without regard to letter case.

```bash
# 查看当前 Shell 继承的代理环境变量。/ Show proxy environment variables inherited by the current shell.
env | grep -i proxy
```

可能看到 / Possible output：

```text
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

变量存在只表示配置已导入，不保证代理服务器可达。可用以下任一命令发起实际联网测试；`-I` 仅请求响应头，而 IP 查询会把出口公网 IP 输出到终端。

The presence of these variables only proves that configuration was imported; it does not guarantee that the proxy server is reachable. Use either command below for an actual network test. `-I` requests response headers only, while the IP query prints the public egress IP.

```bash
# 通过当前代理设置请求 HTTPS 响应头。/ Request HTTPS response headers using the current proxy settings.
curl -I https://www.google.com
```

或者 / Or：

```bash
# 显示当前网络出口的公网 IP。/ Display the current network's public egress IP.
curl https://ipinfo.io/ip
```

---

## 方法二：手动指定代理 / Method 2: Set proxy variables manually

如果自动代理没有生效，可以直接指定 Windows 代理端口。以下 `export` 只影响当前 Shell 及其随后启动的子进程；关闭终端后不会保留。

If automatic proxy discovery does not work, specify the Windows proxy port directly. The following `export` commands affect only the current shell and child processes started from it; they do not persist after the terminal is closed.

先在 FlClash 中查看本地端口，例如 / First check the local port in FlClash, for example：

```text
混合端口：7890
```

镜像网络模式下，在 Ubuntu 中执行。小写变量被许多 Linux 命令行工具识别；具体程序是否读取这些变量仍取决于该程序自身的代理支持。

In mirrored networking mode, run these commands in Ubuntu. Many Linux command-line tools recognize lowercase proxy variables, but whether a particular application reads them still depends on that application's proxy support.

```bash
# HTTP 请求使用本机的 HTTP/混合代理端口。/ Route HTTP requests through the local HTTP or mixed proxy port.
export http_proxy="http://127.0.0.1:7890"
# HTTPS 目标通过 HTTP CONNECT 使用同一代理端口。/ Route HTTPS destinations through the same proxy by using HTTP CONNECT.
export https_proxy="http://127.0.0.1:7890"
# 其他支持 all_proxy 的程序使用 SOCKS5，并由代理端解析域名。/ Use SOCKS5 with proxy-side DNS for programs that honor all_proxy.
export all_proxy="socks5h://127.0.0.1:7890"
```

三条命令可以重复执行；新的赋值会替换当前 Shell 中的旧值，不会追加重复变量。端口必须支持 URL 中声明的代理协议。

These commands may be repeated; each new assignment replaces the old value in the current shell rather than appending a duplicate variable. The selected port must support the protocol declared in its URL.

测试 / Test：

```bash
# 发起 HTTPS HEAD 请求以验证解析、连接和代理转发。/ Send an HTTPS HEAD request to verify DNS, connectivity, and proxy forwarding.
curl -I https://www.google.com
```

取消代理 / Clear the temporary variables：

```bash
# 仅从当前 Shell 环境移除三个变量。/ Remove the three variables from the current shell environment only.
unset http_proxy
unset https_proxy
unset all_proxy
```

如果这些变量也写在启动文件中，`unset` 不会删除启动文件里的配置；新开终端时它们仍会再次设置。

If the variables are also present in a shell startup file, `unset` does not remove those file entries; a new terminal sets them again.

### 永久保存 / Persist the settings

编辑当前 Linux 用户的 Bash 启动文件。此操作不需要 `sudo`；`~` 代表当前 Linux 用户的主目录。

Edit the current Linux user's Bash startup file. This does not require `sudo`; `~` represents the current Linux user's home directory.

```bash
# 在终端编辑器中打开 .bashrc。/ Open .bashrc in a terminal editor.
nano ~/.bashrc
```

在末尾加入以下内容。每次启动交互式 Bash 时都会重新导出这些值；手动重复粘贴会产生重复行，因此再次编辑前应先检查文件现有内容。

Append the following content at the end. Every interactive Bash startup exports these values again. Manually pasting the block repeatedly creates duplicate lines, so inspect the existing file before editing it again.

```bash
# 为每个交互式 Bash 会话设置 HTTP 代理。/ Set the HTTP proxy for each interactive Bash session.
export http_proxy="http://127.0.0.1:7890"
# 为每个交互式 Bash 会话设置 HTTPS 代理。/ Set the HTTPS proxy for each interactive Bash session.
export https_proxy="http://127.0.0.1:7890"
# 为支持该变量的程序设置 SOCKS5 代理。/ Set a SOCKS5 proxy for applications that honor this variable.
export all_proxy="socks5h://127.0.0.1:7890"
```

使配置在当前终端立即生效；这会在当前 Shell 中重新执行整个 `.bashrc`，因此文件中的其他有副作用命令也会再次运行。

Apply the configuration immediately in the current terminal. This re-executes the entire `.bashrc` in the current shell, so any other commands in that file with side effects also run again.

```bash
# 在当前 Bash 进程中重新加载启动文件。/ Reload the startup file in the current Bash process.
source ~/.bashrc
```

端口不一定是 `7890`，应以 FlClash 设置中的 **混合端口或 HTTP 端口**为准。

The correct port is not necessarily `7890`; use the **mixed port or HTTP port** shown in FlClash.

---

## 方法三：WSL 使用 NAT 网络时 / Method 3: WSL in NAT networking mode

如果你使用 Windows 10，或者没有启用 `networkingMode=mirrored`，WSL 不能通过 `127.0.0.1` 访问 Windows 代理，需要使用 Windows 主机在 WSL 网络中的 IP。微软文档也说明，NAT 模式下从 WSL 访问 Windows 服务需要使用主机 IP。([Microsoft Learn][3])

If you use Windows 10 or have not enabled `networkingMode=mirrored`, WSL cannot reach the Windows proxy through `127.0.0.1`; it must use the Windows host address on the WSL network. Microsoft also documents that WSL in NAT mode uses the host IP to access Windows services. ([Microsoft Learn][3])

在 Ubuntu 中获取 Windows 主机 IP。第一条命令从默认路由中提取网关地址并保存到当前 Shell 变量；第二条命令仅显示该值。

Obtain the Windows host IP in Ubuntu. The first command extracts the gateway from the default route and stores it in a current-shell variable; the second command only displays the value.

```bash
# 从默认路由提取 Windows 主机地址。/ Extract the Windows host address from the default route.
WIN_HOST=$(ip route show | awk '/default/ {print $3}')
# 输出地址，便于确认变量不是空值。/ Print the address so you can verify that the variable is not empty.
echo "$WIN_HOST"
```

`WIN_HOST` 仅存在于当前 Shell，关闭终端后失效；如果网络或 WSL 实例重建，主机 IP 也可能变化。

`WIN_HOST` exists only in the current shell and disappears when the terminal closes. The host IP may also change when networking or the WSL instance is recreated.

配置代理 / Configure the proxy：

```bash
# 通过 NAT 网关地址设置 HTTP 代理。/ Set the HTTP proxy through the NAT gateway address.
export http_proxy="http://${WIN_HOST}:7890"
# 通过 NAT 网关地址设置 HTTPS 代理。/ Set the HTTPS proxy through the NAT gateway address.
export https_proxy="http://${WIN_HOST}:7890"
# 通过 NAT 网关地址设置 SOCKS5 代理。/ Set the SOCKS5 proxy through the NAT gateway address.
export all_proxy="socks5h://${WIN_HOST}:7890"
```

测试 / Test：

```bash
# 验证 WSL 能否经 Windows 主机代理访问 HTTPS 站点。/ Verify that WSL can reach an HTTPS site through the Windows-host proxy.
curl -I https://www.google.com
```

这种方式还需要在 FlClash 中 / This method also requires the following FlClash settings：

1. 开启 **允许局域网连接 / Allow LAN**。 / Enable **Allow LAN**.
2. 确认监听地址不是仅限 `127.0.0.1`，而是允许 WSL 访问。 / Ensure the listener is not restricted to `127.0.0.1` and can accept WSL connections.
3. Windows 防火墙允许该代理端口。 / Allow the proxy port through Windows Firewall.

这些设置会扩大代理服务的可访问范围。如果监听所有网卡且防火墙规则允许广泛来源，同一网络中的其他设备也可能连接代理；应了解现有监听和防火墙规则的实际范围，且不要在不可信网络上暴露代理端口。

These settings broaden the proxy service's reachability. If it listens on all interfaces and the firewall rule allows broad sources, other devices on the same network may also connect to it. Understand the actual listener and firewall scope, and do not expose the proxy port on an untrusted network.

可以将动态配置放进 `~/.bashrc`。该片段会在每次交互式 Bash 启动时重新计算网关，因此能适应 NAT 地址变化；手动重复添加同一片段会在文件中产生重复配置。

The dynamic configuration can be placed in `~/.bashrc`. It recalculates the gateway whenever an interactive Bash starts, allowing it to follow NAT address changes. Manually adding the same block repeatedly creates duplicate configuration in the file.

```bash
# 每次启动 Bash 时重新读取默认网关。/ Re-read the default gateway whenever Bash starts.
WIN_HOST=$(ip route show | awk '/default/ {print $3}')

# 使用当前 NAT 网关地址设置 HTTP 代理。/ Set the HTTP proxy with the current NAT gateway address.
export http_proxy="http://${WIN_HOST}:7890"
# 使用当前 NAT 网关地址设置 HTTPS 代理。/ Set the HTTPS proxy with the current NAT gateway address.
export https_proxy="http://${WIN_HOST}:7890"
# 使用当前 NAT 网关地址设置 SOCKS5 代理。/ Set the SOCKS5 proxy with the current NAT gateway address.
export all_proxy="socks5h://${WIN_HOST}:7890"
```

## APT 使用代理 / Use the proxy with APT

普通命令能联网，但 `sudo apt update` 不走代理时，可以让 `sudo` 尝试保留当前环境变量。该命令需要管理员权限，会刷新 APT 软件包索引但不会安装或升级软件包；`-E` 是否能保留具体变量仍受系统 `sudoers` 安全策略约束。

If ordinary commands have network access but `sudo apt update` does not use the proxy, ask `sudo` to preserve the current environment. This command requires administrator privileges and refreshes APT package indexes without installing or upgrading packages. Whether `-E` may preserve a particular variable still depends on the system's `sudoers` security policy.

```bash
# 保留获准的当前环境变量并刷新 APT 索引。/ Preserve permitted current environment variables and refresh APT indexes.
sudo -E apt update
```

你的环境是 Windows 11 的话，建议直接采用以下用户级 WSL 2 配置，然后在 FlClash 中开启系统代理。这样通常不需要在 Ubuntu 的 `~/.bashrc` 里长期写死代理端口。

On Windows 11, the following per-user WSL 2 configuration is recommended, together with enabling the system proxy in FlClash. This usually avoids hard-coding a proxy port permanently in Ubuntu's `~/.bashrc`.

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

这段摘要与方法一的主要网络设置一致，但没有列出 `firewall=true`；配置文件中最终实际存在的键决定 WSL 行为。修改后仍需执行前述 `wsl --shutdown` 才会在下次启动时加载。

This summary matches the main networking settings in Method 1 but does not list `firewall=true`; the keys actually present in the configuration file determine WSL behavior. After editing, the earlier `wsl --shutdown` is still required before the settings are loaded on the next start.

[1]: https://learn.microsoft.com/en-us/windows/wsl/networking?utm_source=chatgpt.com "Accessing network applications with WSL | Microsoft Learn"
[2]: https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config?utm_source=chatgpt.com "WSL 中的高级设置配置 | Microsoft Learn"
[3]: https://learn.microsoft.com/zh-cn/windows/wsl/networking?utm_source=chatgpt.com "使用 WSL 访问网络应用程序 | Microsoft Learn"
