"""Cửa tươi chuyển từ worktree sang sau Uq; không còn kiểm HEAD để chọn mã."""
import pytest
from test_deploy_vong import t
from tram.deploy import chay
from tram.chu import estop


@pytest.mark.parametrize("doi", ["tat", "bat_ghi", "estop", "lenh"])
def test_change_during_uq_stops_start(t, doi):
    t.cd(tu_deploy=True)
    t.merge()
    def change():
        if doi == "tat":
            t.cd(tu_deploy=False)
        if doi == "bat_ghi":
            t.bg = False
        if doi == "estop":
            estop.bat("test")
        if doi == "lenh":
            t.cd(lenh_deploy="d2")
    t.khi_kiem = change
    try:
        assert t.buoc() == {"deploy_hoan": 1}
        assert not t.sk("deploy.bat_dau")
    finally:
        estop.tat()


def test_new_verified_merge_during_uq_coalesces_next_tick(t):
    t.cd(tu_deploy=True)
    t.merge()
    more = []
    def change():
        if not more:
            more.append(t.merge())
    t.khi_kiem = change
    assert t.buoc() == {"deploy_hoan": 1}
    assert t.buoc() == {"deploy_dat": 1} and t.ban == more[0]


def test_unverified_head_never_replaces_m(t):
    t.cd(tu_deploy=True)
    m = t.merge()
    t.k.day("main", {"direct.py": "unsafe"})
    assert t.buoc() == {"deploy_dat": 1} and t.ban == m


def test_scope_outside_verified_merges_requires_manual(t, monkeypatch):
    t.cd(tu_deploy=True)
    m = t.merge()
    monkeypatch.setattr(chay, "pham_vi_du", lambda *a: False)
    assert t.buoc() == {"deploy_cho_pham_vi": 1}
    t.bam(m)
    assert t.buoc() == {"deploy_dat": 1}


def test_manual_merge_after_auto_still_waits(t):
    t.cd(tu_deploy=True)
    t.merge()
    m = t.merge(tu=False)
    assert t.buoc() == {'san_sang_deploy': 1}
    assert not t.calls
    t.bam(m)
    assert t.buoc() == {'deploy_dat': 1}


def test_enabling_without_intervening_tick_waits(t):
    t.merge()
    t.cd(tu_deploy=True)
    assert t.buoc() == {'san_sang_deploy': 1}
    assert not t.calls


def test_estop_cancels_queued_manual_request(t):
    m = t.merge()
    t.buoc()
    t.bam(m)
    estop.bat('test')
    try:
        assert t.buoc() == {'deploy_huy': 1}
        assert not t.calls
    finally:
        estop.tat()
    t.buoc()
    assert not t.calls


def test_new_merge_during_deploy_survives(t):
    t.cd(tu_deploy=True)
    m = t.merge()
    more = []
    def add(buoc):
        if buoc == 'deploy' and not more:
            more.append(t.merge())
    t.khi_goi = add
    assert t.buoc() == {'deploy_dat': 1} and t.ban == m
    assert t.buoc() == {'deploy_dat': 1} and t.ban == more[0]


def test_project_lock_prevents_second_writer(t):
    from tram.giao_viec.ban_chep import giu_khoa
    from tram.duong_dan import tram_home
    t.cd(tu_deploy=True)
    t.merge()
    with giu_khoa(tram_home() / 'deploy-khoa' / f'{t.da.ten}.lock'):
        assert t.buoc() == {'deploy_dang_chay': 1}
    assert not t.calls


@pytest.mark.parametrize('toan_tram', [False, True])
def test_pause_during_uq_prevents_start(t, toan_tram):
    from tram.tu_dong.luu import ghi_tam_dung
    t.cd(tu_deploy=True)
    t.merge()
    t.khi_kiem = lambda: ghi_tam_dung(t.kho.db, '_tram' if toan_tram else t.da.ten,
                                     tam_dung=True, tac_nhan='dai-ca/dashboard')
    assert t.buoc() == {'deploy_hoan': 1}
    assert not t.sk('deploy.bat_dau')


def test_crash_inside_rollback_disables_next_tick(t):
    from tram.tu_dong.luu import doc_trang_thai
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add('deploy')
    def crash(buoc):
        if buoc == 'lui':
            raise OSError('fake-crash')
    t.khi_goi = crash
    t.buoc()
    count = len(t.calls)
    assert t.buoc() == {'deploy_khong_ro': 1}
    assert len(t.calls) == count
    assert doc_trang_thai(t.kho.db, t.da.ten).cai_dat.tu_deploy is False


def test_manual_scope_does_not_bypass_forbidden_diff(t, monkeypatch):
    m = t.merge(tu=False)
    t.buoc()
    t.bam(m)
    monkeypatch.setattr(chay, 'ban_an_toan', lambda *a: False)
    assert t.buoc() == {'deploy_cho_cam': 1}
    assert not t.sk('deploy.bat_dau')
