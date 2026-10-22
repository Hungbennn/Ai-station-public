"""Một dòng của kho sự kiện (tách khỏi `kho.py` — bs-2bd.1.20, chỉ dời chỗ)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SuKien:
    luc: str
    du_an: str
    bead_id: str | None
    loai: str
    tac_nhan: str
    du_lieu: dict
    id: int = 0
    token_vao: int | None = None
    token_ra: int | None = None
    mo_hinh: str | None = None
    thoi_gian_ms: int | None = None
