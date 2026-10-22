from dataclasses import replace
from types import SimpleNamespace
import subprocess
import pytest
from git_gia import git
from tho_chay_gia import dung_may, lay_phieu
from tram.tho.chuan_bi import chuan_bi
from tram.tho.phieu_chay import don_phieu


def dung(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    m.nc.chay_lenh = lambda *a, **kw: subprocess.CompletedProcess(a[0], 0)
    return m, k, so, hop, tt


def test_restart_giu_ban_sua_va_khong_cap_lai_acl(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'a.txt').write_text('dang-do')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    again = chuan_bi(m.nc, k, so, hop, tt)
    assert (again.wt / 'a.txt').read_text() == 'dang-do'
    assert git(again.wt, 'status', '--porcelain')  # Không tự commit/reset khi restart.
    assert not any('/usr/bin/find' in a for a in calls)


def test_code_qc_khac_luot_khac_khe_khong_dung_lai_cay(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'chi-code.txt').write_text('khong-sang-qc')
    tt2 = replace(tt, phieu={**tt.phieu, 'luot': tt.phieu['luot'] + 1,
                            'khe_id': 'B/claude-2', 'buoc': 'qc', 'vai': 'qc'})
    qc = chuan_bi(m.nc, replace(k, ten='claude-2'), so, hop, tt2)
    assert qc.wt != pc.wt and not (qc.wt / 'chi-code.txt').exists()
    assert qc.thu_muc != pc.thu_muc


def test_don_xoa_cay_khong_go_acl_file_uid_khe(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'file-khe').write_text('x')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    don_phieu(pc, m.nc)
    assert not pc.wt.exists() and not pc.thu_muc.exists()
    assert not any('-a' in a or '/usr/bin/find' in a for a in calls)


def test_dung_mem_giu_commit_roi_don(tmp_path, monkeypatch):
    from tram.tho import ket_thuc
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'a.txt').write_text('WIP cua khe')
    monkeypatch.setattr(ket_thuc, '_day', lambda *a: 'chua-cong-bo')
    ket_thuc.ket_thuc_mem(pc, m.nc, 'khe-tat')
    sha = git(pc.wt, 'rev-parse', 'HEAD')
    don_phieu(pc, m.nc)
    assert not pc.wt.exists()
    assert git(m.b.tho, 'show', f'{sha}:a.txt') == 'WIP cua khe'
    assert 'rac/' in git(m.b.tho, 'branch', '--contains', sha)


def test_don_hong_dong_cong_giu_so_khong_chmod_file_khe(tmp_path, monkeypatch):
    from tram.tho import luot_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    so.luu_phieu(tt)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    monkeypatch.setattr(luot_b.shutil, 'rmtree', lambda p: (_ for _ in ()).throw(PermissionError('UID khe')))
    with pytest.raises(LoiThuHoi):
        don_phieu(pc, m.nc)
    assert so.doc_phieu() is not None
    assert calls == [['/bin/chmod', '-N', str(pc.wt.parent)]]
    assert not (pc.wt.parent / 'san-sang').exists()


def test_tat_tho_giu_cay_nhung_dong_cong(tmp_path, monkeypatch):
    from tram.tho import phieu_chay
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    vk = SimpleNamespace(k=k, so=so, hop=hop, pc=None, buoc='', lenh='tat-tho')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    assert phieu_chay.chay_phieu(m.nc, vk, tt) == 'tat-tho'
    gates = list(m.nc.goc_wt.iterdir())
    assert len(gates) == 1 and (gates[0] / 'san-sang').is_file()
    assert calls[-1] == ['/bin/chmod', '-N', str(gates[0])]


def test_khong_don_duoc_uid_khong_xoa_cay(tmp_path, monkeypatch):
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    m.nc.don_uid = lambda p: (_ for _ in ()).throw(LoiThuHoi('con-tien-trinh'))
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    with pytest.raises(LoiThuHoi):
        don_phieu(pc, m.nc)
    assert pc.wt.exists() and calls[-1] == ['/bin/chmod', '-N', str(pc.wt.parent)]


def test_chuan_bi_loi_retry_dung_phieu_khong_reuse_nua_cay(tmp_path, monkeypatch):
    from tram.tho import chuan_bi_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    that = chuan_bi_b.tao_noi_dung
    monkeypatch.setattr(chuan_bi_b, 'tao_noi_dung', lambda *a: (_ for _ in ()).throw(ValueError('loi-deps')))
    with pytest.raises(LoiThuHoi):
        chuan_bi(m.nc, k, so, hop, tt)
    cong = next(m.nc.goc_wt.iterdir())
    (cong / 'cay/rac').touch()
    monkeypatch.setattr(chuan_bi_b, 'tao_noi_dung', that)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert not (pc.wt / 'rac').exists() and (cong / 'san-sang').is_file()


