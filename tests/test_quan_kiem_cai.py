import plistlib
from pathlib import Path
from tram.chu.cai_quan_kiem import plist, lap, UQ, DAEMON
from tram.chu.so_cai_tho import SoCai


def test_daemon_khong_tro_nha_dai_ca():
    d = plistlib.loads(plist())
    assert d['UserName'] == UQ
    assert d['GroupName'] == UQ
    assert d['SessionCreate'] is True
    assert d['WorkingDirectory'] == '/var/empty'
    assert all('/Users/' not in x for x in d['ProgramArguments'])
    assert '-I' in d['ProgramArguments']


def test_lap_chua_goi_lenh_va_co_so_r2(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_REPO", str(tmp_path))
    so = SoCai(tmp_path / 'so.jsonl')
    (tmp_path / 'du-an').mkdir()
    (tmp_path / 'du-an/repo.yaml').write_text(
        'ten: repo\nduong_dan: /fake\nlenh_cho_phep: ["python -m pytest"]\n'
        'lenh_kiem_mac_dinh: ["python -m pytest"]\n')
    kh = lap(tmp_path, 'hungle', so, quan_sat=lambda *a, **kw: None)
    assert kh.buoc and not so.p.exists()
    assert 'dong-y' in '\n'.join(kh.canh_bao)
    assert any('tram-quan-kiem' in ten for ten, f in kh.buoc)
    assert any(str(DAEMON) in ten for ten, f in kh.buoc)


def test_khong_nhan_user_la(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        lap(tmp_path, 'hungle', SoCai(tmp_path / 'so'), quan_sat=lambda *a, **kw: {'uid': 777})


def test_cai_lai_da_co_plist_chua_bootstrap_giu_danh_tinh(tmp_path):
    from types import SimpleNamespace
    so = SoCai(tmp_path / 'so')
    hien = {
        ('tep', str(DAEMON)): {'sha256': 'plist-da-cai', 'uid': 0},
        ('nhom', UQ): {'gid': 504, 'guid': 'guid-nhom'},
        ('user', UQ): {'uid': 505, 'guid': 'guid-user'},
    }
    for i, ((k, n), h) in enumerate(hien.items()):
        so.du_dinh(str(i), k, n, h)
        so.ket(str(i), 'da_tao', dinh_danh=h)
    calls = []
    def chay(a, **kw):
        calls.append(a)
        assert a[:2] == ['sudo', '/bin/launchctl']
        if a[2] == 'bootout':
            assert kw['check'] is False
            return SimpleNamespace(returncode=5)  # Không lấy mã bootout làm bằng chứng vắng.
        assert a[2:] == ['print', 'system/vn.tram.quan-kiem']
        return SimpleNamespace(returncode=113, stdout=b'', stderr=(
            b'Bad request.\nCould not find service "vn.tram.quan-kiem" in domain for system\n'))
    kh = lap(tmp_path, 'hungle', so, quan_sat=lambda k, n, **kw: hien.get((k, n)), chay=chay,
             policy={'repo': {'mac_dinh': ['true'], 'cho_phep': ['true']}})
    for ten, buoc in kh.buoc[:4]:  # Đối soát → dừng cũ → giữ nhóm → giữ user, trước mọi bước cài tiếp.
        buoc()
    assert len(calls) == 2 and calls[-1][2] == 'print'
    assert len(so.muc()) == 3 and all(m.su == 'da_tao' for m in so.muc().values())
    assert kh.lenh == [['sudo', '/bin/launchctl', 'bootstrap', 'system', str(DAEMON)]]


def test_go_doi_soat_tai_nguyen_crash_truoc_receipt(tmp_path):
    from tram.chu.go_quan_kiem import lap_go
    so = SoCai(tmp_path / 'so')
    name = '/usr/local/tram/quan-kiem/crash.py'
    so.du_dinh('x', 'tep', name, {'sha256': 'a'})
    state = {'hien': {'sha256': 'a', 'uid': 0}}
    calls = []
    def chay(a, **kw):
        calls.append(a)
        state['hien'] = None
    kh = lap_go(so, quan_sat=lambda k, n, **kw: state['hien'] if n == name else None, chay=chay)
    for _, f in kh.buoc:
        f()
    assert calls == [['sudo', '/bin/rm', '-f', name]]
    assert so.muc()['x'].su == 'da_go'
