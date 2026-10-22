"""Hình của yêu cầu tạo feature (D46/D47; spec 4 §7.1; plan 4d 4D-0): mã, dấu dòng đầu, mô tả bead, digest payload.

Mã `yc-<32 hex>` do máy A sinh một lần, KHÔNG suy từ nội dung — là khoá chống trùng. Digest là sha256 của payload đã
chuẩn hoá (dự án, tiêu đề, ưu tiên, phiếu sau `model_dump`), không gồm mã. Dấu `<!-- ma-yeu-cau: … -->` ở dòng đầu mô
tả chỉ để đối soát khi kết quả `bd create` không rõ; không phải quyền, không phải khoá chống trùng."""
import hashlib
import json
import re
from dataclasses import dataclass

from tram.beads.mo_hinh import Bead
from tram.giao_viec.phieu_yeu_cau import DAU, PhieuYeuCau

MA_RE = re.compile(r"yc-[0-9a-f]{32}")
DAU_MA_RE = re.compile(r"<!-- ma-yeu-cau: (yc-[0-9a-f]{32}) -->")
LOAI = "feature"
NHAN = ("can-spec",)
TAC_NHAN_A = "dai-ca/may-a"          # nhãn nguồn của `bd --actor`, KHÔNG phải chứng thực (D47)


@dataclass(frozen=True)
class YeuCau:
    ma: str
    du_an: str
    tieu_de: str
    uu_tien: int
    phieu: PhieuYeuCau


def dong_dau(ma: str) -> str:
    return f"<!-- ma-yeu-cau: {ma} -->"


def mo_ta(yc: YeuCau) -> str:
    khoi = json.dumps(yc.phieu.model_dump(), ensure_ascii=False, indent=2)
    return f"{dong_dau(yc.ma)}\n{DAU}\n{khoi}\n{DAU}"


def digest(yc: YeuCau) -> str:
    tho = json.dumps({"du_an": yc.du_an, "tieu_de": yc.tieu_de, "uu_tien": yc.uu_tien, "phieu": yc.phieu.model_dump()},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(tho.encode()).hexdigest()


def dau_xem(yc: YeuCau) -> str:
    """Mã xem: gắn CẢ mã yêu cầu lẫn nội dung — mã xem của yêu cầu này không dùng được cho yêu cầu khác."""
    return hashlib.sha256(f"{yc.ma}\n{digest(yc)}".encode()).hexdigest()[:16]


def ma_cua(b: Bead) -> str | None:
    m = DAU_MA_RE.fullmatch((b.description or "").split("\n", 1)[0].strip())
    return m.group(1) if m else None


def tim_theo_dau(beads: list[Bead], ma: str) -> list[str]:
    """Id các bead `feature` có ĐÚNG dòng đầu là dấu của `ma` (dấu ở dòng khác, bead loại khác: không tính)."""
    return sorted(b.id for b in beads if b.issue_type == LOAI and ma_cua(b) == ma)
