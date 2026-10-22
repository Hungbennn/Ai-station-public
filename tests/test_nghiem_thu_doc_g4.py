"""G4 CLI: chỉ adapter giả, không sudo/launchctl ghi, không nhà thật."""
import json
from types import SimpleNamespace

import pytest


def test_cli_khong_dong_y_khong_doc_cau_hinh(monkeypatch):
    from tram.giao_viec import nghiem_thu_doc as g4
    monkeypatch.setattr(g4, '_cau_hinh', lambda: pytest.fail('không được nạp cấu hình'))
    assert g4.main([]) == 2


def test_fixture_co_home_operator_dac_mo_symlink_va_positive(tmp_path):
    from tram.giao_viec.mau_g4 import tao_mau
    home = tmp_path / 'home'
    home.mkdir()
    calls = []
    chay = lambda argv: calls.append(argv) or (0, b'')
    pk = SimpleNamespace(boc_lenh=lambda a: ['uid-503', *a])
    fixture = tao_mau(pk, tmp_path / 'luot', home, tmp_path, chay)
    assert fixture['home'].is_relative_to(home)
    assert fixture['dac'].stat().st_mode & 0o777 == 0o644
    assert fixture['dac'].parent.stat().st_mode & 0o777 == 0o755
    assert len(fixture['tep']) == 5
    assert fixture['tep'][-1] == tmp_path / 'luot' / 'mau'
    assert 'ln -s' in calls[0][-1]
    assert 'CANARY' not in repr(fixture)


def test_controls_bat_buoc_ngoai_trong_va_receipt_truoc_lenh(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    receipt = tmp_path / 'receipt.json'
    calls = []
    pk = SimpleNamespace(boc_lenh=lambda a: ['ngoai', *a], boc_luot=lambda p: lambda a: ['trong', *a])
    def chay(argv):
        assert receipt.exists()
        calls.append(argv)
        if argv[-1] == 'submit' and 'help' in argv:
            return 0, b''
        if '/bin/sh' in argv:
            return 0, b''
        if 'print' in argv or 'bootout' in argv:
            return 113, ('Could not find service ' + argv[-1].rsplit('/', 1)[-1]).encode()
        return 1, b'PRIVATE-RAW'
    rows = do_launchd(pk, tmp_path, receipt, 503, 501, chay)
    assert {r['ho_so'] for r in rows} == {'ngoai', 'trong'}
    assert {r['binary'] for r in rows} == {'goc', 'copy'}
    assert {r['lenh'] for r in rows} == {'submit', 'bootstrap'}
    assert 'PRIVATE-RAW' not in repr(rows)
    assert len(rows) == 8
    assert any('submit' in a for a in calls) and any('bootstrap' in a for a in calls)
    assert json.loads(receipt.read_text())['trang_thai'] == 'da-don'


def test_fixture_receipt_co_truoc_khi_gui_lenh_cho_principal(tmp_path):
    from tram.giao_viec.mau_g4 import tao_mau
    receipt = tmp_path / 'fixture.json'
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    def chay(argv):
        data = json.loads(receipt.read_text())
        assert data['luot'] == str(tmp_path / 'luot')
        assert data['home'].startswith(str(tmp_path))
        return 0, b''
    tao_mau(pk, tmp_path / 'luot', tmp_path, tmp_path, chay, receipt=receipt)


def test_quan_sat_print_loi_van_di_het_cac_ca(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    chay = lambda argv: (0, b'') if '/bin/sh' in argv else (5, b'PRIVATE')
    rows = do_launchd(pk, tmp_path, tmp_path / 'r.json', 503, 501, chay)
    assert len(rows) == 8 and all(r['don'] for r in rows)
    assert 'PRIVATE' not in repr(rows)


def test_service_duoc_nhan_nhung_chua_chay_van_la_lot(tmp_path):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    seen = set()
    def chay(argv):
        target = argv[-1]
        if target not in seen:
            seen.add(target)
            return 0, b'state = waiting'
        return 113, b'Could not find service nhan'
    observed, clean = _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay)
    assert len(observed) == 3 and all(r['pid'] is None for r in observed)
    assert clean is False


def test_receipt_luu_chung_cu_huu_han_sau_moi_ca(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    receipt = tmp_path / 'r.json'
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    chay = lambda argv: (0, b'') if '/bin/sh' in argv else (5, b'PRIVATE')
    do_launchd(pk, tmp_path, receipt, 503, 501, chay)
    data = json.loads(receipt.read_text())
    assert data['trang_thai'] == 'da-don'
    assert len(data['ket_qua']) == 8
    assert 'PRIVATE' not in receipt.read_text()


def test_smoke_dung_toolchain_ghim_va_boc_luot(tmp_path):
    from tram.giao_viec.mau_g4 import smoke_toolchain
    calls = []
    pk = SimpleNamespace(boc_luot=lambda p: lambda a: ['ho-so', *a])
    result = smoke_toolchain(pk, tmp_path, lambda argv: calls.append(argv) or (0, b'PRIVATE'))
    assert all(result.values()) and len(result) == 6
    assert all(a[0] == 'ho-so' for a in calls)
    assert any('--without-pip' in a for a in calls)
    assert 'PRIVATE' not in repr(result)


@pytest.mark.parametrize('ps_rc, ps_out', [(1, b''), (0, b'PRIVATE'),
                                          (0, b'503 501 Sun Oct 18 12:00:00 2026')])
def test_khong_xac_nhan_danh_tinh_thi_chua_sach(ps_rc, ps_out):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    seen = set()
    ps_calls = 0
    def chay(argv):
        nonlocal ps_calls
        if '/bin/ps' in argv:
            ps_calls += 1
            return (ps_rc, ps_out) if ps_calls % 2 else (1, b'')
        target = argv[-1]
        if target not in seen:
            seen.add(target)
            return 0, b'pid = 4242'
        return 113, b'Could not find service nhan'
    observed, clean = _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay)
    assert clean is False
    assert 'PRIVATE' not in repr(observed)


def test_vang_phai_dung_ma_va_dung_nhan():
    from tram.giao_viec.do_launchd_g4 import _vang
    assert not _vang(5, b'Could not find service nhan', 'nhan')
    assert not _vang(113, b'Could not find service nhan-khac', 'nhan')
    assert _vang(113, b'Could not find service "nhan" in domain for user gui: 501', 'nhan')


def test_sudo_loi_canary_khong_chay_launchd(tmp_path, monkeypatch, tram_home_tam):
    from tram.giao_viec import nghiem_thu_doc as g4
    monkeypatch.setattr(g4, 'tao_mau', lambda *a, **k: {'tep': [], 'mau': tmp_path})
    monkeypatch.setattr(g4, 'smoke_toolchain', lambda *a: {'python': True})
    monkeypatch.setattr(g4, 'do_canary', lambda *a, **k: {'ngoai': None, 'trong': None})
    monkeypatch.setattr(g4, 'do_launchd', lambda *a: pytest.fail('canary lỗi phải dừng'))
    result = g4.nghiem_thu(None, tmp_path, 503, home=tmp_path, tam=tmp_path)
    assert result['don'] is False


def test_submit_nhan_nhung_khong_tim_duoc_mien_khong_tinh_sach(tmp_path):
    from tram.giao_viec.do_launchd_g4 import do_launchd
    pk = SimpleNamespace(boc_lenh=lambda a: a, boc_luot=lambda p: lambda a: a)
    def chay(argv):
        if 'print' in argv:
            return 113, ('Could not find service ' + argv[-1].rsplit('/', 1)[-1]).encode()
        return 0, b''
    rows = do_launchd(pk, tmp_path, tmp_path / 'r.json', 503, 501, chay)
    assert len(rows) == 1 and rows[0]['don'] is False


@pytest.mark.parametrize('rc', [1, 5, 112, 113, 125, 255, -9])
@pytest.mark.parametrize('out', [b'', b'Bad request.', b'Permission denied',
                                b'Could not find service nhan-khac'])
def test_print_ma_khac_khong_la_vang_bat_ke_thong_bao(rc, out):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: ['uid-503', *a])
    mien = ['user/503', 'gui/503', 'user/505', 'gui/505', 'login/100001', 'system', 'gui/501']
    calls = []
    def chay(argv):
        calls.append(argv)
        return rc, out
    assert _quan_sat_don(pk, mien, 'nhan', chay) == ([], True)
    assert calls == [(['uid-503'] if m in mien[:2] else []) +
                     ['/bin/launchctl', 'print', f'{m}/nhan'] for m in mien]


