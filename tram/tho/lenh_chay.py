"""Lệnh phía TÀI KHOẢN QUẢN LÝ THỢ (lát 3a-2): `tram tho chay` (một tiến trình/máy, mỗi khe một vòng — spec 3 §5),
`tram tho nhan-token` (token B vào file kín, máy từ xa vào Keychain, đọc từ ống/ô ẩn, không in). Chạy thật cần cổng
S2–S4, S6, S7 (`tram tho kiem` xanh hết) — không có cờ nào bỏ qua."""
import re
import subprocess
import sys
import threading

import yaml

from tram.tho.khach import KEYCHAIN_THO, doc_token_may
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.khoi_dong import dang_ky
from tram.tho.principal import ChuaCoPrincipal, doc_principal

TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{40,64}")


def chay_may(nc: NguCanhTho, tat: threading.Event, *, chu_ky_don: float = 600.0, cho=None) -> int:
    from tram.tho.don_dep import don_da_dong
    from tram.tho.vong_khe import VongKhe
    ch = nc.ch
    if ch.chay.day is None:
        print("Chưa khai chay.day trong tho.yaml (ref-tam | kho-tho — Đại ca chốt sau S7).", file=sys.stderr)
        return 2
    try:
        for k in ch.khe:
            doc_principal(k.principal)
    except ChuaCoPrincipal as e:
        print(f"{e}", file=sys.stderr)
        return 2
    san_sang, ma = dang_ky(nc, tat, cho)
    if not san_sang:
        return ma
    luong = [threading.Thread(target=VongKhe(nc, k).chay, args=(tat,), name=f"khe-{k.ten}") for k in ch.khe]
    for t in luong:
        t.start()
    while not tat.wait(chu_ky_don):
        don_da_dong(nc)
    for t in luong:
        t.join()
    return 0


def _chay(args) -> int:
    from tram.tho.khoi_dong import khoi_dong
    return khoi_dong(chay_may, doc_token_may)


def luu_token_may(token: str, *, tren_may_b=False, chay=subprocess.run, doc=doc_token_may) -> None:
    """B dùng file kín; máy từ xa giữ stdin Keychain. Không in token."""
    if not TOKEN_RE.fullmatch(token):
        raise ValueError("Token máy sai dạng")
    if tren_may_b:
        from tram.tho.token_may_file import ghi_token_b
        ghi_token_b(token)
        return
    chay(["security", "-i"], input=f"add-generic-password -U -s {KEYCHAIN_THO} -a tram -w {token}\n", text=True,
         check=True, capture_output=True, timeout=10)
    if doc() != token:
        raise RuntimeError("Không lưu được token vào Keychain (Keychain của user này có mở không? — S2)")


def _nhan_token(args) -> int:
    import getpass
    token = (sys.stdin.readline() if not sys.stdin.isatty() else getpass.getpass("Dán token máy (ẩn): ")).strip()
    try:
        from tram.duong_dan import tram_home
        from tram.tho.cau_hinh import nap_cau_hinh_tho
        may_b = getattr(args, "may_b", False)
        if not may_b and (tram_home() / "tho.yaml").exists():
            may_b = nap_cau_hinh_tho().tren_may_b
        if may_b:
            luu_token_may(token, tren_may_b=True)
        else:
            luu_token_may(token)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, yaml.YAMLError):
        print("Chưa xác nhận lưu token máy; giữ thợ tắt và đối soát kho token.", file=sys.stderr)
        return 2
    print("Đã lưu token máy; chưa bật thợ.")
    return 0


def them_lenh_chay(tho) -> None:
    tho.add_parser("chay", help="Chạy máy thợ: nhịp tim, nhận phiếu, chạy CLI (chờ cổng S2–S7)").set_defaults(ham=_chay)
    nhan = tho.add_parser("nhan-token", help="Lưu token qua stdin/ô ẩn; B dùng --may-b trước khi có YAML")
    nhan.add_argument("--may-b", action="store_true")
    nhan.set_defaults(ham=_nhan_token)
