# Claude Code 一键安装工具

专为国内用户打造的 Claude Code 安装神器。不用敲命令，鼠标点三下，全部搞定。

## 下载

👉 **[点我下载最新版](https://github.com/jinwen-huang/claude-code-installer/releases)**

下载 `ClaudeCode安装工具.exe`，双击直接运行，无需安装 Python。

## 功能

- **环境检测** — 自动检测 Node.js、npm、Git、Python 是否安装及版本是否符合要求
- **一键安装基础软件** — 缺什么点什么，离线安装包已内置，不用联网下载
- **一键安装 Claude Code** — 自动配置 npm 镜像，一条命令搞定
- **一键安装 ccswitch** — Claude Code 模型切换工具，自由切换模型

## 安装要求

- Windows 10/11

## 使用方法

1. 从 [Releases](https://github.com/jinwen-huang/claude-code-installer/releases) 下载 exe
2. 双击运行
3. 环境检测 → 安装 Claude Code → 安装 ccswitch → 完成

---

## 开发环境

### 运行源码

```bash
git clone https://github.com/jinwen-huang/claude-code-installer.git
cd claude-code-installer
pip install -r requirements.txt
python main.py
```

### 打包

双击 `build.bat`，或手动：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ClaudeCode安装工具" --add-data "core;core" --add-data "installers;installers" main.py
```

## 技术栈

Python · PyQt6 · PyInstaller · npm

## 使用说明

工具默认使用 npm 镜像 `https://registry.npmmirror.com`，国内网络友好。

如需配置代理（访问 anthropic.com），在安装 Claude Code / ccswitch 时输入代理地址，例如：`http://127.0.0.1:7890`
