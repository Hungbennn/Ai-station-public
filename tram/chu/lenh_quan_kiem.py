"""python -m tram.chu.lenh_quan_kiem cai|go; in kế hoạch rồi chờ dong-y."""
import argparse
import getpass
import json
import subprocess
from pathlib import Path

from tram.chu.cai_dat import in_ke_hoach, thuc_hien
from tram.chu.cai_quan_kiem import lap
from tram.chu.go_quan_kiem import lap_go
from tram.chu.quan_kiem_membership import quan_sat
from tram.chu.so_cai_tho import SoCai


def main(argv=None, *, hoi=input):
    p = argparse.ArgumentParser()
    p.add_argument('viec', choices=['cai', 'go'])
    p.add_argument('--repo', type=Path, default=Path.cwd())
    p.add_argument('--bang-chung-g4', type=Path)
    p.add_argument('--deps-manifest', type=Path)
    a = p.parse_args(argv)
    def chay(cmd, **kw):
        return subprocess.run(cmd, **({'timeout': 30} | kw))
    from tram.duong_dan import tram_home
    with SoCai(tram_home() / 'cai-quan-kiem' / 'so-cai.jsonl').giu() as so:
        if a.viec == 'cai':
            kh = lap(a.repo, getpass.getuser(), so, quan_sat=quan_sat, chay=chay,
                     deps_manifest=a.deps_manifest,
                     g4=a.bang_chung_g4 is None,
                     bang_chung=json.loads(a.bang_chung_g4.read_bytes()) if a.bang_chung_g4 else None)
        else:
            kh = lap_go(so, quan_sat=quan_sat, chay=chay)
        print(in_ke_hoach(kh))
        if hoi('Gõ dong-y để thực hiện: ').strip() != 'dong-y':
            return 1
        thuc_hien(kh, chay=chay)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
