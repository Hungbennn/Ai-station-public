from typing import Literal

from pydantic import BaseModel, ConfigDict


class KetQuaCham(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cot: Literal["ai-lam", "can-chot"]
    ly_do: str
    thieu: list[str]
    cau_hoi_can_chot: list[str]
    do_tin_cay: float


_DS_CHUOI = {"type": "array", "items": {"type": "string"}}

SCHEMA: dict = {
    "type": "object",
    "properties": {
        "cot": {"type": "string", "enum": ["ai-lam", "can-chot"]},
        "ly_do": {"type": "string"},
        "thieu": _DS_CHUOI,
        "cau_hoi_can_chot": _DS_CHUOI,
        "do_tin_cay": {"type": "number"},
    },
    "required": ["cot", "ly_do", "thieu", "cau_hoi_can_chot", "do_tin_cay"],
    "additionalProperties": False,
}


def loi_ngu_nghia(kq: KetQuaCham) -> list[str]:
    loi: list[str] = []
    if not kq.ly_do.strip():
        loi.append("ly_do không được rỗng")
    if kq.cot == "can-chot" and not (kq.cau_hoi_can_chot or kq.thieu):
        loi.append("cot = can-chot thì phải có ít nhất một mục trong cau_hoi_can_chot hoặc thieu")
    if kq.cot == "ai-lam" and kq.thieu:
        loi.append("cot = ai-lam thì thieu phải rỗng")
    if not 0.0 <= kq.do_tin_cay <= 1.0:
        loi.append("do_tin_cay phải nằm trong [0, 1]")
    return loi
