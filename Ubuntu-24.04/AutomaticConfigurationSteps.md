综合兼容性和稳定性，安装 **Ubuntu 24.04 LTS** 最合适。

```powershell
wsl --update
wsl --install -d Ubuntu-24.04
```
安装完成后检查：

```powershell
wsl -l -v
```

进入 Ubuntu 后检查版本：

```bash
cat /etc/os-release
```

预计显示：

```text
VERSION="24.04.x LTS (Noble Numbat)"
```