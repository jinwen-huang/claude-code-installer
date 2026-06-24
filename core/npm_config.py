"""npm 配置模块"""
import subprocess


def configure_npm(registry: str = 'https://registry.npmmirror.com', proxy: str = '') -> tuple[bool, str]:
    """配置 npm 镜像和代理"""
    commands = [
        f'npm config set registry {registry}',
    ]
    if proxy:
        commands.append(f'npm config set proxy {proxy}')
        commands.append(f'npm config set https-proxy {proxy}')

    for cmd in commands:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f'配置失败: {result.stderr}'

    return True, 'npm 配置完成'
