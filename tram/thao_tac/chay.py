"""Chạy một thao tác ghi idempotent theo ma_thao_tac (spec 2 §12.3)."""
import hashlib
import json
import re
import sqlite3
import threading
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass

from tram.duong_dan import doc_luc
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

MA_RE = re.compile(r"[A-Za-z0-9-]{8,64}")
Buoc = tuple[str, Callable[[dict], object]]


@dataclass(frozen=True)
class YeuCau:
    ma: str
    loai: str
    du_an: str
    bead_id: str | None
    noi_dung: dict
    expected_version: str


@dataclass(frozen=True)
class KetQuaThaoTac:
    ket_qua: dict
    lap_lai: bool


_KHOA_CHUNG = threading.Lock()
_KHOA: dict[tuple[str, str | None], threading.Lock] = {}


@contextmanager
def khoa_bead(du_an: str, bead_id: str | None) -> Iterator[None]:
    """Một tram-api một tiến trình (Global Constraints) → khoá trong bộ nhớ đủ tuần tự hoá theo bead."""
    with _KHOA_CHUNG:
        k = _KHOA.setdefault((du_an, bead_id), threading.Lock())
    with k:
        yield


def digest(yc: YeuCau) -> str:
    tho = json.dumps({"loai": yc.loai, "du_an": yc.du_an, "bead_id": yc.bead_id, "noi_dung": yc.noi_dung},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(tho.encode()).hexdigest()


def cung_version(a: str, b: str) -> bool:
    try:
        return doc_luc(a) == doc_luc(b)
    except ValueError:
        return a == b


def chay_thao_tac(kho_tt: KhoThaoTac, yc: YeuCau, *, kiem_moi: Callable[[], None],
                  cac_buoc: Sequence[Buoc], kiem_quyen: Callable[[], None] = lambda: None) -> KetQuaThaoTac:
    """`digest` gồm loại, dự án, bead, nội dung — **không** gồm `expected_version` (N4): gửi lại cùng mã
    sau khi bead đã đổi (do chính thao tác này) vẫn nhận kết quả cũ thay vì 409."""
    if not MA_RE.fullmatch(yc.ma):
        raise KhongHopLe("ma_thao_tac phải 8–64 ký tự chữ, số hoặc '-'")
    dg = digest(yc)
    with khoa_bead(yc.du_an, yc.bead_id):
        bg = kho_tt.lay(yc.ma)
        if bg is not None:
            if bg.digest_noi_dung != dg:
                raise XungDot("Cùng ma_thao_tac nhưng nội dung khác")
            if bg.ket_qua is not None:
                return KetQuaThaoTac(bg.ket_qua, True)
            da_xong = dict(bg.buoc_da_xong)
        else:
            kiem_quyen()
            kiem_moi()
            try:
                kho_tt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=yc.bead_id, digest=dg,
                           expected_version=yc.expected_version)
            except sqlite3.IntegrityError:
                raise XungDot("ma_thao_tac đã được dùng cho thao tác khác") from None
            da_xong = {}
        if bg is not None:
            kiem_quyen()  # Lần trước lỗi giữa các bước: quyền cũ có thể đã hết hạn/thu hồi.
        for ten, ham in cac_buoc:
            if ten not in da_xong:
                da_xong[ten] = ham(da_xong)
                kho_tt.xong_buoc(yc.ma, ten, da_xong[ten])
        kho_tt.ket_thuc(yc.ma, da_xong)
        return KetQuaThaoTac(da_xong, False)
