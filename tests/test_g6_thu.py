"""G6 chạy với Terminal giả, HOME/repo và mọi tích hợp là lệnh giả trong tmp_path; không mạng/Beads thật."""
import os
import select
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

GOC = Path(__file__).resolve().parents[1]
KB = GOC / "docs/handovers/g6-thu.sh"
MA = "yc-" + "a" * 32
GIA = r'''
import json, os, signal, sys, time
from pathlib import Path
d = Path(os.environ['G6_GIA']); ten = Path(sys.argv[0]).name; a = sys.argv[1:]
def nk(s):
    with (d/'nhat-ky').open('a') as f: f.write(s+'\n')
def song(loai):
    (d/(loai+'-pid')).write_text(str(os.getpid()))
    nk('bat '+loai+' '+str(os.getpid()))
    def dung(sig, frame):
        nk('dung '+loai+' '+str(os.getpid()))
        (d/(loai+'-pid')).unlink(missing_ok=True)
        sys.exit(0)
    signal.signal(signal.SIGTERM, dung)
    while True: time.sleep(.05)
if ten == 'terminal': sys.exit(1 if os.getenv('G6_SAI') == 'terminal' else 0)
if ten == 'Tailscale':
    nk('Tailscale '+' '.join(a))
    if a == ['status', '--json']:
        if os.getenv('G6_SAI') == 'login': print('{"BackendState":"NeedsLogin"}'); sys.exit(0)
        print(json.dumps({'BackendState':'Running','Self':{'UserID':1,'DNSName':'may-b.test.ts.net.'},
                          'User':{'1':{'LoginName':'dai-ca@example.test'}}})); sys.exit(0)
    if a == ['serve','status']:
        if os.getenv('G6_DON') == 'serve' and 'bat serve' in ((d/'nhat-ky').read_text() if (d/'nhat-ky').exists() else ''):
            print('config còn sót'); sys.exit(0)
        if os.getenv('G6_SAI') == 'status-loi': sys.exit(1)
        print('https://dang-co' if os.getenv('G6_SAI') == 'serve' else 'No serve config'); sys.exit(0)
    if a == ['serve','--https=443','http://127.0.0.1:7700']: song('serve')
    sys.exit(98)
if ten == 'api':
    if os.getenv('G6_SAI') == 'api': sys.exit(1)
    song('api')
if ten == 'pgrep':
    if os.getenv('G6_DON') == 'process' and 'bat serve' in ((d/'nhat-ky').read_text() if (d/'nhat-ky').exists() else ''): sys.exit(0)
    nk('pgrep '+' '.join(a))
    if os.getenv('G6_SAI') == 'pgrep-loi': sys.exit(2)
    sys.exit(0 if (d/'serve-pid').exists() or os.getenv('G6_SAI') == 'process' else 1)
if ten == 'lsof':
    if os.getenv('G6_DON') == 'port' and 'bat api' in ((d/'nhat-ky').read_text() if (d/'nhat-ky').exists() else ''): sys.exit(0)
    nk('lsof '+' '.join(a))
    if os.getenv('G6_SAI') == 'lsof-loi': sys.exit(2)
    sys.exit(0 if (d/'api-pid').exists() or os.getenv('G6_SAI') == 'port' else 1)
if ten == 'curl':
    nk('curl '+' '.join(a))
    if '-X' in a: print('200' if os.getenv('G6_SAI') == '403' else '403', end='')
    else: print('502' if os.getenv('G6_SAI') == '200' else '200', end='')
    sys.exit(0)
if ten == 'git':
    nk('git '+' '.join(a)); sys.exit(0)
if ten == 'bd':
    nk('bd '+' '.join(a))
    if a[0] == 'init':                           # như bd 1.2.2 thật: init chạy trong thư mục kho, không -C
        kho = Path(os.getcwd()).resolve()
        assert kho.parent == (d/'home').resolve() and kho.name.startswith('tram-thu-g6-') and a[1:] == ['--prefix', 'g6']
        (kho/'.beads').mkdir(); sys.exit(0)
    assert a[0] == '-C'
    kho = Path(a[1]); assert kho.parent == d/'home' and kho.name.startswith('tram-thu-g6-')
    if a[2] == 'init': sys.stderr.write('Error: cannot use -C directory: no beads project found\n'); sys.exit(1)
    assert a[2:] == ['list','--json','--all','--limit','0']
    if os.getenv('G6_SAI') == 'bd-loi': sys.exit(1)
    n = 2 if os.getenv('G6_SAI') == 'trung' else 1
    print(json.dumps([{'id':'g6-'+str(i+1),'issue_type':'feature',
                      'description':'<!-- ma-yeu-cau: yc-'+'a'*32+' -->\nPhieu thu'} for i in range(n)], indent=2))
    sys.exit(0)
if ten == 'sqlite3':
    nk('sqlite3 '+' '.join(a)); assert a[0] == '-readonly'
    if os.getenv('G6_SAI') == 'ledger-loi': sys.exit(1)
    if os.getenv('G6_SAI') == 'ledger-rong': sys.exit(0)
    login = 'la@example.test' if os.getenv('G6_SAI') == 'nguoi-gui' else 'dai-ca@example.test'
    print('yc-'+'a'*32+'|da_tao|g6-1|'+login); sys.exit(0)
sys.exit(99)
'''


