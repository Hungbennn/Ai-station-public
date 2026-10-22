"""Danh sách bead đề xuất `docs/plans/<feature-id>.beads.json` do khe spec viết (spec 4 §7.2) — dữ liệu không tin cậy.

Khe spec chỉ ĐỀ XUẤT; trạm là bên tạo bead (Q11) sau khi Đại ca duyệt đúng bản này (`digest_ke_hoach`, G11).
`digest_ke_hoach` băm JSON đã đọc (khoá sắp xếp, không khoảng trắng) — skill "xem spec chờ duyệt" trên máy A tính
y hệt (`ky-nang/xem-spec-cho-duyet/xem_spec.py`)."""
import hashlib
import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

GIOI_HAN_BYTE = 256 * 1024
NHAN_RE = re.compile(r"^[a-z0-9][a-z0-9:._-]{0,49}$")
NHAN_CAM = frozenset({"cot-khoa", "co-do", "can-spec", "cho-duyet-spec", "theo-plan"})
TIEN_TO_CAM = ("cot:", "tram:", "co:")
DUONG_RE = re.compile(r"^docs/[A-Za-z0-9._/-]+\.md$")


def duong_ke_hoach(feature: str) -> str:
    return f"docs/plans/{feature}.beads.json"


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DeXuatBead(_M):
    khoa: str = Field(pattern=r"^[a-z0-9-]{1,20}$")
    tieu_de: str = Field(min_length=1, max_length=200)
    loai: Literal["task", "bug", "chore", "spike"]
    uu_tien: int = Field(ge=0, le=4, strict=True)
    mo_ta: str = Field(default="", max_length=8000)
    nghiem_thu: str = Field(max_length=4000)
    phu_thuoc: list[str] = Field(default_factory=list, max_length=30)
    nhan: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tieu_de")
    @classmethod
    def _tieu_de(cls, v: str) -> str:
        if not v.strip() or v.lstrip().startswith("-") or any(c in v for c in "\r\n"):
            raise ValueError("tiêu đề rỗng, bắt đầu bằng '-' (thành cờ của bd) hoặc nhiều dòng")
        return v

    @field_validator("nghiem_thu")
    @classmethod
    def _nghiem_thu(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("nghiem_thu không được rỗng")
        return v

    @field_validator("nhan")
    @classmethod
    def _nhan(cls, v: list[str]) -> list[str]:
        for n in v:
            if not NHAN_RE.fullmatch(n) or n in NHAN_CAM or n.startswith(TIEN_TO_CAM):
                raise ValueError(f"nhãn {n!r} không được dùng (nhãn cột, luồng, cờ, tram:*)")
        return v


class KeHoachBead(_M):
    phien_ban: Literal[1]
    feature: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
    spec_file: str = Field(max_length=200)
    plan_file: str = Field(max_length=200)
    bead: list[DeXuatBead] = Field(min_length=1, max_length=30)

    @field_validator("spec_file", "plan_file")
    @classmethod
    def _duong(cls, v: str) -> str:
        if not DUONG_RE.fullmatch(v) or any(p in ("", ".", "..") for p in v.split("/")):
            raise ValueError("phải là file .md tương đối dưới docs/, không '..'")
        return v

    @model_validator(mode="after")
    def _phu_thuoc(self):
        khoa = [b.khoa for b in self.bead]
        if len(set(khoa)) != len(khoa):
            raise ValueError("khoa trùng")
        ke = {b.khoa: b.phu_thuoc for b in self.bead}
        for b in self.bead:
            if b.khoa in b.phu_thuoc or set(b.phu_thuoc) - set(khoa):
                raise ValueError(f"{b.khoa}: phu_thuoc chỉ trỏ khoa khác trong cùng file")
        trang = {}

        def tham(k: str) -> None:                 # DFS: 1 đang thăm, 2 xong — gặp 1 lần nữa là vòng
            trang[k] = 1
            for t in ke[k]:
                if trang.get(t) == 1:
                    raise ValueError(f"phụ thuộc vòng qua {k} → {t}")
                if t not in trang:
                    tham(t)
            trang[k] = 2

        for k in khoa:
            if k not in trang:
                tham(k)
        return self


def digest_ke_hoach(van_ban: str) -> str:
    tho = json.dumps(json.loads(van_ban), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(tho.encode()).hexdigest()


def doc_ke_hoach(van_ban: str | None, feature: str) -> tuple[KeHoachBead | None, list[str]]:
    if van_ban is None:
        return None, [f"Không thấy file thường {duong_ke_hoach(feature)}"]
    if len(van_ban.encode()) > GIOI_HAN_BYTE:
        return None, ["File *.beads.json vượt 256 KB"]
    try:
        kh = KeHoachBead.model_validate_json(van_ban)
    except ValidationError as e:
        return None, [f"{'.'.join(str(x) for x in l.get('loc', ())) or 'file'}: {l.get('msg')}"[:300]
                      for l in e.errors()[:20]]
    if kh.feature != feature:
        return None, [f"feature trong file ({kh.feature}) khác bead ({feature})"]
    return kh, []
