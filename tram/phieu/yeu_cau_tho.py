"""Phần chung của các lời gọi thợ có phiếu (spec 3 §5.1, §6.6): khe/giao_id phải thuộc máy của token (403);
`request_id` idempotent — cùng nội dung trả kết quả cũ, khác nội dung → 409."""
import hashlib
import json
from datetime import datetime

from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.khe import su_kien_khe


class KhongThuocMay(Exception):
    """403: khe/giao_id không thuộc máy của token, hoặc khe chưa đăng ký."""


class TrungRequest(Exception):
    """409: cùng request_id, khác nội dung."""


def kiem_thuoc_may(kho: KhoPhieu, may_id: str, khe_id: str, giao_id: str | None = None) -> None:
    if not khe_id.startswith(f"{may_id}/") or su_kien_khe(kho, khe_id, ("khe.dang_ky",)) is None:
        raise KhongThuocMay(f"Khe {khe_id} không thuộc máy {may_id} hoặc chưa đăng ký")
    b = kho.lay(giao_id) if giao_id else None
    if b is not None and b.may_id != may_id:
        raise KhongThuocMay(f"Phiếu {giao_id} không thuộc máy {may_id}")


def digest_than(than: dict) -> str:
    noi_dung = {k: v for k, v in than.items() if k != "request_id"}
    return hashlib.sha256(json.dumps(noi_dung, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def ket_qua_cu(kho: KhoPhieu, request_id: str, digest: str) -> dict | None:
    h = kho.db.execute("SELECT digest, ket_qua FROM bao_tho WHERE request_id = ?", (request_id,)).fetchone()
    if h is None:
        return None
    if h[0] != digest:
        raise TrungRequest(f"request_id {request_id} đã dùng cho nội dung khác")
    return json.loads(h[1])


def luu_ket_qua(kho: KhoPhieu, request_id: str, *, giao_id: str, loai: str, digest: str, ket_qua: dict,
                luc: datetime) -> None:
    kho.db.execute("INSERT INTO bao_tho (request_id, giao_id, loai, digest, ket_qua, luc) VALUES (?,?,?,?,?,?)",
                   (request_id, giao_id, loai, digest, json.dumps(ket_qua), chuoi_gio(luc)))
