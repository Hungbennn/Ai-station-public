"""Ống `git archive | tar -x` của bản chép kiểm có CHỦ cả hai đầu (H1 — V2-6a, bs-863.18; dot7-C02; B02/B03 vòng 1;
R2-02/R2-03 vòng 2). Nguồn `git archive` của TRẠM qua primitive P1 (nhóm riêng, kill cục bộ) theo hợp đồng sở hữu
`kiem.so_huu`: `nguon_archive(..., chu=chu)` — `Nhom` vào `chu` TRONG `ngat.hoan()` trước mọi lối ra, ngắt phát lại
lúc đó vẫn để nguồn có chủ ở `finally`. Đích `tar` dưới `tram-kiem` qua `chay` của người gọi (`chay_gioi_han` với kill
của principal), `stdin=` là ống của nguồn — không đọc archive vào RAM. MỘT hạn cho cả ống, tính TRƯỚC khi chuẩn bị
nguồn: đích nhận `timeout=` đúng phần CÒN LẠI (hết rồi thì không chạy đích), nguồn chờ phần còn lại sau đó. Mọi lối ra
(đích xong/lỗi/quá hạn/không khởi chạy, đóng ống lỗi, ngắt) → `thu_hoi_con_lai(chu)` trong `finally` (trong `hoan()`).
Ưu tiên: nguồn CHƯA xác nhận thu hồi → ném `loi` (mặc định `LoiThuHoi`) THAY mọi lỗi khác, kể cả lỗi đích, `from None`
— không nối chuỗi lỗi bên dưới (có thể mang byte môi trường); riêng ngắt (KeyboardInterrupt) vẫn là ngắt — người gọi
coi mọi ngắt là chưa sạch (cổng đóng)."""
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from contextlib import suppress
from tram.kiem.ngat import hoan

from tram.giao_viec.cay_kiem import nguon_archive
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import LoiThuHoi


def chay_ong(kho: Path, commit: str, dich: list[str], *, chay: Callable, han: float,
             loi: type[BaseException] = LoiThuHoi) -> tuple[int | None, int]:
    """(mã `git archive` — None khi hết phần hạn còn lại, mã của đích). Ném `loi` khi nguồn chưa xác nhận thu hồi,
    `TimeoutExpired` khi hết hạn chung, hoặc lỗi của đích/đóng ống — SAU khi nguồn đã thu hồi."""
    het, chu, ma, ngat = time.monotonic() + han, [], None, False
    try:
        nguon = nguon_archive(kho, commit, chu=chu)
        chu[:] = chu or [nguon]             # nguồn giả không tự ghi `chu`: nhận Nhom nó trả
        try:
            con = het - time.monotonic()
            if con <= 0:                    # chuẩn bị nguồn đã tiêu hết hạn chung: không chạy đích
                raise subprocess.TimeoutExpired([Path(dich[0]).name], han)
            r = chay(dich, stdin=nguon.p.stdout, timeout=con)
        finally:
            nguon.p.stdout.close()
        ma = nguon.cho(max(0.0, het - time.monotonic()))
    except KeyboardInterrupt:
        ngat = True
        raise
    finally:
        with hoan():
            try:
                for n in chu:
                    with suppress(OSError):
                        n.p.stdout.close()
            finally:
                if chu and not thu_hoi_con_lai(chu) and not ngat:
                    raise loi("git archive: nguồn của ống CHƯA xác nhận thu hồi "
                              "(thu hồi CHƯA) — không công nhận") from None
    return ma, r.returncode