def dung(tmp_path, **env):
    d = tmp_path
    (d / 'home/.tram').mkdir(parents=True)
    (d / 'repo/du-an').mkdir(parents=True)
    (d / 'repo/du-an/hr-codex.yaml').write_text('ten: hr-codex\nbat_ghi: false\n')
    (d / 'home/.tram/cau-hinh.yaml').write_text(
        '# giữ nguyên cả chú thích\ntelegram:\n  chat_id: "KHONG-DUOC-LO"\n'
        'dai_ca_logins: [cu@example.test]\nten_may_b: cu.ts.net\ndashboard_url: https://cu.ts.net\n')
    (d / 'home/.tram/cau-hinh.yaml').chmod(0o600)
    for ten in ('terminal', 'Tailscale', 'api', 'pgrep', 'lsof', 'curl', 'git', 'bd', 'sqlite3'):
        p = d / ten
        p.write_text('#!' + os.path.realpath(sys.executable) + '\n' + GIA)
        p.chmod(0o755)
    (d / 'python').write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' \"$@\"\n')
    (d / 'python').chmod(0o755)
    return {**os.environ, 'G6_GIA': str(d), 'TERM_PROGRAM': 'Apple_Terminal', **env}


def nk(d):
    p = d / 'nhat-ky'
    return p.read_text() if p.exists() else ''


PHIEN = []


@pytest.fixture(autouse=True)
def don_phien():
    yield
    for s in PHIEN:
        s.dung()
    PHIEN.clear()


