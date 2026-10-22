from pathlib import Path
from types import SimpleNamespace
import pytest
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import tao, kiem_truoc
from tram.chu.go_cai_dat_tho import go


def test_acl_r2_dung_principal_va_go_khong_xoa_acl_khac(tmp_path):
    from tram.chu import acl_tho
    path = tmp_path / 'home'; path.mkdir()
    state = ['group:everyone deny delete']
    calls = []
    who = lambda: {'uid': 701, 'guid': 'THO'}
    def read(p):
        return list(state)
    def observe(k, n, **kw):
        return acl_tho.quan_sat(Path(n), doc=read, nguoi=who)
    def run(cmd, **kw):
        calls.append(cmd)
        if '+a' in cmd:
            state.append(acl_tho.ACE)
        elif '-a' in cmd:
            state.remove(acl_tho.ACE)
    resource = acl_tho.tai_nguyen(path, doc=read, nguoi=who)
    so = SoCai(tmp_path / 'so')
    assert kiem_truoc(so, [resource], quan_sat=observe) == ['tạo']
    assert tao(so, resource, quan_sat=observe, chay=run) == 'tao'
    assert tao(so, resource, quan_sat=observe, chay=run) == 'giu'
    item = so.da_tao('acl_search', str(path))[0]
    assert go(so, item, quan_sat=observe, chay=run, bao=lambda s: None)
    assert state == ['group:everyone deny delete']
    assert calls == [['sudo', '/bin/chmod', '+a', acl_tho.ACE, str(path)],
                     ['sudo', '/bin/chmod', '-a', acl_tho.ACE, str(path)]]


def test_acl_co_san_khong_nhan_va_thay_doi_khong_go(tmp_path):
    from tram.chu import acl_tho
    path = tmp_path / 'home'; path.mkdir()
    state = [acl_tho.ACE]
    who = lambda: {'uid': 701, 'guid': 'THO'}
    observe = lambda k, n, **kw: acl_tho.quan_sat(Path(n), doc=lambda p: state, nguoi=who)
    resource = acl_tho.tai_nguyen(path, doc=lambda p: state, nguoi=who)
    so = SoCai(tmp_path / 'so')
    with pytest.raises(ValueError, match='không phải của trạm'):
        kiem_truoc(so, [resource], quan_sat=observe)
    so.du_dinh('receipt', 'acl_search', str(path), resource.mong('receipt'))
    so.ket('receipt', 'da_tao', dinh_danh=observe('acl_search', str(path)))
    state.append('group:staff allow search')
    assert not go(so, so.da_tao('acl_search', str(path))[0], quan_sat=observe,
                  chay=lambda *a, **k: pytest.fail('không được chmod'), bao=lambda s: None)


def test_acl_symlink_va_quyen_rong_bi_chan(tmp_path):
    from tram.chu import acl_tho
    link = tmp_path / 'link'; link.symlink_to(tmp_path)
    with pytest.raises(ValueError):
        acl_tho.tai_nguyen(link, doc=lambda p: [], nguoi=lambda: {})
    with pytest.raises(ValueError):
        acl_tho.tai_nguyen(tmp_path, doc=lambda p: ['user:tram-tho allow list,search'], nguoi=lambda: {})


def test_preflight_duong_that_va_kiem_am(tmp_path):
    from tram.chu import acl_tho
    seen = []
    def run(cmd, **kw):
        seen.append(cmd)
        return SimpleNamespace(returncode=1 if cmd[3] == '/bin/test' and cmd[2] in ('tram-kiem', 'tram-khe1') else 0)
    acl_tho.kiem_quyen([(tmp_path, '-x'), (tmp_path / 'code', '-r')], chay=run)
    assert seen[-2:] == [['sudo', '-u', u, '/bin/test', '-x', '/Users/dai-ca']
                        for u in ('tram-khe1', 'tram-kiem')]
    with pytest.raises(ValueError):
        acl_tho.kiem_quyen([], chay=lambda *a, **k: SimpleNamespace(returncode=0))


def test_duong_can_bao_gom_python_that_va_khong_sync(tmp_path):
    from scripts.acl_tho import duong_can
    from tram.chu.cai_dat_tho import plist_tho
    import plistlib
    repo = tmp_path / 'repo'; (repo / '.venv/bin').mkdir(parents=True)
    (repo / 'tram').mkdir()
    for rel in ('pyproject.toml', 'tram/__init__.py', '.venv/pyvenv.cfg'):
        (repo / rel).touch()
    python = tmp_path / 'python'; python.touch()
    uv = tmp_path / 'uv'; uv.touch()
    (repo / '.venv/bin/python').symlink_to(python)
    pl = plistlib.loads(plist_tho(uv=str(uv), repo=repo, quan_ly='tram-tho'))
    assert (python, '-x') in duong_can(pl)
    assert (repo / '.venv/bin/python', '-x') in duong_can(pl)
    pl['ProgramArguments'].remove('--no-sync')
    with pytest.raises(ValueError, match='offline/no-sync'):
        duong_can(pl)


def test_acl_drift_truoc_chmod_khong_ghi(tmp_path):
    from tram.chu.acl_tho import tai_nguyen
    state = []
    resource = tai_nguyen(tmp_path, doc=lambda p: list(state), nguoi=lambda: {'uid': 701, 'guid': 'THO'})
    state.append('group:everyone deny delete')
    with pytest.raises(ValueError, match='đổi sau preview'):
        resource.lenh('receipt')


def test_acl_parser_giu_noi_dung_khong_lay_so_thu_tu(tmp_path, monkeypatch):
    from tram.chu import acl_tho
    monkeypatch.setattr(acl_tho.subprocess, 'run', lambda *a, **k: SimpleNamespace(
        stdout='drwxr-x---+ 3 hungle staff 96 Oct 19 00:00 home\n 0: user:tram-tho allow search\n'))
    assert acl_tho.doc_acl(tmp_path) == [acl_tho.ACE]


def test_acl_crash_du_dinh_doi_soat_va_guid_la(tmp_path):
    from tram.chu import acl_tho, dinh_danh
    from tram.chu.so_cai_tho import doi_soat
    state = []
    who = {'uid': 701, 'guid': 'THO'}
    resource = acl_tho.tai_nguyen(tmp_path, doc=lambda p: state, nguoi=lambda: dict(who))
    so = SoCai(tmp_path / 'so')
    so.du_dinh('pending', 'acl_search', str(tmp_path), resource.mong('pending'))
    state.append(acl_tho.ACE)  # giả lập crash sau chmod, trước da_tao
    obs = lambda k, n, **kw: acl_tho.quan_sat(Path(n), doc=lambda p: state, nguoi=lambda: dict(who))
    doi_soat(so, obs, dinh_danh.khop)
    assert so.da_tao('acl_search', str(tmp_path))
    who['guid'] = 'OTHER'
    assert not go(so, so.da_tao('acl_search', str(tmp_path))[0], quan_sat=obs,
                  chay=lambda *a, **k: pytest.fail('không gỡ ACL của danh tính khác'), bao=lambda s: None)


def test_sudo_loi_khong_duoc_tinh_thanh_dac_chan():
    from tram.chu.acl_tho import kiem_quyen
    with pytest.raises(ValueError, match='đối chứng sudo'):
        kiem_quyen([], chay=lambda *a, **k: SimpleNamespace(returncode=1))
