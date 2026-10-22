"""`subprocess.run` có hạn và sở hữu cây (lát 3C-B, dot6-C02) — cùng hình dạng gọi `chay(argv, capture_output=…,
text=…, timeout=…)` mà mã dọn lịch/tiến trình của 3c đã dùng, nhưng đi qua `vong_doi`: trong lúc chờ vẫn chụp cây mỗi
`CHU_KY_CHUP` giây; quá hạn → thu hồi cả cây qua `kill` của principal rồi ném `TimeoutExpired`; không xác nhận thu hồi
→ `LoiThuHoi`. Ngoại lệ chỉ mang TÊN chương trình, không argv/đường dẫn/stdout/stderr (dot6-Q06). Luôn đọc bytes rồi
giải mã `errors="replace"` khi `text=True` — đầu ra không phải UTF-8 không làm bỏ qua bước thu hồi.
Review A03, R2-02, R2-04: KHÔNG gặt gốc bằng `communicate` — `_ong` đọc/ghi ống bằng `selectors` (selector đóng bằng
`with` ở mọi lối ra) và chờ gốc bằng `Nhom.cho` (xác giữ số nhóm gốc tới `thu_hoi`). Hạn tuyệt đối tính TRƯỚC spawn;
spawn và mọi bước sau trong vùng sở hữu (`so_huu`): lỗi/ngắt ở đâu cũng `_don` — đóng TỪNG ống (lỗi đóng không chặn
ống sau) rồi LUÔN thu hồi, cả hai trong `ngat.hoan()`. Chưa xác nhận → `LoiThuHoi` THAY lỗi thường/lỗi ống (`from
None`); ngắt (KeyboardInterrupt) vẫn là ngắt — mọi ngắt đều là "chưa công nhận" ở người gọi.
H1 (V2-6a, bs-863.18 — plan B): `stdin=` (file object/FD, vd. ống của `git archive`) đưa THẲNG cho Popen — không đọc vào
RAM, `p.stdin` khi đó là None nên `_ong`/`_don` không đụng tới; loại trừ `input` TRƯỚC spawn; người gọi giữ và đóng bản
sao của mình (sau khi hàm trả, để nguồn nhận SIGPIPE)."""
import contextlib
import math
import os
import selectors
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from tram.kiem.ngat import hoan
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, LoiThuHoi, khoi_chay

_doc, _ghi, _bo_chon = os.read, os.write, selectors.DefaultSelector       # test thay để tiêm lỗi đúng điểm đọc/ghi


def _ong(n, input: bytes | None, het: float) -> tuple[bytes | None, bytes | None, bool]:
    """(stdout, stderr, xong) — xong: mọi ống đã EOF VÀ gốc đã thoát trước `het`. Không gặt gốc."""
    p, ra, ma = n.p, {}, None
    with _bo_chon() as sel:
        for f in (p.stdout, p.stderr):
            if f is not None:
                sel.register(f, selectors.EVENT_READ)
                ra[f] = bytearray()
        vao = memoryview(input or b"")
        if p.stdin is not None:
            sel.register(p.stdin, selectors.EVENT_WRITE) if vao else p.stdin.close()
        while (con := het - time.monotonic()) > 0:
            for k, _ in sel.select(min(CHU_KY_CHUP, con)) if sel.get_map() else ():
                if k.fileobj is p.stdin:
                    try:
                        vao = vao[_ghi(k.fd, vao[:512]):]               # ≤ PIPE_BUF: select báo ghi được thì không chặn
                    except BrokenPipeError:
                        vao = vao[:0]
                    if not vao:
                        sel.unregister(p.stdin)
                        p.stdin.close()
                elif d := _doc(k.fd, 65536):
                    ra[k.fileobj] += d
                else:
                    sel.unregister(k.fileobj)
            if ma is None:
                ma = n.cho(0.0 if sel.get_map() else min(CHU_KY_CHUP, max(0.0, het - time.monotonic())))
            elif time.monotonic() >= n.lan_chup + CHU_KY_CHUP:
                n.cay()                                                   # gốc đã thoát, ống còn mở: vẫn theo dõi cây
            if ma is not None and not sel.get_map():
                return (bytes(ra[p.stdout]) if p.stdout else None), (bytes(ra[p.stderr]) if p.stderr else None), True
    return None, None, False


def _don(chu: list, ten: list[str], loi: BaseException | None) -> None:
    """Đóng TỪNG ống của ta rồi LUÔN thu hồi mọi `Nhom` trong `chu`, cả hai trong `hoan()` (ngắt lần hai ném SAU khi
    xong). Chưa xác nhận → `LoiThuHoi` THAY `loi` và mọi lỗi đóng ống; `loi` là ngắt thì ngắt vẫn thắng."""
    with hoan():
        try:
            for n in chu:
                for f in (n.p.stdin, n.p.stdout, n.p.stderr):
                    if f is not None:
                        with contextlib.suppress(OSError):
                            f.close()
        finally:
            if not thu_hoi_con_lai(chu) and not isinstance(loi, KeyboardInterrupt):
                qua = " quá hạn và" if isinstance(loi, subprocess.TimeoutExpired) else ":"
                raise LoiThuHoi(f"{ten}{qua} không xác nhận thu hồi cây tiến trình") from None


def chay_gioi_han(argv: list[str], *, kill: Kill, timeout: float, capture_output: bool = False, text: bool = False,
                  input=None, stdin=None, env=None, cwd=None, check: bool = False,
                  khoi: Callable = khoi_chay) -> subprocess.CompletedProcess:
    if not math.isfinite(timeout):
        raise ValueError("timeout phải hữu hạn")
    if input is not None and stdin is not None:
        raise ValueError("input và stdin loại trừ nhau")
    ten = [Path(str(argv[0])).name] if argv else []
    ong = subprocess.PIPE if capture_output else subprocess.DEVNULL
    if text and isinstance(input, str):
        input = input.encode()
    vao = stdin if stdin is not None else subprocess.PIPE if input is not None else subprocess.DEVNULL
    het, chu = time.monotonic() + timeout, []                            # hạn tuyệt đối tính TRƯỚC spawn
    try:
        try:
            n = khoi(list(argv), kill=kill, stdin=vao, stdout=ong, stderr=ong, env=env, cwd=cwd, chu=chu)
        except OSError as e:                    # `khoi_chay`: OSError chỉ khi Popen chưa tạo được tiến trình
            raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
        chu[:] = chu or [n]                     # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
        ra, loi, xong = _ong(n, input, het)
    except BaseException as e:
        _don(chu, ten, e)
        raise
    _don(chu, ten, None if xong else subprocess.TimeoutExpired(ten, timeout))
    if not xong:
        raise subprocess.TimeoutExpired(ten, timeout)
    if check and n.p.returncode:
        e = subprocess.CalledProcessError(n.p.returncode, ten, ra, loi)     # cmd rút gọn; argv đủ chỉ để ghi log Uq
        e.argv = list(argv)
        raise e
    if text:
        ra, loi = (None if x is None else x.decode("utf-8", "replace") for x in (ra, loi))
    return subprocess.CompletedProcess(list(argv), n.p.returncode, ra, loi)
