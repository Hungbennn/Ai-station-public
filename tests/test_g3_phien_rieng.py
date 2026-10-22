"""G3.12 chạy hoàn toàn bằng lệnh giả; không sudo/launchd/ps thật, không xác nhận ngữ nghĩa macOS."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.g3

KB = Path(__file__).resolve().parents[1] / "docs/handovers/g3-phien-rieng.sh"
PROBE = KB.with_name("g3-phien-rieng-probe.sh")
GIA = r'''
import json, os, pathlib, signal, sys, time, plistlib, shutil
d = pathlib.Path(os.environ['G3_GIA']); cmd = sys.argv[1]; a = sys.argv[2:]
with (d/'nhat-ky').open('a') as f: f.write(json.dumps([cmd, *a])+'\n')
sfile = d/'state'; s = json.loads(sfile.read_text()) if sfile.exists() else {}
def save(): sfile.write_text(json.dumps(s))
def receipt(word):
    assert any(word in p.read_text() for p in (d/'out').glob('*.receipt')), word
if cmd == 'id':
    if 'tram-quan-kiem' in a:
        if os.getenv('UQ_THIEU'): sys.exit(1)
        print('tram-quan-kiem' if '-un' in a or '-gn' in a else ('520' if '-g' in a or '-G' in a else '519')); sys.exit()
    print('503' if 'tram-kiem' in a else ('hungle' if '-un' in a else '501')); sys.exit()
if cmd == 'sudo':
    if a == ['-v']: sys.exit()
    assert a[0] == '-n'
    if a[1:3] == ['-H', '-u'] and a[3] in ('tram-kiem', 'tram-quan-kiem'): a = a[4:]
    else:
        assert pathlib.Path(a[1]).name in ('install', 'rm', 'launchctl')
        if pathlib.Path(a[1]).name == 'launchctl':
            assert a[2] == 'procinfo' or (a[2] in ('bootstrap', 'bootout') and a[3].startswith('system'))
        else: assert 'vn.tram.g3p.' in a[-1] and str(d/'root') in a[-1]
        a = a[1:]
    if a[0].startswith(str(d)+'/'):
        cmd = pathlib.Path(a[0]).name; a = a[1:]
        with (d/'nhat-ky').open('a') as f: f.write(json.dumps([cmd, *a])+'\n')
    else:
        assert a[0] in ('/bin/cat', '/bin/mkdir', '/bin/rm', '/usr/bin/perl', '/usr/bin/tee') and str(d) in a[-1]
        if a[0] == '/usr/bin/perl':
            if os.getenv('G3_DON_TK_LOI'): sys.exit(1)
            p = pathlib.Path(a[-1])
            for f in p.iterdir():
                if f.is_dir(): shutil.rmtree(f)
                else: f.unlink()
            sys.exit(0)
        os.execv(a[0], a)
if cmd == 'install':
    receipt(a[-1]); dest = pathlib.Path(a[-1])
    if '-d' in a: dest.mkdir()
    else: shutil.copyfile(a[-2], dest)
    dest.chmod(int(a[a.index('-m')+1], 8))
    sys.exit()
if cmd == 'rm':
    receipt(a[-1]); p = pathlib.Path(a[-1])
    assert not s, 'xoa chuong trinh khi con job'
    if p.is_dir(): shutil.rmtree(p)
    elif p.exists(): p.unlink()
    sys.exit()
if cmd == 'plutil':
    plistlib.loads(pathlib.Path(a[-1]).read_bytes()); sys.exit()
if cmd == 'ps':
    if '-A' in a:
        if os.getenv('DON_PS_LOI') and (d/'da-go').exists(): sys.exit(1)
        print(f'{os.getppid()} 1 501 501 /bin/bash')
        if os.getenv('LA'): print('9999 1 503 503 /usr/libexec/la')
        if os.getenv('LA_UQ'): print('9997 1 519 519 /untrusted/process')
        if os.getenv('APPLE'): print('9998 1 503 503 /usr/sbin/distnoted')
        if (d/'pid-sot').exists(): print('8103 1 501 501 /usr/bin/perl')
    else:
        pid = a[a.index('-p')+1]
        if pid == '8103' and (d/'pid-sot').exists() and os.getenv('PID_TAI_DUNG') and not any(pid in x.get('pids', []) for x in s.values()):
            print('Sun Oct 18 23:59:59 2026'); sys.exit(0)
        if not any(pid in x.get('pids', []) for x in s.values()): sys.exit(1)
        if 'lstart=' in a:
            f = d/('ps-'+pid); n = int(f.read_text())+1 if f.exists() else 1; f.write_text(str(n))
            print('Sun Oct 18 22:03:00 2026' if not os.getenv('PID_DOI') or n == 1 else 'khac luc sinh')
        else:
            v = next(x for x in s.values() if pid in x.get('pids', []))
            print('503 503 20' if pid.endswith('2') or (pid.endswith('3') and v.get('ca') in ('v3','v4','v5'))
                  else ('519 519 '+os.getenv('UQ_GID','520') if v.get('ca') in ('v4','v5') else '501 501 20'))
    sys.exit()
if cmd == 'launchctl':
    if a[0] == 'procinfo':
        pid = a[1]; v = next(x for x in s.values() if pid in x.get('pids', []))
        if os.getenv('PROC_LOI'): sys.exit(1)
        print('audit info\n\tsession id = '+('100003' if v['ca'] not in ('v3','v4','v5') else '100333')); sys.exit()
    if a[0] == 'bootstrap':
        p = plistlib.loads(pathlib.Path(a[2]).read_bytes()); n = p['Label']; receipt('nap '+n)
        args = p['ProgramArguments']; w = pathlib.Path(args[4]); ca = n.split('.')[-1]
        assert not s, 'chua don xong ca truoc'
        assert w.stat().st_mode & 0o777 == 0o711
        assert all((w/k).stat().st_mode & 0o777 == 0o700 for k in ('toi', 'tk'))
        assert pathlib.Path(args[0]).stat().st_mode & 0o777 == 0o555
        assert p.get('SessionCreate', False) == (ca in ('v3','v5'))
        assert p.get('UserName') == ('tram-quan-kiem' if ca in ('v4','v5') else 'hungle') if ca != 'v1' else 'UserName' not in p
        s[n] = {'ca': ca, 'domain': a[1], 'pids': ['8101', '8102', '8103'], 'w': str(w)}
        domain = 'gui/501' if ca not in ('v3','v4','v5') else os.getenv('G3_MIEN_V3', 'login/100333')
        if not os.getenv('AN_NHAN') and not os.getenv('SUDO_LOI') and not os.getenv('REFUSE'):
            s[n+'.submit'] = {'domain': domain, 'pids': ['8103']}
        for role, pid, uid in [('driver', '8101', '519' if ca in ('v4','v5') else '501'), ('leaf', '8102', '503'),
                               ('job', '8103', '501' if ca not in ('v3','v4','v5') else '503')]:
            if os.getenv('SUDO_LOI') and role != 'driver': continue
            if role == 'job' and (os.getenv('CHUA_CHAY') or os.getenv('REFUSE')): continue
            if role == 'job': uid = os.getenv('G3_JOB_UID', uid)
            out = w/('tk' if uid == '503' else 'uq' if uid == '519' else 'toi')/(role+'.txt')
            out.with_suffix('.groups').write_text('520' if uid == '519' else '20')
            out.with_suffix('.context').write_text('manageruid='+uid+'\nmanagername=Background\n')
            out.write_text(f'{args[2]} {role} {pid} {uid} {uid} {(os.getenv('UQ_GID','520')+' '+os.getenv('UQ_GID','520')) if uid == '519' else '20 20'}\nSun Oct 18 22:03:00 2026\n')
        for target in ['gui-501', 'user-'+('519' if ca in ('v4','v5') else '501'), 'user-503']:
            (w/'tk'/('target-'+target+'.txt')).write_text('actor_uid=503 target='+target+' exit=0 signal=0')
        if os.getenv('SUDO_LOI'): (w/'toi/driver-exit.txt').write_text('1\n')
        else:
            (w/'tk/submit.txt').write_text(('1' if os.getenv('REFUSE') else os.getenv('SUBMIT_RC', '0'))+'\n')
            (w/'tk/submit.err').write_text(os.getenv('ERR', 'launchctl: submit failed: Operation not permitted'))
            (w/'tk/submit.phase').write_text('returned')
            (w/'tk/submit.status').write_text('exit='+('1' if os.getenv('REFUSE') else os.getenv('SUBMIT_RC','0'))+' signal='+os.getenv('SIGNAL', '0'))
        save()
        time.sleep(float(os.getenv('G3_TRE_NAP', '0')))
        if ca == 'v2' and os.getenv('G3_NGAT'):
            os.kill(os.getppid(), signal.SIGINT)
            signal.signal(signal.SIGINT, signal.SIG_DFL); os.kill(os.getpid(), signal.SIGINT)
        sys.exit()
    if a[0] == 'print':
        target = a[1]
        if target == 'system' and os.getenv('MIEN_RAC'): print('khong phai mien'); sys.exit()
        if target.startswith('login/') and os.getenv('LOGIN_VANG'):
            print('Could not print domain: 113: Could not find specified service'); sys.exit(113)
        if target == 'login/100333' and os.getenv('MIEN_CAM'):
            print('Permission denied', file=sys.stderr); sys.exit(1)
        if target in s: print(target+' = {\n\tenvironment = { G3_BI_MAT_GIA = khong_luu }\n}'); sys.exit()
        if target.startswith('gui/503'):
            print('Could not print domain: 125: Domain does not support specified action'); sys.exit(125)
        canonical = 'gui/501' if target == 'login/100003' and os.getenv('G3_ALIAS') else target
        print(canonical+' = {\n\thandle = 100003\n\tservices = {')
        for n, v in s.items():
            if v.get('domain') == canonical: print('  0 - '+n)
        print('}\n\tenvironment = {\n\t\tG3_BI_MAT_GIA = khong_luu\n\t}\n\tendpoints = {')
        if target == 'user/501' and os.getenv('ENDPOINTS'):
            for n in s:
                if n.endswith('.submit'): print('  0 - '+n)
        print('}\n}'); sys.exit()
    if a[0] == 'bootout':
        (d/'da-go').touch()
        n = a[1].split('/')[-1]; receipt('nap '+n.split('.submit')[0])
        if n.endswith('.submit'):
            if os.getenv('PID_SOT'): (d/'pid-sot').touch()
            if os.getenv('DON_HONG'): sys.exit()
            if os.getenv('NAP_LAI') and not (d/'nap-lai').exists():
                (d/'nap-lai').touch(); sys.exit()
        s.pop(n, None)
        # Job con không giữ PID của lá/cha; cha cũng không giữ PID job sau bootout con.
        for v in s.values():
            if n.endswith('.submit'): v['pids'] = [p for p in v.get('pids', []) if p != '8103']
        save(); sys.exit()
sys.exit(99)
'''


def dung(d):
    fake = d / 'fake.py'; fake.write_text(GIA)
    for cmd in ("sudo", "launchctl", "id", "ps", "install", "rm", "plutil"):
        p = d / cmd
        p.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{fake}" "{cmd}" "$@"\n')
        p.chmod(0o755)
    (d / "root").mkdir()


def chay(d, **env):
    dung(d)
    r = subprocess.run(["/bin/bash", str(KB)], env={**os.environ, "G3_GIA": str(d), **env},
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
    nk = [json.loads(l) for l in (d / "nhat-ky").read_text().splitlines()] if (d / "nhat-ky").exists() else []
    return r, nk


def sach(d):
    state = json.loads((d/'state').read_text()) if (d/'state').exists() else {}
    return not state and not list((d / "root").iterdir()) and not list(d.glob('g3p-*-v*'))


@pytest.mark.parametrize('endpoint', [False, True])
def test_bang_ba_cot_va_pid_la_khong_phai_sudo(tmp_path, endpoint):
    r, nk = chay(tmp_path, ENDPOINTS='1' if endpoint else '')
    assert r.returncode == 0, r.stdout
    assert 'v1 | CÓ | gui/501; UID=501 | XÁC NHẬN' in r.stdout
    assert 'v2 | CÓ | gui/501; UID=501 | XÁC NHẬN' in r.stdout
    assert 'v3 | KHÔNG | login/100333; UID=503 | XÁC NHẬN' in r.stdout
    assert 'Ứng viên thiết kế: v4 v5' in r.stdout and sach(tmp_path)
    assert any(x[-2:] == ['procinfo', '8102'] for x in nk)
    assert not any('procinfo' in x and '8100' in x for x in nk)
    assert not any('print' in x for x in nk if x[0] == 'sudo' and x[1:4] != ['-n', '-H', '-u'])
    assert all('submit' not in x for x in nk if x[0] == 'sudo')
    assert len(list((tmp_path/'out').glob('g3p-*.receipt'))) == 1
    assert not any('G3_BI_MAT_GIA' in f.read_text() for f in (tmp_path/'out').iterdir() if f.is_file())


@pytest.mark.parametrize('env, ma, chu', [
    ({'PROC_LOI': '1'}, 3, 'phase=driver'), ({'NAP_LAI': '1'}, 0, 'XÁC NHẬN'),
    ({'DON_HONG': '1'}, 3, 'CHƯA XÁC NHẬN'), ({'MIEN_CAM': '1'}, 3, 'không quyền'),
    ({'G3_JOB_UID': '0'}, 3, 'UID bất thường'), ({'CHUA_CHAY': '1'}, 1, 'KHÔNG KẾT LUẬN'),
    ({'PID_DOI': '1'}, 3, 'phase=driver'), ({'SUDO_LOI': '1'}, 1, 'sudo -n/PAM'),
    ({'AN_NHAN': '1'}, 3, 'CHƯA XÁC NHẬN'), ({'DON_PS_LOI': '1'}, 3, 'CHƯA XÁC NHẬN'),
    ({'SUBMIT_RC': '5'}, 1, 'KHÔNG KẾT LUẬN'), ({'APPLE': '1'}, 0, 'XÁC NHẬN'),
    ({'PID_SOT': '1'}, 3, 'CHƯA XÁC NHẬN'),
    ({'PID_SOT': '1', 'PID_TAI_DUNG':'1'}, 0, 'XÁC NHẬN'),
    ({'MIEN_RAC': '1'}, 3, 'CHƯA XÁC NHẬN'), ({'G3_JOB_UID': '504'}, 3, 'UID bất thường'),
    ({'G3_DON_TK_PERMISSION': '1'}, 0, 'XÁC NHẬN'),
    ({'G3_DON_TK_LOI': '1'}, 3, 'CHƯA XÁC NHẬN'),
])
def test_loi_va_don_huu_han(tmp_path, env, ma, chu):
    r, nk = chay(tmp_path, **env)
    assert r.returncode == ma and chu in r.stdout, r.stdout
    nap = [x for x in nk if x[0] == 'launchctl' and x[1] == 'bootstrap']
    if ma == 3 and 'DON_HONG' in env: assert len(nap) == 1
    if ma == 1 and 'G3_JOB_UID' in env: assert len(nap) == 1
    assert len([x for x in nk if 'bootout' in x]) < 100
    if 'PROC_LOI' in env or 'PID_DOI' in env:
        # Một biến thể chưa kết luận không chặn biến thể sau; miền login của lá không đo được → dọn chưa xác nhận.
        assert 'DỌN: CHƯA XÁC NHẬN' in r.stdout and 'v2 submit' not in r.stdout


def test_het_han_tong_van_go_nhan_truoc_khi_xoa_probe(tmp_path):
    r, nk = chay(tmp_path, G3_HAN_TONG='8', G3_TRE_NAP='10')
    assert r.returncode == 142 and sach(tmp_path), r.stdout
    assert any(x[0:2] == ['launchctl', 'bootstrap'] for x in nk)
    assert not any('v2' in ' '.join(x) for x in nk)


def test_asid_moi_khong_co_login_domain_van_do_user_503(tmp_path):
    r, nk = chay(tmp_path, LOGIN_VANG='1', G3_MIEN_V3='user/503')
    assert r.returncode == 0 and sach(tmp_path), r.stdout
    assert 'v3 | KHÔNG | user/503; UID=503 | XÁC NHẬN' in r.stdout


def test_login_co_the_in_ten_gui_cung_handle(tmp_path):
    r, nk = chay(tmp_path, G3_ALIAS='1')
    assert r.returncode == 0 and sach(tmp_path), r.stdout
    assert 'v1 | CÓ | gui/501; UID=501 | XÁC NHẬN' in r.stdout


def test_khoa_dang_co_khong_sudo(tmp_path):
    (tmp_path/'out/g3b.khoa').mkdir(parents=True)
    r, nk = chay(tmp_path)
    assert r.returncode == 2 and not nk


def test_tien_trinh_la_chan_truoc_lenh_ghi(tmp_path):
    r, nk = chay(tmp_path, LA='1')
    assert r.returncode == 1 and 'không giết' in r.stdout
    assert not any(x[0] == 'sudo' or 'bootstrap' in x or x[0] == 'install' for x in nk)


def test_int_giua_v2_go_dung_receipt(tmp_path):
    r, nk = chay(tmp_path, G3_NGAT='1')
    assert r.returncode == 130 and sach(tmp_path), r.stdout
    assert any(x[0] == 'rm' and 'v2' in x[-1] for x in nk)
    assert not any('v3.plist' in ' '.join(x) for x in nk)


def test_khong_terminal_khong_chay():
    env = {k: v for k, v in os.environ.items() if not k.startswith('G3_')}
    r = subprocess.run(['/bin/bash', str(KB)], env=env, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=5)
    assert r.returncode == 2 and 'Terminal' in r.stdout


def test_thieu_uq_bao_truoc_sudo_va_khong_tu_tao(tmp_path):
    r, nk = chay(tmp_path, UQ_THIEU='1')
    assert r.returncode == 1 and 'thiếu tram-quan-kiem' in r.stdout, r.stdout
    assert not any(x[0] in ('sudo', 'install', 'dscl') for x in nk)


@pytest.mark.parametrize('symlink', [False, True])
def test_probe_khong_ghi_de_hay_theo_symlink(tmp_path, symlink):
    for n in ('toi', 'tk'): (tmp_path/n).mkdir()
    dich = tmp_path/'bang-chung'; dich.write_text('khong doi')
    marker = tmp_path/'toi/job.txt'
    if symlink: marker.symlink_to(dich)
    else: marker.write_text('co san')
    ps = tmp_path/'ps-gia'; ps.write_text('#!/bin/sh\necho "Sun Oct 18 22:03:00 2026"\n'); ps.chmod(0o755)
    uid = str(os.getuid())
    r = subprocess.run(['/bin/sh', str(PROBE), 'job', 'lan', 'vn.tram.g3p.lan.v1', str(tmp_path),
                        uid, '503', '/unused', '/unused', str(ps)], capture_output=True, timeout=5)
    assert r.returncode != 0 and b'tao doc quyen' in r.stderr and dich.read_text() == 'khong doi'
    assert marker.is_symlink() if symlink else marker.read_text() == 'co san'


def test_probe_tu_bao_pid_getuid_geteuid(tmp_path):
    for n in ('toi', 'tk'): (tmp_path/n).mkdir()
    ps = tmp_path/'ps-gia'; ps.write_text('#!/bin/sh\necho ngay-sinh\n'); ps.chmod(0o755)
    uid = str(os.getuid()); p = subprocess.Popen(
        ['/bin/sh', str(PROBE), 'job', 'lan', 'vn.tram.g3p.lan.v1', str(tmp_path), uid, '503',
         '/unused', '/unused', str(ps)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        het = time.monotonic()+5
        while not (tmp_path/'toi/job.txt').exists():
            assert p.poll() is None and time.monotonic() < het
            time.sleep(0.02)
        dong = (tmp_path/'toi/job.txt').read_text().splitlines()[0].split()
        assert dong == ['lan', 'job', str(p.pid), uid, str(os.geteuid()), str(os.getgid()), str(os.getegid())]
        assert (tmp_path/'toi/job.txt').stat().st_mode & 0o777 == 0o644
    finally:
        if p.poll() is None: p.terminate()
        p.communicate(timeout=5)


def test_tu_choi_hop_le_co_the_chon_uq(tmp_path):
    r, _ = chay(tmp_path, REFUSE='1')
    assert r.returncode == 0, r.stdout
    assert 'TỪ CHỐI HỢP LỆ; UID=khong-ap-dung' in r.stdout
    assert 'Ứng viên thiết kế: v4 v5' in r.stdout and sach(tmp_path)


@pytest.mark.parametrize('extra', [{'ERR':'exec failed: Operation not permitted'}, {'SIGNAL':'9'}])
def test_tu_choi_thieu_chung_cu_khong_chon(tmp_path, extra):
    r, _ = chay(tmp_path, REFUSE='1', **extra)
    assert r.returncode == 1 and 'Ứng viên thiết kế: không có' in r.stdout, r.stdout
    assert sach(tmp_path)


def test_uq_co_tien_trinh_la_dung_truoc_sudo(tmp_path):
    r,nk = chay(tmp_path, LA_UQ='1')
    assert r.returncode == 1 and 'không giết' in r.stdout
    assert not any(x[0] == 'sudo' for x in nk)


def test_han_don_khong_ke_thua_bo_qua_alarm():
    source = KB.read_text(); start = source.index('han() {'); end = source.index('\nuq()', start)
    code = source[start:end] + '\nHET=$((SECONDS+1)); trap "" ALRM\nhan /bin/sleep 3\necho ma=$?\n'
    r = subprocess.run(['/bin/bash', '-c', code], capture_output=True, text=True, timeout=5)
    assert 'ma=142' in r.stdout, r.stdout


def test_driver_uq_phai_dung_nhom_rieng(tmp_path):
    r,_ = chay(tmp_path, UQ_GID='20')
    assert r.returncode == 1 and 'nhóm Uq' in r.stdout, r.stdout
    assert 'v5 submit' not in r.stdout and sach(tmp_path)
