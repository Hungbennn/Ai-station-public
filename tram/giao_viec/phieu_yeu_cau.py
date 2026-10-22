"""Phiếu yêu cầu của bead feature (spec 4 §7.1): khối JSON trong MÔ TẢ, giữa hai dấu `<!-- phieu-yeu-cau -->`.

Dữ liệu không tin cậy: đúng MỘT khối, schema chặt (trường lạ bị từ chối), `du_an` phải là dự án của bead. Thiếu
`muc_tieu`/`pham_vi` (hay chỉ có khoảng trắng) → không hợp lệ. `nghiem_thu_so_bo` phải có ít nhất một dòng: nó là
`tieu_chi[]` của phiếu `spec` (spec 4 §6.1) mà phần 3 bắt buộc khác rỗng."""
import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

DAU = "<!-- phieu-yeu-cau -->"
KHOI_RE = re.compile(r"<!-- phieu-yeu-cau -->\s*(.*?)\s*<!-- phieu-yeu-cau -->", re.S)
GIOI_HAN_BYTE = 32 * 1024
Dong = Annotated[str, Field(min_length=1, max_length=1000)]


class PhieuYeuCau(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phien_ban: Literal[1]
    muc_tieu: str = Field(max_length=2000)
    nghiep_vu_da_chot: list[Dong] = Field(default_factory=list, max_length=50)
    pham_vi: str = Field(max_length=4000)
    khong_lam: list[Dong] = Field(default_factory=list, max_length=50)
    nghiem_thu_so_bo: list[Dong] = Field(min_length=1, max_length=50)
    cau_hoi_mo: list[Dong] = Field(default_factory=list, max_length=50)
    du_an: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    module: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(default_factory=list, max_length=30)
    bien_ban: str | None = Field(default=None, max_length=300)

    @field_validator("muc_tieu", "pham_vi")
    @classmethod
    def _khong_rong(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("không được rỗng")
        return v

    @field_validator("nghiep_vu_da_chot", "khong_lam", "nghiem_thu_so_bo", "cau_hoi_mo")
    @classmethod
    def _dong_khong_rong(cls, v: list[str]) -> list[str]:
        if any(not x.strip() for x in v):
            raise ValueError("có dòng rỗng")
        return v

    @field_validator("bien_ban")
    @classmethod
    def _duong_dan(cls, v: str | None) -> str | None:
        if v is not None and (not v.startswith("docs/") or "\\" in v or ".." in v.split("/")):
            raise ValueError("phải là đường dẫn tương đối dưới docs/, không '..'")
        return v


def tieu_chi_spec(p: PhieuYeuCau) -> list[str]:
    """`tieu_chi[]` của phiếu `spec` = `nghiem_thu_so_bo` đã gộp khoảng trắng (spec 4 §6.1)."""
    return [" ".join(x.split()) for x in p.nghiem_thu_so_bo]


def _loi(e: dict) -> str:
    noi = ".".join(str(x) for x in e.get("loc", ())) or "khối"
    return f"{noi}: {e.get('msg', 'sai')}"[:300]


def doc_phieu(mo_ta: str, du_an: str) -> tuple[PhieuYeuCau | None, list[str]]:
    """(phiếu, []) khi hợp lệ; (None, lỗi) khi không — lỗi không chép lại nội dung khối."""
    so_dau = (mo_ta or "").count(DAU)
    if so_dau == 0:
        return None, [f"Mô tả không có khối {DAU}"]
    if so_dau != 2:
        return None, [f"Mô tả phải có đúng một khối phiếu yêu cầu (hai dấu {DAU}), đang có {so_dau} dấu"]
    tho = KHOI_RE.search(mo_ta).group(1)
    if len(tho.encode()) > GIOI_HAN_BYTE:
        return None, ["Khối phiếu yêu cầu vượt 32 KB"]
    try:
        p = PhieuYeuCau.model_validate_json(tho)
    except ValidationError as e:
        return None, [_loi(x) for x in e.errors()[:20]]
    if p.du_an != du_an:
        return None, [f"du_an của phiếu ({p.du_an}) khác dự án của bead ({du_an})"]
    return p, []
