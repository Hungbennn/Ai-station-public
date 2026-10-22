import pytest
from tram.quan_kiem.policy import chup_policy, kiem_policy


@pytest.mark.parametrize('phien_ban', [1, 2, 3])
def test_cong_quan_kiem_chi_nhan_ho_so_v3(tmp_path, monkeypatch, phien_ban):
    import json
    from pathlib import Path
    import tram.quan_kiem.cong as cong
    from tram.tho.quyen_kiem import manifest_ho_so
    goc = tmp_path.resolve()
    hs, mf = manifest_ho_so(tram_home_tram=goc / 'tram', nha_quan_ly=Path('/Users/tram-tho'), goc=goc, cong=[])
    mf = json.dumps(json.loads(mf) | {'phien_ban': phien_ban}).encode()
    monkeypatch.setattr(cong, 'doc_tep_root', lambda p: mf if p == cong.MANIFEST_KIEM else hs)
    cau_hinh = {'goc': str(goc), 'home_tram': str(goc / 'tram')}
    if phien_ban == 3:
        cong.ho_so(cau_hinh)
    else:
        with pytest.raises(ValueError, match='khác phiên bản'):
            cong.ho_so(cau_hinh)


def test_policy_daemon_khong_nap_loader_yaml_cua_tram(monkeypatch):
    import builtins
    import runpy
    nhap = builtins.__import__
    def chi_stdlib(ten, *a, **kw):
        if ten == 'tram.cau_hinh.du_an':
            raise ModuleNotFoundError('loader YAML chỉ dùng phía trạm khi chụp policy')
        return nhap(ten, *a, **kw)
    monkeypatch.setattr(builtins, '__import__', chi_stdlib)
    ns = runpy.run_path('tram/quan_kiem/policy.py')
    policy = {'repo': {'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest']}}
    assert ns['kiem_policy'](policy) == policy


def test_go_g3_dung_api_d162(monkeypatch):
    import runpy
    import tram.kiem.ngoai_le_uid as m
    ns = runpy.run_path('cong-cu/g3-tai-khoan.py')
    calls = []
    c = ns['CaiGo'](chay=lambda *a: calls.append(a) or '')
    c.xac_minh = lambda s: None
    c.luu = lambda s: None
    state = {'uid': 505, 'made': [], 'removed': []}
    monkeypatch.setattr(m, 'con_uid', lambda uid, **kw: calls.append((uid, kw['ten'])) or [])
    c.go(state)
    assert calls[0] == (505, 'tram-quan-kiem')
    monkeypatch.setattr(m, 'con_uid', lambda *a, **kw: [object()])
    with pytest.raises(RuntimeError, match='ngoài D162'):
        c.go(state)


def test_chup_dung_cau_hinh_du_an(tmp_path):
    (tmp_path / 'repo.yaml').write_text(
        'ten: repo\nduong_dan: /fake\nlenh_cho_phep: ["python -m pytest"]\n'
        'lenh_kiem_mac_dinh: ["python -m pytest"]\n')
    assert chup_policy(tmp_path) == {'repo': {'mac_dinh': ['python -m pytest'],
                                           'cho_phep': ['python -m pytest']}}


@pytest.mark.parametrize('p', [{}, {'repo': {'mac_dinh': ['sh x'], 'cho_phep': ['*']}},
    {'repo': {'mac_dinh': ['sh x'], 'cho_phep': ['python -m pytest']}}])
def test_khong_mo_rong_policy(p):
    with pytest.raises(ValueError):
        kiem_policy(p)


@pytest.mark.parametrize('lenh,chap_nhan', [(['python -m pytest'], True), (['python -V'], False)])
def test_server_bat_buoc_lenh_mac_dinh(monkeypatch, lenh, chap_nhan):
    from types import SimpleNamespace
    import tram.quan_kiem.dich_vu as m
    from test_quan_kiem_giao_thuc import mau
    calls, reply = [], []
    d = mau() | {'lenh': lenh, 'policy': 'd' * 64}
    monkeypatch.setattr(m, 'xac_thuc', lambda *a: None)
    monkeypatch.setattr(m, 'doc', lambda *a, **kw: d)
    monkeypatch.setattr(m, 'digest_policy', lambda *a: 'd' * 64)
    monkeypatch.setattr(m, 'nhan', lambda *a: b'')
    monkeypatch.setattr(m, 'ghi', lambda s, r: reply.append(r))
    q = SimpleNamespace(chay=lambda *a: calls.append(a) or {'ok': True}, dong=lambda: None)
    c = {'uid_tram': 501, 'g4': False, 'policy': {'repo': {
        'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest', 'python -V']}}}
    m.phuc_vu(SimpleNamespace(close=lambda: None), q, c)
    assert bool(calls) is chap_nhan
    assert [{k: v for k, v in r.items() if k != 'ly_do'} for r in reply] == (
        [{'ok': True}] if chap_nhan else [{'loi': 'khong-cong-nhan'}])
