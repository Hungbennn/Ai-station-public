"""Kịch bản giả lập 4a-2 (spec 4 §16 mục 3 — phần nối thật, chưa cần cổng): tram-api thật trong tiến trình phát phiếu
qua `/api/tho/nhip` bằng bộ giao việc (bộ đệm beads + đọc lại trước cấp); kéo cột xen kẽ; G5 với kiểm lại dài ở dự
án này và Git hỏng ở dự án kia. Thợ, remote GitHub, principal đều giả (CHỈ trong test)."""
import threading
from dataclasses import replace

from bd_gia import BdGia
from giao_viec_gia import TC, bug, du_an_gia
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu
from su_kien_gia import cong_bo, nhan
from test_luong_giao import BdKhoa, cho_toi
from test_tick import GIU
from test_xet_xong import F, bg
from tho_api_gia import tao_tram
from tram.api.bo_dem import BoDemBeads
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.luong import bat_dau_luong_giao
from tram.giao_viec.noi_that import an_toan
from tram.giao_viec.su_kien import su_kien_bead
from tram.phieu.kho import KhoPhieu
from xu_ly_gia import ket_thuc_bang

NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}


def tram_http(tmp_path, *beads):
    t = tao_tram(tmp_path)
    k, da, g = dung_kho(tmp_path), du_an_gia(tmp_path), BdGia(beads)
    fetch(k.kho)
    bo = BoGiaoViec(cac_du_an=lambda: [da], tao_bd=lambda d: g, mo_kho=t.pt.mo_kho_phieu, ch=t.pt.cau_hinh,
                    dong_ho=lambda: t.gio[0], kho_git=lambda d: k.kho, boc=lambda a: a,
                    doc_beads=DocBeads(BoDemBeads(lambda ten: g, tuoi_toi_da=3600), tuoi=3600))
    pt = t.app.state.pt
    pt.chon_phieu, pt.con_hop_le_phieu = an_toan(bo.chon, None, "chon"), an_toan(bo.con_hop_le, False, "con_hop_le")
    pt.bo_giao = bo
    return t, bo, g, da


def test_http_phat_phieu_qua_bo_giao_viec(tmp_path):
    t, bo, g, _ = tram_http(tmp_path, bug())
    p = t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]
    assert (p["bead_id"], p["buoc"], p["luot"]) == ("hr-1", "code", 1) and g.beads["hr-1"].status == "in_progress"
    assert t.goi("POST", "/api/tho/nhip", json_body={**NHIP, "khe_id": "B/claude-2"}).json()["phieu"] is None
    assert t.goi("GET", "/api/giao-viec").json()["bat"] is True


def test_http_keo_cot_xen_ke_khong_cap(tmp_path):
    t, bo, g, da = tram_http(tmp_path, bug())
    bo.doc_beads.lay(da, g)                                              # bộ chọn đã có snapshot
    g.beads["hr-1"] = replace(g.beads["hr-1"], labels=("cot:can-chot",))  # Đại ca kéo sang cột 2
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json() == {"tiep_tuc": True, "phieu": None}
    assert g.so_lan("nhan_viec") == 0 and g.beads["hr-1"].status == "open"


def test_g5_hai_du_an_kiem_lai_dai_va_git_hong(tmp_path):
    vao, tha = threading.Event(), threading.Event()

    def boc(argv):
        vao.set()
        tha.wait(20)
        return argv

    k, db = dung_kho(tmp_path), tmp_path / "su-kien.db"
    da_a = du_an_gia(tmp_path)
    da_b = replace(da_a, ten="hr-hong")
    g_a, g_b = BdKhoa(BdGia([bug(**GIU)])), BdKhoa(BdGia([bug("hb-1", **GIU)], tien_to="hb"))
    bo = BoGiaoViec(cac_du_an=lambda: [da_a, da_b], tao_bd=lambda d: g_a if d.ten == da_a.ten else g_b,
                    mo_kho=lambda: KhoPhieu(db), ch=CauHinhTram(), dong_ho=lambda: LUC,
                    kho_git=lambda d: k.kho if d.ten == da_a.ten else tmp_path / "khong-phai-git", boc=boc)
    kho = KhoPhieu(db)
    sha = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"}, tu=k.main)
    p = dat_phieu(kho, bead_id="hr-1", lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"], tieu_chi=[TC])
    nhan(kho, p.giao_id, p.luot)
    cong_bo(kho, p.luot, sha)
    ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg(sha, lenh_kiem=[
        {"lenh": "sh kiem.sh", "ket_qua": "pass", "tom_tat": "", "digest_log": "sha256:1"}]))
    dung_ev = threading.Event()
    luong = bat_dau_luong_giao(bo, dung_ev, chu_ky=0.05)
    try:
        assert vao.wait(10)
        pb = dat_phieu(kho, "B/claude-2", du_an="hr-hong", bead_id="hb-1")
        ket_thuc_bang(kho, pb, "bi", ly_do="agent", noi_dung="vướng")
        assert cho_toi(lambda: any("bead_goc: hb-1" in b.description for b in g_b.tat_ca()
                                   if b.issue_type == "decision"))
        assert not [s for s in su_kien_bead(kho, da_a.ten, "hr-1") if s.loai == "kiem.lai"]
        tha.set()
        assert cho_toi(lambda: [s for s in su_kien_bead(kho, da_a.ten, "hr-1") if s.loai == "kiem.lai"])
    finally:
        tha.set()
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong)