@pytest.mark.parametrize('rc', [0, 1, 5, 112, 113, 125, 255, -9])
@pytest.mark.parametrize('con_pid', [False, True])
def test_thay_job_phai_bootout_roi_het_job_va_pid(rc, con_pid):
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: ['uid-503', *a])
    danh_tinh = b'503 503 Sun Oct 18 12:00:00 2026'
    ket_qua = iter([(0, b'pid = 4242'), (0, danh_tinh), (0, b''), (rc, b'PRIVATE'),
                    (0, danh_tinh) if con_pid else (1, b'')])
    calls = []
    def chay(argv):
        calls.append(argv)
        return next(ket_qua)
    observed, clean = _quan_sat_don(pk, ['user/503'], 'nhan', chay)
    assert observed == [{'mien': 'user/503', 'co_service': True, 'pid': 4242,
                         'danh_tinh': danh_tinh.decode()}]
    assert clean is (rc != 0 and not con_pid)
    ps = ['/bin/ps', '-p', '4242', '-o', 'uid=,ruid=,lstart=']
    xem = ['uid-503', '/bin/launchctl', 'print', 'user/503/nhan']
    assert calls == [xem, ps, ['uid-503', '/bin/launchctl', 'bootout', 'user/503/nhan'], xem, ps]


def test_mien_gui_khong_co_phien_125_la_vang(tmp_path):
    """Đo 20/10: tài khoản không phiên GUI → launchctl print trả 125."""
    from tram.giao_viec.do_launchd_g4 import _quan_sat_don
    pk = SimpleNamespace(boc_lenh=lambda a: a)
    def chay(argv):
        if argv[-1].startswith('gui/503/'):
            return 125, b'Could not print domain: 125: Domain does not support specified action\n'
        return 113, b'Bad request.\nCould not find service "nhan" in domain for uid: 503\n'
    assert _quan_sat_don(pk, ['user/503', 'gui/503', 'gui/501'], 'nhan', chay) == ([], True)
