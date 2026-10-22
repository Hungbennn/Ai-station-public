"""Kịch bản giả lập máy thợ (spec 3 §15 mục 2 — phần 3a-2): vòng `tram tho chay` thật với CLI GIẢ, tram-api trong bộ
nhớ, remote Git cục bộ; không gọi Claude/mạng, không sudo."""
import json
import threading
import time
from contextlib import closing
from dataclasses import replace

import pytest

from git_gia import git
from tho_chay_gia import FILE_BG, dung_may, khoi_bg, tram_bao
from tram.tho.vong_khe import VongKhe

TC = "Tên kết thúc 'ỷ' không mất byte"


def su_kien(m, loai):
    with closing(m.t.kho()) as kho:
        return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = ? ORDER BY id",
                                                          (loai,))]


def chay_toi(m, dieu_kien, giay=40):
    tat, vk = threading.Event(), VongKhe(m.nc, m.nc.ch.khe[0])
    th = threading.Thread(target=vk.chay, args=(tat,), daemon=True)
    th.start()
    het = time.monotonic() + giay
    try:
        while not (dat := dieu_kien()) and time.monotonic() < het:
            tat.wait(0.1)
    finally:
        tat.set()
        th.join(timeout=30)
    assert not th.is_alive(), "vòng khe chưa dừng; không được khởi động vòng mới"
    assert dat, "chưa đạt điều kiện chờ của kịch bản"
    return vk


@pytest.mark.parametrize('tren_may_b', [True, False], ids=['B', 'tu-xa'])
def test_tron_vong_code_moc_cong_bo_xong_lenh_kiem(tmp_path, monkeypatch, tren_may_b):
    m = dung_may(tmp_path, monkeypatch, [
        {"in": {"type": "system", "subtype": "init", "model": "claude-gia"}},
        {"ghi": ["x.txt", "sửa 1\n"]}, tram_bao("--moc", "mốc 1"),
        {"ghi": [FILE_BG, khoi_bg(TC)]}, tram_bao("--xong", "--ban-giao", FILE_BG, "xong rồi"),
        {"in": {"type": "result", "usage": {"input_tokens": 5, "output_tokens": 7}}}])
    if not tren_may_b:
        m.nc.ch = replace(m.nc.ch, tram_api='https://b.ts.net')
    vk = chay_toi(m, lambda: su_kien(m, "bao.xong"))
    xong = su_kien(m, "bao.xong")
    assert len(xong) == 1 and xong[0]["loi_ban_giao"] == [] and xong[0]["ban_giao"]["lenh_kiem"][0]["ket_qua"] == "pass"
    cb = su_kien(m, "giao.cong_bo")
    # QĐ3-A; spec "Mốc tạm hoặc báo cáo giả SHA": B chỉ công bố sau thu hồi.
    assert len(cb) == (1 if tren_may_b else 2)
    assert cb[-1]["commit"] == xong[0]["commit"] and cb[0]["luot"] == 1
    assert git(m.b.remote, "rev-parse", "tram/hr-1") == xong[0]["commit"]
    assert [s["ket_thuc"] for s in su_kien(m, "chay.xong")] == ["xong"]
    assert len(su_kien(m, "bao.moc")) == (0 if tren_may_b else 1)
    assert vk.so.doc_phieu() is None and vk.hop.cho_gui() == [] and not vk.so.pid.exists()


@pytest.mark.parametrize('tren_may_b', [True, False], ids=['B', 'tu-xa'])
def test_cli_thoat_giua_chung_lan_sau_co_ban_giao_tam_roi_xong(tmp_path, monkeypatch, tren_may_b):
    import tram.tho.phieu_chay as phieu_chay
    that, stdin_2, cay = phieu_chay.chay_mot_lan, [], []
    def chay(pc, *a):
        kq = that(pc, *a)
        p = pc.wt / '.tram/stdin-2.md'
        if p.is_file():
            stdin_2.append(p.read_text())
            cay.append(pc.wt)
        return kq
    monkeypatch.setattr(phieu_chay, 'chay_mot_lan', chay)
    m = dung_may(tmp_path, monkeypatch, {
        "1": [{"ghi": [".tram/tien-do.md", "làm được nửa"]}, {"in": {"type": "assistant", "message": {"id": "a"}}},
              {"thoat": 1}],
        "2": [{"ghi": [FILE_BG, khoi_bg(TC)]}, tram_bao("--xong", "--ban-giao", FILE_BG, "xong")]})
    if not tren_may_b:
        m.nc.ch = replace(m.nc.ch, tram_api='https://b.ts.net')
    chay_toi(m, lambda: su_kien(m, "bao.xong"))
    assert [s["ket_thuc"] for s in su_kien(m, "chay.xong")] == ["loi", "xong"]
    assert len(stdin_2) == 1 and "## Lần chạy 2" in stdin_2[0]
    if tren_may_b:
        # Design §4 C1: B dọn cây/registration sau kết thúc; đọc prompt trước dọn.
        assert not cay[0].exists()
    else:
        wt = m.nc.goc_wt / "hr-codex" / "hr-1"
        assert "## Lần chạy 2" in (wt / ".tram" / "stdin-2.md").read_text()


