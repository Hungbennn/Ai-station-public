"""Mô hình con của khối bàn giao (tách khỏi `schema.py` — bs-2bd.1.20, chỉ dời chỗ): trường lạ bị từ chối."""
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Nghiem(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DoiChieu(Nghiem):
    tieu_chi: str
    dat: bool
    bang_chung: str


class LenhKiem(Nghiem):
    lenh: str
    ket_qua: Literal["pass", "fail"]
    tom_tat: str
    digest_log: str


class HuongDaBo(Nghiem):
    huong: str
    vi_sao: str
