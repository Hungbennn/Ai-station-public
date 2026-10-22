"""Gộp (spec 1b §6.3): chỉ trong cùng `pham_vi`; bảo vệ ký ức của Đại ca (#18); kiểm lại nội dung cuối.

LLM chỉ quyết `giu_ca_hai | gop | thay` và soạn câu gộp. `pham_vi`, `nguon`, `nguon_dai_ca`, `hieu_luc_tu`, `id`
do trạm tính tất định. Lỗi LLM hay câu gộp không qua kiểm → giữ nguyên các bản cũ (`giu_ca_hai`)."""
import json
from dataclasses import dataclass

from tram.cham_cot.prompt import boc_khong_tin_cay
from tram.nho.llm import LoiLLMNho, goi_json
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.mo_hinh import DO_DAI_TOI_DA, KyUc

NGUONG_GOP = 0.85
TOI_DA_UNG_VIEN = 3
HANH_DONG = ("giu_ca_hai", "gop", "thay")
SCHEMA_GOP = {
    "type": "object", "additionalProperties": False, "required": ["quyet_dinh", "noi_dung_gop", "co_ten_rieng"],
    "properties": {
        "quyet_dinh": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "hanh_dong"],
            "properties": {"id": {"type": "string"}, "hanh_dong": {"type": "string", "enum": list(HANH_DONG)}}}},
        "noi_dung_gop": {"type": "string"}, "co_ten_rieng": {"type": "boolean"}}}


@dataclass(frozen=True)
class KetQuaGop:
    noi_dung: str                       # nội dung cuối sẽ ghi (câu gộp, hoặc nguyên ký ức mới)
    xoa: tuple[str, ...] = ()           # id bản cũ xoá mềm (gop + thay)
    gop_tu: tuple[KyUc, ...] = ()       # bản cũ được gộp — hợp nguồn, lấy max quan_trong


def _kiem(ids: list[str]):
    """Chịu mọi đầu ra sai kiểu: trả danh sách lỗi (→ thử lại, hết lượt thì giữ nguyên — G7), không ném."""
    def kiem(d: dict) -> list[str]:
        qd = d.get("quyet_dinh")
        if not isinstance(qd, list) or not all(isinstance(q, dict) and isinstance(q.get("id"), str) for q in qd):
            return ["quyet_dinh phải là mảng các đối tượng {id: chuỗi, hanh_dong}"]
        loi = [] if sorted(q["id"] for q in qd) == sorted(ids) else [f"Cần đúng một quyết định cho mỗi id {ids}"]
        if any(q.get("hanh_dong") not in HANH_DONG for q in qd):
            loi.append(f"hanh_dong phải thuộc {HANH_DONG}")
        nd = d.get("noi_dung_gop")
        if not isinstance(nd, str) or not isinstance(d.get("co_ten_rieng"), bool):
            return loi + ["noi_dung_gop phải là chuỗi, co_ten_rieng phải là boolean"]
        if any(q.get("hanh_dong") == "gop" for q in qd) and not (0 < len(nd.strip()) <= DO_DAI_TOI_DA):
            loi.append(f"Có gop thì noi_dung_gop phải khác rỗng, tối đa {DO_DAI_TOI_DA} ký tự")
        return loi
    return kiem


def loc_ung_vien(tim_ra: list[tuple[KyUc, float]], pham_vi: str) -> list[KyUc]:
    """Tối đa 3 bản cùng `pham_vi`, chưa xoá, cosine ≥ 0,85, cao nhất trước (`tim_ra` đã lọc model, giảm dần)."""
    ds = [k for k, cos in tim_ra if cos >= NGUONG_GOP and k.pham_vi == pham_vi and not k.da_xoa]
    return ds[:TOI_DA_UNG_VIEN]


def bao_ve(cu: KyUc, moi_dai_ca: bool, hanh_dong: str) -> str:
    """#18: ký ức của Đại ca chỉ bị gop/thay bởi ký ức mới cũng của Đại ca."""
    return "giu_ca_hai" if cu.nguon_dai_ca and not moi_dai_ca else hanh_dong


def gop(client, vai: tuple[str, str], *, noi_dung_moi: str, moi_dai_ca: bool, pham_vi: str,
        ung_vien: list[KyUc], luat: LuatDuAn) -> KetQuaGop:
    """`ung_vien` từ `loc_ung_vien`. Không có ứng viên → ghi mới, không gọi LLM."""
    ung_vien = [k for k in ung_vien if k.pham_vi == pham_vi and not k.da_xoa]    # phòng thủ: không vượt phạm vi
    if not ung_vien:
        return KetQuaGop(noi_dung_moi)
    du_lieu = json.dumps({"moi": noi_dung_moi, "cu": [{"id": k.id, "noi_dung": k.noi_dung} for k in ung_vien]},
                         ensure_ascii=False)
    try:
        kq = goi_json(client, he_thong=vai[1], noi_dung=boc_khong_tin_cay(du_lieu), schema=SCHEMA_GOP,
                      kiem=_kiem([k.id for k in ung_vien])).du_lieu
    except LoiLLMNho:
        return KetQuaGop(noi_dung_moi)
    hd = {q["id"]: q["hanh_dong"] for q in kq["quyet_dinh"]}
    hd = {k.id: bao_ve(k, moi_dai_ca, hd[k.id]) for k in ung_vien}
    cau_gop = kq["noi_dung_gop"].strip()
    if "gop" in hd.values() and not pham_vi.endswith("/nghiep-vu") and ly_do_nghiep_vu(
            cau_gop, luat, co_ten_rieng=kq["co_ten_rieng"]):        # cach-lam, /vai, /chung (1b-3): luật do người gọi
        hd = {i: "giu_ca_hai" if h == "gop" else h for i, h in hd.items()}   # câu gộp chạm nghiệp vụ: bỏ gộp
    gop_tu = tuple(k for k in ung_vien if hd[k.id] == "gop")
    return KetQuaGop(cau_gop if gop_tu else noi_dung_moi, tuple(k.id for k in ung_vien if hd[k.id] != "giu_ca_hai"),
                     gop_tu)
