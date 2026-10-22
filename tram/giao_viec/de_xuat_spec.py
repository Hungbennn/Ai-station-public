"""Dựng `DeXuatPhieu` cho bước `spec` của feature (spec 4 §6.1, §7.2): vai `spec`, nhánh `tram/spec-<feature>`, `cha`
= `origin/<nhanh_chinh>` lần đầu, SHA công bố/snapshot mới nhất của nhánh spec khi làm lại (sau trả về, lỗi, bí).

Không chạy mã dự án: `lenh_kiem = lenh_cho_phep = []`, không môi trường kiểm. `tieu_chi[]` = nghiệm thu sơ bộ của
phiếu yêu cầu. Lớp 4: lỗi xét lượt spec trước, góp ý trả về spec, câu trả lời escalation, bàn giao tạm của vòng này.
Ngân sách phiếu = mức `qc` (spec 4 §8: 2 lần chạy, 45 phút, 100k token ra)."""
from dataclasses import replace
from pathlib import Path

from pydantic import ValidationError

from tram.beads.mo_hinh import Bead
from tram.cham_cot.prompt import nap_vai
from tram.giao_viec.chon import UngVien
from tram.giao_viec.quyen import phien_ban_quyen
from tram.giao_viec.de_xuat import cha_cua
from tram.giao_viec.feature import cua_so_spec
from tram.giao_viec.goi import DauVaoGoi, GoiQuaLon, Lop4, dung_goi
from tram.giao_viec.lop_5 import thu_lop_5
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c, luong_lien_quan
from tram.giao_viec.lop_4 import GIU_TOI_DA, doc_tai_lieu, thu_lop_4
from tram.giao_viec.ngan_sach import ngan_sach_phieu
from tram.giao_viec.phieu_yeu_cau import doc_phieu, tieu_chi_spec
from tram.giao_viec.su_kien import SK, moi_nhat
from tram.giao_viec.tieu_chi import khoa_chong_trung
from tram.phieu.mo_hinh import DeXuatPhieu, Repo


def lop_4_spec(ds: list[SK], bead: Bead, kho_git: Path, nhanh_chinh: str) -> Lop4:
    w = cua_so_spec(ds)
    l4 = thu_lop_4(w, bead, {}, buoc="spec", kho_git=kho_git, nhanh_chinh=nhanh_chinh, commit_code=None)
    kt = moi_nhat(w, "giao.ket_thuc", lambda s: s.du_lieu.get("buoc") == "spec")
    return replace(
        l4, loi_ban_giao=tuple(kt.du_lieu.get("loi") or ()) if kt and kt.du_lieu.get("ly_do") else (),
        gop_y=tuple(s.du_lieu.get("gop_y", "") for s in ds if s.loai == "spec.tra_ve")[-GIU_TOI_DA:],
        tra_loi=tuple(s.du_lieu.get("tra_loi", "") for s in ds if s.loai == "escalation.dong")[-GIU_TOI_DA:])


def dung_de_xuat_spec(uv: UngVien, ds: list[SK], kho_git: Path, *,
                      p4c: PhuThuoc4c = PhuThuoc4c(), theo_id: dict | None = None) -> DeXuatPhieu | None:
    """None khi phiếu yêu cầu không hợp lệ, chưa có `cha`, hoặc nội dung vượt khuôn phiếu/gói (không cấp)."""
    b, da = uv.bead, uv.du_an
    phieu, _ = doc_phieu(b.description, da.ten)
    if phieu is None or (cha := cha_cua(ds, "spec", kho_git, da.nhanh_chinh)) is None:
        return None
    phien_ban, than = nap_vai("spec")
    tieu_chi = tieu_chi_spec(phieu)
    try:
        goi = dung_goi(DauVaoGoi(doc_tai_lieu(kho_git, da.nhanh_chinh, da.giao.tai_lieu_du_an),
                                ("spec", phien_ban, than), b, "spec", tuple(tieu_chi), (),
                                lop_4_spec(ds, b, kho_git, da.nhanh_chinh),
                                lop_5=thu_lop_5(b, theo_id or {}, du_an=da.ten, vai="spec", nho_lai=p4c.nho_lai),
                                luong=luong_lien_quan(p4c.gitnexus, da, b)))
        return DeXuatPhieu(
            du_an=da.ten, bead_id=b.id, tieu_de=b.title[:300], buoc="spec", vai="spec",
            repo=Repo(kho=f"~/tram/kho/{da.ten}", nhanh=f"tram/spec-{b.id}", cha=cha, nhanh_chinh=da.nhanh_chinh),
            goi_ngu_canh=goi, ngan_sach=ngan_sach_phieu("spec", da.giao.ngan_sach), lenh_kiem=[], lenh_cho_phep=[],
            can_lenh_kiem=False, can_moi_truong_kiem=False, tieu_chi=tieu_chi,
            khoa_chong_trung=khoa_chong_trung(da.ten, cha, b.id, "spec", phien_ban, phien_ban_quyen("spec")))
    except (ValidationError, GoiQuaLon):
        return None
