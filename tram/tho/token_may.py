"""Ghi token: B dùng file kín; máy từ xa giữ Keychain/stdin, không log giá trị."""
import hmac
import re
import subprocess

from tram.tho.khach import KEYCHAIN_THO, doc_token_may

MAY_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,31}")
TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{32,128}")


def ghi_token_may(may_id: str, token: str, *, tren_may_b=False, chay=subprocess.run) -> None:
    if not MAY_RE.fullmatch(may_id or "") or not TOKEN_RE.fullmatch(token or ""):
        raise ValueError("may_id hoặc token trạm trả về sai dạng — không ghi kho token")
    if tren_may_b:
        from tram.tho.token_may_file import ghi_token_b
        ghi_token_b(token)
        return
    chay(["security", "-i"], input=f'add-generic-password -U -s {KEYCHAIN_THO} -a {may_id} -w "{token}"\n',
         text=True, check=True, capture_output=True)
    doc = doc_token_may(chay=chay)
    if doc is None or not hmac.compare_digest(doc, token):
        raise RuntimeError(f"Không ghi được Keychain {KEYCHAIN_THO} — kiểm Keychain của tài khoản quản lý thợ")
