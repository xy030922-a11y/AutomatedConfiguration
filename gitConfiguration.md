# Git 配置 / Git configuration

## 配置全局用户信息 / Configure global identity

以下命令会把身份信息写入当前操作系统用户的全局 Git 配置，并默认用于该用户之后操作的所有仓库。请将占位文字替换为真实姓名和邮箱；这些值会写入新提交的作者/提交者元数据，而不是 GitHub、GitLab 等平台的登录凭据。

The following commands write identity information to the current OS user's global Git configuration and use it by default for all repositories handled by that user. Replace the placeholders with your real name and email address. These values become author/committer metadata in new commits; they are not credentials for GitHub, GitLab, or another hosting service.

```bash
# 设置所有仓库默认使用的提交者姓名。/ Set the default commit author name for all repositories.
git config --global user.name "你的名字"
# 设置所有仓库默认使用的提交者邮箱。/ Set the default commit author email for all repositories.
git config --global user.email "你的邮箱"
```

例如 / Example：

以下内容只是格式示例。重复执行同一条 `git config` 命令会覆盖该键原来的值，不会追加重复条目。

The following values only demonstrate the format. Re-running the same `git config` command replaces the previous value for that key instead of appending another entry.

```bash
# 示例姓名；请按需替换。/ Example name; replace it as needed.
git config --global user.name "y"
# 示例邮箱；请按需替换。/ Example email; replace it as needed.
git config --global user.email "y@"
```

查看是否配置成功 / Verify the configuration：

该命令只读取配置，不会修改仓库或全局设置。输出可能还包含凭据助手、默认分支等其他全局配置。

This command is read-only and does not modify repositories or global settings. Its output may also contain other global options, such as a credential helper or default branch name.

```bash
# 列出当前用户的全部全局 Git 配置。/ List all global Git settings for the current user.
git config --global --list
```

应该能看到 / Expected entries：

实际值应以你在上一步输入的姓名和邮箱为准。

The actual values should match the name and email address entered in the previous step.

```text
user.name=y
user.email=example@gmail.com
```

然后重新执行提交即可。已经存在的历史提交不会被上述配置自动改写。

You can then retry the commit. Existing commits in the repository history are not rewritten automatically by these settings.

## 只给当前项目配置 / Configure only the current repository

不想影响其他 Git 仓库时，先进入目标仓库目录，再去掉 `--global`。配置会写入该仓库的 `.git/config`，并优先于同名全局配置。若当前目录不属于 Git 仓库，命令会失败。

To avoid affecting other repositories, enter the target repository first and omit `--global`. The values are stored in that repository's `.git/config` and override matching global values. The commands fail if the current directory is not inside a Git repository.

```bash
# 仅设置当前仓库的提交者姓名。/ Set the commit author name only for the current repository.
git config user.name "y"
# 仅设置当前仓库的提交者邮箱。/ Set the commit author email only for the current repository.
git config user.email "example@gmail.com"
```

重复执行会更新当前仓库对应的键，不会创建多个相同配置项。

Re-running these commands updates the corresponding keys for the current repository and does not create duplicate settings.

## 设置全局代理配置 / Configure a global proxy

以下示例假设代理服务运行在本机回环地址 `127.0.0.1` 的 `7890` 端口。执行前必须确认代理程序已启动，并将主机、端口和协议替换为实际值。`--global` 会使设置影响当前用户访问的所有 Git 仓库；代理不可用时，拉取、推送和克隆等联网操作可能失败。

The example assumes that a proxy service is listening on local loopback address `127.0.0.1`, port `7890`. Before running it, make sure the proxy application is active and replace the host, port, and scheme with the actual values. Because `--global` is used, the settings affect every Git repository accessed by the current user; network operations such as fetch, push, and clone may fail while the proxy is unavailable.

```bash
# 为使用 HTTP URL 的 Git 连接设置全局代理。/ Set the global proxy for Git connections that use HTTP URLs.
git config --global http.proxy "http://127.0.0.1:7890"
# 按现有示例写入名为 https.proxy 的全局键；实际是否读取该键取决于 Git 配置支持。/ Write the existing example's global https.proxy key; whether it is read depends on Git configuration support.
git config --global https.proxy "http://127.0.0.1:7890"
```

这两条命令是可重复执行的：同名键会被新值覆盖。代理 URL 如果包含用户名或密码，会以明文形式保存在用户配置中，因此不要把包含敏感信息的配置文件提交到版本库。

These commands are repeatable: a new value replaces the existing value for the same key. If a proxy URL includes a username or password, it is stored as plain text in the user's configuration, so never commit a configuration file containing sensitive data.

