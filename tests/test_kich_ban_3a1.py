"""Kịch bản giả lập phía trạm (spec 3 §15 mục 2) qua HTTP — không CLI thật, không Git remote (công bố ref là 3a-2):
hai khe giả, một bead nhiều lượt; H1, H2 (phía trạm), H3, H5, H6 (snapshot), H8; estop/tắt khe → dừng mềm."""
import json
import threading
from contextlib import closing

from phieu_gia import CHA, de_xuat, khoa
from tho_api_gia import tao_tram
from tram.api.app import tao_app
from tram.chu import estop
from tram.phieu.canh import mot_vong_canh
from tram.phieu.cong_viec import doc_quyet_toan
from tram.phieu.khe import bat_tat_khe

BG_TAM = {"phien_ban": 1, "loai": "tam", "luot": 1, "file_ban_giao": "", "nhanh": "tram/hr-1", "commit": None,
          "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [],
          "buoc_tiep": ["làm tiếp"], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": []}


def chon_gia(t):
    """Đứng thay phần 4 (CHỈ TRONG TEST): bead hr-1 khi chưa có phiếu; `cha` = snapshot mới nhất (§6.5)."""
    def chon(khe_id, han_muc):
        with closing(t.kho()) as kho:
            if kho.phieu_hieu_luc("hr-codex", "hr-1"):
                return None
            h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'giao.snapshot' ORDER BY id DESC LIMIT 1"
                               ).fetchone()
        cha = json.loads(h[0])["commit"] if h else CHA
        return de_xuat("hr-1", cha=cha, khoa_chong_trung=khoa("hr-1", cha))
    return chon


def nhip(t, khe, phieu=None, buoc="ranh"):
    than = {"khe_id": f"B/{khe}", "buoc_tho": buoc}
    if phieu:
        than |= {"giao_id": phieu["giao_id"], "luot": phieu["luot"], "buoc_tho": "chay"}
    return t.goi("POST", "/api/tho/nhip", json_body=than).json()


def canh(t):
    with closing(t.kho()) as kho:
        return mot_vong_canh(kho, bay_gio=t.gio[0], ch=t.pt.cau_hinh)


def test_khe_chet_giua_chung_khe_khac_tiep_tuc_tu_snapshot_khe_cu_thuc_day_bi_chan(tmp_path):
    t = tao_tram(tmp_path)
    t.pt.chon_phieu = chon_gia(t)
    p1 = nhip(t, "claude-1")["phieu"]                                         # H8: nhịp đầu tiên đã có phiếu
    assert p1["luot"] == 1 and p1["repo"]["cha"] == CHA
    giu = {"khe_id": "B/claude-1", "giao_id": p1["giao_id"], "luot": 1}
    assert t.goi("POST", "/api/tho/su-kien", json_body={**giu, "loai": "chay.bat_dau", "du_lieu": {"lan": 1},
                                                        "request_id": "r-k1-lan-1"}).status == 200
    with closing(t.kho()) as kho, kho.giao_dich():                            # trạm đã công bố một commit (3a-2)
        kho.ghi_su_kien("hr-codex", "giao.cong_bo", {"bead_id": "hr-1", "luot": 1, "commit": "c0ffee1",
                                                     "ref": "tram/hr-1"}, luc=t.gio[0], bead_id="hr-1")
    for _ in range(4):
        t.toi(seconds=30)
        assert nhip(t, "claude-1", p1)["tiep_tuc"] is True
        assert nhip(t, "claude-2")["phieu"] is None                          # H1: bead đang có phiếu
    cuoi = t.gio[0]                                                           # khe 1 chết sau nhịp này
    while not canh(t)["thu_hoi"]:
        t.toi(seconds=60)
        nhip(t, "claude-2")
    assert (t.gio[0] - cuoi).total_seconds() <= 11 * 60                       # H3
    p2 = nhip(t, "claude-2")["phieu"]
    assert p2["luot"] == 2 and p2["khe_id"] == "B/claude-2" and p2["repo"]["cha"] == "c0ffee1"      # H6
    assert doc_quyet_toan(t.kho(), p1["giao_id"])["thieu_chay_xong"] == 1
    assert nhip(t, "claude-1", p1) == {"tiep_tuc": False, "ly_do": "thu-hoi"}                     # H2
    r = t.goi("POST", "/api/tho/bao", json_body={**giu, "loai": "moc", "request_id": "r-k1-moc-9"})
    assert (r.status, r.json()) == (409, {"ly_do": "luot-cu"})
    assert t.goi("POST", "/api/tho/su-kien", json_body={**giu, "loai": "chay.xong", "request_id": "r-k1-xong",
                                                        "du_lieu": {"lan": 1, "ket_thuc": "xong"}}).status == 409


