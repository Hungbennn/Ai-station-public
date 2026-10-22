"""Lưu cài đặt tự động và TẠM DỪNG bằng sự kiện trong kho sự kiện (D88, design D-4) — không bảng mới, không YAML.

`tu_dong.cai_dat` mang TOÀN BỘ cài đặt sau khi đổi (`cai_dat`) + tên các trường đổi (`doi`); giá trị hiện hành =
sự kiện mới nhất của dự án, phiên bản = id của nó ("0" khi chưa có). `tu_dong.tam_dung` / `tu_dong.tiep_tuc` trên
dự án, hoặc trên `_tram` cho toàn trạm; trạng thái = sự kiện mới nhất trong hai loại.

Mọi hàm nhận KẾT NỐI `su-kien.db`: `KhoSuKien.db` (tram-api) hay `KhoPhieu.db` (tiến trình giao việc — TM-2, TM-3).
Ghi: đọc–so–ghi trong một `BEGIN IMMEDIATE` (`giao_dich`) nên ghi của trạm không đè ghi của Đại ca và ngược lại;
gọi khi đang trong giao dịch của người gọi thì nhập vào giao dịch đó (người gọi commit)."""
import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.thao_tac.loi import XungDot
from tram.tu_dong.cai_dat import MAC_DINH, CaiDatTuDong, truong_doi, tu_phang

DU_AN_TRAM = "_tram"
LOAI_CAI_DAT = "tu_dong.cai_dat"
LOAI_TAM_DUNG, LOAI_TIEP_TUC = "tu_dong.tam_dung", "tu_dong.tiep_tuc"


@dataclass(frozen=True)
class TamDung:
    boi: str            # tác nhân: dai-ca/dashboard | tram/...
    luc: str
    ly_do: str          # mã của trạm (vd lui-hong); "" khi Đại ca bấm


@dataclass(frozen=True)
class TrangThaiTuDong:
    cai_dat: CaiDatTuDong
    phien_ban: str
    tam_dung_du_an: TamDung | None
    tam_dung_tram: TamDung | None


@contextmanager
def giao_dich(db: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    if db.in_transaction:                       # trong giao dịch của người gọi (vd `KhoPhieu.giao_dich()`)
        yield db
        return
    db.execute("BEGIN IMMEDIATE")
    try:
        yield db
    except BaseException:
        db.execute("ROLLBACK")
        raise
    db.execute("COMMIT")


def _moi_nhat(db: sqlite3.Connection, du_an: str, *loai: str) -> tuple | None:
    return db.execute(f"SELECT id, loai, luc, tac_nhan, du_lieu FROM su_kien WHERE du_an=? AND loai IN"
                      f" ({','.join('?' * len(loai))}) ORDER BY id DESC LIMIT 1", (du_an, *loai)).fetchone()


def doc_cai_dat(db: sqlite3.Connection, du_an: str) -> tuple[CaiDatTuDong, str]:
    h = _moi_nhat(db, du_an, LOAI_CAI_DAT)
    return (tu_phang(json.loads(h[4])["cai_dat"]), str(h[0])) if h else (MAC_DINH, "0")


def doi_cai_dat(db: sqlite3.Connection, du_an: str, doi: Callable[[CaiDatTuDong], CaiDatTuDong], *, tac_nhan: str,
                expected: str | None = None, them: dict | None = None) -> int | None:
    """Đọc bản mới nhất, áp `doi`, ghi nếu khác — cùng một giao dịch. `expected` (Đại ca) khác phiên bản hiện hành →
    `XungDot`; trạm truyền `expected=None` (áp lên bản mới nhất). Trả id sự kiện mới, None khi không có gì đổi."""
    with giao_dich(db):
        cu, pb = doc_cai_dat(db, du_an)
        if expected is not None and expected != pb:
            raise XungDot(f"Cài đặt tự động của {du_an} đã đổi (hiện {pb}, đang xem {expected}) — tải lại")
        moi = doi(cu)
        if not (ds := truong_doi(cu, moi)):
            return None
        return ghi_trong_giao_dich(db, du_an, LOAI_CAI_DAT, {**(them or {}), "cai_dat": moi.phang(), "doi": ds},
                                   tac_nhan=tac_nhan, luc=bay_gio())


def lich_su_doi(db: sqlite3.Connection, du_an: str, gioi_han: int = 20) -> list[dict]:
    """Mới → cũ; mỗi dòng: lúc, tác nhân, các trường đổi kèm giá trị trước/sau (so hai bản liền nhau)."""
    ds = db.execute("SELECT luc, tac_nhan, du_lieu FROM su_kien WHERE du_an=? AND loai=? ORDER BY id DESC LIMIT ?",
                    (du_an, LOAI_CAI_DAT, gioi_han + 1)).fetchall()[::-1]
    truoc = tu_phang(json.loads(ds.pop(0)[2])["cai_dat"]) if len(ds) > gioi_han else MAC_DINH
    ra = []
    for luc, tac_nhan, du_lieu in ds:
        sau = tu_phang(json.loads(du_lieu)["cai_dat"])
        ra.append({"luc": luc, "tac_nhan": tac_nhan, "doi": [
            {"truong": t, "truoc": getattr(truoc, t), "sau": getattr(sau, t)} for t in truong_doi(truoc, sau)]})
        truoc = sau
    return ra[::-1]


def tam_dung_cua(db: sqlite3.Connection, du_an: str) -> TamDung | None:
    h = _moi_nhat(db, du_an, LOAI_TAM_DUNG, LOAI_TIEP_TUC)
    if h is None or h[1] != LOAI_TAM_DUNG:
        return None
    return TamDung(h[3], h[2], str(json.loads(h[4]).get("ly_do") or ""))


def ghi_tam_dung(db: sqlite3.Connection, du_an: str, *, tam_dung: bool, tac_nhan: str,
                 them: dict | None = None) -> bool:
    """`du_an` = tên dự án hoặc `DU_AN_TRAM`. Đã ở đúng trạng thái → không ghi, trả False."""
    with giao_dich(db):
        if (tam_dung_cua(db, du_an) is not None) == tam_dung:
            return False
        ghi_trong_giao_dich(db, du_an, LOAI_TAM_DUNG if tam_dung else LOAI_TIEP_TUC, dict(them or {}),
                            tac_nhan=tac_nhan, luc=bay_gio())
        return True


def doc_trang_thai(db: sqlite3.Connection, du_an: str) -> TrangThaiTuDong:
    cd, pb = doc_cai_dat(db, du_an)
    return TrangThaiTuDong(cd, pb, tam_dung_cua(db, du_an), tam_dung_cua(db, DU_AN_TRAM))
