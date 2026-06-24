"""激活验证模块 — 母码派生 + 机器指纹绑定"""
import hashlib
import hmac
import uuid
import subprocess
import winreg
from pathlib import Path

# 母码（仅用于派生验证，不会直接暴露在 exe 中）
MASTER_KEY = "jinwen"

# 注册表路径
REG_KEY = r"Software\ClaudeInstaller"
REG_VALUE = "activation"

# 版本标签（换母码时更新，相当于新一轮激活）
VERSION = "v1"


def _get_machine_id() -> str:
    """获取机器指纹"""
    parts = []

    # 主板 UUID
    try:
        result = subprocess.run(
            ['wmic', 'csproduct', 'get', 'uuid'],
            capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and l.strip() != 'UUID']
        if lines:
            parts.append(lines[0])
    except Exception:
        pass

    # 硬盘序列号
    try:
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'serialnumber'],
            capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and l.strip() != 'SerialNumber']
        if lines:
            parts.append(lines[0])
    except Exception:
        pass

    # MAC 地址
    try:
        result = subprocess.run(
            ['getmac', '/v', '/fo', 'list'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split('\n'):
            if '物理地址' in line or 'Physical Address' in line:
                mac = line.split(':')[-1].strip().replace('-', '').replace(':', '')
                if mac:
                    parts.append(mac)
                    break
    except Exception:
        pass

    # 兜底：随机 UUID
    if not parts:
        parts.append(str(uuid.uuid4()))

    combined = '|'.join(parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def _derive_key(machine_id: str) -> bytes:
    """从母码 + 机器码派生密钥"""
    return hmac.new(
        MASTER_KEY.encode(),
        f"{VERSION}:{machine_id}".encode(),
        hashlib.sha256
    ).digest()


def generate_activation_code(machine_id: str) -> str:
    """
    生成激活码（给你用的）。
    输入用户的机器码，输出激活码。
    """
    key = _derive_key(machine_id)
    suffix = hashlib.sha256(key).hexdigest()[:4]
    code = key.hex()[:8] + '-' + suffix
    return code.upper()


def validate_activation_code(code: str, machine_id: str) -> bool:
    """验证激活码是否有效"""
    code = code.replace('-', '').strip().lower()
    key = _derive_key(machine_id)
    expected_part = key.hex()[:8]
    return code[:8] == expected_part


def get_machine_code() -> str:
    """获取机器码（脱敏，给用户看的）"""
    return _get_machine_id()


def is_activated() -> bool:
    """检查是否已激活"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        value, _ = winreg.QueryValueEx(key, REG_VALUE)
        winreg.CloseKey(key)
        # 格式: versionsion:machine_id:signature
        parts = value.split(':')
        if len(parts) == 3 and parts[0] == VERSION:
            machine_id = parts[1]
            if machine_id == _get_machine_id():
                return True
        return False
    except FileNotFoundError:
        return False


def save_activation(code: str) -> bool:
    """保存激活信息到注册表"""
    code = code.replace('-', '').strip()
    machine_id = _get_machine_id()

    if not validate_activation_code(code, machine_id):
        return False

    # 写入注册表
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        value = f"{VERSION}:{machine_id}:{code[:16]}"
        winreg.SetValueEx(key, REG_VALUE, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
