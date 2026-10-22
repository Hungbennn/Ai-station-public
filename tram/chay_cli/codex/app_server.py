"""Hỏi hạn mức Codex qua `codex app-server` lúc khe RẢNH (spec 3 §8.1: mỗi 5 phút, không cần gửi tin cho model).

Giao thức theo tài liệu app-server (JSON-RPC qua stdio, mỗi dòng một JSON, không trường `jsonrpc`): `initialize` (id 0)
→ chờ trả lời → thông báo `initialized` → `account/rateLimits/read` (id 1). CHƯA chạy thật — chờ spike S5 (dưới launchd,
`CODEX_HOME` riêng của khe). Lát P1: tiến trình đi qua `vong_doi` — đọc stdout bằng `select` theo MỘT hạn tổng (không
Timer/luồng nền), chụp cây mỗi giây trong lúc chờ, xong hay lỗi đều `thu_hoi` cả cây qua `kill` của người gọi; không xác
nhận thu hồi → `LoiThuHoi`. Cận trên một lần hỏi: 10 s (+ ≤ 5 s một lần `ps` lố hạn) + `thu_hoi(1, 3, 2)` ≤ 1 + 3 +
2 × (2 + 5) + 3 × 5 = 33 s → 48 s.
Thông báo lỗi cố định: không chép argv, stderr hay chữ do app-server gửi về (dot6-Q06).
bs-78r.10 (dot6-Q02): app-server chạy dưới PRINCIPAL CỦA KHE (`principal.boc`, `principal.kill_nhom`) với env dựng mới
(PATH của CLI theo cấu hình thợ, LANG, CODEX_HOME) — không đọc env của tài khoản quản lý; không có principal → không
spawn."""
import json
import os
import select
import subprocess
import time
from datetime import datetime
from pathlib import Path

from tram.chay_cli.codex.han_muc import han_muc_app_server
from tram.han_muc.mo_hinh import HanMuc
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, khoi_chay, kill_cuc_bo

PHUONG_THUC = "account/rateLimits/read"
CHU_KY_RANH_GIAY = 300
THOI_GIAN_CHO = 10.0
DONG_TOI_DA = 1 << 20


class LoiAppServer(RuntimeError):
    pass


class _HetGio(Exception):
    pass


def _gui(p, tin: dict) -> None:
    p.stdin.write((json.dumps(tin) + "\n").encode())
    p.stdin.flush()


def _dong(n, han: float, dem: bytearray) -> bytes | None:
    """Một dòng stdout trước `han` (monotonic); None khi EOF. Chụp cây mỗi `CHU_KY_CHUP` giây khi chưa có dữ liệu."""
    fd = n.p.stdout.fileno()
    while b"\n" not in dem:
        con = han - time.monotonic()
        if con <= 0:
            raise _HetGio
        if not select.select([fd], [], [], min(con, CHU_KY_CHUP))[0]:
            n.cay()
            continue
        khuc = os.read(fd, 65536)
        if not khuc:
            ra = bytes(dem)
            dem.clear()
            return ra or None
        dem += khuc
        if len(dem) > DONG_TOI_DA:
            raise LoiAppServer("app-server gửi dòng quá dài")
    i = dem.index(b"\n") + 1
    ra = bytes(dem[:i])
    del dem[:i]
    return ra


def _cho(n, ma: int, han: float, dem: bytearray) -> dict:
    while (dong := _dong(n, han, dem)) is not None:
        try:
            tin = json.loads(dong)
        except ValueError:
            continue
        if isinstance(tin, dict) and tin.get("id") == ma:
            if "error" in tin:
                loi = tin["error"] if isinstance(tin["error"], dict) else {}
                so = loi.get("code") if type(loi.get("code")) is int else "?"
                raise LoiAppServer(f"app-server trả lỗi (mã {so})")
            return tin["result"] if isinstance(tin.get("result"), dict) else {}
    raise LoiAppServer("app-server đóng trước khi trả lời")


def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float = THOI_GIAN_CHO,
                   kill: Kill = kill_cuc_bo, khoi=khoi_chay) -> dict:
    han, dem = time.monotonic() + thoi_gian_cho, bytearray()
    with so_huu("không xác nhận thu hồi tiến trình app-server", cho_term=1.0, cho_cuoi=3.0, han_gui=2.0) as chu:
        n = khoi(argv, kill=kill, chu=chu, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                 env=env)                        # sở hữu từ PID (`so_huu`): mọi lối ra thu hồi cả cây, kể cả ngắt
        try:
            _gui(n.p, {"method": "initialize", "id": 0,
                       "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi", "version": "3b"}}})
            _cho(n, 0, han, dem)
            _gui(n.p, {"method": "initialized"})
            _gui(n.p, {"method": PHUONG_THUC, "id": 1})
            return _cho(n, 1, han, dem)
        except _HetGio:
            raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
        except OSError as e:
            raise LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
        finally:
            for f in (n.p.stdin, n.p.stdout):
                try:
                    f.close()
                except OSError:
                    pass


def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, principal, path: str,
                     codex: str = "codex", hoi=hoi_app_server) -> HanMuc | None:
    """Số đo của khe, hoặc None khi không đọc được (vòng 3a-2 gửi nhịp không có số đo → cửa sổ chưa biết, #15).
    `principal` None → None, KHÔNG chạy dưới tài khoản quản lý. `LoiThuHoi` để nổi lên: người gọi phải biết."""
    if principal is None:
        return None
    env = {"PATH": path, "LANG": "C.UTF-8", "CODEX_HOME": str(thu_muc_cau_hinh)}
    try:
        kq = hoi(principal.boc([codex, "app-server"]), env=env, kill=principal.kill_nhom)
    except (LoiAppServer, OSError, ValueError):
        return None
    return han_muc_app_server(kq, khe_id=khe_id, bay_gio=bay_gio)
