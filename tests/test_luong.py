import threading
import time

from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, khung, mot_nhip
from tram.su_kien.kho import KhoSuKien


def _moi(tmp_path, bd):
    return KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: bd)


def test_khung_dung_dinh_dang():
    assert khung("su_kien", {"a": "ă"}, 7) == 'event: su_kien\nid: 7\ndata: {"a": "ă"}\n\n'
    assert khung("phe_duyet_doi", {}) == "event: phe_duyet_doi\ndata: {}\n\n"


def test_su_kien_moi_va_moc(tmp_path):
    k, bo = _moi(tmp_path, BdGia([bead("hr-1")]))
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam"}, bead_id="hr-1")
    tt = TrangThaiLuong(moc=0)
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert len(ra) == 1 and ra[0].startswith("event: su_kien\nid: 1\n") and '"bead_id": "hr-1"' in ra[0]
    assert tt.moc == 1 and tt.phien_ban == {"hr": 1}
    assert mot_nhip(k, bo, ["hr"], tt) == []


def test_quet_xong_lam_moi_va_bao_doi(tmp_path):
    bd = BdGia([bead("hr-1")])
    k, bo = _moi(tmp_path, bd)
    tt = TrangThaiLuong(moc=0)
    mot_nhip(k, bo, ["hr"], tt)
    bd.beads["hr-1"] = bead("hr-1", labels=["cot:ai-lam"], updated_at="2026-10-13T02:00:00Z")
    k.ghi("hr", "quet.xong", {})
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert any(x.startswith("event: cong_viec_doi") and '"du_an": "hr"' in x for x in ra)
    assert ra[-1].startswith("event: phe_duyet_doi")


def test_su_kien_tram_khong_doc_lai_du_an_nhung_bao_phe_duyet(tmp_path):
    bd = BdGia([bead("hr-1")])
    k, bo = _moi(tmp_path, bd)
    tt = TrangThaiLuong(moc=0)
    mot_nhip(k, bo, ["hr"], tt)
    k.ghi("_tram", "estop.bat", {"ly_do": "x"})
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert bd.so_lan("tat_ca") == 1 and ra[-1].startswith("event: phe_duyet_doi")


def test_bd_loi_bo_qua_du_an(tmp_path):
    k, bo = _moi(tmp_path, BdGia(ra_loi_truoc={"tat_ca": 1}))
    assert mot_nhip(k, bo, ["hr"], TrangThaiLuong(moc=0)) == []


def test_tuyen_luong_tra_event_stream(tmp_path):
    app, _ = tao_app_gia(tmp_path, {"hr": BdGia()})
    r = goi(app, "GET", "/api/luong")       # asgi_gia báo ngắt kết nối ngay sau thân → luồng dừng
    assert r.status == 200 and r.headers["content-type"].startswith("text/event-stream")


class _KhoDocCham:
    """Kho giả: đọc chậm ở luồng worker, ghi lại nếu bị đóng giữa lúc đọc (bs-64w: đóng sqlite khi luồng khác
    còn dùng → segfault)."""

    def __init__(self):
        self.dang_doc, self.dong_khi_dang_doc, self.da_dong = threading.Event(), False, False

    def id_moi_nhat(self):
        self.dang_doc.set()
        time.sleep(0.05)
        self.dang_doc.clear()
        return 0

    def close(self):
        self.dong_khi_dang_doc, self.da_dong = self.dang_doc.is_set(), True


def test_tuyen_luong_cho_luong_doc_xong_moi_dong_kho(tmp_path):
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia()})
    kho = _KhoDocCham()
    pt.mo_kho = lambda: kho
    goi(app, "GET", "/api/luong")           # ngắt ngay → luồng bị huỷ khi đang chờ id_moi_nhat
    assert kho.da_dong and not kho.dong_khi_dang_doc