class Phien:
    def __init__(self, env):
        self.p = subprocess.Popen(['/bin/bash', str(KB)], env=env, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.master = self.p.stdout.fileno()
        self.ra = ''
        PHIEN.append(self)

    def cho(self, chu):
        het = time.monotonic() + 25
        while chu not in self.ra:
            assert time.monotonic() < het, self.ra
            if select.select([self.master], [], [], .05)[0]:
                try:
                    b = os.read(self.master, 65536)
                except OSError:
                    b = b''
                self.ra += b.decode(errors='replace')
                if not b:
                    break
        assert chu in self.ra, self.ra

    def gui(self, chu):
        self.p.stdin.write((chu + '\n').encode())
        self.p.stdin.flush()

    def xong(self):
        self.p.wait(timeout=25)
        while select.select([self.master], [], [], .05)[0]:
            try:
                b = os.read(self.master, 65536)
            except OSError:
                break
            if not b:
                break
            self.ra += b.decode(errors='replace')
        self.p.stdout.close()
        self.p.stdin.close()
        return self.p.returncode, self.ra

    def dung(self):
        if self.p.poll() is None:
            self.p.send_signal(signal.SIGTERM)
            self.p.wait(timeout=25)


def vao(env, cau_hinh=True):
    s = Phien(env)
    s.cho('Gõ dong-y để bắt đầu:')
    s.gui('dong-y')
    if cau_hinh:
        s.cho('Gõ dong-y để áp cấu hình:')
        s.gui('dong-y')
    return s


def sach(d, cu):
    assert (d / 'home/.tram/cau-hinh.yaml').read_bytes() == cu
    assert not list((d / 'repo/du-an').glob('g6-*.yaml'))
    assert not (d / 'api-pid').exists() and not (d / 'serve-pid').exists()
    assert (d / 'repo/du-an/hr-codex.yaml').read_text() == 'ten: hr-codex\nbat_ghi: false\n'
    assert 'KHONG-DUOC-LO' not in ''.join(p.read_text() for p in (d / 'home/.tram/g6').rglob('*.log'))


def test_khong_terminal_khong_lam_gi(tmp_path):
    e = dung(tmp_path, G6_SAI='terminal')
    r = subprocess.run(['/bin/bash', str(KB)], env=e, stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
    assert r.returncode == 2 and 'Terminal.app' in r.stdout.decode()
    assert nk(tmp_path) == '' and not (tmp_path / 'home/.tram/g6').exists()


@pytest.mark.parametrize('tra_loi', ['khong', ''])
def test_khong_dong_y_khong_lam_gi(tmp_path, tra_loi):
    s = Phien(dung(tmp_path))
    s.cho('Gõ dong-y để bắt đầu:'); s.gui(tra_loi)
    rc, ra = s.xong()
    assert rc == 2 and nk(tmp_path) == '' and not (tmp_path / 'home/.tram/g6').exists(), ra


@pytest.mark.parametrize('sai', ['login', 'serve', 'status-loi', 'process', 'pgrep-loi', 'port', 'lsof-loi',
                                 'giao-viec', 'hr', 'yaml'])
def test_tien_dieu_kien_sai_khong_doi_gi(tmp_path, sai):
    e = dung(tmp_path, G6_SAI=sai)
    ch = tmp_path / 'home/.tram/cau-hinh.yaml'
    if sai == 'giao-viec': ch.write_text('giao_viec: {bat: true}\n')
    if sai == 'yaml': ch.write_text('giao_viec: [\n')
    if sai == 'hr': (tmp_path / 'repo/du-an/hr-codex.yaml').write_text('bat_ghi: true\n')
    cu = ch.read_bytes()
    s = vao(e, False)
    rc, ra = s.xong()
    assert rc != 0 and 'DỪNG' in ra, ra
    assert ch.read_bytes() == cu and not (tmp_path / 'home/.tram/g6').exists()
    assert 'bat api' not in nk(tmp_path) and 'bd ' not in nk(tmp_path)


def test_tu_choi_diff_khong_ap_cau_hinh(tmp_path):
    e = dung(tmp_path); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e, False); s.cho('Gõ dong-y để áp cấu hình:'); s.gui('khong')
    rc, ra = s.xong()
    assert rc != 0 and 'KHONG-DUOC-LO' not in ra and 'bat api' not in nk(tmp_path), ra
    sach(tmp_path, cu)


@pytest.mark.parametrize('giu', [False, True])
def test_luong_chinh_pid_dung_va_kho_thu_giu_lai(tmp_path, giu):
    e = dung(tmp_path); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e)
    try:
        s.cho('ĐANG CHỜ MÁY A')
        ch = yaml.safe_load((tmp_path / 'home/.tram/cau-hinh.yaml').read_text())
        assert ch['telegram'] == {'chat_id':'KHONG-DUOC-LO'} and ch['ten_may_b'] == 'may-b.test.ts.net'
        assert ch['dai_ca_logins'] == ['dai-ca@example.test']
        ds = list((tmp_path / 'repo/du-an').glob('g6-*.yaml'))
        assert len(ds) == 1 and yaml.safe_load(ds[0].read_text())['bat_ghi'] is True
        assert s.p.poll() is None                       # thực sự dừng chờ
        for backup in (tmp_path / 'home/.tram/g6').rglob('cau-hinh-truoc.yaml'):
            assert backup.stat().st_mode & 0o777 == 0o600
            assert backup.read_bytes() == cu
        s.gui(''); s.cho('Gõ giu để giữ cấu hình'); s.gui('giu' if giu else '')
        rc, ra = s.xong()
    finally:
        s.dung()
    assert rc == 0 and 'G6.9: ĐẠT' in ra and 'DỌN: ĐẠT' in ra, ra
    assert 'G6.7: để sau' in ra and 'G6 chưa đạt toàn bộ' in ra
    assert 'Taildrop' in ra and 'ai-do@gia' in ra and 'XUNG ĐỘT' in ra and 'G6.10' in ra and 'urllib.request' in ra
    assert 'KHONG-DUOC-LO' not in ra
    events = nk(tmp_path).splitlines()
    for loai in ('api', 'serve'):
        bat = next(x for x in events if x.startswith('bat '+loai+' '))
        assert bat.replace('bat ', 'dung ', 1) in events
    assert not any('/usr/local/bin/tailscale' in x or '--bg' in x for x in events)
    assert list((tmp_path / 'home').glob('tram-thu-g6-*/.beads'))
    if not giu:
        sach(tmp_path, cu)
    else:
        assert not list((tmp_path / 'repo/du-an').glob('g6-*.yaml'))
        assert yaml.safe_load((tmp_path / 'home/.tram/cau-hinh.yaml').read_text()) == ch


