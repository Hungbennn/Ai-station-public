"""Kiểm khối bàn giao ở mức CẤU TRÚC (spec 3 §7.4 bước 1) — dùng ở `tram bao`, ở thợ khi đọc hàng đợi và ở trạm
khi nhận `bao`. Luật `chinh-thuc` đầy đủ KHÔNG kiểm ở đây (`lenh_kiem[]` do thợ điền sau — §7.5)."""
import json

from pydantic import ValidationError

from tram.ban_giao.schema import GIOI_HAN_BYTE, BanGiao


class LoiCauTruc(ValueError):
    pass


def kiem_cau_truc(khoi: object, *, can_chinh_thuc: bool) -> BanGiao:
    if not isinstance(khoi, dict):
        raise LoiCauTruc("Khối bàn giao phải là một JSON object")
    if len(json.dumps(khoi, ensure_ascii=False).encode()) > GIOI_HAN_BYTE:
        raise LoiCauTruc("Khối bàn giao vượt 64 KB")
    try:
        bg = BanGiao.model_validate(khoi)
    except ValidationError as e:
        loi = "; ".join(f"{'.'.join(map(str, x['loc'])) or 'khoi'}: {x['msg']}" for x in e.errors()[:5])
        raise LoiCauTruc(f"Khối bàn giao sai schema: {loi}") from None
    if can_chinh_thuc and bg.loai != "chinh-thuc":
        raise LoiCauTruc("Báo xong phải kèm bàn giao loai 'chinh-thuc'")
    if bg.loai == "chinh-thuc" and not bg.file_ban_giao.strip():
        raise LoiCauTruc("Bàn giao chính thức phải điền file_ban_giao")
    if bg.loai == "tam" and (not bg.nhanh or not bg.buoc_tiep):
        raise LoiCauTruc("Bàn giao tạm phải có nhanh và buoc_tiep")
    return bg
