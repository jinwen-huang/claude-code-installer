"""核心模块包"""
from .env_checker import check_environment
from .installer import install_software, install_claude_code, install_ccswitch
from .npm_config import configure_npm

__all__ = [
    'check_environment',
    'install_software',
    'install_claude_code',
    'install_ccswitch',
    'configure_npm',
]
