"""安装模块"""
import subprocess
from pathlib import Path

INSTALLERS_DIR = Path(__file__).parent.parent / 'installers'


def _run_process(cmd_args, use_shell=False, callback=None) -> tuple[bool, str]:
    """静默执行命令，返回 (成功, 消息)"""
    try:
        proc = subprocess.Popen(
            cmd_args,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in proc.stdout:
            line = line.strip()
            if line and callback:
                callback(line)

        proc.wait()

        if proc.returncode == 0:
            return True, '安装成功'
        else:
            return False, f'安装失败 (退出码 {proc.returncode})'

    except Exception as e:
        return False, f'安装异常: {str(e)}'


def install_software(name: str, callback=None) -> tuple[bool, str]:
    """从本地安装包目录安装基础软件"""
    file_map = {
        'Node.js': INSTALLERS_DIR / 'node-v24.16.0-x64.msi',
        'Python': INSTALLERS_DIR / 'python-3.12.10-amd64.exe',
        'Git': None,  # 文件名带括号，需匹配
    }

    path = file_map.get(name)

    # Git 文件名有 "(2)"，用 glob 精确匹配
    if name == 'Git':
        git_files = list(INSTALLERS_DIR.glob('Git*.exe'))
        if git_files:
            path = git_files[0]
        else:
            return False, f'{name} 安装包不存在'

    if not path or not path.exists():
        return False, f'{name} 安装包不存在'

    if callable(callback):
        callback(f'正在安装 {name}...')

    if name == 'Node.js':
        cmd = ['msiexec', '/i', str(path), '/qn', '/norestart']
    elif name == 'Python':
        cmd = [str(path), '/quiet', 'InstallAllUsers=0', 'PrependPath=1']
    elif name == 'Git':
        cmd = [str(path), '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-']
    else:
        return False, f'未知的安装项: {name}'

    return _run_process(cmd, callback=callback)


def install_claude_code(callback=None, proxy: str = '') -> tuple[bool, str]:
    """安装 Claude Code（使用 npm 镜像）"""
    from .npm_config import configure_npm

    if callable(callback):
        callback('正在配置 npm 镜像...')
    ok, msg = configure_npm(proxy=proxy)
    if not ok:
        return False, msg

    if callable(callback):
        callback('正在安装 Claude Code...')
    cmd = 'npm install -g @anthropic-ai/claude-code'

    ok, msg = _run_process(cmd, use_shell=True, callback=callback)
    if not ok:
        return False, f'安装失败: {msg}'

    # 验证
    if callable(callback):
        callback('正在验证安装...')
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True, text=True, timeout=30
        )
        version = result.stdout.strip() if result.returncode == 0 else '未知版本'
        if callable(callback):
            callback(f'Claude Code 安装成功! 版本: {version}')
        return True, f'Claude Code 安装成功! 版本: {version}'
    except Exception:
        if callable(callback):
            callback('Claude Code 安装成功!')
        return True, 'Claude Code 安装成功!'


def install_ccswitch(callback=None) -> tuple[bool, str]:
    """安装 ccswitch（从本地 MSI 安装包）"""
    path = INSTALLERS_DIR / 'CC-Switch-v3.16.1-Windows.msi'

    if not path.exists():
        return False, 'ccswitch 安装包不存在'

    if callable(callback):
        callback('正在安装 ccswitch...')
    cmd = ['msiexec', '/i', str(path), '/qn', '/norestart']

    ok, msg = _run_process(cmd, callback=callback)
    if not ok:
        return False, f'安装失败: {msg}'

    # 验证安装
    if callable(callback):
        callback('正在验证安装...')
    try:
        result = subprocess.run(
            ['ccswitch', '--version'],
            capture_output=True, text=True, timeout=10
        )
        version = result.stdout.strip() if result.returncode == 0 else ''
        if version:
            if callable(callback):
                callback(f'ccswitch 安装成功! 版本: {version}')
            return True, f'ccswitch 安装成功! 版本: {version}'
    except Exception:
        pass

    if callable(callback):
        callback('ccswitch 安装成功!')
    return True, 'ccswitch 安装成功!'


def install_vscode(callback=None) -> tuple[bool, str]:
    """安装 VS Code（选装，从本地安装包）"""
    vscode_files = list(INSTALLERS_DIR.glob('VSCodeUserSetup*.exe'))
    if not vscode_files:
        return False, 'VS Code 安装包不存在'
    path = vscode_files[0]

    if callable(callback):
        callback('正在安装 VS Code...')
    # VS Code 用户级静默安装
    cmd = [str(path), '/VERYSILENT', '/NORESTART', '/MERGETASKS=!runcode']

    ok, msg = _run_process(cmd, callback=callback)
    if not ok:
        return False, f'安装失败: {msg}'

    if callable(callback):
        callback('VS Code 安装成功!')
    return True, 'VS Code 安装成功!'