@pytest.mark.parametrize('tin', [signal.SIGINT, signal.SIGTERM, signal.SIGHUP])
def test_ngat_van_khoi_phuc_go_du_an_dung_pid(tmp_path, tin):
    e = dung(tmp_path); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e)
    try:
        s.cho('ĐANG CHỜ MÁY A'); s.p.send_signal(tin)
        rc, ra = s.xong()
    finally:
        s.dung()
    assert rc != 0 and 'DỌN: ĐẠT' in ra, ra
    sach(tmp_path, cu)
    for loai in ('api', 'serve'):
        p = next(x.split()[-1] for x in nk(tmp_path).splitlines() if x.startswith('bat '+loai+' '))
        assert f'dung {loai} {p}' in nk(tmp_path)


@pytest.mark.parametrize('sai', ['403', '200', 'ledger-rong', 'nguoi-gui', 'trung', 'bd-loi', 'ledger-loi'])
def test_do_loi_khong_bao_dat_va_van_don(tmp_path, sai):
    e = dung(tmp_path, G6_SAI=sai); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e)
    try:
        if sai not in ('403', '200'):
            s.cho('ĐANG CHỜ MÁY A'); s.gui('')
        s.cho('TỔNG:')
        rc, ra = s.xong()
    finally:
        s.dung()
    assert rc != 0 and 'KHÔNG ĐẠT' in ra, ra
    sach(tmp_path, cu)


def test_che_do_that_khong_terminal_dung_truoc_moi_lenh(tmp_path):
    e = {k: v for k, v in os.environ.items() if not k.startswith('G6_')}
    e['HOME'] = str(tmp_path)
    r = subprocess.run(['/bin/bash', str(KB)], env=e, stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
    assert r.returncode == 2 and 'Terminal.app' in r.stdout.decode()
    assert list(tmp_path.iterdir()) == []


def test_het_30_phut_gia_thi_khoi_phuc_va_don(tmp_path):
    e = dung(tmp_path, G6_HAN_CHO='1'); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e)
    s.cho('ĐANG CHỜ MÁY A')
    rc, ra = s.xong()
    assert rc != 0 and 'hết hạn chờ' in ra and 'DỌN: ĐẠT' in ra, ra
    sach(tmp_path, cu)


@pytest.mark.parametrize('bo_sung', [
    'dai_ca_logins:\n  - cu@example.test\ntelegram: {chat_id: KHONG-DUOC-LO}\n',
    '# chỉ có telegram\ntelegram: {chat_id: KHONG-DUOC-LO}\n',
    'dai_ca_logins: [] # chú thích cuối dòng\nten_may_b: cu.ts.net # tên cũ\n',
])
def test_sua_chi_ba_khoa_va_giu_chu_thich(tmp_path, bo_sung):
    e = dung(tmp_path); ch = tmp_path / 'home/.tram/cau-hinh.yaml'
    ch.write_text(bo_sung); cu = ch.read_bytes()
    s = vao(e); s.cho('ĐANG CHỜ MÁY A')
    updated = yaml.safe_load(ch.read_text())
    before = yaml.safe_load(bo_sung)
    for k in set(before) - {'dai_ca_logins', 'ten_may_b', 'dashboard_url'}:
        assert updated[k] == before[k]
    if '# chú thích cuối dòng' in bo_sung: assert '# chú thích cuối dòng' in ch.read_text()
    s.p.send_signal(signal.SIGTERM); s.xong()
    sach(tmp_path, cu)


@pytest.mark.parametrize('sai', ['serve', 'port', 'process'])
def test_don_chua_sach_phai_bao_loi(tmp_path, sai):
    e = dung(tmp_path, G6_DON=sai); cu = (tmp_path / 'home/.tram/cau-hinh.yaml').read_bytes()
    s = vao(e); s.cho('ĐANG CHỜ MÁY A'); s.p.send_signal(signal.SIGTERM)
    rc, ra = s.xong()
    assert rc == 3 and 'DỌN: KHÔNG ĐẠT' in ra, ra
    sach(tmp_path, cu)
    assert 'serve reset' not in nk(tmp_path)