def test_tat_khe_dung_mem_wip_cong_bo_va_bao_bi(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"ghi": ["dang-lam.txt", "dở\n"]},
                                         {"in": {"type": "assistant", "message": {"id": "a"}}}, {"ngu": 30}])
    from tram.phieu.khe import bat_tat_khe

    def tat_khe_khi_dang_chay():
        if su_kien(m, "chay.bat_dau") and not su_kien(m, "khe.tat"):
            with closing(m.t.kho()) as kho, kho.giao_dich():
                bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="thử", tac_nhan="dai-ca", luc=m.t.gio[0])
        return su_kien(m, "bao.bi")
    chay_toi(m, tat_khe_khi_dang_chay)
    bi = su_kien(m, "bao.bi")
    assert len(bi) == 1 and bi[0]["ly_do"] == "khe-tat" and bi[0]["ban_giao"]["loai"] == "tam"
    assert su_kien(m, "giao.cong_bo")[-1]["commit"] == bi[0]["commit"]
    assert git(m.b.tho, "show", f"{bi[0]['commit']}:dang-lam.txt") == "dở"


@pytest.mark.parametrize('tren_may_b', [True, False], ids=['B', 'tu-xa'])
def test_thu_hoi_dung_cung_khong_push_khong_bao_va_push_tre_khong_doi_ref_h2(tmp_path, monkeypatch, tren_may_b):
    m = dung_may(tmp_path, monkeypatch, [{"ghi": ["x.txt", "1"]}, tram_bao("--moc", "m1"), {"ngu": 30}])
    if not tren_may_b:
        m.nc.ch = replace(m.nc.ch, tram_api='https://b.ts.net')
    from tram.phieu.ket_thuc import thu_hoi
    from tram.tho.so_khe import SoKhe
    so = SoKhe('B', 'claude-1', m.nc.goc)

    def thu_hoi_sau_moc():
        tt = so.doc_phieu()
        # Spec "Mốc tạm hoặc báo cáo giả SHA": mốc B lưu cục bộ, không gửi bao.moc.
        co_moc = tt and tt.vi_tri_hang_doi >= 1 if tren_may_b else su_kien(m, 'bao.moc')
        if co_moc and not su_kien(m, "giao.thu_hoi"):
            with closing(m.t.kho()) as kho, kho.giao_dich():
                thu_hoi(kho, kho.phieu_hieu_luc("hr-codex", "hr-1"), ly_do="mat-nhip", luc=m.t.gio[0])
        return su_kien(m, "tho.tu_choi")
    vk = chay_toi(m, thu_hoi_sau_moc)
    assert su_kien(m, "bao.bi") == [] and su_kien(m, "bao.xong") == [] and vk.so.doc_phieu() is None
    if tren_may_b:
        assert su_kien(m, 'bao.moc') == [] and su_kien(m, 'giao.cong_bo') == []
        cong_bo = git(m.b.remote, 'for-each-ref', '--format=%(objectname)', 'refs/heads/tram/hr-1')
        assert cong_bo == ''
    else:
        cong_bo = git(m.b.remote, "rev-parse", "tram/hr-1")
    p = su_kien(m, "giao.nhan")[0]
    r = m.t.goi("POST", "/api/tho/da-push", json_body={"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": 1,
                                                       "commit": m.b.cha, "ref_tam": "tram/luot/hr-1/1",
                                                       "request_id": "r-tre-00001"})
    assert r.status == 409
    if tren_may_b:
        assert git(m.b.remote, 'for-each-ref', '--format=%(objectname)', 'refs/heads/tram/hr-1') == cong_bo
    else:
        assert git(m.b.remote, "rev-parse", "tram/hr-1") == cong_bo


