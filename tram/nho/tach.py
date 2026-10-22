"""Bước tách (spec 1b §6.2 bước 1): một sự kiện → 0–3 ký ức ngắn, tự đứng được. LLM chỉ chọn nhánh."""
from dataclasses import dataclass

from tram.cham_cot.prompt import boc_khong_tin_cay
from tram.nho.llm import KetQuaLLM, goi_json
from tram.nho.mo_hinh import DO_DAI_TOI_DA
from tram.nho.pham_vi import NHANH

TOI_DA_KY_UC = 3
SCHEMA_TACH = {
    "type": "object", "additionalProperties": False, "required": ["ky_uc"],
    "properties": {"ky_uc": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["noi_dung", "nhanh", "nhan", "quan_trong", "co_ten_rieng"],
        "properties": {"noi_dung": {"type": "string"}, "nhanh": {"type": "string", "enum": list(NHANH)},
                       "nhan": {"type": "array", "items": {"type": "string"}}, "quan_trong": {"type": "number"},
                       "co_ten_rieng": {"type": "boolean"}}}}}}


@dataclass(frozen=True)
class KyUcTach:
    noi_dung: str
    nhanh: str
    nhan: tuple[str, ...] = ()
    quan_trong: float = 0.5
    co_ten_rieng: bool = False


def loi_tach(d: dict) -> list[str]:
    ds = d.get("ky_uc")
    if not isinstance(ds, list):
        return ["Thiếu mảng ky_uc"]
    loi = [f"Tối đa {TOI_DA_KY_UC} ký ức"] if len(ds) > TOI_DA_KY_UC else []
    for i, k in enumerate(ds, 1):
        if not isinstance(k, dict):
            loi.append(f"Ký ức {i} không phải đối tượng")
            continue
        nd = k.get("noi_dung")
        if not isinstance(nd, str) or not nd.strip() or len(nd.strip()) > DO_DAI_TOI_DA:
            loi.append(f"Ký ức {i}: noi_dung phải khác rỗng, tối đa {DO_DAI_TOI_DA} ký tự")
        if k.get("nhanh") not in NHANH:
            loi.append(f"Ký ức {i}: nhanh phải là nghiep-vu hoặc cach-lam")
        nhan = k.get("nhan")
        if not isinstance(nhan, list) or len(nhan) > 5 or not all(
                isinstance(x, str) and 0 < len(x) <= 30 for x in nhan):
            loi.append(f"Ký ức {i}: nhan tối đa 5 chuỗi, mỗi chuỗi 1–30 ký tự")
        q = k.get("quan_trong")
        if isinstance(q, bool) or not isinstance(q, (int, float)) or not 0 <= q <= 1:
            loi.append(f"Ký ức {i}: quan_trong phải trong [0, 1]")
        if not isinstance(k.get("co_ten_rieng"), bool):
            loi.append(f"Ký ức {i}: co_ten_rieng phải là true/false")
    return loi


def tach(client, van_ban: str, *, vai: tuple[str, str]) -> tuple[list[KyUcTach], KetQuaLLM]:
    """Nội dung sự kiện bọc `<du_lieu_khong_tin_cay>`. Hết lượt → LoiLLMNho (người gọi ghi nho.loi_tach)."""
    kq = goi_json(client, he_thong=vai[1], noi_dung=boc_khong_tin_cay(van_ban), schema=SCHEMA_TACH, kiem=loi_tach)
    return [KyUcTach(k["noi_dung"].strip(), k["nhanh"], tuple(k["nhan"]), float(k["quan_trong"]), k["co_ten_rieng"])
            for k in kq.du_lieu["ky_uc"]], kq
