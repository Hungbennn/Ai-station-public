"""Ứng viên bước `spec` của một dự án cho lần xin việc (spec 4 §5.1 "Bead feature", §5.2, §8): feature đủ điều kiện,
bước kế tiếp là `spec`, còn ngân sách cho một phiếu (`du_mot_phieu`, mức phiếu `spec`) và đợt sửa spec chưa hết.
Feature KHÔNG claim (`status` giữ `open` — điều kiện giao `spec` là `open` + `bd ready`)."""
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.chon import UngVien
from tram.giao_viec.feature import buoc_feature, con_dot_spec, ly_do_khong_giao_spec
from tram.giao_viec.ngan_sach import du_mot_phieu, ngan_sach_phieu
from tram.giao_viec.su_kien import su_kien_bead
from tram.giao_viec.ung_vien import la_do, trang_thai_bead, viec_ton_cua
from tram.phieu.kho import KhoPhieu


def liet_ke_spec(kho: KhoPhieu, du_an: DuAn, beads: list[Bead], san_sang: set[str]) -> list[UngVien]:
    theo_id, ton, ra = {b.id: b for b in beads}, viec_ton_cua(kho, du_an.ten), []
    ns = du_an.giao.ngan_sach
    for b in beads:
        if ly_do_khong_giao_spec(b, san_sang, du_an.ten) is not None:
            continue
        ds = su_kien_bead(kho, du_an.ten, b.id)
        if (buoc_feature(ds, trang_thai_bead(kho, du_an.ten, b, theo_id, ton)) == "spec" and con_dot_spec(ds)
                and du_mot_phieu(kho, ds, ngan_sach_phieu("spec", ns), ns.bead)):
            ra.append(UngVien(du_an, b, "spec", la_do(ds), frozenset()))
    return ra
