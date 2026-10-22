"""Mã ghép Mac thợ từ xa (spec 3 §9.2) — phía trạm. `tram chu cap-ma <may_id>` cấp mã dùng MỘT lần, hết hạn sau
10 phút; `POST /api/ghep-may {ma}` đổi mã lấy token máy (cùng bảng `may_tho` của 3a-1, trạm chỉ giữ sha256).

Mã = 12 ký tự Crockford base32 (60 bit), in dạng `XXXX-XXXX-XXXX`; trạm chỉ lưu sha256 của mã đã chuẩn hoá. Sai 5 lần
trong 10 phút → khoá đổi mã 10 phút và huỷ mọi mã đang chờ (chặn dò mã qua tailnet). Sự kiện `_tram`: `may.cap_ma`,
`may.ghep`, `may.ghep_sai` — không chứa mã hay token."""
import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, chuoi_gio
from tram.phieu.may import MAY_RE

BANG_CHU = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
DO_DAI, PHUT_HIEU_LUC, SAI_TOI_DA, PHUT_KHOA = 12, 10, 5, 10
LUOC_DO_GHEP = """
CREATE TABLE IF NOT EXISTS ma_ghep (
  bam_ma TEXT PRIMARY KEY, may_id TEXT NOT NULL, tao_luc TEXT NOT NULL, het_luc TEXT NOT NULL,
  dung_luc TEXT, huy_luc TEXT);
CREATE TABLE IF NOT EXISTS ghep_sai (id INTEGER PRIMARY KEY, luc TEXT NOT NULL);
"""


class MaGhepSai(Exception):
    pass


class GhepBiKhoa(Exception):
    pass


@dataclass(frozen=True)
class MaGhep:
    ma: str
    may_id: str
    het_luc: str


def _bam(ma: str) -> str:
    return hashlib.sha256(re.sub(r"[\s-]", "", ma).upper().encode()).hexdigest()


def _co_token(db, may_id: str) -> bool:
    return db.execute("SELECT 1 FROM may_tho WHERE may_id = ? AND go_luc IS NULL", (may_id,)).fetchone() is not None


def cap_ma_ghep(kho: KhoPhieu, may_id: str, *, luc: datetime, tac_nhan: str = "tram/api") -> MaGhep:
    """Mã mới cho `may_id` (huỷ mã cũ chưa dùng của máy đó). Máy đang có token → ValueError (gỡ trước)."""
    if not MAY_RE.fullmatch(may_id):
        raise ValueError(f"may_id không hợp lệ: {may_id!r}")
    kho.db.executescript(LUOC_DO_GHEP)
    ma = "".join(secrets.choice(BANG_CHU) for _ in range(DO_DAI))
    het = chuoi_gio(luc + timedelta(minutes=PHUT_HIEU_LUC))
    with kho.giao_dich() as db:
        if _co_token(db, may_id):
            raise ValueError(f"Máy {may_id} đang có token — chạy `tram chu go-may {may_id}` trước nếu muốn ghép lại")
        db.execute("UPDATE ma_ghep SET huy_luc = ? WHERE may_id = ? AND dung_luc IS NULL AND huy_luc IS NULL",
                   (chuoi_gio(luc), may_id))
        db.execute("INSERT INTO ma_ghep (bam_ma, may_id, tao_luc, het_luc) VALUES (?,?,?,?)",
                   (_bam(ma), may_id, chuoi_gio(luc), het))
        kho.ghi_su_kien(DU_AN_TRAM, "may.cap_ma", {"may_id": may_id, "het_luc": het},
                        luc=luc, tac_nhan=tac_nhan)
    return MaGhep(f"{ma[:4]}-{ma[4:8]}-{ma[8:]}", may_id, het)


def _doi(kho: KhoPhieu, db, ma: str, luc: datetime) -> tuple[str, str] | str:
    """Trong giao dịch. Trả (may_id, token), hoặc chuỗi lý do thất bại — người gọi raise SAU khi commit."""
    tu = chuoi_gio(luc - timedelta(minutes=PHUT_KHOA))
    if db.execute("SELECT COUNT(*) FROM ghep_sai WHERE luc > ?", (tu,)).fetchone()[0] >= SAI_TOI_DA:
        return "khoa"
    h = db.execute("SELECT may_id FROM ma_ghep WHERE bam_ma = ? AND dung_luc IS NULL AND huy_luc IS NULL"
                   " AND het_luc > ?", (_bam(ma), chuoi_gio(luc))).fetchone()
    if h is None:
        db.execute("INSERT INTO ghep_sai (luc) VALUES (?)", (chuoi_gio(luc),))
        so = db.execute("SELECT COUNT(*) FROM ghep_sai WHERE luc > ?", (tu,)).fetchone()[0]
        if so >= SAI_TOI_DA:
            db.execute("UPDATE ma_ghep SET huy_luc = ? WHERE dung_luc IS NULL AND huy_luc IS NULL", (chuoi_gio(luc),))
        kho.ghi_su_kien(DU_AN_TRAM, "may.ghep_sai", {"so_lan": so}, luc=luc)
        return "sai"
    may_id = h[0]
    db.execute("UPDATE ma_ghep SET dung_luc = ? WHERE bam_ma = ?", (chuoi_gio(luc), _bam(ma)))
    if _co_token(db, may_id):
        return "sai"
    token = secrets.token_urlsafe(32)                 # cùng dạng và cách băm với `cap_token_may` (3a-1)
    db.execute("INSERT INTO may_tho (may_id, bam_token, tao_luc) VALUES (?,?,?) ON CONFLICT(may_id) DO UPDATE"
               " SET bam_token = excluded.bam_token, tao_luc = excluded.tao_luc, go_luc = NULL",
               (may_id, hashlib.sha256(token.encode()).hexdigest(), chuoi_gio(luc)))
    kho.ghi_su_kien(DU_AN_TRAM, "may.ghep", {"may_id": may_id}, luc=luc)
    return may_id, token


def doi_ma_ghep(kho: KhoPhieu, ma: str, *, luc: datetime) -> tuple[str, str]:
    """(may_id, token máy). Token chỉ trả MỘT lần — người gọi không log, không in."""
    kho.db.executescript(LUOC_DO_GHEP)
    with kho.giao_dich() as db:
        kq = _doi(kho, db, ma, luc)
    if kq == "khoa":
        raise GhepBiKhoa(f"Sai mã quá {SAI_TOI_DA} lần — chờ {PHUT_KHOA} phút rồi xin mã mới")
    if isinstance(kq, str):
        raise MaGhepSai("Mã ghép sai, đã dùng hoặc hết hạn")
    return kq
