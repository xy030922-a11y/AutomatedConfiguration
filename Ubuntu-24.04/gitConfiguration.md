# Git 配置

## 配置全局用户信息

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

例如：

```bash
git config --global user.name "y"
git config --global user.email "y@"
```

查看是否配置成功：

```bash
git config --global --list
```

应该能看到：

```text
user.name=y
user.email=example@gmail.com
```

然后重新执行提交即可。

## 只给当前项目配置

不想影响其他 Git 仓库时，进入项目目录后去掉 `--global`：

```bash
git config user.name "y"
git config user.email "example@gmail.com"
```

## 查看代理配置

```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

