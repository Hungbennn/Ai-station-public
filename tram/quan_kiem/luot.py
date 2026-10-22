"""Lượt tin cậy Uq; mọi chạm cây dự án đều qua boc_luot dưới tram-kiem."""
import json
from pathlib import Path

from tram.cau_hinh.lenh import khop_bat_ky
from tram.giao_viec.ban_chep import _chay, don_ban, ten_ban_chep, CayKhacNguon
from tram.giao_viec.repo_ban_chep import lenh_repo, lenh_cay
from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
from tram.kiem.toolchain import PYTHON


NHAN = '/usr/local/tram/quan-kiem/tram/quan_kiem/nhan.py'


def chay_luot(d, nguon, env_tar, *, pk, goc, log, policy, thu_hoi, cfg=None):
    wt = Path(goc) / ('luot-' + d['id'])
    boc, kill = pk.boc_luot(wt), pk.kill_nhom
    thu_hoi()
    try:
        _chay(boc(['/bin/mkdir', str(wt)]), kill=kill, check=True)
        _chay(boc(['/bin/mkdir', '-m', '700', f'{wt}.nha', f'{wt}.nha/tmp']), kill=kill, check=True)
        argv = boc([f'{PYTHON}/bin/python3.12', '-I', '-c', Path(NHAN).read_text(), str(wt)])
        _chay(argv, kill=kill, input=nguon, check=True)
        for a in lenh_repo(wt).values():
            _chay(boc(a), kill=kill, check=True)
        r = _chay(boc(lenh_cay(wt)), kill=kill, check=True)
        if r.stdout.decode('ascii').strip() != d['tree']:
            raise CayKhacNguon('cay-khac-nguon')
        deps = cfg['policy'][d['du_an']].get('deps') if cfg else None
        if deps:
            from tram.quan_kiem.cap_deps import kiem_dich_env, cap_deps
            kiem_dich_env(d['dich'])
        _chay([*argv, d['dich']], kill=kill, input=env_tar, check=True)
        if deps:
            cap_deps(wt, deps, boc=boc, kill=kill)
        if cfg and cfg['g4']:
            from tram.quan_kiem.doi_chung_g4 import doi_chung
            doi_chung(cfg, pk, wt, d['id'])
        env = moi_truong_kiem({}, {'HOME': f'{wt}.nha', 'TMPDIR': f'{wt}.nha/tmp'})
        boc_chay = (lambda a: boc(['/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', *a])) if deps else boc
        ket = []
        for i, lenh in enumerate(d['lenh']):
            kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, policy), cwd=wt, env=env, boc=boc_chay, kill=kill,
                              log=Path(log) / f'{d["id"]}-{i}.log', thoi_gian_cho=900)
            if not kq.da_thu_hoi:
                raise OSError('thu-hoi-chua-ro')
            k = kq.sang_lenh_kiem()
            k['tom_tat'] = ''
            ket.append(k)
        return {'dat': bool(ket) and all(k['ket_qua'] == 'pass' for k in ket), 'ket_qua': ket}
    finally:
        don_ban(wt, boc=boc, kill=kill, don_sach=thu_hoi)


def worker(p, cfg):
    from tram.giao_viec.principal_kiem import tu_cach_ly
    from tram.giao_viec.cong_that import thu_hoi_theo_uid
    pk = tu_cach_ly('user:tram-kiem')
    d = json.loads((p / 'yeu-cau.json').read_bytes())
    from tram.quan_kiem.cong import dung
    from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
    cong = dung(cfg, pk, ngu_canh_hien_hanh(pk.ten))
    if cong.trang_thai() != {'trang_thai': 'dang-chay', 'luot': d['id']}:
        raise OSError('cong-khong-khop-luot')
    for q in cong.quan_sat:
        q()
    r = chay_luot(d, (p / 'nguon').read_bytes(), (p / 'env').read_bytes(), pk=pk,
                 goc=cfg['goc'], log=cfg['home'] + '/log', policy=cfg['policy'][d['du_an']]['cho_phep'],
                 thu_hoi=lambda: thu_hoi_theo_uid(pk), cfg=cfg)
    cong.ra(d['id'])
    (p / 'ket-qua.json').write_text(json.dumps(r))
