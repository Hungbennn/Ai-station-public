"""Điều phối dùng kho SQLite tạm và biên Uq/deploy giả; không tác động host."""
from dataclasses import replace
from types import SimpleNamespace as NS
import pytest
from tram.deploy import chay
from tram.deploy.ghi import ghi, ket_thuc
from tram.deploy.trang_thai import doc_su_kien
from tram.deploy.doi_soat import chua_doi_soat
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.luu import doi_cai_dat, doc_trang_thai
from tram.tu_dong.cai_dat import CaiDatTuDong

M, L = "a" * 40, "b" * 40


@pytest.fixture
def bo(tmp_path, monkeypatch):
    k = KhoPhieu(tmp_path / "sk.db")
    da = NS(ten="a", nhanh_chinh="main")
    doi_cai_dat(k.db, "a", lambda c: CaiDatTuDong(tu_deploy=True, lenh_deploy="d", lenh_kiem_song="k",
                                                lenh_lui="l"), tac_nhan="dai-ca/dashboard")
    ghi(k.db, "a", "tu_merge.bat_dau", {"commit": "h", "loai": "code"})
    ghi(k.db, "a", "pr.da_merge", {"commit": "h", "merge_commit": M})
    calls, ans = [], {}
    class Duong:
        def __init__(self, *a):
            pass
        def goi(self, buoc, ma, c, truoc):
            calls.append((buoc, c, truoc))
            if buoc in ans:
                r = ans[buoc]
                return r() if callable(r) else r
            return dict(dat=True, da_dung=True, san_sang=True, ban_truoc=L)
    monkeypatch.setattr(chay, "DuongDeploy", Duong)
    monkeypatch.setattr(chay, "cong_mo", lambda: True)
    monkeypatch.setattr(chay, "kiem_ban", lambda *a: True)
    monkeypatch.setattr(chay, "pham_vi_du", lambda *a: True)
    monkeypatch.setattr(chay, "ban_an_toan", lambda *a: True)
    monkeypatch.setattr(chay, "phu", lambda *a: [2])
    monkeypatch.setattr(chay, "chon_ban", lambda *a: M)
    monkeypatch.setattr(chay, "tu_merge_cho_deploy", lambda *a, **kw: NS(du_lieu={"merge_commit": M}))
    run = lambda: chay.chuoi(k.db, None, da, M, "tu_dong", "sk-2", lambda ten: True)
    yield NS(k=k, da=da, calls=calls, ans=ans, run=run)
    k.close()


def test_success_pins_versions_and_idempotent(bo):
    assert bo.run() == "deploy_dat"
    assert [x[0] for x in bo.calls] == ["chuan_bi", "deploy", "kiem_song"]
    assert bo.calls[-1][1] == M
    assert bo.run() == "deploy_da_co"
    assert len(bo.calls) == 3


def test_known_failure_rolls_back_once_and_checks_old_version(bo):
    bo.ans["deploy"] = dict(dat=False, da_dung=True)
    assert bo.run() == "deploy_da_lui"
    assert [x[0] for x in bo.calls] == ["chuan_bi", "deploy", "lui", "kiem_song_sau_lui"]
    assert bo.calls[-1][1] == L


@pytest.mark.parametrize("step", ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"])
def test_unknown_never_runs_next_step(bo, step):
    if step in ("lui", "kiem_song_sau_lui"):
        bo.ans["deploy"] = dict(dat=False, da_dung=True)
    bo.ans[step] = None
    assert bo.run() == "deploy_khong_ro"
    assert bo.calls[-1][0] == step
    assert chua_doi_soat(doc_su_kien(bo.k.db, "a"))
    assert doc_trang_thai(bo.k.db, "a").tam_dung_du_an is not None


def test_no_baseline_or_failed_uq_never_deploys(bo, monkeypatch):
    bo.ans["chuan_bi"] = dict(dat=True, da_dung=True, san_sang=False, ban_truoc=L)
    assert bo.run() == "deploy_cho_ban_nen"
    bo.ans.clear()
    monkeypatch.setattr(chay, "kiem_ban", lambda *a: False)
    assert bo.run() == "deploy_cho_kiem"
    assert all(x[0] == "chuan_bi" for x in bo.calls)


def test_changed_settings_after_uq_do_not_start(bo, monkeypatch):
    def kiem(*args):
        doi_cai_dat(bo.k.db, "a", lambda c: replace(c, tu_deploy=False), tac_nhan="dai-ca/dashboard")
        return True
    monkeypatch.setattr(chay, "kiem_ban", kiem)
    assert bo.run() == "deploy_hoan"
    assert all(x[0] == "chuan_bi" for x in bo.calls)


def test_finish_is_idempotent(bo):
    assert bo.run() == "deploy_dat"
    ds = doc_su_kien(bo.k.db, "a")
    m = next(s.du_lieu["ma_thao_tac"] for s in ds if s.loai == "deploy.bat_dau")
    ket_thuc(bo.k.db, "a", m, "dat")
    assert len([s for s in doc_su_kien(bo.k.db, "a") if s.loai == "deploy.xong"]) == 1
