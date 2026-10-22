"""Bộ lọc nội dung đề nghị của agent (change agent-tu-cap-nhat-viec, design D-3, D106) — MỘT hàm thuần, ba chỗ gọi:
`tram bao` (agent thấy lỗi ngay), hàng đợi phía thợ (agent có thể ghi thẳng file) và `nhan_bao` của trạm — chỗ DUY
NHẤT quyết định. Dừng ở lỗi đầu tiên: cấu trúc → loại việc → độ dài → ký tự điều khiển → dấu dành riêng → bí mật
(`tram.nho.bi_mat.quet` — chỉ gọi, không sửa luật quét). Lỗi chỉ mang mã lý do (+ nhóm và số lượng khi có bí mật),
không bao giờ chép chữ của agent (INV-001)."""
import unicodedata
from dataclasses import dataclass, field

from tram.cham_cot.prompt import THE_RE
from tram.nho.bi_mat import quet

LOAI_DE_NGHI = ("tien_do", "viec_moi")
LOAI_VIEC = ("bug", "task", "chore")                                             # D104
GIOI_HAN = {"tien_do": 1000, "ly_do": 2000, "tieu_de": 200, "mo_ta": 4000, "tieu_chi": 2000}   # D106
TRUONG_VIEC = frozenset({"tieu_de", "mo_ta", "loai_viec", "tieu_chi"})
CAN_VIEC = frozenset({"tieu_de", "mo_ta", "loai_viec"})
KHONG_DI_KEM = ("ban_giao", "commit", "loai_hoi", "ly_do", "loi_ban_giao")       # trường của các loại báo khác
VO_HINH = frozenset({*range(0x200B, 0x2010), *range(0x202A, 0x202F), *range(0x2060, 0x206A), 0xFEFF})
THAY_BI_MAT = "Agent báo bị chặn; lý do bị trạm giữ lại vì có dấu hiệu bí mật"
THAY_KY_TU = "Agent báo bị chặn; lý do bị trạm giữ lại vì có ký tự hoặc dấu không cho phép"
DA_CAT = " (đã cắt)"


@dataclass(frozen=True)
class LoiLoc:
    ly_do: str          # cau-truc | loai-viec-sai | qua-dai | ky-tu-dieu-khien | dau-danh-rieng | co-bi-mat
    nhom: dict = field(default_factory=dict)        # chỉ khi co-bi-mat: nhóm dấu hiệu → số lượng


def ky_tu_cam(s: str, *, mot_dong: bool) -> bool:
    """Nhóm Cc (trừ xuống dòng, tab — tiêu đề cấm cả hai) và ký tự vô hình / đảo chiều chữ."""
    return any(ord(c) in VO_HINH or (unicodedata.category(c) == "Cc" and (mot_dong or c not in "\n\t")) for c in s)


def dau_rieng(s: str) -> bool:
    """Dấu trạm tự dùng: chú thích HTML (khối bàn giao, dấu mã thao tác) và thẻ bọc dữ liệu không tin cậy."""
    return "<!--" in s or "-->" in s or THE_RE.search(s) is not None


def _chu(loai: str, d: dict) -> dict[str, str] | None:
    """Các trường chữ (tên giới hạn → giá trị) nếu đúng cấu trúc; None = sai cấu trúc."""
    if any(d.get(k) for k in KHONG_DI_KEM):
        return None
    if loai == "tien_do":
        nd = d.get("noi_dung")
        return {"tien_do": nd} if d.get("viec_moi") is None and isinstance(nd, str) and nd.strip() else None
    vm = d.get("viec_moi")
    if d.get("noi_dung") or not isinstance(vm, dict) or set(vm) - TRUONG_VIEC or not CAN_VIEC <= set(vm):
        return None
    chu = {k: vm.get(k, "") for k in ("tieu_de", "mo_ta", "tieu_chi")}
    if not all(isinstance(v, str) for v in (*chu.values(), vm["loai_viec"])):
        return None
    if not chu["tieu_de"].strip() or chu["tieu_de"].lstrip().startswith("-") or not chu["mo_ta"].strip():
        return None                                 # tiêu đề đi qua argv của `bd create`: không bắt đầu bằng "-"
    return chu


def loc(loai: str, d: dict) -> LoiLoc | None:
    """`d` = dòng hàng đợi hoặc thân `POST /api/tho/bao` (trường của loại báo khác → cấu trúc). None = nhận."""
    if loai not in LOAI_DE_NGHI or (chu := _chu(loai, d)) is None:
        return LoiLoc("cau-truc")
    if loai == "viec_moi" and d["viec_moi"]["loai_viec"] not in LOAI_VIEC:
        return LoiLoc("loai-viec-sai")
    if any(len(v) > GIOI_HAN[k] for k, v in chu.items()):
        return LoiLoc("qua-dai")
    if any(ky_tu_cam(v, mot_dong=k == "tieu_de") for k, v in chu.items()):
        return LoiLoc("ky-tu-dieu-khien")
    if any(dau_rieng(v) for v in chu.values()):
        return LoiLoc("dau-danh-rieng")
    if nhom := quet(chu.values()):
        return LoiLoc("co-bi-mat", nhom)
    return None


def ly_do_bi_chan(s: str) -> str:
    """Bị chặn (D-3, D102): báo bí / cần hỏi không bị từ chối — lý do không qua lọc được THAY bằng câu của trạm; quá
    2.000 ký tự thì cắt, ghi "(đã cắt)". Quét bí mật trên bản gốc chưa cắt."""
    if quet([s]):
        return THAY_BI_MAT
    if ky_tu_cam(s, mot_dong=False) or dau_rieng(s):
        return THAY_KY_TU
    s = s.strip()
    return s if len(s) <= GIOI_HAN["ly_do"] else s[:GIOI_HAN["ly_do"] - len(DA_CAT)] + DA_CAT
