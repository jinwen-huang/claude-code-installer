# Claude Code 一键安装工具

专为国内用户打造的 Claude Code 安装神器。无需技术背景，三步搞定。

## 功能

- **环境检测** — 自动检测 Node.js、npm、Git、Python 是否安装及版本是否符合要求
- **一键安装基础软件** — 缺少什么就点什么，支持单独安装和批量安装
- **一键安装 Claude Code** — 自动配置 npm 镜像和代理，一条命令搞定
- **一键安装 ccswitch** — Claude Code 模型切换工具，Opus/Sonnet/Haiku/Fable 自由切换

## 安装要求

- Windows 10/11
- Python 3.10+

## 使用方法

### 开发运行

```bash
git clone https://github.com/jinwen-huang/claude-code-installer.git
cd claude-code-installer
pip install -r requirements.txt
python main.py
```

### 打包为 exe

```bash
# 双击运行
build.bat
```

或手动打包：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ClaudeCode安装工具" --add-data "core;core" --add-data "installers;installers" main.py
```

## 项目结构

```
claude-installer/
├── main.py              # 程序入口 + UI
├── core/
│   ├── env_checker.py   # 环境检测
│   ├── installer.py     # 安装逻辑
│   └── npm_config.py    # npm 配置
├── installers/          # 本地安装包
├── requirements.txt
└── build.bat
```

## 技术栈

- **Python** — 核心逻辑
- **PyQt6** — 桌面 UI
- **PowerShell** — 静默安装逻辑
- **PyInstaller** — 打包为 exe

## 网络配置

工具默认使用 npm 镜像 `https://registry.npmmirror.com`。

如需配置代理（访问 anthropic.com），在安装 Claude Code / ccswitch 时输入代理地址即可，例如：`http://127.0.0.1:7890`
