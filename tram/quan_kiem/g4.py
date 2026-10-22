"""G4 dùng kho giả đã chuẩn bị cho đúng lệnh dự án; không thêm lệnh vào policy."""
import argparse
import io
import json
from pathlib import Path

from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.kich_ban_nghiem_thu import git_nhap
from tram.quan_kiem.cau_hinh import nap
from tram.quan_kiem.client import kiem_tu_xa
from tram.quan_kiem.nguon import archive
from tram.quan_kiem.nhan import giai_nen


def chuan_bi(goc, c, ten, fixture):
    if ten not in c['policy']:
        raise ValueError('du-an-chua-dang-ky')
    # Người vận hành duyệt kho dữ liệu giả trước dong-y; không tự lấy repo dự án thật.
    source = git_nhap(fixture, 'rev-parse', 'HEAD').strip()
    data = archive(fixture, source)
    goc.mkdir(mode=0o700)
    kho = goc / 'kho'
    kho.mkdir()
    giai_nen(io.BytesIO(data), kho)
    git_nhap(kho, 'init', '-q', '-b', 'main')
    git_nhap(kho, 'add', '.')
    git_nhap(kho, '-c', 'user.name=Tram G4', '-c', 'user.email=g4@invalid', 'commit', '-qm', 'Fixture G4')
    sha = git_nhap(kho, 'rev-parse', 'HEAD').strip()
    git_nhap(kho, 'update-ref', 'refs/remotes/origin/main', sha)
    home = Path(c['home_tram']).parent / 'tram-g4-quan-kiem'
    dac = Path('/Users/Shared/tram-g4-quan-kiem')
    (goc / 'fixture.json').write_text(json.dumps({'home': str(home), 'dac': str(dac)}))
    for path in (home, dac):
        path.mkdir(mode=0o755)
        (path / 'canary').write_text('TRAM-G4-NONSECRET\n')
        (path / 'canary').chmod(0o644)
    (goc / 'env.testing').write_text('NGHIEM_THU=1\n')
    (goc / 'env.testing').chmod(0o600)
    (goc / 'lan.json').write_text(json.dumps({'sha': sha, 'du_an': ten, 'policy': c['policy'][ten]}))
    return sha


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('buoc', choices=['chuan-bi', 'sach'])
    p.add_argument('thu_muc', type=Path)
    p.add_argument('--du-an')
    p.add_argument('--fixture', type=Path)
    a = p.parse_args(argv)
    c = nap()
    if not c['g4']:
        raise ValueError('chi-chay-khi-cai-che-do-g4')
    if a.buoc == 'chuan-bi' and (a.du_an not in c['policy'] or a.fixture is None):
        p.error('chuan-bi cần --du-an đã đăng ký và --fixture là kho Git dữ liệu giả đã duyệt')
    print('G4 qua socket thật; kho giả:', a.fixture, 'dự án:', a.du_an)
    print('Policy:', json.dumps(c['policy'], ensure_ascii=False))
    if input('Gõ dong-y: ').strip() != 'dong-y':
        return 1
    g = a.thu_muc.resolve()
    if a.buoc == 'chuan-bi':
        chuan_bi(g, c, a.du_an, a.fixture)
        return 0
    info = json.loads((g / 'lan.json').read_bytes())
    ten, sha = info['du_an'], info['sha']
    if info['policy'] != c['policy'].get(ten):
        raise ValueError('policy-da-doi-do-lai-g4')
    policy = c['policy'][ten]
    da = DuAn(ten, g / 'kho', None, {}, moi_truong_kiem=MoiTruongKiem(g / 'env.testing', '.env.testing'),
              giao=CauHinhGiao(lenh_kiem_mac_dinh=tuple(policy['mac_dinh'])))
    from secrets import token_hex
    id_ = 'g4-' + token_hex(8)
    policy = c['policy'][ten]
    r = kiem_tu_xa(g / 'kho', da, giao_id=id_, luot=1, commit=sha, lenh_kiem=policy['mac_dinh'],
                   lenh_cho_phep=policy['cho_phep'], chay_lenh=True)
    print(json.dumps({'giao_id': id_, 'commit': sha, 'dat': r.dat, 'ket_qua': r.ket_qua}, ensure_ascii=False))
    return 0 if r.dat else 2


if __name__ == '__main__':
    raise SystemExit(main())
