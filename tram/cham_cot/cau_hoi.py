"""Câu hỏi cần chốt cho bead mà luật cứng đã xếp cột 2 (spec 0+1a §5.2 bước 4–5).

Đầu ra của LLM chế độ rút gọn chỉ có `cau_hoi_can_chot` — không có `cot`, nên LLM không đổi được cột.
LLM lỗi → câu hỏi dự phòng theo mẫu cố định, để cột 2 luôn có câu hỏi.
"""
from pydantic import BaseModel, ConfigDict

from tram.cham_cot.luat_cung import KetQuaLuat
from tram.llm.claude import DauRa

SO_CAU_TOI_DA = 3
DO_DAI_CAU_TOI_DA = 300


class CauHoiChot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cau_hoi_can_chot: list[str]


SCHEMA_CAU_HOI: dict = {
    "type": "object",
    "properties": {"cau_hoi_can_chot": {"type": "array", "items": {"type": "string"}}},
    "required": ["cau_hoi_can_chot"],
    "additionalProperties": False,
}


def loi_cau_hoi(kq: CauHoiChot) -> list[str]:
    loi: list[str] = []
    ds = kq.cau_hoi_can_chot
    if not 1 <= len(ds) <= SO_CAU_TOI_DA:
        loi.append(f"cau_hoi_can_chot phải có từ 1 đến {SO_CAU_TOI_DA} câu")
    if any(not q.strip() for q in ds):
        loi.append("câu hỏi không được rỗng")
    if any(len(q) > DO_DAI_CAU_TOI_DA for q in ds):
        loi.append(f"mỗi câu hỏi tối đa {DO_DAI_CAU_TOI_DA} ký tự")
    return loi


DAU_RA_CAU_HOI = DauRa(CauHoiChot, SCHEMA_CAU_HOI, loi_cau_hoi, max_tokens=1024, effort="low")

MAU_DU_PHONG = {
    "tien": "Việc này chạm tiền, giá hoặc thuế ({chi_tiet}). Đại ca chốt quy tắc tính: công thức, làm tròn, "
            "thời điểm áp dụng?",
    "schema": "Việc này đổi cấu trúc dữ liệu ({chi_tiet}). Đại ca có duyệt thay đổi schema này không, và dữ liệu "
              "thật được chuyển thế nào?",
    "quyen": "Việc này chạm phân quyền hoặc bảo mật ({chi_tiet}). Sau thay đổi, vai trò nào được làm gì?",
    "khach_thay": "Việc này đổi thứ khách nhìn thấy ({chi_tiet}). Đại ca duyệt nội dung hiển thị cuối cho khách "
                  "ở đâu, khi nào?",
}
MAU_CHUNG = "Việc này chạm hàng rào {loai} ({chi_tiet}). Đại ca chốt cách làm được phép là gì?"
MAU_DECISION = "Đại ca chốt quyết định này: {tieu_de}"
CAU_CUOI = "Đại ca chốt phạm vi và cách làm của việc này?"


def cau_hoi_du_phong(luat: KetQuaLuat, tieu_de: str = "") -> list[str]:
    """Mẫu cố định theo từng loại hàng rào đã chạm; decision mở → hỏi chốt chính decision. Không bao giờ rỗng."""
    if luat.la_decision_mo:
        return [MAU_DECISION.format(tieu_de=" ".join(tieu_de.split())[:200] or "(không tiêu đề)")]
    cau = []
    for c in luat.cham:  # dạng "<loai> (<chi tiết>)" — luat_cung._cham_loai
        loai, _, chi_tiet = c.partition(" (")
        cau.append(MAU_DU_PHONG.get(loai, MAU_CHUNG).format(loai=loai, chi_tiet=chi_tiet.removesuffix(")")))
    return cau or [CAU_CUOI]
