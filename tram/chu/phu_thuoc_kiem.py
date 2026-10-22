"""Soạn/cài bundle Ben Station offline; luôn in kế hoạch và chờ dong-y."""
import argparse
from pathlib import Path

from tram.chu.cai_dat import in_ke_hoach, thuc_hien
from tram.chu.cai_phu_thuoc import lap_cai
from tram.chu.soan_phu_thuoc import lap_soan
from tram.chu.so_cai_tho import SoCai


def main(argv=None, *, hoi=input):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='viec', required=True)
    s = sub.add_parser('soan')
    s.add_argument('--du-an', required=True, choices=['ben-station'])
    for name in ('nguon', 'venv', 'node-modules', 'dich'):
        s.add_argument('--' + name, type=Path, required=True)
    s.add_argument('--commit', required=True)
    c = sub.add_parser('cai')
    c.add_argument('--goi', type=Path, required=True)
    a = p.parse_args(argv)
    try:
        with SoCai().giu() as so:
            kh = lap_soan(a.nguon, a.commit, a.venv, a.node_modules, a.dich) if a.viec == 'soan' else lap_cai(a.goi, so)
            print(in_ke_hoach(kh))
            if hoi('Gõ dong-y để thực hiện: ').strip() != 'dong-y':
                return 1
            thuc_hien(kh)
        return 0
    except (OSError, ValueError, RuntimeError):
        print('Không hoàn tất bundle phụ thuộc; giữ staging và phần đã ghi sổ R2 để đối soát.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
