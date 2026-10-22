"""Đối soát thao tác công bố còn mở của một bead (spec 3 §6.4 bước 6, §6.6) — sau crash, timeout push (`khong_ro`),
hay phiếu bị thu hồi khi push đang bay (`can_hoan_tac`). Không bao giờ đoán "lần trước đã thất bại": so SHA của ref
công bố trên remote với commit của thao tác:
- remote = commit mới, phiếu còn hiệu lực đúng lượt → ghi `giao.cong_bo` (muộn), thao tác `xong`;
- remote = commit mới mà phiếu đã hết hiệu lực/lượt đổi → HOÀN TÁC bằng CAS về `sha_cu` (snapshot đã lấy `sha_cu`);
- remote = `sha_cu` và thao tác đã cũ hơn `cu_hon_giay` → push không tới: `bo` (còn trẻ thì chờ — push bị kill vẫn
  có thể tới muộn);
- khác cả hai → ai đó đẩy ngoài luồng: giữ nguyên, người gọi báo `nhanh-bi-day-ngoai-luong`."""
from datetime import datetime, timedelta
from pathlib import Path

from tram.cong_bo.git import LoiGit, day_cas, sha_remote, xoa_cas
from tram.cong_bo.op import OpCongBo, dat_trang_thai, ghi_cong_bo, op_mo
from tram.duong_dan import doc_luc
from tram.phieu.kho import KhoPhieu


def _con_hieu_luc(kho: KhoPhieu, op: OpCongBo) -> bool:
    b = kho.lay(op.giao_id)
    return (b is not None and b.trang_thai == "hieu_luc" and b.phieu.luot == op.luot
            and kho.luot_hien_hanh(op.du_an, op.bead_id) == op.luot)


def hoan_tac(kho: KhoPhieu, op: OpCongBo, *, kho_git: Path, timeout: float, bay_gio: datetime) -> str:
    kq = (day_cas(kho_git, op.sha_cu, op.nhanh, op.commit_moi, timeout=timeout) if op.sha_cu
          else xoa_cas(kho_git, op.nhanh, op.commit_moi, timeout=timeout))
    with kho.giao_dich():
        dat_trang_thai(kho, op.id, "hoan_tac" if kq == "ok" else "can_hoan_tac", bay_gio)
    return "hoan_tac" if kq == "ok" else "can_hoan_tac"


def doi_soat_bead(kho: KhoPhieu, du_an: str, bead_id: str, *, kho_git: Path, timeout: float, bay_gio: datetime,
                  cu_hon_giay: float) -> str | None:
    """Trả trạng thái của thao tác mở sau đối soát (None = không có thao tác mở). Thao tác `dang` trẻ hơn
    `cu_hon_giay` là của một yêu cầu đang chạy — không đụng; thao tác `khong_ro` thì remote đã có commit là xác
    nhận được ngay, còn kết luận "không tới" phải chờ đủ `cu_hon_giay`."""
    op = op_mo(kho, du_an, bead_id)
    if op is None:
        return None
    if op.trang_thai == "dang" and bay_gio - doc_luc(op.luc) < timedelta(seconds=cu_hon_giay):
        return "dang"
    try:
        remote = sha_remote(kho_git, op.nhanh, timeout=timeout)
    except LoiGit:
        return op.trang_thai
    if remote == op.commit_moi:
        with kho.giao_dich():
            if op.trang_thai != "can_hoan_tac" and _con_hieu_luc(kho, op):
                ghi_cong_bo(kho, du_an=du_an, bead_id=bead_id, luot=op.luot, commit=op.commit_moi, ref=op.nhanh,
                            luc=bay_gio)
                dat_trang_thai(kho, op.id, "xong", bay_gio)
                return "xong"
            dat_trang_thai(kho, op.id, "can_hoan_tac", bay_gio)
        return hoan_tac(kho, op, kho_git=kho_git, timeout=timeout, bay_gio=bay_gio)
    if remote == op.sha_cu and bay_gio - doc_luc(op.luc) >= timedelta(seconds=cu_hon_giay):
        with kho.giao_dich():                       # push không rõ mà đủ lâu vẫn chưa tới remote: coi như bỏ
            dat_trang_thai(kho, op.id, "bo", bay_gio)
        return "bo"
    return op.trang_thai
