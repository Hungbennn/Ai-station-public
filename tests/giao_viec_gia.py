"""Bộ giao việc trên bản giả (CHỈ DÙNG TRONG TEST): BdGia, kho phiếu tạm, remote Git cục bộ, khe đã đăng ký."""
from dataclasses import dataclass, field
from pathlib import Path

from bd_gia import BdGia
from bead_gia import bead
from kho_kiem_gia import KhoGia, dung_kho
from kho_phieu_gia import LUC
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.phieu.khe import dang_ky_khe, bat_tat_khe
from tram.phieu.kho import KhoPhieu
from tram.phieu.nhip_tim import ghi_nhip

TC = "Tên kết thúc 'ỷ' không mất byte"
KHE = (("claude-1", ("coder",)), ("claude-2", ("qc",)))


def bug(id="hr-1", **kw):
    kw.setdefault("labels", ["cot:ai-lam"])
    kw.setdefault("acceptance_criteria", f"- {TC}")
    kw.setdefault("issue_type", "bug")
    kw.setdefault("title", "Sửa cắt UTF-8")
    return bead(id, **kw)


@dataclass
class TramGiao:
    bo: BoGiaoViec
    kho: KhoPhieu
    g: BdGia
    k: KhoGia
    da: DuAn
    gio: list = field(default_factory=lambda: [LUC])


def du_an_gia(tmp_path: Path, *, env: bool = True) -> DuAn:
    f = tmp_path / "env.testing"
    f.write_text("DB_DATABASE=test\n")
    return DuAn("hr-codex", Path("/r"), None, {}, lenh_cho_phep=("sh kiem.sh",),
                moi_truong_kiem=MoiTruongKiem(f, ".env.testing") if env else None,
                giao=CauHinhGiao(lenh_kiem_mac_dinh=("sh kiem.sh",)))


def dung(tmp_path: Path, *beads, khe=KHE, boc=lambda a: a, env: bool = True) -> TramGiao:
    k, db, gio = dung_kho(tmp_path), tmp_path / "su-kien.db", [LUC]
    da, g, kho = du_an_gia(tmp_path, env=env), BdGia(beads), KhoPhieu(tmp_path / "su-kien.db")
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": list(v)} for t, v in khe],
                    luc=LUC)
        for t, _ in khe:
            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
    bo = BoGiaoViec(cac_du_an=lambda: [da], tao_bd=lambda d: g, mo_kho=lambda: KhoPhieu(db), ch=CauHinhTram(),
                    dong_ho=lambda: gio[0], kho_git=lambda d: k.kho, boc=boc)
    return TramGiao(bo, kho, g, k, da, gio)
