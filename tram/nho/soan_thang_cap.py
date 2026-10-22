"""Soạn nội dung ký ức thăng cấp (spec 1b §8): LLM chỉ viết bài học tổng quát từ HAI ký ức `cach-lam`.

Không đưa tên dự án, bead hay `nguon` cho LLM — chỉ nội dung. Phạm vi đích, `nguon`, `hieu_luc_tu` do trạm tính.
`noi_dung` rỗng = LLM thấy không có bài học chung → không thăng cấp cặp này."""
import json
from dataclasses import dataclass

from tram.cham_cot.prompt import boc_khong_tin_cay
from tram.nho.llm import goi_json
from tram.nho.mo_hinh import DO_DAI_TOI_DA

SCHEMA_SOAN = {
    "type": "object", "additionalProperties": False, "required": ["noi_dung", "nhan", "co_ten_rieng"],
    "properties": {"noi_dung": {"type": "string"}, "nhan": {"type": "array", "items": {"type": "string"}},
                   "co_ten_rieng": {"type": "boolean"}}}


@dataclass(frozen=True)
class BanSoan:
    noi_dung: str                  # "" = không thăng cấp
    nhan: tuple[str, ...] = ()
    co_ten_rieng: bool = False


def loi_soan(d: dict) -> list[str]:
    loi = []
    nd = d.get("noi_dung")
    if not isinstance(nd, str) or len(nd.strip()) > DO_DAI_TOI_DA:
        loi.append(f"noi_dung phải là chuỗi, tối đa {DO_DAI_TOI_DA} ký tự (rỗng nếu không có bài học chung)")
    nhan = d.get("nhan")
    if not isinstance(nhan, list) or len(nhan) > 5 or not all(isinstance(x, str) and 0 < len(x) <= 30 for x in nhan):
        loi.append("nhan tối đa 5 chuỗi, mỗi chuỗi 1–30 ký tự")
    if not isinstance(d.get("co_ten_rieng"), bool):
        loi.append("co_ten_rieng phải là true/false")
    return loi


def soan(client, vai: tuple[str, str], noi_dung_a: str, noi_dung_b: str) -> BanSoan:
    """Hết lượt guardrail / model từ chối → LoiLLMNho; lỗi mạng/API → anthropic.APIError (người gọi dừng lượt)."""
    du_lieu = json.dumps({"ky_uc": [noi_dung_a, noi_dung_b]}, ensure_ascii=False)
    d = goi_json(client, he_thong=vai[1], noi_dung=boc_khong_tin_cay(du_lieu), schema=SCHEMA_SOAN,
                 kiem=loi_soan).du_lieu
    return BanSoan(d["noi_dung"].strip(), tuple(d["nhan"]), d["co_ten_rieng"])