def test_estop_va_tat_khe_dung_mem_bao_van_nhan(tmp_path):
    t = tao_tram(tmp_path)
    t.pt.chon_phieu = chon_gia(t)
    p = nhip(t, "claude-1")["phieu"]
    estop.bat("Đại ca")
    assert nhip(t, "claude-1", p)["ly_do"] == "estop"
    bi = {"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": 1, "loai": "bi", "ly_do": "estop",
          "ban_giao": BG_TAM, "request_id": "r-bi-estop1"}
    assert t.goi("POST", "/api/tho/bao", json_body=bi).status == 200          # estop chỉ chặn phát phiếu
    assert nhip(t, "claude-2")["phieu"] is None
    estop.tat()
    p2 = nhip(t, "claude-2")["phieu"]
    with closing(t.kho()) as kho, kho.giao_dich():
        bat_tat_khe(kho, "B/claude-2", bat=False, vi_sao="để dành", tac_nhan="dai-ca", luc=t.gio[0])
    assert nhip(t, "claude-2", p2) == {"tiep_tuc": False, "ly_do": "khe-tat", "han_giu": "2026-10-13T03:10:00Z"}


def test_het_han_muc_cau_dao_toi_gio_roi_tu_dong(tmp_path):
    t = tao_tram(tmp_path)
    t.pt.chon_phieu = chon_gia(t)
    p = nhip(t, "claude-1")["phieu"]
    giu = {"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": 1}
    assert t.goi("POST", "/api/tho/su-kien", json_body={**giu, "loai": "chay.bat_dau",
        "request_id": "r-hhm-bat1", "du_lieu": {"lan": 1}}).status == 200
    t.goi("POST", "/api/tho/su-kien", json_body={**giu, "loai": "chay.xong", "request_id": "r-hhm-0001",
                                                 "du_lieu": {"lan": 1, "ket_thuc": "het_han_muc"}})
    assert nhip(t, "claude-1", p)["ly_do"] == "cau-dao"                       # H5
    t.goi("POST", "/api/tho/bao", json_body={**giu, "loai": "het_han_muc", "request_id": "r-hhm-0002"})
    t.toi(minutes=30)
    assert nhip(t, "claude-1")["phieu"] is None
    t.toi(minutes=30)
    assert canh(t)["cau_dao_dong"] == ["B/claude-1"] and nhip(t, "claude-1")["phieu"]["luot"] == 2


def test_hai_nhip_dong_thoi_mot_bead_va_khoi_dong_lai_giu_phieu(tmp_path):
    t = tao_tram(tmp_path)
    t.pt.chon_phieu = chon_gia(t)
    ra, rao = {}, threading.Barrier(2)

    def chay(khe):
        rao.wait()
        ra[khe] = nhip(t, khe)["phieu"]

    luong = [threading.Thread(target=chay, args=(k,)) for k in ("claude-1", "claude-2")]
    for x in luong:
        x.start()
    for x in luong:
        x.join()
    co = [k for k, p in ra.items() if p]
    assert len(co) == 1                                                        # H1
    t.app = tao_app(t.pt)                                                      # "khởi động lại" tram-api
    p = ra[co[0]]
    assert nhip(t, co[0], p)["tiep_tuc"] is True
    assert t.kho().phieu_theo_giao_id(p["giao_id"])["ma_giao"] == p["ma_giao"]
