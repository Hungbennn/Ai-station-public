"""§5.2 thứ tự, §5.3 khe nào nhận bước nào — Q14 (G2), vai lan, ưu tiên khe đã code."""
from pathlib import Path

from bead_gia import bead
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.chon import UngVien, khe_nhan, khoa_sap_xep
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.trang_thai import TrangThaiKhe

CH = CauHinhTram()
DA = DuAn("hr-codex", Path("/r"), None, {})
NGAT = {"ngat": True, "ly_do": "x", "toi_luc": None}


def khe(ten, vai=("coder",), tt="ranh", cau_dao=None, pt=None):
    cua_so = [] if pt is None else [{"loai": "5h", "trang_thai": "biet", "phan_tram": pt, "reset_luc": None,
                                     "doc_luc": "2026-10-13T03:00:00Z", "het_hieu_luc": None}]
    return TrangThaiKhe(f"B/{ten}", "claude", ten, tuple(vai), tt, None,
                        {"khe_id": f"B/{ten}", "cua_so": cua_so, "nguon": "stream"},
                        cau_dao or {"ngat": False, "ly_do": None, "toi_luc": None}, 0, None)


def uv(buoc="code", da_code=(), do=False, id="hr-1", **kw):
    return UngVien(DA, bead(id, **kw), buoc, do, frozenset(da_code))


def nhan(ten, u, ds, han_muc=None):
    return khe_nhan(f"B/{ten}", han_muc, u, ds, CH)


def test_thu_tu_va_tie_break():
    ds = [uv(id="hr-5", priority=0), uv("qc", id="hr-4", priority=3), uv(id="hr-3", priority=1, created_at="2026-10-02"),
          uv(id="hr-2", priority=1, created_at="2026-10-01"), uv(id="hr-9", do=True, priority=4),
          uv(id="hr-0", priority=1, created_at="2026-10-01"), uv(id="hr-6")]
    assert [u.bead.id for u in sorted(ds, key=khoa_sap_xep)] == ["hr-9", "hr-4", "hr-5", "hr-0", "hr-2", "hr-3",
                                                                 "hr-6"]


def test_q14_khe_da_code_khong_qc_ke_ca_khi_vai_lan():
    ds = [khe("c1", ("coder",)), khe("c2", ("coder",))]
    u = uv("qc", da_code={"B/c1"})
    assert not nhan("c1", u, ds)                         # không có khe qc nào khác — vẫn không hạ chuẩn
    assert nhan("c2", u, ds)                             # vai lan sang c2 (chưa code bead)


def test_vai_uu_tien_va_lan_khi_khe_chinh_can():
    ds = [khe("q1", ("qc",)), khe("c1", ("coder",))]
    assert nhan("q1", uv("qc"), ds) and not nhan("c1", uv("qc"), ds)
    assert not nhan("c1", uv("qc"), [khe("q1", ("qc",), tt="lam"), ds[1]])   # khe chính đang làm → chờ
    for q1 in (khe("q1", ("qc",), tt="mat_ket_noi"), khe("q1", ("qc",), tt="tat"), khe("q1", ("qc",), cau_dao=NGAT),
               khe("q1", ("qc",), pt=95)):
        assert nhan("c1", uv("qc"), [q1, ds[1]])          # khe chính cạn → lan


def test_uu_tien_khe_da_code_khi_code_lai():
    ds = [khe("c1"), khe("c2")]
    u = uv(da_code={"B/c1"})
    assert not nhan("c2", u, ds) and nhan("c1", u, ds)
    assert nhan("c2", u, [khe("c1", tt="lam"), khe("c2")])         # khe đã code không rảnh → khe khác nhận


def test_han_muc_cua_khe_xin_viec():
    het = HanMuc(khe_id="B/c1", nguon="stream", cua_so=[CuaSo(loai="tuan", trang_thai="biet", phan_tram=85,
                                                              doc_luc="2026-10-13T03:00:00Z")])
    assert not nhan("c1", uv(priority=2), [khe("c1")], het) and nhan("c1", uv(priority=1), [khe("c1")], het)
