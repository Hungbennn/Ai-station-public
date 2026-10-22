"""Đọc/ghi sự kiện của bộ giao việc trong bảng `su_kien` (spec 4 §12) qua kho phiếu của phần 3 (cùng
`su-kien.db`). Mọi trạng thái pipeline SUY lúc đọc từ sự kiện (Q12); "mới nhất" = id lớn nhất."""
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from tram.phieu.kho import KhoPhieu

TAC_NHAN = "tram/giao-viec"


@dataclass(frozen=True)
class SK:
    id: int
    loai: str
    du_lieu: dict
    luc: str


def su_kien_bead(kho: KhoPhieu, du_an: str, bead_id: str) -> list[SK]:
    """Mọi sự kiện của bead (cột `bead_id`), cũ → mới."""
    return [SK(i, l, json.loads(d), luc) for i, l, d, luc in kho.db.execute(
        "SELECT id, loai, du_lieu, luc FROM su_kien WHERE du_an = ? AND bead_id = ? ORDER BY id", (du_an, bead_id))]


def moi_nhat(ds: list[SK], loai: str, dieu_kien: Callable[[SK], bool] | None = None) -> SK | None:
    return next((s for s in reversed(ds) if s.loai == loai and (dieu_kien is None or dieu_kien(s))), None)


def cua_so(ds: list[SK]) -> list[SK]:
    """Sự kiện kể từ `cot.tra_ve` gần nhất (§6.6) — trả về không tái dùng kiểm lại hay QC của vòng trước."""
    tv = moi_nhat(ds, "cot.tra_ve")
    return [s for s in ds if tv is None or s.id > tv.id]


def ref_cong_bo(ds: list[SK]) -> str | None:
    """SHA trạm đã công bố mới nhất của bead (`giao.cong_bo`, phần 3 §6.4 — chờ S7)."""
    s = moi_nhat(ds, "giao.cong_bo")
    return s.du_lieu["commit"] if s else None


def cong_bo_cua_luot(ds: list[SK], luot: int) -> str | None:
    s = moi_nhat(ds, "giao.cong_bo", lambda x: x.du_lieu.get("luot") == luot)
    return s.du_lieu["commit"] if s else None


def da_co(kho: KhoPhieu, du_an: str, loai: str, khoa: dict[str, object]) -> bool:
    """Đã có sự kiện `loai` của dự án mang đúng các trường `khoa` (khoá do mã đặt, không từ ngoài)."""
    loc = "".join(" AND json_extract(du_lieu, ?) = ?" for _ in khoa)
    tham = [x for k, v in khoa.items() for x in (f"$.{k}", v)]
    return kho.db.execute(f"SELECT 1 FROM su_kien WHERE du_an = ? AND loai = ?{loc} LIMIT 1",
                          (du_an, loai, *tham)).fetchone() is not None


def ghi_mot_lan(kho: KhoPhieu, du_an: str, loai: str, du_lieu: dict, *, bead_id: str | None, luc: datetime,
                khoa: tuple[str, ...]) -> int | None:
    """Ghi trong MỘT giao dịch nếu chưa có sự kiện cùng giá trị các trường `khoa` — phát lại không ghi hai lần."""
    with kho.giao_dich():
        if da_co(kho, du_an, loai, {k: du_lieu[k] for k in khoa}):
            return None
        return kho.ghi_su_kien(du_an, loai, du_lieu, luc=luc, bead_id=bead_id, tac_nhan=TAC_NHAN)
