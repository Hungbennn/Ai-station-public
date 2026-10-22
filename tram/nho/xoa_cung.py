"""Xoá cứng (spec 1b §5, §11): lệnh riêng của Đại ca, chỉ khi dịch vụ dừng (khoá flock rảnh — một tiến trình ghi).

Chỉ xoá ký ức ĐÃ xoá mềm (hai bước: xoá mềm trên dashboard / `tram nho xoa`, rồi xoá cứng), theo `id` hoặc theo
phạm vi khớp CHÍNH XÁC (một trong bốn dạng — không bao giờ so tiền tố). Xoá luôn nội dung trong kế hoạch đã xong của
nhật ký và dọn hết phiên bản LanceDB cũ. Ký ức thăng cấp: ghi cặp gốc vào sổ cặp để không thăng cấp lại (§8)."""
import json
import warnings
from dataclasses import dataclass
from datetime import timedelta
from itertools import combinations
from pathlib import Path

from tram.nho.ap_dung import TAC_NHAN
from tram.nho.bang import sql
from tram.nho.khoa import khoa_dich_vu
from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import SO_CHIEU
from tram.nho.nhat_ky import NhatKy
from tram.nho.pham_vi import LoiVungCap, du_an_cua, la_pham_vi
from tram.su_kien.kho import KhoSuKien


class DichVuDangChay(RuntimeError):
    pass


class ConThaoTacDo(RuntimeError):
    """Nhật ký còn thao tác dở: áp dụng lại có thể tạo lại ký ức vừa xoá — chạy dịch vụ cho xong rồi dừng."""


@dataclass(frozen=True)
class KetQuaXoaCung:
    hang: tuple[dict, ...]          # {id, pham_vi}
    da_xoa: bool


def _dieu_kien(id: str | None, pham_vi: str | None) -> str:
    if (id is None) == (pham_vi is None):
        raise ValueError("Cần đúng một trong id hoặc pham_vi")
    if pham_vi is not None and not la_pham_vi(pham_vi):
        raise LoiVungCap(f"Phạm vi phải khớp chính xác một trong bốn dạng (vd /du-an/x/cach-lam): {pham_vi[:80]!r}")
    return "da_xoa = true AND " + (f"id = {sql(id)}" if id is not None else f"pham_vi = {sql(pham_vi)}")


def xoa_cung(thu_muc: Path, kho_sk: KhoSuKien, *, id: str | None = None, pham_vi: str | None = None,
             that: bool = False, so_chieu: int = SO_CHIEU) -> KetQuaXoaCung:
    """`that=False`: chỉ liệt kê (để hỏi `dong-y`). Dịch vụ đang chạy → DichVuDangChay."""
    dk = _dieu_kien(id, pham_vi)
    with khoa_dich_vu(thu_muc) as duoc:
        if not duoc:
            raise DichVuDangChay("memory service đang chạy — dừng trước: launchctl bootout gui/$(id -u)/vn.tram.nho")
        kho = KhoKyUc(thu_muc / "lancedb", so_chieu=so_chieu)
        hang = kho.quet(dk, cot=["id", "pham_vi", "nguon"])
        if not that or not hang:
            return KetQuaXoaCung(tuple({"id": h["id"], "pham_vi": h["pham_vi"]} for h in hang), False)
        nk = NhatKy(thu_muc / "nhat-ky.db")
        try:
            if nk.dang_do():
                raise ConThaoTacDo("Nhật ký còn thao tác dở — chạy dịch vụ để nó làm xong, dừng lại rồi xoá cứng")
            for h in hang:
                goc = sorted({n["id_goc"] for n in json.loads(h["nguon"])
                              if n.get("loai") == "thang_cap" and n.get("id_goc")})
                for a, b in combinations(goc, 2):
                    nk.ghi_cap(f"{a}|{b}", "xoa_cung")
                nk.xoa_noi_dung_ke_hoach(h["id"])
        finally:
            nk.close()
        kho.xoa_cung([h["id"] for h in hang])
        with warnings.catch_warnings():                 # cảnh báo "0 phá người đọc đang mở" — dịch vụ đã dừng
            warnings.simplefilter("ignore", UserWarning)
            kho.don_dep(timedelta(0))
        for h in hang:
            kho_sk.ghi(du_an_cua(h["pham_vi"]) or "_tram", "nho.xoa_cung", {"id": h["id"], "pham_vi": h["pham_vi"]},
                       tac_nhan=TAC_NHAN)
        return KetQuaXoaCung(tuple({"id": h["id"], "pham_vi": h["pham_vi"]} for h in hang), True)
