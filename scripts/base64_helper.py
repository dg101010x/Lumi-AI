"""Helper to encode/decode using the vendored Node CLI or Python fallback."""
import subprocess
import shutil
import sys
import base64 as _pybase64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_CLI = ROOT / 'vendor' / 'progers-base64' / 'cli.js'

def _run_node(cmd, encoding, data: bytes) -> bytes:
    node = shutil.which('node')
    if not node:
        raise FileNotFoundError('node not found in PATH')
    p = subprocess.run([node, str(NODE_CLI), cmd, '--encoding', encoding], input=data, stdout=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f'node cli failed: {p.returncode}')
    return p.stdout

def encode(text: str, encoding: str = 'utf8') -> str:
    data = text.encode('utf8')
    try:
        out = _run_node('encode', encoding, data)
        return out.decode('utf8')
    except FileNotFoundError:
        if encoding == 'ascii':
            return _pybase64.b64encode(text.encode('latin1')).decode('ascii')
        return _pybase64.b64encode(text.encode('utf8')).decode('ascii')

def decode(b64text: str, encoding: str = 'utf8') -> str:
    data = b64text.encode('utf8')
    try:
        out = _run_node('decode', encoding, data)
        return out.decode('utf8')
    except FileNotFoundError:
        raw = _pybase64.b64decode(b64text)
        if encoding == 'ascii':
            return raw.decode('latin1')
        return raw.decode('utf8')

if __name__ == '__main__':
    # simple CLI: encode/decode stdin
    if len(sys.argv) < 2:
        print('Usage: base64_helper.py encode|decode [--encoding utf8|ascii]')
        sys.exit(2)
    cmd = sys.argv[1]
    enc = 'utf8'
    if '--encoding' in sys.argv:
        i = sys.argv.index('--encoding')
        if i + 1 < len(sys.argv):
            enc = sys.argv[i+1]
    data = sys.stdin.read()
    if cmd == 'encode':
        print(encode(data, enc))
    elif cmd == 'decode':
        print(decode(data, enc))
    else:
        print('unknown command')
        sys.exit(2)
