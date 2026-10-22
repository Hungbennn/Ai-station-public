"""Điểm vào DUY NHẤT đọc nguồn ký ức từ một sự kiện (spec 1b §6.1) — vòng nạp, `la_nguon`, `tram nho thu`.

1a/2a và agent (`nguon.doc_dau_vao` — chỉ cần sự kiện); phần 4 (cần tra kho sự kiện: `qc.ket_qua` → `kiem.lai` →
`bao.xong`, `giao.nhan`). None: không phải nguồn (mốc tiến). ValueError: sự kiện độc (`nho.loi_tach`, bỏ, mốc tiến)."""
import re

from tram.nho.nguon import DauVao, doc_dau_vao
from tram.nho.nguon_ban_giao import doc_ban_giao
from tram.nho.nguon_giao_viec import doc_escalation_dong, doc_spec_tra_ve
from tram.nho.pham_vi import TEN
from tram.su_kien.kho import KhoSuKien, SuKien

LOAI_PHAN_4 = ("kiem.lai", "qc.ket_qua", "escalation.dong", "spec.tra_ve")


def doc_nguon(sk: SuKien, kho_sk: KhoSuKien) -> DauVao | None:
    if sk.loai not in LOAI_PHAN_4:
        return doc_dau_vao(sk)
    if not re.fullmatch(TEN, sk.du_an or "") or not isinstance(sk.du_lieu, dict):
        return None                                        # `_tram`, tên sai dạng: không phải nguồn
    if sk.loai in ("kiem.lai", "qc.ket_qua"):                # D8: bàn giao sau QC đạt; spike sau kiểm lại
        return doc_ban_giao(sk, kho_sk)
    return doc_escalation_dong(sk) if sk.loai == "escalation.dong" else doc_spec_tra_ve(sk)
