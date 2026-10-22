"""Nối bộ giao việc vào tram-api (spec 4 §10, §13; 3a-1 G11) — CHỈ khi `giao_viec.bat: true` (sau mọi cổng):
`chon_phieu` = `bo.chon` và `con_hop_le_phieu` = `bo.con_hop_le` (router `/api/tho/nhip` truyền vào `cap_phieu`),
bọc an toàn — lỗi của phần 4 thành "không phát phiếu", không thành HTTP 500; hai luồng tick. `bo_giao` luôn được
gắn (cả khi tắt) để dashboard đọc lý do không giao. Dựng `BoGiaoViec` không gọi `bd`/Git nào."""
import sys
import threading
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import yaml

from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.giao_viec.noi_4c import nap_phu_thuoc_4c
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.dieu_kien import ASSIGNEE
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.luong import bat_dau_luong_giao
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat


def _bao(ten: str, e: Exception) -> None:
    print(f"[giao-viec] {ten}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)


def cac_du_an_that(thu_muc: Path | None = None) -> list:
    """Mọi `du-an/<ten>.yaml` (bỏ tên bắt đầu `_`); một file hỏng chỉ làm dự án đó bị bỏ qua.
    Lát 1a-2 (D31): dự án có `bat_ghi: false` không được giao việc — không vào danh sách."""
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    ra = []
    for ten in liet_ke_du_an(thu_muc):
        if ten.startswith("_"):
            continue
        try:
            da = nap_du_an(ten, thu_muc=thu_muc)
            if bat_ghi(ten, thu_muc=thu_muc):
                ra.append(da)
        except (ValueError, OSError, KeyError, AttributeError, yaml.YAMLError) as e:
            _bao(f"bỏ qua dự án {ten}", e)
    return ra


def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
                 thu_muc_du_an: Path | None = None) -> BoGiaoViec:
    from tram.beads.bd import Bd
    from tram.beads.bd_de_nghi import BdDeNghi
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.de_nghi.vong import NguonDeNghi
    from tram.phieu.kho import mo_kho_phieu
    from tram.quan_kiem.client import CongTuXa, kiem_tu_xa
    cac = lambda: [d for d in cac_du_an_that(thu_muc_du_an) if not cg.du_an or d.ten in cg.du_an]
    return BoGiaoViec(cac_du_an=cac,
                      tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                      dong_ho=lambda: datetime.now(timezone.utc), kiem_tu_xa=kiem_tu_xa, cong=CongTuXa(),
                      doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                      p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c(),
                      de_nghi=NguonDeNghi(tao_bd=lambda da: BdDeNghi(da.duong_dan), bat_ghi=bat_ghi))


def an_toan(ham: Callable, mac_dinh, ten: str) -> Callable:
    def boc(*a):
        try:
            return ham(*a)
        except Exception as e:                       # noqa: BLE001 — nhịp tim không được hỏng vì phần 4
            _bao(ten, e)
            return mac_dinh
    return boc


def noi_giao_viec(pt, dung: threading.Event, *, cg: CauHinhGiaoViec | None = None,
                  tao_bo: Callable = dung_bo_that) -> tuple[object, list[threading.Thread]]:
    cg = cg or nap_cau_hinh_giao_viec()
    bo = tao_bo(cg, pt.cau_hinh, bo_dem=pt.bo_dem)
    if not cg.bat:
        return replace(pt, bo_giao=bo), []
    luong = bat_dau_luong_giao(bo, dung, chu_ky=cg.chu_ky_giay)
    return replace(pt, bo_giao=bo, chon_phieu=an_toan(bo.chon, None, "chon"),
                   con_hop_le_phieu=an_toan(bo.con_hop_le, False, "con_hop_le")), luong
