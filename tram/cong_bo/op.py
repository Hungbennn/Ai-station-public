"""Thao tác công bố BỀN (spec 3 §6.6: "ghi ID thao tác bền trước khi gọi Git; kết quả không rõ thì đối soát theo SHA").
Bảng `cong_bo_op` trong `~/.tram/su-kien.db` (cạnh kho phiếu); tối đa MỘT thao tác mở mỗi bead (chỉ mục có điều kiện)
— hai `da-push` đồng thời cho một bead không cùng đẩy ref công bố. Sự thật về ref công bố là sự kiện `giao.cong_bo`
mới nhất (snapshot §6.5, phần 4 đọc) — không suy từ HEAD remote đang di động (§6.4 bước 7)."""
import json
from dataclasses import dataclass
from datetime import datetime

from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.mo_hinh import Phieu

LUOC_DO_OP = """
CREATE TABLE IF NOT EXISTS cong_bo_op (
  id INTEGER PRIMARY KEY, request_id TEXT NOT NULL, giao_id TEXT NOT NULL, luot INTEGER NOT NULL,
  du_an TEXT NOT NULL, bead_id TEXT NOT NULL, nhanh TEXT NOT NULL, commit_moi TEXT NOT NULL, sha_cu TEXT,
  trang_thai TEXT NOT NULL CHECK (trang_thai IN ('dang', 'khong_ro', 'can_hoan_tac', 'xong', 'bo', 'hoan_tac')),
  luc TEXT NOT NULL, cap_nhat TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS cong_bo_op_mo ON cong_bo_op(du_an, bead_id)
  WHERE trang_thai IN ('dang', 'khong_ro', 'can_hoan_tac');
"""
MO = ("dang", "khong_ro", "can_hoan_tac")
_COT = "id, request_id, giao_id, luot, du_an, bead_id, nhanh, commit_moi, sha_cu, trang_thai, luc"


@dataclass(frozen=True)
class OpCongBo:
    id: int
    request_id: str
    giao_id: str
    luot: int
    du_an: str
    bead_id: str
    nhanh: str
    commit_moi: str
    sha_cu: str | None
    trang_thai: str
    luc: str


def dam_bao_luoc_do(kho: KhoPhieu) -> None:
    """Gọi NGOÀI giao dịch (executescript tự commit)."""
    kho.db.executescript(LUOC_DO_OP)


def cong_bo_hien_tai(kho: KhoPhieu, du_an: str, bead_id: str) -> str | None:
    h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'giao.cong_bo'"
                       " ORDER BY id DESC LIMIT 1", (du_an, bead_id)).fetchone()
    return json.loads(h[0])["commit"] if h else None


def cong_bo_cua_luot(kho: KhoPhieu, du_an: str, bead_id: str, luot: int) -> str | None:
    h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'giao.cong_bo'"
                       " AND json_extract(du_lieu, '$.luot') = ? ORDER BY id DESC LIMIT 1",
                       (du_an, bead_id, luot)).fetchone()
    return json.loads(h[0])["commit"] if h else None


def mo_op(kho: KhoPhieu, p: Phieu, *, request_id: str, commit: str, sha_cu: str | None, luc: datetime) -> int:
    """Trong giao dịch. `sqlite3.IntegrityError` khi bead đã có thao tác mở."""
    g = chuoi_gio(luc)
    return kho.db.execute(
        f"INSERT INTO cong_bo_op ({_COT.removeprefix('id, ')}, cap_nhat) VALUES (?,?,?,?,?,?,?,?,'dang',?,?)",
        (request_id, p.giao_id, p.luot, p.du_an, p.bead_id, p.repo.nhanh, commit, sha_cu, g, g)).lastrowid


def dat_trang_thai(kho: KhoPhieu, op_id: int, trang_thai: str, luc: datetime) -> None:
    kho.db.execute("UPDATE cong_bo_op SET trang_thai = ?, cap_nhat = ? WHERE id = ?",
                   (trang_thai, chuoi_gio(luc), op_id))


def op_mo(kho: KhoPhieu, du_an: str, bead_id: str) -> OpCongBo | None:
    h = kho.db.execute(f"SELECT {_COT} FROM cong_bo_op WHERE du_an = ? AND bead_id = ? AND trang_thai IN"
                       " ('dang', 'khong_ro', 'can_hoan_tac')", (du_an, bead_id)).fetchone()
    return OpCongBo(*h) if h else None


def ghi_cong_bo(kho: KhoPhieu, *, du_an: str, bead_id: str, luot: int, commit: str, ref: str, luc: datetime) -> int:
    """Trong giao dịch. `giao.cong_bo {bead_id, luot, commit, ref}` (spec 3 §10 — đúng dạng 4a-1 đọc)."""
    return kho.ghi_su_kien(du_an, "giao.cong_bo", {"bead_id": bead_id, "luot": luot, "commit": commit, "ref": ref},
                           luc=luc, bead_id=bead_id)
