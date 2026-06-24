"""环境检测模块"""
import subprocess
import re


def _run_cmd(cmd: str) -> str | None:
    """执行命令并返回输出，失败返回 None"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _extract_version(output: str | None) -> str | None:
    """从命令输出中提取版本号"""
    if not output:
        return None
    match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', output)
    return match.group(1) if match else None


def _compare_versions(a: str, b: str) -> int:
    """比较版本号：a>b 返回 1，a<b 返回 -1，相等返回 0"""
    parts_a = [int(x) for x in a.split('.')]
    parts_b = [int(x) for x in b.split('.')]
    # 补齐长度
    max_len = max(len(parts_a), len(parts_b))
    parts_a.extend([0] * (max_len - len(parts_a)))
    parts_b.extend([0] * (max_len - len(parts_b)))
    for a_part, b_part in zip(parts_a, parts_b):
        if a_part > b_part:
            return 1
        if a_part < b_part:
            return -1
    return 0


def check_environment() -> list[dict]:
    """检测系统环境，返回检测结果列表"""
    checks = [
        {'name': 'Node.js', 'cmd': 'node --version', 'min_ver': '20.0.0'},
        {'name': 'npm', 'cmd': 'npm --version', 'min_ver': '10.0.0'},
        {'name': 'Git', 'cmd': 'git --version', 'min_ver': '2.40.0'},
        {'name': 'Python', 'cmd': 'python --version', 'min_ver': '3.10'},
    ]

    results = []
    for check in checks:
        output = _run_cmd(check['cmd'])
        version = _extract_version(output)
        installed = version is not None
        pass_check = _compare_versions(version, check['min_ver']) >= 0 if installed else False
        results.append({
            'name': check['name'],
            'installed': installed,
            'version': version,
            'pass': pass_check,
            'min_ver': check['min_ver'],
        })
    return results
