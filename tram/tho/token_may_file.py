"""Kho token máy B theo passwd của UID, không tin HOME/TRAM_HOME từ môi trường."""
import os
import pwd
import re
from pathlib import Path

from tram.tho.tep_token import doc, ghi


def duong() -> Path:
    user = pwd.getpwuid(os.geteuid())
    if user.pw_name != 'tram-tho':
        raise ValueError('Token B chỉ do tram-tho giữ')
    return Path(user.pw_dir) / '.tram/token-may'


def doc_token_b() -> str | None:
    try:
        token = doc(duong())
        return token if re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token) else None
    except (OSError, ValueError, KeyError):
        return None


def ghi_token_b(token: str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
        raise ValueError('Token máy sai dạng')
    ghi(duong(), token)
