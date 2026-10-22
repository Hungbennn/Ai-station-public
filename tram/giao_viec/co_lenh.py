"""Đại ca duyệt đúng ID plan; tác giả/review chỉ do trạm nhận từ phiếu spec đã kiểm."""
import argparse
from contextlib import closing
from datetime import datetime, timezone

from tram.giao_viec.co_plan import duyet
from tram.phieu.kho import mo_kho_phieu


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("du_an")
    p.add_argument("bead")
    p.add_argument("plan", type=int)
    a = p.parse_args(argv)
    with closing(mo_kho_phieu()) as k:
        duyet(k, a.du_an, a.bead, a.plan, datetime.now(timezone.utc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
