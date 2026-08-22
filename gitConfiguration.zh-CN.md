# Git 配置

## 配置全局用户信息

以下命令会把身份信息写入当前操作系统用户的全局 Git 配置，并默认用于该用户之后操作的所有仓库。请将占位文字替换为真实姓名和邮箱；这些值会写入新提交的作者和提交者元数据，而不是 GitHub、GitLab 等平台的登录凭据。

```bash
# 设置所有仓库默认使用的提交者姓名。
git config --global user.name "你的名字"

# 设置所有仓库默认使用的提交者邮箱。
git config --global user.email "你的邮箱"
```

例如：

以下内容只是格式示例。重复执行同一条 `git config` 命令会覆盖该键原来的值，不会追加重复条目。

```bash
# 示例姓名，请按需替换。
git config --global user.name "y"

# 示例邮箱，请按需替换。
git config --global user.email "y@example.com"
```

查看是否配置成功：

该命令只读取配置，不会修改仓库或全局设置。输出可能还包含凭据助手、默认分支等其他全局配置。

```bash
# 列出当前用户的全部全局 Git 配置。
git config --global --list
```

应该能看到：

```text
user.name=y
user.email=y@example.com
```

实际值应以你在上一步输入的姓名和邮箱为准。然后重新执行提交即可；已经存在的历史提交不会被上述配置自动改写。

## 只给当前项目配置

不想影响其他 Git 仓库时，先进入目标仓库目录，再去掉 `--global`。配置会写入该仓库的 `.git/config`，并优先于同名全局配置。若当前目录不属于 Git 仓库，命令会失败。

```bash
# 仅设置当前仓库的提交者姓名。
git config user.name "y"

# 仅设置当前仓库的提交者邮箱。
git config user.email "y@example.com"
```

重复执行会更新当前仓库对应的键，不会创建多个相同配置项。

## 设置全局代理配置

以下示例假设代理服务运行在本机回环地址 `127.0.0.1` 的 `7890` 端口。执行前必须确认代理程序已启动，并将主机、端口和协议替换为实际值。`--global` 会使设置影响当前用户访问的所有 Git 仓库；代理不可用时，拉取、推送和克隆等联网操作可能失败。

```bash
# 为使用 HTTP URL 的 Git 连接设置全局代理。
git config --global http.proxy "http://127.0.0.1:7890"

# 按现有示例写入名为 https.proxy 的全局键；实际是否读取该键取决于 Git 配置支持。
git config --global https.proxy "http://127.0.0.1:7890"
```

这两条命令可重复执行：同名键会被新值覆盖。代理 URL 如果包含用户名或密码，会以明文形式保存在用户配置中，因此不要把包含敏感信息的配置文件提交到版本库。
