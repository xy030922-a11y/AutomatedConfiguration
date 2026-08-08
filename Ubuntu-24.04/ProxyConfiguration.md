你是在 Windows 上运行代理软件，再让 WSL Ubuntu 复用它。建议优先使用 **WSL 镜像网络 + 自动代理**。

## 方法一：镜像网络模式，推荐

适用于 **Windows 11 22H2 及以上版本**。镜像网络允许 WSL 直接通过 `127.0.0.1` 访问 Windows 上运行的代理，并且对 VPN、DNS 的兼容性更好。([Microsoft Learn][1])

### 1. 更新 WSL

在 PowerShell 中执行：

```powershell
wsl --update
wsl --version
```

### 2. 编辑 `.wslconfig`

在 PowerShell 中执行：

```powershell
notepad $env:USERPROFILE\.wslconfig
```

写入：

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
firewall=true
```

保存后执行：

```powershell
wsl --shutdown
```

然后重新打开 Ubuntu。

`autoProxy=true` 会让 WSL 使用 Windows 的 HTTP 代理信息；因此你的 FlClash、Clash、v2rayN 等软件需要先开启 **系统代理**。([Microsoft Learn][2])

### 3. 检查代理是否自动导入

在 Ubuntu 中执行：

```bash
env | grep -i proxy
```

可能看到：

```text
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

测试：

```bash
curl -I https://www.google.com
```

或者：

```bash
curl https://ipinfo.io/ip
```

---

## 方法二：手动指定代理

如果自动代理没有生效，可以直接指定 Windows 代理端口。

先在 FlClash 中查看本地端口，例如：

```text
混合端口：7890
```

镜像网络模式下，在 Ubuntu 中执行：

```bash
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export all_proxy="socks5h://127.0.0.1:7890"
```

测试：

```bash
curl -I https://www.google.com
```

取消代理：

```bash
unset http_proxy
unset https_proxy
unset all_proxy
```

### 永久保存

编辑：

```bash
nano ~/.bashrc
```

在末尾加入：

```bash
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export all_proxy="socks5h://127.0.0.1:7890"
```

使配置生效：

```bash
source ~/.bashrc
```

端口不一定是 `7890`，应以 FlClash 设置中的 **混合端口或 HTTP 端口**为准。

---

## 方法三：WSL 使用 NAT 网络时

如果你使用 Windows 10，或者没有启用 `networkingMode=mirrored`，WSL 不能通过 `127.0.0.1` 访问 Windows 代理，需要使用 Windows 主机在 WSL 网络中的 IP。微软文档也说明，NAT 模式下从 WSL 访问 Windows 服务需要使用主机 IP。([Microsoft Learn][3])

获取 Windows 主机 IP：

```bash
WIN_HOST=$(ip route show | awk '/default/ {print $3}')
echo "$WIN_HOST"
```

配置代理：

```bash
export http_proxy="http://${WIN_HOST}:7890"
export https_proxy="http://${WIN_HOST}:7890"
export all_proxy="socks5h://${WIN_HOST}:7890"
```

测试：

```bash
curl -I https://www.google.com
```

这种方式还需要在 FlClash 中：

1. 开启 **允许局域网连接 / Allow LAN**。
2. 确认监听地址不是仅限 `127.0.0.1`，而是允许 WSL 访问。
3. Windows 防火墙允许该代理端口。

可以将动态配置放进 `~/.bashrc`：

```bash
WIN_HOST=$(ip route show | awk '/default/ {print $3}')

export http_proxy="http://${WIN_HOST}:7890"
export https_proxy="http://${WIN_HOST}:7890"
export all_proxy="socks5h://${WIN_HOST}:7890"
```

## APT 使用代理

普通命令能联网，但 `sudo apt update` 不走代理时，可以保留当前环境变量：

```bash
sudo -E apt update
```

你的环境是 Windows 11 的话，建议直接采用：

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

然后在 FlClash 中开启系统代理。这样通常不需要在 Ubuntu 的 `~/.bashrc` 里长期写死代理端口。

[1]: https://learn.microsoft.com/en-us/windows/wsl/networking?utm_source=chatgpt.com "Accessing network applications with WSL | Microsoft Learn"
[2]: https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config?utm_source=chatgpt.com "WSL 中的高级设置配置 | Microsoft Learn"
[3]: https://learn.microsoft.com/zh-cn/windows/wsl/networking?utm_source=chatgpt.com "使用 WSL 访问网络应用程序 | Microsoft Learn"
