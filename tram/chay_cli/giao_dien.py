"""Giao diện chạy CLI headless một lần (spec 3 §7.2, §7.8) — CHƯA CÓ BẢN THẬT (spike S2–S4, #5 chưa duyệt).

Bản thật (3a-2) chạy `claude -p --output-format stream-json …` dưới principal thực thi của khe (S6) và điền
`KetQuaChay`. Lát 3a-1 chỉ chốt kết quả và cách phân loại kết thúc mà trạm dùng cho cầu dao (§8.3)."""
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from tram.han_muc.nguon import NguonHanMuc

KET_THUC = ("xong", "loi", "loi_he", "het_han_muc", "dung", "mo-coi")


@dataclass(frozen=True)
class KetQuaChay:
    ma_thoat: int | None
    co_assistant: bool          # stream có ít nhất một thông điệp `assistant`
    het_han_muc: bool           # `rejected` / 429 / mẫu chữ "đã hết"
    chua_dang_nhap: bool        # mẫu "chưa đăng nhập" của CLI
    bi_dung: bool               # thợ dừng (ngân sách, dừng mềm/cứng)
    token_vao: int = 0
    token_ra: int = 0
    token_cache_doc: int = 0
    token_cache_ghi: int = 0
    mo_hinh: str | None = None
    thoi_gian_ms: int = 0
    digest_log: str = ""
    reset_luc: str | None = None
    model_lech: bool = False


def ket_thuc_tu(kq: KetQuaChay) -> str:
    """`loi_he` = lỗi KHÔNG do agent (§8.3): thoát ≠ 0 mà stream không có `assistant`, hoặc chưa đăng nhập."""
    if kq.het_han_muc:
        return "het_han_muc"
    if kq.bi_dung:
        return "dung"
    if kq.chua_dang_nhap:
        return "loi_he"
    if kq.ma_thoat == 0:
        return "xong"
    return "loi" if kq.co_assistant else "loi_he"


@runtime_checkable
class ChayCLI(Protocol):
    def chay(self, argv: list[str], *, cwd: Path, env: dict[str, str], stdin: Path, log: Path,
             dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
        """Chạy một lần trong nhóm tiến trình riêng; `dung` được đặt → kết thúc nhóm (SIGTERM, 10 s, SIGKILL)."""
