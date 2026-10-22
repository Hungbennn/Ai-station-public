"""Chọn ngoài giao dịch; kiểm lại trong giao dịch cấp. Beads đọc lại trước claim (4a-2)."""
import os
from collections.abc import Callable, Mapping
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.chon import khe_nhan, khoa_sap_xep
from tram.giao_viec.co_de_xuat import gan_co, con_luat, con_quy_trinh
from tram.giao_viec.de_xuat import dung_de_xuat
from tram.giao_viec.de_xuat_spec import dung_de_xuat_spec
from tram.giao_viec.dieu_kien import ASSIGNEE
from tram.giao_viec.feature import con_dot_spec
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.doc_lai import con_nguyen
from tram.giao_viec.kho_kiem_san import kho_kiem_co_san
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.ngan_sach import du_mot_phieu
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.su_kien import su_kien_bead
from tram.giao_viec.ung_vien import liet_ke, viec_ton_cua
from tram.giao_viec.ung_vien_spec import liet_ke_spec
from tram.han_muc.mo_hinh import HanMuc
from tram.kiem.chay_lenh import _kill_nhom
from tram.phieu.kho import KhoPhieu
from tram.phieu.mo_hinh import DeXuatPhieu
from tram.phieu.trang_thai import trang_thai_khe


@dataclass
class BoGiaoViec:
    cac_du_an: Callable[[], list[DuAn]]
    tao_bd: Callable[[DuAn], object]                  # Bd(repo, actor="tram/giao-viec")
    mo_kho: Callable[[], KhoPhieu]
    ch: CauHinhTram
    dong_ho: Callable[[], datetime]
    kho_git: Callable[[DuAn], Path | None] = kho_kiem_co_san
    kiem_tu_xa: Callable | None = None
    boc: Callable[[list[str]], list[str]] | None = None   # principal `tram-kiem` (chờ S6); None: chưa kiểm lại
    env_goc: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
    doc_beads: DocBeads | None = None                     # 4a-2: bộ đệm beads của tram-api; None: đọc `bd` mỗi lần
    don_sach: Callable[[], None] | None = None            # 3c: giết mọi tiến trình `tram-kiem`, xác nhận sạch (D22)
    cong: object | None = None                            # 3C-D2: CongLuot — lượt trước chưa sạch thì không kiểm lại
    boc_luot: Callable[[Path], Callable] | None = None    # 3C-D1: PrincipalKiem.boc_luot — hồ sơ Seatbelt mỗi lượt
    adr_hop_le: Callable[[DuAn, object], bool] = lambda da, b: False
    kill: Callable[[int, int], None] = _kill_nhom        # 3a-2: kill nhóm qua principal kiểm
    thu_muc_kiem: Path | None = None                      # 4a-2: gốc bản chép kiểm lại; None: ~/.tram/kiem
    de_nghi: object | None = None                         # TC: NguonDeNghi; None: không ghi
    p4c: PhuThuoc4c = field(default_factory=PhuThuoc4c)

    def _da_nhan(self, bd, bead_id: str) -> bool:
        """`--claim` có ID thao tác là chính trạng thái đích: đã `in_progress` với assignee trạm → coi như xong."""
        try:
            bd.nhan_viec(bead_id)
            return True
        except LoiBd:
            try:
                b = bd.mot(bead_id)
            except LoiBd:
                return False
            return b.status == "in_progress" and b.assignee == ASSIGNEE

    def _chot(self, bd, uv, kho, kg, *, chi_plan=False) -> bool:
        """Đọc lại NGAY TRƯỚC cấp (4a-1 G3); bead `open` → `--claim` rồi đọc lại lần nữa (spec 4 §5.4)."""
        if not con_nguyen(bd, uv.du_an, uv.bead, buoc=uv.buoc, adr_hop_le=self.adr_hop_le,
                          da_merge=lambda beads: feature_da_merge(kho, uv.du_an, beads, kg)):
            return False
        if chi_plan or uv.buoc == "spec" or uv.bead.status != "open":
            return True
        if not self._da_nhan(bd, uv.bead.id):
            return False
        if self.doc_beads is not None:
            self.doc_beads.danh_dau_cu(uv.du_an.ten)
        return con_nguyen(bd, uv.du_an, uv.bead, sau_claim=True, buoc=uv.buoc, adr_hop_le=self.adr_hop_le,
                          da_merge=lambda beads: feature_da_merge(kho, uv.du_an, beads, kg))

    def chon(self, khe_id: str, han_muc: HanMuc | None) -> DeXuatPhieu | None:
        with closing(self.mo_kho()) as kho:
            cac_khe, ung_vien = trang_thai_khe(kho, bay_gio=self.dong_ho(), ch=self.ch), []
            for da in self.cac_du_an():
                if (kg := self.kho_git(da)) is None:
                    continue
                bd = self.tao_bd(da)
                try:
                    beads, san = self.doc_beads.lay(da, bd) if self.doc_beads else (bd.tat_ca(), bd.san_sang())
                except LoiBd:
                    continue
                merge = feature_da_merge(kho, da, beads, kg)
                ung_vien += [(uv, beads, bd, kg) for uv in liet_ke(kho, da, beads, san, merge)
                             + liet_ke_spec(kho, da, beads, san)]
            for uv, beads, bd, kg in sorted(ung_vien, key=lambda x: khoa_sap_xep(x[0])):
                if uv.du_an.theo_co is None and not khe_nhan(khe_id, han_muc, uv, cac_khe, self.ch):
                    continue
                ds = su_kien_bead(kho, uv.du_an.ten, uv.bead.id)
                dx = (dung_de_xuat_spec(uv, ds, kg, p4c=self.p4c, theo_id={b.id: b for b in beads}) if uv.buoc == "spec"
                      else dung_de_xuat(uv, ds, {b.id: b for b in beads}, kg, self.p4c, kho.db))
                if dx is not None:
                    dx = gan_co(kho, uv, beads, kg, ds, dx, khe_id, han_muc, cac_khe, self.ch, self.dong_ho(), bd)
                if dx is None or not self._chot(bd, uv, kho, kg, chi_plan=bool(dx.co and dx.co.get("pha"))):
                    continue
                return dx
        return None

    def con_hop_le(self, dx: DeXuatPhieu) -> bool:
        """Kiểm lại nhanh trong giao dịch cấp phiếu: không còn công việc chờ/câu hỏi chưa chuyển escalation của bead,
        chưa có escalation mở trong sự kiện, còn ngân sách cho phiếu này."""
        da = next((d for d in self.cac_du_an() if d.ten == dx.du_an), None)
        if da is None or not con_luat(da, dx):
            return False
        with closing(self.mo_kho()) as kho:
            ds = su_kien_bead(kho, dx.du_an, dx.bead_id)
            mo = {s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.tao"} - {
                s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.dong"}
            return (con_quy_trinh(ds, dx) and not mo and dx.bead_id not in viec_ton_cua(kho, dx.du_an)
                    and du_mot_phieu(kho, ds, dx.ngan_sach, da.giao.ngan_sach.bead)
                    and (dx.buoc != "spec" or con_dot_spec(ds)))
