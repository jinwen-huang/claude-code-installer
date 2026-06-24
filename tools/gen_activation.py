"""激活码生成器 — 只有你用的"""
import sys

MASTER_KEY = "jinwen"
VERSION = "v1"

if __name__ == '__main__':
    print('=' * 50)
    print('  Claude Code 安装工具 — 激活码生成器')
    print('=' * 50)
    print()
    print('输入用户的机器码（16位），生成激活码。')
    print()

    while True:
        machine_id = input('机器码: ').strip()
        if not machine_id:
            break
        if len(machine_id) < 8:
            print('❌ 机器码格式不对，至少8位')
            print()
            continue

        import hashlib
        import hmac

        key = hmac.new(
            MASTER_KEY.encode(),
            f"{VERSION}:{machine_id}".encode(),
            hashlib.sha256
        ).digest()
        suffix = hashlib.sha256(key).hexdigest()[:4]
        code = key.hex()[:8] + '-' + suffix
        code = code.upper()

        print(f'✅ 激活码: {code}')
        print()

    print('退出。')
