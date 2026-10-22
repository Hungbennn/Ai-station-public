"""Dựng dữ liệu giả của G4; không đọc dữ liệu cá nhân có sẵn."""
import json
import hashlib
import os
import re
import subprocess
import secrets
import shlex
from pathlib import Path


def tao_mau(pk, luot: Path, home: Path, tam: Path, chay, *, receipt: Path | None = None) -> dict:
    run = secrets.token_hex(12)
    cay_home, cay_dac = home / f'tram-g4-canary-{run}', tam / f'tram-g4-dac-{run}'
    if receipt is not None:
        with receipt.open('x') as f:
            json.dump({'luot': str(luot), 'home': str(cay_home), 'dac': str(cay_dac)}, f)
            f.flush()
            os.fchmod(f.fileno(), 0o600)
            os.fsync(f.fileno())
    dau = secrets.token_hex(32)
    for cay in (cay_home, cay_dac):
        cay.mkdir()
        cay.chmod(0o755)
        (cay / 'canary').write_text(dau)
        (cay / 'canary').chmod(0o644)
    q = shlex.quote
    mau, link = luot / 'mau', luot / 'canary-link'
    script = (f'mkdir -p {q(str(luot))} {q(str(luot) + ".nha/tmp")}; '
              f'printf %s {q(dau)} > {q(str(mau))}; '
              f'ln -s {q(str(cay_home / "canary"))} {q(str(link))}; '
              f'cp /bin/launchctl {q(str(luot / "launchctl-copy"))} && '
              f'cmp -s /bin/launchctl {q(str(luot / "launchctl-copy"))}')
    ma, _ = chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
    if ma != 0:
        raise ValueError('không dựng được fixture G4; giữ cây để kiểm/dọn')
    tep_home, tep_dac = cay_home / 'canary', cay_dac / 'canary'
    firmlink = Path('/System/Volumes/Data') / tep_home.relative_to('/')
    return {'home': tep_home, 'dac': tep_dac, 'mau': mau, 'tep': [tep_home, link, firmlink, tep_dac, mau]}


def smoke_toolchain(pk, luot: Path, chay) -> dict[str, bool]:
    from tram.kiem.toolchain import PYTHON, UV, GIT, NODE, bien_kiem
    env = ['/usr/bin/env', '-i', f'HOME={luot}.nha', f'TMPDIR={luot}.nha/tmp',
           *(f'{k}={v}' for k, v in bien_kiem(f'{luot}.nha').items()), 'UV_OFFLINE=1']
    lenh = {
        'venv': [f'{PYTHON}/bin/python3.12', '-B', '-I', '-m', 'venv', '--without-pip', str(luot / 'venv')],
        'python': [str(luot / 'venv/bin/python'), '-I', '-B', '-c',
                   f'import sys; assert sys.base_prefix == {PYTHON!r}'],
        'uv': [f'{UV}/bin/uv', '--version'], 'git': [f'{GIT}/bin/git', '--version'],
        'node': [f'{NODE}/bin/node', '--version'], 'npm': [f'{NODE}/bin/npm', '--version'],
    }
    return {ten: chay(pk.boc_luot(luot)([*env, *argv]))[0] == 0 for ten, argv in lenh.items()}


def do_canary(pk, luot: Path, tep: list[Path], mau: Path, *, chay=subprocess.run) -> dict:
    """Bên gọi chuẩn bị LUOT/NHA, mẫu và canary; chỉ trả mã hữu hạn, lỗi/timeout thành None."""
    from tram.giao_viec.kich_ban_nghiem_thu import kich_ban_canary
    script = kich_ban_canary(tep, mau)
    ra = {}
    for ten, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        try:
            kq = chay(boc(['/bin/sh', '-c', script]), capture_output=True, text=True, timeout=15)
            dong = kq.stdout.splitlines()
            hop_le = len(dong) == len(tep) and all(
                re.fullmatch(rf'{i}:(match|different|no-match):(yes|no):(yes|no)', d) for i, d in enumerate(dong))
            ra[ten] = dong if kq.returncode == 0 and hop_le else None
        except (OSError, subprocess.SubprocessError):
            ra[ten] = None
    return ra


NGUON_LAUNCHD = ('submit', 'launchd', 'submitcopy', 'launchdcopy')


def nhan_luot(dau: Path) -> str:
    return 'vn.tram.nghiem-thu.' + hashlib.sha256(str(dau).encode()).hexdigest()[:24]


def ghi_receipt(tep: Path, dau: Path, uid_kiem: int, uid_tram: int, *, mien=None) -> None:
    if uid_kiem <= 0 or uid_tram <= 0 or uid_kiem == uid_tram:
        raise ValueError('UID nghiệm thu phải khác nhau và khác root')
    nhan = nhan_luot(dau)
    dich = [{'mien': m, 'nhan': f'{nhan}.{n}'} for m in
            (mien or (f'user/{uid_kiem}', f'gui/{uid_kiem}', f'gui/{uid_tram}')) for n in NGUON_LAUNCHD]
    with tep.open('x', encoding='utf-8') as f:
        json.dump({'run': nhan, 'trang_thai': 'chua-do', 'dich': dich}, f, ensure_ascii=False)
        f.flush()
        os.fchmod(f.fileno(), 0o600)
        os.fsync(f.fileno())


def lenh_don(receipt: dict) -> list[list[str]]:
    """Chỉ sinh argv để chủ miền duyệt/chạy; không biến exit 0 thành chứng cứ sạch."""
    run = receipt.get('run', '')
    if not re.fullmatch(r'vn\.tram\.nghiem-thu\.[a-f0-9]{24}', run):
        raise ValueError('run receipt sai dạng')
    ra = []
    for dich in receipt['dich']:
        mien, nhan = dich['mien'], dich['nhan']
        if not re.fullmatch(r'(?:(?:user|gui|login)/[1-9][0-9]*|system)', mien) or nhan not in {
            f'{run}.{n}' for n in NGUON_LAUNCHD
        }:
            raise ValueError('đích dọn không thuộc receipt của run')
        ra.append(['/bin/launchctl', 'bootout', f'{mien}/{nhan}'])
    return ra


def receipt_truoc_luot(dau: Path, uid_kiem: int) -> None:
    import os
    from tram.duong_dan import tram_home
    goc = tram_home() / 'log' / 'nghiem-thu'
    goc.mkdir(parents=True, exist_ok=True)
    ghi_receipt(goc / f'receipt-{nhan_luot(dau)}.json', dau, uid_kiem, os.getuid())