def test_het_han_muc_bao_va_cau_dao(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"in": {"type": "rate_limit_event", "rate_limit_info": {
        "status": "rejected", "rateLimitType": "five_hour", "resetsAt": 4102444800}}}, {"thoat": 1}])
    vk = chay_toi(m, lambda: su_kien(m, "bao.het_han_muc"))
    assert len(su_kien(m, "bao.het_han_muc")) == 1 and su_kien(m, "khe.cau_dao_ngat")
    assert vk.so.cau_dao_ngat(m.nc.dong_ho())


def test_can_hoi_bao_roi_dung_mem(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [tram_bao("--can-hoi", "--loai", "can_quyet_dinh", "Chọn A hay B?"),
                                         {"ngu": 30}])
    chay_toi(m, lambda: su_kien(m, "bao.bi"))
    assert su_kien(m, "bao.can_hoi")[0]["noi_dung"] == "Chọn A hay B?"
    assert su_kien(m, "bao.bi")[0]["ly_do"] == "can-hoi"
    from types import SimpleNamespace
    import tram.tho.phieu_chay as phieu_chay
    calls = []
    td = SimpleNamespace(can_hoi=True, xong={"request_id": "x"}, bi=None, ket_thuc=lambda: None)
    monkeypatch.setattr(phieu_chay, "TheoDoi", lambda *a, **kw: SimpleNamespace(bat_dau=lambda: td))
    monkeypatch.setattr(phieu_chay, "ly_do_khong_chay", lambda *a: None)
    monkeypatch.setattr(phieu_chay, "chay_mot_lan", lambda *a: SimpleNamespace(het_han_muc=False, bi_dung=False))
    monkeypatch.setattr(phieu_chay, "ket_thuc_mem", lambda *a, **kw: calls.append("mem"))
    monkeypatch.setattr(phieu_chay, "ket_thuc_xong", lambda *a, **kw: calls.append("xong"))
    vk = SimpleNamespace(lenh=None)
    assert phieu_chay._mot_vong(object(), m.nc, vk) == "can-hoi" and calls == ["mem"]


def test_thieu_moi_truong_kiem_bao_bi_khong_chay_cli(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 0}])
    (tmp_path / "env.testing").unlink()
    chay_toi(m, lambda: su_kien(m, "bao.bi"))
    assert su_kien(m, "bao.bi")[0]["ly_do"] == "thieu-moi-truong-kiem" and su_kien(m, "chay.bat_dau") == []


def test_tat_tram_tho_chay_roi_khoi_dong_lai_chay_tiep(tmp_path, monkeypatch):
    san_sang = tmp_path / "cli-da-nhan-stdin"
    m = dung_may(tmp_path, monkeypatch, {"1": [{"in": {"type": "assistant", "message": {"id": "a"}}},
                                               {"ghi": [str(san_sang), "1"]}, {"cho_dung": True}],
                                         "2": [{"ghi": [FILE_BG, khoi_bg(TC)]},
                                               tram_bao("--xong", "--ban-giao", FILE_BG, "xong")]})
    # chay.bat_dau được ghi TRƯỚC spawn. Chờ CLI nhận stdin để số kịch bản không lệch số lần của thợ.
    vk = chay_toi(m, san_sang.is_file)
    assert vk.so.doc_phieu() is not None and [s["ket_thuc"] for s in su_kien(m, "chay.xong")] == ["dung"]
    chay_toi(m, lambda: su_kien(m, "bao.xong"))
    assert [s["lan"] for s in su_kien(m, "chay.bat_dau")] == [1, 2] and len(su_kien(m, "bao.xong")) == 1
    from types import SimpleNamespace
    from tram.tho.so_khe import TrangThaiPhieu
    from tram.tho.chuan_bi import Phieu
    from tho_chay_gia import lay_phieu
    fresh = dung_may(tmp_path / "fresh", monkeypatch, [])
    _, _, _, tt = lay_phieu(fresh)
    vu = VongKhe(fresh.nc, fresh.nc.ch.khe[0])
    vu.phieu_moi = tt
    sent = []
    ph = Phieu.model_validate(tt.phieu)
    fresh.nc.khach = SimpleNamespace(goi=lambda method, url, body: (
        sent.append(body) or (200, {"tiep_tuc": True, "han_giu": ph.han_giu})))
    vu.hop = SimpleNamespace(gui=lambda _: None)
    assert not vu.da_xac_nhan
    vu.nhip()
    assert sent[0]["giao_id"] == ph.giao_id and sent[0]["luot"] == ph.luot and vu.da_xac_nhan
    fresh.nc.khach.goi = lambda *a: (401, {})
    vu.nhip()
    assert vu.lenh == "thu-hoi" and vu.dung.is_set() and not vu.da_xac_nhan
