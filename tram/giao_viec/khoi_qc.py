"""Khối QC trong file bàn giao của phiếu `qc` (spec 4 §6.3), giữa hai dấu `<!-- qc -->` — dữ liệu không tin cậy."""
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

KHOI_QC_RE = re.compile(r"<!-- qc -->\s*(\{.*?\})\s*<!-- qc -->", re.S)


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PhatHien(_M):
    muc: Literal["chan", "quan-trong", "nho"]
    noi_dung: str = Field(max_length=2000)
    vi_tri: str = Field(default="", max_length=300)


class NoiDungQC(_M):
    ket_luan: Literal["dat", "tra_ve"]
    commit_code: str = Field(pattern=r"^[0-9a-f]{7,40}$")
    phat_hien: list[PhatHien] = Field(default_factory=list, max_length=50)


class KhoiQC(_M):
    qc: NoiDungQC


def doc_khoi_qc(van_ban: str | None) -> NoiDungQC | None:
    """Khối cuối cùng trong file; thiếu, JSON lỗi hay sai schema → None (trạm coi như `tra_ve`)."""
    khop = KHOI_QC_RE.findall(van_ban or "")
    if not khop:
        return None
    try:
        return KhoiQC.model_validate_json(khop[-1]).qc
    except ValidationError:
        return None
