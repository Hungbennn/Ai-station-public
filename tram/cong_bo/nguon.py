"""Nơi trạm lấy commit của thợ để công bố (spec 3 §6.4). D4 (chốt đợt 4, chính thức khi S7 đạt) chọn `lai`:
máy B dùng `kho-tho`, máy từ xa đã xác thực dùng `ref-tam` (xem `nguon_lai.py`). Hai nguồn thành phần:
- `ref-tam`: thợ push lên ref tạm của lượt trên origin (credential thợ chỉ được `tram/luot/*` — S7 kiểm); trạm
  fetch từ origin; xoá ref tạm cũ bằng CAS;
- `kho-tho`: thợ KHÔNG có credential GitHub, chỉ đặt nhánh cục bộ `tram/luot/<bead>/<luot>` trong kho của tài khoản
  quản lý thợ; trạm fetch thẳng từ đường dẫn kho đó (tài khoản trạm cần quyền đọc — S6/S7; `safe.directory` chỉ
  cho đúng kho đó). Chỉ dùng được cho máy B (lát 3a).
Hai phương án kết thúc giống nhau: commit nằm ở `refs/tram/nhan/<giao_id>` trong kho trạm."""
from pathlib import Path

from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.cong_bo.git import LoiGit, cac_ref_remote, fetch_ve, xoa_cas


def ref_tam_cua(bead_id: str, luot: int) -> str:
    """Ref tạm của lượt — tất định từ phiếu, thợ và trạm tính giống nhau (`repo.ref_tam` của 3a-1 vẫn để None)."""
    return f"tram/luot/{bead_id}/{luot}"


def ref_nhan(giao_id: str) -> str:
    return f"refs/tram/nhan/{giao_id}"


class NguonRefTam:
    ten = "ref-tam"

    def lay(self, kho: Path, *, may_id: str, du_an: str, ref_tam: str, giao_id: str, timeout: float) -> str | None:
        return fetch_ve(kho, "origin", f"refs/heads/{ref_tam}", ref_nhan(giao_id), timeout=timeout)

    def don_cu(self, kho: Path, *, bead_id: str, luot: int, timeout: float) -> list[str]:
        """Xoá (CAS) mọi ref tạm của các lượt TRƯỚC `luot` trên origin (§6.4 bước 8); lỗi thì để lần sau."""
        try:
            cac = cac_ref_remote(kho, f"tram/luot/{bead_id}/*", timeout=timeout)
        except LoiGit:
            return []
        da_xoa = []
        for sha, ten in cac:
            so = ten.rsplit("/", 1)[-1]
            if so.isdigit() and int(so) < luot and xoa_cas(kho, ten, sha, timeout=timeout) == "ok":
                da_xoa.append(ten)
        return da_xoa


class NguonKhoTho:
    ten = "kho-tho"

    def __init__(self, kho_tho: dict[str, Path]):
        self.kho_tho = kho_tho

    def lay(self, kho: Path, *, may_id: str, du_an: str, ref_tam: str, giao_id: str, timeout: float) -> str | None:
        if may_id not in self.kho_tho:
            return None
        nguon = self.kho_tho[may_id] / du_an
        return fetch_ve(kho, str(nguon), f"refs/heads/{ref_tam}", ref_nhan(giao_id), timeout=timeout, safe=nguon)

    def don_cu(self, kho: Path, *, bead_id: str, luot: int, timeout: float) -> list[str]:
        """Ref tạm nằm ở kho thợ — thợ tự xoá nhánh cục bộ khi phiếu kết thúc."""
        return []


def chon_nguon(cb: CauHinhCongBo):
    if cb.phuong_an == "lai":
        from tram.cong_bo.nguon_lai import NguonLai
        return NguonLai(cb.kho_tho)
    if cb.phuong_an == "ref-tam":
        return NguonRefTam()
    if cb.phuong_an == "kho-tho":
        return NguonKhoTho(cb.kho_tho)
    return None
