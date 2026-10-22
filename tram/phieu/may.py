"""Token máy thợ (spec 3 §5.1, §9.2) — phía trạm. Trạm chỉ giữ sha256 của token (bảng `may_tho`, tài khoản trạm);
token thật chỉ trao MỘT lần cho tài khoản quản lý thợ (Keychain `tram-tho-token`). Thu hồi (`tram chu go-may`) vô
hiệu mọi phiếu hiệu lực của máy — thu hồi như mất nhịp — và vì thế mọi `ma_giao` tương ứng."""
import hashlib
import hmac
import re
import secrets
from datetime import datetime

from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.ket_thuc import thu_hoi

MAY_RE = re.compile(r"[A-Za-z0-9-]{1,32}")


def _bam(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def cap_token_may(kho: KhoPhieu, may_id: str, *, luc: datetime) -> str:
    """Token ngẫu nhiên 32 byte; cấp lại cho cùng máy thay token cũ và bỏ trạng thái đã gỡ. Người gọi KHÔNG in token."""
    if not MAY_RE.fullmatch(may_id):
        raise ValueError(f"may_id không hợp lệ: {may_id!r}")
    token = secrets.token_urlsafe(32)
    with kho.giao_dich() as db:
        db.execute("INSERT INTO may_tho (may_id, bam_token, tao_luc) VALUES (?,?,?) ON CONFLICT(may_id) DO UPDATE"
                   " SET bam_token = excluded.bam_token, tao_luc = excluded.tao_luc, go_luc = NULL",
                   (may_id, _bam(token), chuoi_gio(luc)))
    return token


def xac_thuc_may(kho: KhoPhieu, token: str | None) -> str | None:
    """may_id của token còn hiệu lực, hoặc None. So hằng thời gian."""
    if not token:
        return None
    bam, ra = _bam(token), None
    for may_id, luu in kho.db.execute("SELECT may_id, bam_token FROM may_tho WHERE go_luc IS NULL"):
        if hmac.compare_digest(luu, bam):
            ra = may_id
    return ra


def go_may(kho: KhoPhieu, may_id: str, *, luc: datetime) -> int:
    """Trả số phiếu đã thu hồi (`giao.thu_hoi {ly_do: "go-may"}`)."""
    with kho.giao_dich() as db:
        if db.execute("UPDATE may_tho SET go_luc = ? WHERE may_id = ? AND go_luc IS NULL",
                      (chuoi_gio(luc), may_id)).rowcount != 1:
            raise ValueError(f"Máy {may_id} không có token còn hiệu lực")
        cua_may = [b for b in kho.cac_phieu_hieu_luc() if b.may_id == may_id]
        for b in cua_may:
            thu_hoi(kho, b, ly_do="go-may", luc=luc)
    return len(cua_may)