def test_phieu_cu_sau_restart_don_ma_khong_chuan_bi_lai(tmp_path, monkeypatch):
    import threading
    from tram.tho.vong_khe import VongKhe
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    so.luu_phieu(tt)
    vk = VongKhe(m.nc, k)
    vk.phieu_moi, vk.lenh = tt, 'luot-cu'
    tat = threading.Event()
    monkeypatch.setattr(vk, 'khoi_dong', lambda: None)
    monkeypatch.setattr(vk, '_vong_nhip', lambda t: None)
    that = vk.so.xoa_phieu
    def xoa():
        assert not pc.wt.exists()
        that()
        tat.set()
    monkeypatch.setattr(vk.so, 'xoa_phieu', xoa)
    vk.chay(tat)
    assert so.doc_phieu() is None and not pc.wt.parent.exists()


@pytest.mark.parametrize('thieu', ['file', 'cau-hinh'])
def test_b_thieu_moi_truong_don_cay_bao_bi_khong_trao_quyen_khong_chay(tmp_path, monkeypatch, thieu):
    from tram.tho import phieu_chay, chuan_bi_b
    from test_kich_ban_3a2 import su_kien
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    so.luu_phieu(tt)
    if thieu == 'file':
        (tmp_path / 'env.testing').unlink()
    else:
        monkeypatch.setattr(chuan_bi_b, 'nap_du_an', lambda _: SimpleNamespace(moi_truong_kiem=None))
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    m.nc.principal_cua = lambda *a: SimpleNamespace(user='tram-khe1')
    def cam(*a, **kw):
        pytest.fail('Không được trao quyền hay chạy CLI khi thiếu môi trường kiểm')
    monkeypatch.setattr(chuan_bi_b, 'trao_quyen_b', cam)
    monkeypatch.setattr(phieu_chay, 'chay_mot_lan', cam)
    vk = SimpleNamespace(k=k, so=so, hop=hop, buoc='')
    assert phieu_chay.chay_phieu(m.nc, vk, tt) == 'thieu-moi-truong-kiem'
    assert so.doc_phieu() is None and list(m.nc.goc_wt.iterdir()) == []
    assert not any('/worktrees/' in s for s in git(m.b.tho, 'worktree', 'list', '--porcelain').splitlines())
    assert all(a[:2] == ['/bin/chmod', '-N'] for a in calls)
    assert su_kien(m, 'bao.bi')[0]['ly_do'] == 'thieu-moi-truong-kiem'
    assert su_kien(m, 'chay.bat_dau') == []


@pytest.mark.parametrize('loi', [OSError('loi-he-thong'), PermissionError('quyen'),
                                 subprocess.CalledProcessError(1, ['git'])])
def test_b_loi_he_thong_chuan_bi_giu_phieu_va_cong_dong(tmp_path, monkeypatch, loi):
    from tram.tho import chuan_bi_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    so.luu_phieu(tt)
    def hong(*a):
        raise loi
    monkeypatch.setattr(chuan_bi_b, 'tao_noi_dung', hong)
    with pytest.raises(LoiThuHoi):
        chuan_bi(m.nc, k, so, hop, tt)
    cong = next(m.nc.goc_wt.iterdir())
    assert so.doc_phieu() is not None and (cong / 'cay').is_dir()
    assert cong.stat().st_mode & 0o777 == 0o700 and not (cong / 'san-sang').exists()


def test_b_thieu_moi_truong_nhung_don_loi_giu_phieu(tmp_path, monkeypatch):
    from tram.tho import luot_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    so.luu_phieu(tt)
    (tmp_path / 'env.testing').unlink()
    def hong(*a):
        raise PermissionError('khong-don-duoc')
    monkeypatch.setattr(luot_b, 'xoa_cay', hong)
    with pytest.raises(LoiThuHoi):
        chuan_bi(m.nc, k, so, hop, tt)
    cong = next(m.nc.goc_wt.iterdir())
    assert so.doc_phieu() is not None and cong.stat().st_mode & 0o777 == 0o700


@pytest.mark.parametrize('tren_may_b', [True, False], ids=['B', 'tu-xa'])
def test_git_kiem_file_moi_truong_loi_khong_thanh_thieu_moi_truong_b(tmp_path, monkeypatch, tren_may_b):
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    if not tren_may_b:
        m.nc.ch = replace(m.nc.ch, tram_api='https://b.ts.net')
    so.luu_phieu(tt)
    that = subprocess.run
    def chay(argv, **kw):
        if 'ls-files' in argv:
            return subprocess.CompletedProcess(argv, 128)
        return that(argv, **kw)
    monkeypatch.setattr(subprocess, 'run', chay)
    if tren_may_b:
        with pytest.raises(LoiThuHoi):
            chuan_bi(m.nc, k, so, hop, tt)
        cong = next(m.nc.goc_wt.iterdir())
        assert so.doc_phieu() is not None and cong.stat().st_mode & 0o777 == 0o700
    else:
        assert chuan_bi(m.nc, k, so, hop, tt) == 'thieu-moi-truong-kiem'
