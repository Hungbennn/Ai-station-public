import pytest

from test_phu_thuoc_kiem import mau
from tram.quan_kiem.giao_thuc import digest_policy
from tram.quan_kiem.policy import kiem_policy


def test_bundle_tham_gia_digest_ca_client_va_server():
    a, b = mau(), mau()
    b['nguon']['pyproject.toml'] = 'e'*64
    assert digest_policy(['x'], ['x'], a) != digest_policy(['x'], ['x'], b)
    assert digest_policy(['x'], ['x']) != digest_policy(['x'], ['x'], a)


def test_policy_chi_nhan_metadata_chot_khong_nhan_duong_tuy_y():
    m = mau()
    p = {'ben-station': {'mac_dinh': ['x'], 'cho_phep': ['x'], 'deps': m}}
    assert kiem_policy(p) == p
    for doi in ({'duong': '/tmp/x'}, m | {'du_an': 'other'}):
        with pytest.raises(ValueError):
            kiem_policy({'ben-station': p['ben-station'] | {'deps': doi}})


def test_cai_manager_gan_manifest_root_truoc_in_policy(tmp_path, monkeypatch):
    import tram.chu.cai_quan_kiem as c
    import tram.kiem.deps_root as r
    from tram.chu.so_cai_tho import SoCai
    m = mau()
    monkeypatch.setattr(r, 'doc_bundle', lambda p: m)
    monkeypatch.setenv('TRAM_HOME', str(tmp_path / 'home'))
    kh = c.lap(tmp_path, 'hungle', SoCai(tmp_path / 'so'), quan_sat=lambda *a, **kw: None,
               policy={'ben-station': {'mac_dinh': ['x'], 'cho_phep': ['x']}}, deps_manifest=tmp_path / 'mf')
    assert 'artifacts' in '\n'.join(kh.canh_bao)
    assert 'deps' in '\n'.join(kh.canh_bao)
    assert not (tmp_path / 'so').exists()


def test_server_bundle_cu_dong_truoc_upload(monkeypatch):
    from types import SimpleNamespace
    from test_quan_kiem_giao_thuc import mau as request
    import tram.quan_kiem.dich_vu as s
    d = request() | {'du_an': 'ben-station', 'policy': digest_policy(['python -m pytest'], ['python -m pytest'])}
    monkeypatch.setattr(s, 'xac_thuc', lambda *a: None)
    monkeypatch.setattr(s, 'doc', lambda *a, **kw: d)
    calls = []
    monkeypatch.setattr(s, 'nhan', lambda *a: calls.append('upload'))
    monkeypatch.setattr(s, 'ghi', lambda *a: None)
    q = SimpleNamespace(dong=lambda: calls.append('dong'), chay=lambda *a: calls.append('chay'))
    c = {'uid_tram': 501, 'g4': False, 'policy': {'ben-station': {
        'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest'], 'deps': mau()}}}
    s.phuc_vu(SimpleNamespace(close=lambda: None), q, c)
    assert calls == ['dong']


def test_yaml_ben_station_dung_sau_lenh_va_env_duoc_git_nhan():
    from pathlib import Path
    import yaml
    from tram.cau_hinh.du_an import nap_du_an
    p = Path(__file__).resolve().parents[1] / 'du-an'
    d = nap_du_an('ben-station', thu_muc=p)
    raw = yaml.safe_load((p / 'ben-station.yaml').read_text())
    assert raw['bat_ghi'] is True        # Đại ca bật 20/10 (nhận yêu cầu máy A)
    assert len(d.giao.lenh_kiem_mac_dinh) == 6
    assert d.giao.lenh_kiem_mac_dinh == d.lenh_cho_phep
    assert '.handover' not in str(d.moi_truong_kiem.file)
    assert (p / d.moi_truong_kiem.file.name).read_bytes() == b''


def test_client_lay_bundle_tu_config_root_khong_gui_duong(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import tram.quan_kiem.client as c
    from tram.quan_kiem.giao_thuc import fingerprint
    monkeypatch.setattr(c, 'diff_cham_cam', lambda *a, **kw: [])
    monkeypatch.setattr(c, 'archive', lambda *a: b'source')
    monkeypatch.setattr(c, 'moi_truong', lambda *a: b'env')
    monkeypatch.setattr(c, 'cay_goc', lambda *a: 'b'*40)
    m, req = mau(), []
    d = SimpleNamespace(ten='ben-station', nhanh_chinh='main', moi_truong_kiem=SimpleNamespace(dich='.env.testing'),
                        giao=SimpleNamespace(duong_dan_cam=(), duong_dan_cam_cho_phep=(), lenh_kiem_mac_dinh=('x',)))
    def gui(r, *a):
        req.append(r)
        return r | dict(trang_thai='xong', da_thu_hoi=True, fingerprint=fingerprint(r),
                        ket_qua={'dat': True, 'ket_qua': []})
    r = c.kiem_tu_xa(tmp_path, d, giao_id='giao-1', luot=1, commit='a'*40, lenh_kiem=['x'],
                     lenh_cho_phep=['x'], chay_lenh=True, goi=gui,
                     cau_hinh=lambda: {'policy': {'ben-station': {'deps': m}}})
    assert r.dat
    assert req[0]['policy'] == digest_policy(['x'], ('x',), m)
    assert not {'deps', 'deps_manifest', 'duong'} & set(req[0])
