"""Nguồn ký ức từ chữ của Đại ca trong luồng giao việc (spec 1b §6.1): `escalation.dong`, `spec.tra_ve`.

- `escalation.dong {escalation_id, bead_goc, giao_id, ly_do, tra_loi}` (bộ giao việc ghi khi decision
  `tram:escalation` đóng; `tra_loi` = close_reason Đại ca viết) → nguồn `da_chot`, luôn `nghiep-vu`, sàn 0,8.
  CHỈ dùng `tra_loi` và `ly_do` (mã trạm đặt). Câu hỏi gốc (`bao.can_hoi`, `bao.bi` — agent viết) KHÔNG đưa vào:
  ký ức nguồn Đại ca được bảo vệ khỏi gộp/thay nên không được mang chữ của agent.
- `spec.tra_ve {gop_y, ma_thao_tac}` (dashboard ghi khi Đại ca trả về spec của feature) → nguồn `tra_ve`, sàn 0,6.
Sai tác nhân → None (không phải nguồn, mốc tiến). Dữ liệu sai kiểu → ValueError (sự kiện độc). Mọi trường chữ được
quét bí mật (D23) trước khi dựng văn bản: có dấu hiệu → `LoiBiMat` (bỏ cả nguồn, `nho.bo_bi_mat`)."""
import re

from tram.giao_viec.su_kien import TAC_NHAN as TAC_NHAN_GIAO_VIEC
from tram.nho.bi_mat import chan_bi_mat
from tram.nho.nguon import DauVao, _cat_dong
from tram.nho.pham_vi import TEN
from tram.su_kien.kho import SuKien
from tram.thao_tac.chung import TAC_NHAN as TAC_NHAN_DASHBOARD


def _chuoi(d: dict, khoa: str, loai: str) -> str:
    v = d.get(khoa)
    if v is not None and not isinstance(v, str):
        raise ValueError(f"{loai}: {khoa} phải là chuỗi")
    return (v or "").strip()


def doc_escalation_dong(sk: SuKien) -> DauVao | None:
    if sk.tac_nhan != TAC_NHAN_GIAO_VIEC:
        return None
    eid, tra_loi = _chuoi(sk.du_lieu, "escalation_id", sk.loai), _chuoi(sk.du_lieu, "tra_loi", sk.loai)
    if not eid or not sk.bead_id:
        raise ValueError("escalation.dong: thiếu escalation_id hoặc bead_id")
    if not tra_loi:
        return None                                        # đóng không kèm câu trả lời: không có gì để nhớ
    ly_do = _chuoi(sk.du_lieu, "ly_do", sk.loai)
    chan_bi_mat("da_chot", [eid, tra_loi, ly_do])          # D23: bản gốc, cả ly_do sắp bị thay bằng "không rõ"
    ly_do = ly_do if re.fullmatch(TEN, ly_do) else "không rõ"
    dong = [f"Đại ca trả lời escalation {eid} của bead {sk.bead_id} (lý do trạm chuyển lên: {ly_do}), "
            f"ngày {sk.luc[:10]}:", tra_loi]
    return DauVao(sk.id, sk.du_an, sk.bead_id, "da_chot", van_ban=_cat_dong(dong), ep_nghiep_vu=True, luc=sk.luc)


def doc_spec_tra_ve(sk: SuKien) -> DauVao | None:
    if sk.tac_nhan != TAC_NHAN_DASHBOARD:
        return None
    gop_y = _chuoi(sk.du_lieu, "gop_y", sk.loai)
    if not sk.bead_id:
        raise ValueError("spec.tra_ve: thiếu bead_id")
    if not gop_y:
        return None
    chan_bi_mat("tra_ve", [gop_y])                         # D23
    dong = [f"Đại ca trả về spec của feature {sk.bead_id} ngày {sk.luc[:10]} với góp ý:", gop_y]
    return DauVao(sk.id, sk.du_an, sk.bead_id, "tra_ve", van_ban=_cat_dong(dong), luc=sk.luc)
