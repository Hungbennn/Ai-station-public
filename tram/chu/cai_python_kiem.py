"""Trình cài Python kiểm riêng, offline, dùng cùng sổ R2; luôn in rồi chờ dong-y."""
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.cai_dat import KeHoach, in_ke_hoach, thuc_hien
from tram.chu.python_kiem import phan_python
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao
from tram.duong_dan import tram_home


def lap(nguon: Path, so: SoCai, *, quan_sat=dinh_danh.quan_sat_that) -> KeHoach:
    tep, ds = phan_python(nguon, tram_home() / 'cai-dat-tho/python-soan')
    viec = kiem_truoc(so, ds, quan_sat=quan_sat)
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    buoc += [(f'[{v}] {t.kieu} {t.ten}: {t.mo_ta()}', lambda t=t: tao(so, t, quan_sat=quan_sat))
             for t, v in zip(ds, viec)]
    return KeHoach(tep, [], ['Chưa đổi nhóm: chạy smoke Python và đối chiếu manifest trước khi đổi nhóm.'], buoc)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nguon', type=Path)
    args = parser.parse_args()
    so = SoCai()
    try:
        with so.giu():
            kh = lap(args.nguon, so)
            print(in_ke_hoach(kh))
            if input('Gõ dong-y để cài Python kiểm: ').strip() != 'dong-y':
                return 1
            thuc_hien(kh)
    except (OSError, ValueError, RuntimeError) as e:
        print(f'Không cài Python kiểm: {type(e).__name__}; sổ R2 giữ phần đã tạo.')
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
