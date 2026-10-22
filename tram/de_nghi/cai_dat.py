"""Nút "agent tự cập nhật việc" theo dự án (spec cong-tac-de-nghi-viec, design D-8, D85, D105) — lưu bằng sự kiện
`tu_cap_nhat.cai_dat` mang TOÀN BỘ trạng thái sau khi đổi; hiện hành = sự kiện mới nhất, phiên bản = id của nó ("0"
khi chưa có). Mặc định: nút dự án TẮT, ba nút con BẬT. Cùng khuôn `tram.tu_dong.luu` và dùng lại `giao_dich` của nó:
mọi hàm nhận KẾT NỐI `su-kien.db` — `KhoSuKien.db` (tram-api) hay `KhoPhieu.db` (nhận báo, vòng tick)."""
import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass, fields

import yaml

from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.thao_tac.loi import XungDot
from tram.tu_dong.luu import giao_dich

LOAI_CAI_DAT = "tu_cap_nhat.cai_dat"


@dataclass(frozen=True)
class CaiDatTuCapNhat:
    bat: bool = False           # nút dự án (D85: mặc định tắt)
    tien_do: bool = True        # ba nút con (D105: bật sẵn)
    viec_moi: bool = True
    bi_chan: bool = True

    def cho_ghi(self, loai: str) -> bool:
        """Một loại đề nghị chỉ được ghi khi cả nút dự án lẫn nút con của loại đó đang bật (D85)."""
        return self.bat and getattr(self, loai) is True


MAC_DINH = CaiDatTuCapNhat()


def tu_dict(d: dict) -> CaiDatTuCapNhat:
    """Khoá lạ bỏ qua, thiếu hay sai kiểu lấy mặc định — mã cũ/mới đọc được sự kiện của nhau."""
    return CaiDatTuCapNhat(**{f.name: d[f.name] for f in fields(CaiDatTuCapNhat) if isinstance(d.get(f.name), bool)})


def doc_cai_dat(db: sqlite3.Connection, du_an: str) -> tuple[CaiDatTuCapNhat, str]:
    h = db.execute("SELECT id, du_lieu FROM su_kien WHERE du_an = ? AND loai = ? ORDER BY id DESC LIMIT 1",
                   (du_an, LOAI_CAI_DAT)).fetchone()
    return (tu_dict(json.loads(h[1])), str(h[0])) if h else (MAC_DINH, "0")


def doi_cai_dat(db: sqlite3.Connection, du_an: str, moi: CaiDatTuCapNhat, *, tac_nhan: str,
                expected: str | None = None, ma_thao_tac: str | None = None) -> int | None:
    """Đọc–so–ghi trong một `BEGIN IMMEDIATE`. `expected` khác phiên bản hiện hành → `XungDot` (409). Trả id sự kiện
    mới; None khi không có gì đổi."""
    with giao_dich(db):
        cu, pb = doc_cai_dat(db, du_an)
        if expected is not None and expected != pb:
            raise XungDot(f"Cài đặt agent tự cập nhật việc của {du_an} đã đổi (hiện {pb}, đang xem {expected})"
                          " — tải lại")
        if moi == cu:
            return None
        return ghi_trong_giao_dich(db, du_an, LOAI_CAI_DAT,
                                   {**asdict(moi), **({"ma_thao_tac": ma_thao_tac} if ma_thao_tac else {})},
                                   tac_nhan=tac_nhan, luc=bay_gio())


def lich_su_doi(db: sqlite3.Connection, du_an: str, gioi_han: int = 20) -> list[dict]:
    """Mới → cũ; mỗi dòng: lúc, tác nhân, các nút đổi kèm giá trị trước/sau (so hai bản liền nhau)."""
    ds = db.execute("SELECT luc, tac_nhan, du_lieu FROM su_kien WHERE du_an = ? AND loai = ? ORDER BY id DESC LIMIT ?",
                    (du_an, LOAI_CAI_DAT, gioi_han + 1)).fetchall()[::-1]
    truoc = tu_dict(json.loads(ds.pop(0)[2])) if len(ds) > gioi_han else MAC_DINH
    ra = []
    for luc, tac_nhan, du_lieu in ds:
        sau = tu_dict(json.loads(du_lieu))
        ra.append({"luc": luc, "tac_nhan": tac_nhan, "doi": [
            {"truong": f.name, "truoc": getattr(truoc, f.name), "sau": getattr(sau, f.name)}
            for f in fields(sau) if getattr(truoc, f.name) != getattr(sau, f.name)]})
        truoc = sau
    return ra[::-1]


def bat_ghi_an_toan(doc: Callable[[str], bool], ten: str) -> bool:
    """`bat_ghi` đọc lỗi (yaml hỏng, khoá sai kiểu, thiếu file) → False (INV-005: khoá ghi khi không chắc)."""
    try:
        return doc(ten) is True
    except (OSError, ValueError, AttributeError, KeyError, yaml.YAMLError):
        return False
