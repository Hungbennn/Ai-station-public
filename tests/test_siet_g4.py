"""Chỉ sinh/đọc kịch bản; không chạy launchctl hay đụng nhà người vận hành."""
import json
from pathlib import Path

import pytest

from tram.giao_viec import kich_ban_nghiem_thu as kb
from tram.giao_viec.chung_cu_probe import muc_lich


def test_copy_launchctl_co_doi_chung_exec_va_nhan_rieng(tmp_path):
    a = kb.kich_ban_tai_sinh(tmp_path / 'a')
    b = kb.kich_ban_tai_sinh(tmp_path / 'b')
    assert 'submitcopy' in kb.NGUON and 'launchdcopy' in kb.NGUON
    assert 'cp /bin/launchctl "$PWD/launchctl-copy"' in a
    assert 'cmp -s /bin/launchctl "$PWD/launchctl-copy"' in a
    assert '"$PWD/launchctl-copy" help submit' in a
    assert 'probe:execcopy:' in a
    assert '"$PWD/launchctl-copy" submit' in a
    assert '"$PWD/launchctl-copy" bootstrap' in a
    assert '<key>RunAtLoad</key><true/>' in a
    assert 'KeepAlive' not in a
    assert kb.nhan_luot(tmp_path / 'a') in a
    assert kb.nhan_luot(tmp_path / 'a') not in b


@pytest.mark.parametrize('ma', [126, 127])
def test_loi_exec_khong_duoc_tinh_la_toi_ipc(ma):
    dat, ly_do = muc_lich(f'probe:submitcopy:bat-dau\nprobe:submitcopy:ket:{ma}\n', 'submitcopy')
    assert dat is False
    assert 'exec' in ly_do


def test_receipt_giu_dung_mien_nhan_run_khong_bootout_ca_mien(tmp_path):
    from tram.giao_viec.mau_g4 import ghi_receipt, lenh_don
    tep = tmp_path / 'receipt.json'
    ghi_receipt(tep, tmp_path / 'dau', 503, 501)
    receipt = json.loads(tep.read_text())
    assert receipt['trang_thai'] == 'chua-do'
    assert {x['mien'] for x in receipt['dich']} == {'user/503', 'gui/503', 'gui/501'}
    assert len(receipt['dich']) == 12
    cmds = lenh_don(receipt)
    assert len(cmds) == 12
    assert all(cmd[:2] == ['/bin/launchctl', 'bootout'] and cmd[2].count('/') == 2 for cmd in cmds)
    with pytest.raises(FileExistsError):
        ghi_receipt(tep, tmp_path / 'dau', 503, 501)
    receipt['dich'][0]['nhan'] = 'vn.tram.nho'
    with pytest.raises(ValueError):
        lenh_don(receipt)


def test_harness_ghi_receipt_truoc_khi_cai_lich(tmp_path, monkeypatch, tram_home_tam):
    from types import SimpleNamespace
    from tram.giao_viec import nghiem_thu_kiem as nt
    monkeypatch.setattr(nt, 'git_nhap', lambda *a: 'sha')
    monkeypatch.setattr(nt, 'commit_nhap', lambda *a: 'sha')
    monkeypatch.setattr(nt, 'kiem_lai', lambda *a, **k: SimpleNamespace(loi=None, ket_qua=[]))
    observed = []
    def tai_sinh(*a):
        observed.extend((tram_home_tam / 'log' / 'nghiem-thu').glob('receipt-*.json'))
        return []
    monkeypatch.setattr(nt, '_tai_sinh', tai_sinh)
    pk = SimpleNamespace(ten='gia', boc_lenh=lambda a: a, kill_nhom=lambda *a: None)
    goc = tmp_path / 'kiem'
    goc.mkdir()
    nt.nghiem_thu(pk, goc, cong=None, boc_luot=None, thu_hoi=lambda: None, khang_dinh={},
                 tai_sinh=True, xac_minh=lambda *a: 503, dau_goc=tmp_path)
    assert len(observed) == 1
    assert json.loads(observed[0].read_text())['trang_thai'] == 'chua-do'


@pytest.mark.parametrize('prep', ['', 'probe:execcopy:bat-dau\nprobe:execcopy:ket:126\n'])
def test_copy_that_bai_thieu_doi_chung_exec_khong_la_bang_chung(prep):
    log = prep + 'probe:submitcopy:bat-dau\nprobe:submitcopy:ket:1\n'
    assert muc_lich(log, 'submitcopy')[0] is False


def test_copy_exec_tot_lenh_that_bai_van_chi_vang():
    log = 'probe:execcopy:bat-dau\nprobe:execcopy:ket:0\nprobe:submitcopy:bat-dau\nprobe:submitcopy:ket:1\n'
    assert muc_lich(log, 'submitcopy')[0] is None
