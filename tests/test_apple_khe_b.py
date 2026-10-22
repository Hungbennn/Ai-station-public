"""bs-2bd.1.30: mẫu ps máy B do Đại ca cung cấp 21/10/2026, macOS 15.6.1.
PGID và thời điểm sinh không có trong mẫu: dùng giá trị giả ổn định cho ảnh nhân.
Mọi lệnh/ảnh nhân/proc_pidpath đều giả; COMM chỉ cấp dữ liệu cho bản giả proc_pidpath.
"""
import errno
import json
from dataclasses import replace
from functools import partial
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.kiem import ngoai_le_uid as n
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.tho import don_uid as d, ngu_canh as nc
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.khach import DichKiemAm
from tram.tho.kiem_cong import cach_ly
from tram.tho.mo_coi_khe import don_mo_coi_khe

MAU = (Path(__file__).parent / 'du_lieu/distnoted-may-b-2026-10-21.txt').read_text().splitlines()[1:]


@pytest.fixture(params=MAU, ids=['tram-khe2-506', 'tram-khe1-502'])
def khe(request, tmp_path, monkeypatch):
    pid, ppid, uid, ruid, ten, path = request.param.split()
    t = TienTrinh(int(pid), int(ppid), int(pid), int(uid), int(ruid), 123456)
    k = KheCauHinh('claude-1', 'claude', f'user:{ten}', tmp_path / 'cfg', 'Claude', ('coder',))
    ch = CauHinhTho('B', 'http://127.0.0.1:7700', (k,))
    state = SimpleNamespace(t=t, path=path, ban='24G90', mot=lambda pid: state.t, goi=[], loi=None)

    def duong(pid):
        assert pid == state.t.pid
        if state.loi:
            raise state.loi
        return state.path

    def chay(argv, **kw):
        state.goi.append(argv)
        return SimpleNamespace(returncode=1)  # kill không phải bằng chứng sạch

    monkeypatch.setattr(n, 'build_macos', lambda: state.ban)
    monkeypatch.setattr(d, 'con_uid', partial(n.con_uid, mot=lambda pid: state.mot(pid), duong=duong))
    monkeypatch.setattr(nc, 'don_uid', partial(d.don_uid, xac_minh=lambda *a: int(uid), chay=chay,
                                             chup=lambda: [state.t], han=0))
    return ch, state


def khoi_dong(ch, tmp_path):
    context = nc.NguCanhTho(ch, None, goc=tmp_path, goc_wt=tmp_path / 'wt')
    p = tmp_path / 'pid'
    p.write_text(json.dumps({'pid': 123, 'pgid': 123, 'giao_id': 'g-1', 'luot': 1, 'lan': 1}))
    so = SimpleNamespace(pid=p, doc_phieu=lambda: None)
    return don_mo_coi_khe(context, ch.khe[0], so, SimpleNamespace()), p


def test_distnoted_may_b_khong_lam_khe_tu_dung_nhung_van_kill_1(khe, tmp_path):
    ch, state = khe
    ra, p = khoi_dong(ch, tmp_path)
    assert ra == (None, False)
    assert not p.exists()
    assert len(state.goi) == 1
    assert state.goi[0][-3:] == ['/bin/kill', '-KILL', '-1']
    assert state.goi[0][4] == ch.khe[0].principal.removeprefix('user:')


@pytest.mark.parametrize('sai', ['ngoai-goc', 'ppid', 'uid', 'ruid', 'thieu-dinh-danh',
                                'doi-truoc', 'doi-sau', 'eperm', 'esrch', 'build', 'may-tu-xa', 'ten-khac'])
def test_khong_du_d162_thi_khe_dung_giu_ban_ghi(khe, tmp_path, sai):
    ch, state = khe
    if sai == 'ngoai-goc':
        state.path = '/private/tmp/distnoted'
    elif sai in ('ppid', 'uid', 'ruid', 'thieu-dinh-danh'):
        key, value = {'ppid': ('ppid', 2), 'uid': ('uid', 0), 'ruid': ('ruid', 0),
                      'thieu-dinh-danh': ('sinh', None)}[sai]
        state.t = replace(state.t, **{key: value})
    elif sai in ('doi-truoc', 'doi-sau'):
        anh = [None] if sai == 'doi-truoc' else [state.t, replace(state.t, sinh=123457)]
        state.mot = lambda pid: anh.pop(0)
    elif sai in ('eperm', 'esrch'):
        state.loi = OSError(errno.EPERM if sai == 'eperm' else errno.ESRCH, 'không đọc được')
    elif sai == 'build':
        state.ban = '24G91'
    elif sai == 'may-tu-xa':
        ch = replace(ch, tram_api='https://b.ts.net')
    elif sai == 'ten-khac':
        ch = replace(ch, khe=(replace(ch.khe[0], principal='user:tram-khe3'),))
    ra, p = khoi_dong(ch, tmp_path)
    assert ra == (None, True) and p.exists()
    assert len(state.goi) == 1


@pytest.mark.parametrize('canh', ['apple', 'ngoai-goc', 'ppid', 'eperm', 'may-tu-xa', 'sandbox'])
def test_kiem_tan_du_cung_dung_ngoai_le_d162_cua_khe_b(khe, tmp_path, canh):
    ch, state = khe
    if canh == 'ngoai-goc':
        state.path = '/private/tmp/distnoted'
    elif canh == 'ppid':
        state.t = replace(state.t, ppid=2)
    elif canh == 'eperm':
        state.loi = OSError(errno.EPERM, 'không đọc được')
    elif canh == 'may-tu-xa':
        ch = replace(ch, tram_api='https://b.ts.net')
    elif canh == 'sandbox':
        ch = replace(ch, khe=(replace(ch.khe[0], principal=ch.khe[0].principal.replace('user:', 'sandbox:')),))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / 'wt',
                 dich=lambda: DichKiemAm('dai-ca@x', 'b.ts.net', ()), chay_td=lambda *a, **kw: [],
                 xac_minh=lambda *a: state.t.uid, chup=lambda: [state.t])
    assert [m.muc_do for m in ra] == ['xanh' if canh == 'apple' else 'do']
    if canh != 'apple':
        assert 'tàn dư' in ra[0].chi_tiet
