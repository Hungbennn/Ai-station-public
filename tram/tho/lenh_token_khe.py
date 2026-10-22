"""Chỉ dựng argv không bí mật; helper thuộc runtime tin cậy, được chạy SAU principal.boc."""
from pathlib import Path

from tram.kiem.toolchain import PYTHON


def lenh_token_khe(*args):
    return [f'{PYTHON}/bin/python3.12', '-I', str(Path(__file__).with_name('claude_token.py')), *args]


def boc_token(argv):
    return lenh_token_khe('chay', *argv[1:]) if argv and argv[0] == 'claude' else argv
