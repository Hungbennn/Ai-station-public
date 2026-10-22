"""Hồi quy review độc lập: kho tạm, không gọi Uq/deploy thật."""
from types import SimpleNamespace as NS
from dataclasses import replace
import pytest
from test_tm20_chuoi import bo, M, L
from tram.deploy.trang_thai import SK, tu_merge_cho_deploy, doc_su_kien
from tram.deploy.ghi import ghi
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy import chay, ban


def test_enable_without_tick_does_not_consume_old_merge():
    def s(i, loai, **d):
        return SK(i, loai, d, '', 'tram/tu-deploy', 'b')
    ds = [s(1, 'tu_merge.bat_dau', commit=M), s(2, 'pr.da_merge', commit=M, merge_commit=M),
          s(3, 'tu_dong.cai_dat', doi=['tu_deploy'], cai_dat={'tu_deploy': True})]
    assert tu_merge_cho_deploy(ds) is None


def test_wrong_auto_trigger_cannot_deploy_new_manual_merge(bo, monkeypatch):
    monkeypatch.setattr(chay, 'tu_merge_cho_deploy', lambda *a, **kw: NS(du_lieu={'merge_commit': L}))
    assert bo.run() == 'deploy_hoan'
    assert not any(b == 'deploy' for b, *_ in bo.calls)


def test_baseline_is_observed_after_uq(bo, monkeypatch):
    current = [L]
    def kiem(*a):
        current[0] = 'c' * 40
        return True
    monkeypatch.setattr(chay, 'kiem_ban', kiem)
    bo.ans['chuan_bi'] = lambda: dict(dat=True, da_dung=True, san_sang=True, ban_truoc=current[0])
    assert bo.run() == 'deploy_dat'
    assert next(truoc for b, c, truoc in bo.calls if b == 'deploy') == 'c' * 40


def test_uq_run_id_includes_project(tmp_path, monkeypatch):
    from tram.phieu.kho import KhoPhieu
    calls = []
    monkeypatch.setattr(ban, 'cong_mo', lambda: True)
    monkeypatch.setattr(ban, 'kiem_tu_xa', lambda *a, **kw: (calls.append(kw), NS(dat=True))[1])
    k = KhoPhieu(tmp_path / 'sk.db')
    try:
        for ten in ('a', 'b'):
            da = NS(ten=ten, lenh_cho_phep=('test',), giao=NS(lenh_kiem_mac_dinh=('test',)))
            ban.kiem_ban(k.db, None, da, M, '1')
        assert calls[0]['giao_id'] != calls[1]['giao_id']
    finally:
        k.close()


def test_rollback_intent_persisted_before_external_call(bo):
    bo.ans['deploy'] = dict(dat=False, da_dung=True)
    def crash():
        ds = doc_su_kien(bo.k.db, 'a')
        assert any(s.loai == 'deploy.lenh' and s.du_lieu.get('buoc') == 'lui' for s in ds)
        raise OSError('mat-ket-noi')
    bo.ans['lui'] = crash
    with pytest.raises(OSError):
        bo.run()


def test_missing_baseline_does_not_mark_current_as_healthy(bo, monkeypatch):
    bo.ans['chuan_bi'] = dict(dat=True, da_dung=True, san_sang=False, ban_truoc=L)
    assert bo.run() == 'deploy_cho_ban_nen'
    assert not any(s.loai == 'deploy.bat_dau' for s in doc_su_kien(bo.k.db, 'a'))


def test_wrong_artifact_never_becomes_success(monkeypatch):
    import json
    from tram.deploy import duong
    from test_tm20_duong import cd
    monkeypatch.setattr(duong, 'kiem_tep', lambda p: None)
    monkeypatch.setattr(duong.pwd, 'getpwnam', lambda n: NS(pw_uid=900, pw_dir='/tmp/dp'))
    def run(argv, **kw):
        req = json.loads(kw['input'])
        r = {**req, 'dat': True, 'da_dung': True, 'san_sang': True,
             'ban_truoc': L, 'ban_thuc': L, 'artifact': L}
        return NS(returncode=0, stdout=json.dumps(r).encode())
    monkeypatch.setattr(duong, 'chay_gioi_han', run)
    assert duong.DuongDeploy('a', cd()).goi('kiem_song', 'dp-1', M, L)['dat'] is False
