"""Ghi đề nghị SAU escalation trong `vong_nhanh` (D84, D107, D134; Q11, Q13, V2-Q3). Giữ thứ tự nhận trong
mỗi dự án; luân phiên dự án bằng con trỏ trong NguonDeNghi dùng lại qua các nhịp. Hết ngân sách không bắt đầu đọc
dự án mới. Dự án đã bắt đầu được dự phòng một lệnh ghi sau đọc chậm, vẫn kiểm tươi mọi cửa an toàn. Trần chờ lệnh:
ngan_sach + 2 * HAN_BD (20 + 30 + 30 = 80 giây), chưa tính xử lý cục bộ và thu hồi; không tăng hạn từng lệnh.
Đọc lỗi cũng nhường lượt. Không cache Beads qua nhịp; dấu mã đối soát việc create xong nhưng chưa dep add.
Khoá ghi / estop giữ chờ, nút tắt bỏ. Lỗi bd chỉ ghi mã lỗi; đi hết dự án thì ghi đợt Telegram (D86)."""
import json
import time
from collections import Counter
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime

from tram.beads.loi import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.de_nghi.cho import TAC_NHAN, Cho, de_nghi_cho, ghi_ket_qua
from tram.de_nghi.cua import GIU, Cua, DungGhi
from tram.de_nghi.ghi import ghi_mot
from tram.giao_viec.su_kien import da_co

NGAN_SACH = 20.0                                # giây mỗi nhịp cho phần ghi đề nghị (Q13)


@dataclass
class NguonDeNghi:
    tao_bd: Callable[[DuAn], object]            # BdDeNghi(repo) — actor tram/de-nghi
    bat_ghi: Callable[[str], bool]               # đọc lại `bat_ghi` ngay trước mỗi lần ghi (lỗi → false)
    ngan_sach: float = NGAN_SACH
    dong_ho: Callable[[], float] = time.monotonic
    sau_du_an: str | None = field(default=None, init=False)  # con trỏ luân phiên, chỉ trong RAM


def _du_an(kho, da: DuAn, nguon: NguonDeNghi, ds: list[Cho], luc: datetime, dem: Counter,
           het: float) -> str | None:
    """None = đi hết danh sách; còn lại = lý do dừng (estop | khoa-ghi | het-gio | bd), phần chưa ghi chờ nhịp sau."""
    if not ds:
        return None
    if nguon.dong_ho() >= het:
        return "het-gio"
    cua, bd = Cua(kho, da.ten, nguon.bat_ghi, nguon.dong_ho, het), nguon.tao_bd(da)
    beads = {b.id: b for b in bd.tat_ca()}
    for c in ds:
        try:
            cua.kiem(c.loai)
            dem[f"de_nghi_{ghi_mot(kho, bd, beads, c, luc, cua.truoc_ghi)}"] += 1
        except DungGhi as e:
            if e.ly_do in GIU:
                return e.ly_do
            dem["de_nghi_bo"] += ghi_ket_qua(kho, c, "de_nghi.bo", {"ly_do": e.ly_do}, luc=luc)
        except LoiBd:
            ghi_ket_qua(kho, c, "de_nghi.loi_ghi", {"ma_loi": "bd"}, luc=luc)
            dem["loi"] += 1
            return "bd"
    return None


def ghi_dot(kho, du_an: str, luc: datetime) -> int:
    theo: dict[int, tuple[str, list[str]]] = {}
    for bead_id, d in kho.db.execute("SELECT bead_id, du_lieu FROM su_kien WHERE du_an = ? AND loai ="
                                     " 'de_nghi.da_ghi' AND json_extract(du_lieu, '$.vao_cot_3') IS NOT NULL"
                                     " ORDER BY id", (du_an,)):
        d = json.loads(d)
        theo.setdefault(d["vao_cot_3"], (bead_id, []))[1].append(d["bead_moi"])
    so = 0
    for v, (goc, moi) in theo.items():
        with kho.giao_dich():
            if not da_co(kho, du_an, "de_nghi.dot_ghi", {"vao_cot_3": v}):
                kho.ghi_su_kien(du_an, "de_nghi.dot_ghi", {"bead_goc": goc, "bead_moi": moi, "vao_cot_3": v},
                                luc=luc, bead_id=goc, tac_nhan=TAC_NHAN)
                so += 1
    return so


def vong_de_nghi(bo, nguon: NguonDeNghi, luc: datetime) -> dict[str, int]:
    dem: Counter = Counter()
    het = nguon.dong_ho() + nguon.ngan_sach
    with closing(bo.mo_kho()) as kho:
        cho: dict[str, list[Cho]] = {}
        for c in de_nghi_cho(kho):
            cho.setdefault(c.du_an, []).append(c)
        du_an = list(bo.cac_du_an())
        vi_tri = next((i + 1 for i, da in enumerate(du_an) if da.ten == nguon.sau_du_an), 0)
        for da in du_an[vi_tri:] + du_an[:vi_tri]:
            if cho.get(da.ten):
                if nguon.dong_ho() >= het:
                    dem["de_nghi_giu"] += 1
                    break
                nguon.sau_du_an = da.ten         # kể cả đọc lỗi: nhịp sau nhường dự án kế tiếp
            try:
                dung = _du_an(kho, da, nguon, cho.get(da.ten, []), luc, dem, het)
            except (LoiBd, OSError):
                dem["loi"] += 1
                continue
            if dung is None:
                dem["de_nghi_dot"] += ghi_dot(kho, da.ten, luc)
            elif dung in GIU:
                dem["de_nghi_giu"] += 1
                if dung != "khoa-ghi":
                    break                       # estop / hết ngân sách: dừng cả nhịp, dự án sau chờ nhịp sau
    return {k: v for k, v in dem.items() if v}
