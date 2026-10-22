"""Chuẩn bị phiếu + một lần chạy phía thợ (spec 3 §7.1, §7.2, §7.6, §8.3) — CLI giả, trạm trong bộ nhớ."""
import json
import threading
from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from git_gia import git
from tho_chay_gia import PrincipalGia, dung_may, lay_phieu
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.tho.chuan_bi import chuan_bi
from tram.tho.mot_lan import chay_mot_lan, ly_do_khong_chay

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def test_chuan_bi_worktree_goi_moi_truong_kiem_settings(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert git(pc.wt, "rev-parse", "HEAD") == m.b.cha and pc.wt.parent.parent == m.nc.goc_wt
    assert (pc.wt / ".tram" / "goi.md").read_text() == pc.p.goi_ngu_canh
    assert (pc.wt / ".env.testing").read_text() == "APP_ENV=testing\n" and pc.hang_doi.exists()
    assert git(pc.wt, "status", "--porcelain") == ""                          # .env.testing bị loại khỏi git
    allow = json.loads(pc.settings.read_text())["permissions"]["allow"]
    assert "Bash(python3 kiem_ok.py)" in allow and pc.mcp is None and pc.thu_muc == pc.wt.parent / "phieu"
    import pytest
    from tram.tho.chuan_bi import loai_khoi_git
    from tram.kiem.moi_truong import LoiMoiTruongKiem
    git(pc.wt, "add", "-f", "--", ".env.testing")
    with pytest.raises(LoiMoiTruongKiem, match="theo dõi"):
        loai_khoi_git(pc.wt, ".env.testing")


def test_principal_co_user_thi_trao_quyen_ghi(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    da = []
    m.nc.principal_cua = lambda k, wt, ten: PrincipalGia(m.kb, user="tram-k-b-claude-1")
    m.nc.chay_lenh = lambda argv, **kw: da.append(argv)
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert pc.hang_doi.is_file()
    assert any(a[-1] == str(pc.hang_doi) and "append" in a[-2] for a in da)
    assert any(a[-1] == str(pc.settings) and "allow read," in a[-2] for a in da)
    assert not any(a[-1] == git(pc.wt, "rev-parse", "--absolute-git-dir") for a in da)


def test_khong_chuan_bi_duoc_tra_ly_do(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    m.nc.ch = replace(m.nc.ch, tram_api="https://may-b.example.test")
    k, so, hop, tt = lay_phieu(m)
    assert chuan_bi(replace(m.nc, goc_kho=tmp_path / "khong-co"), k, so, hop, tt) == "loi-may-tho"
    (tmp_path / "env.testing").unlink()
    assert chuan_bi(m.nc, k, so, hop, tt) == "thieu-moi-truong-kiem"


def test_ly_do_khong_chay_truoc_moi_lan(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m, "2026-10-13T03:00:00Z")
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert ly_do_khong_chay(pc, m.nc, LUC) is None
    assert ly_do_khong_chay(pc, m.nc, LUC + timedelta(minutes=90)) == "het-ngan-sach"
    pc.tt.lan = 3
    assert ly_do_khong_chay(pc, m.nc, LUC) == "het-ngan-sach"
    pc.tt.lan, pc.tt.token_ra = 0, 200000
    assert ly_do_khong_chay(pc, m.nc, LUC) == "het-ngan-sach"
    pc.tt.token_ra = 0
    so.luu_han_muc(HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=95, doc_luc="2026-10-13T02:59:00Z")]))
    assert ly_do_khong_chay(pc, m.nc, LUC) == "het_han_muc"
    so.ngat_cau_dao(LUC + timedelta(minutes=5), "loi-he")
    assert ly_do_khong_chay(pc, m.nc, LUC) == "cau-dao"


def test_mot_lan_bat_dau_truoc_xong_sau_va_cau_dao_cuc_bo(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 1}])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    for _ in range(3):
        kq = chay_mot_lan(pc, m.nc, threading.Event())
    with closing(m.t.kho()) as kho:
        ds = [(l, json.loads(d)) for l, d in kho.db.execute(
            "SELECT loai, du_lieu FROM su_kien WHERE loai LIKE 'chay.%' ORDER BY id")]
    assert [(l, d["lan"]) for l, d in ds] == [("chay.bat_dau", 1), ("chay.xong", 1), ("chay.bat_dau", 2),
                                              ("chay.xong", 2), ("chay.bat_dau", 3), ("chay.xong", 3)]
    assert ds[1][1]["ket_thuc"] == "loi_he" and kq.ma_thoat == 1 and tt.lan == 3 and not so.pid.exists()
    assert so.cau_dao_ngat(m.nc.dong_ho())                                    # 3 loi_he liên tiếp → ngắt cục bộ
    assert (m.nc.goc / "log" / "chay" / f"{pc.p.giao_id}-1-3.jsonl").exists()


def test_cli_loi_thi_doc_nguon_lui_log_roi_lan_sau_bao_het_han_muc(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 1}])
    k, so, hop, tt = lay_phieu(m)
    log = k.thu_muc_cau_hinh / "projects" / "-wt"
    log.mkdir(parents=True)
    (log / "s.jsonl").write_text(json.dumps({"apiErrorParams": {"rate_limit_info": {
        "status": "rejected", "rateLimitType": "five_hour", "resetsAt": 4102444800}}}) + "\n")
    pc = chuan_bi(m.nc, k, so, hop, tt)
    chay_mot_lan(pc, m.nc, threading.Event())
    assert so.doc_han_muc().nguon == "log" and ly_do_khong_chay(pc, m.nc, m.nc.dong_ho()) == "het_han_muc"
