"""Vào cột 3 khi chạy thật (4a-2) — trước `vao_cot_3` của 4a-1 kiểm thêm hai điều mà pha Git dài có thể làm cũ:

1. Ref công bố TRÊN REMOTE (kho kiểm vừa `git fetch` đầu pha) đúng bằng commit trong `giao.cong_bo` mới nhất (3a-2
   công bố bằng CAS). Khác = nhánh bị đẩy ngoài luồng → không vào cột 3, escalation `nhanh-bi-day` (G10: PR Đại ca
   tạo từ `tram/<bead>` phải trỏ đúng commit trạm đã kiểm). Một escalation mỗi (chu kỳ ngân sách, SHA remote).
2. Đọc lại bead và sự kiện ngay trước khi ghi nhãn: bead có thể đã bị kéo, bị chặn trong lúc kiểm lại bead khác.
   Điều kiện 8 xét trên feature cha của bản vừa đọc (TM-2, Codex Q3): thiếu tập "spec đã merge" thì con của feature
   `theo-plan` không bao giờ vào cột 3."""
from datetime import datetime
from pathlib import Path

from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.bang_chung import vao_cot_3
from tram.giao_viec.co_nguon import chan_buoc
from tram.giao_viec.dieu_kien import ly_do_khong_giao
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.git_kiem import sha_cua
from tram.giao_viec.ngan_sach import bat_dau_chu_ky
from tram.giao_viec.pipeline import buoc_ke_tiep
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.su_kien import moi_nhat, su_kien_bead
from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
from tram.phieu.kho import KhoPhieu


def ten_nhanh(ref: str) -> str:
    return ref.removeprefix("refs/heads/")


def vao_cot_3_an_toan(bd, kho: KhoPhieu, kg: Path, da: DuAn, b, luc: datetime, *, gitnexus=None) -> str | None:
    ds = su_kien_bead(kho, da.ten, b.id)
    cb = moi_nhat(ds, "giao.cong_bo")
    if cb is None:
        return None
    tu_xa = sha_cua(kg, f"origin/{ten_nhanh(cb.du_lieu['ref'])}")
    if tu_xa != cb.du_lieu["commit"]:
        cau = (f"Nhánh {cb.du_lieu['ref']} trên remote đang ở {tu_xa or '(không có)'}, khác commit trạm đã công bố "
               f"{cb.du_lieu['commit']}. Đưa nhánh về đúng commit (hoặc trả bead về cột 1) rồi trả lời.")
        return "nhanh_bi_day" if tao_escalation(bd, kho, da.ten, b, ly_do="nhanh-bi-day", cau_hoi=cau, giao_id=None,
                                                 nguon=f"ref-{bat_dau_chu_ky(ds)}-{tu_xa or 'mat'}", luc=luc) else None
    try:
        theo_id = {x.id: x for x in bd.tat_ca()}
    except LoiBd:
        return None
    moi = theo_id.get(b.id)
    merge = feature_da_merge(kho, da, [theo_id[moi.parent]], kg) if moi and moi.parent in theo_id else frozenset()
    if moi is None or ly_do_khong_giao(moi, theo_id, set(), da, merge) is not None or buoc_ke_tiep(
            ds, trang_thai_bead(kho, da.ten, moi, theo_id, viec_ton_cua(kho, da.ten))) != "cot_3":
        return None
    if chan_buoc(kho, da, moi, theo_id, kg, luc):
        return None
    return "cot_3" if vao_cot_3(bd, kho, kg, da, moi, ds, la_spike=moi.issue_type == "spike",
                               luc=luc, gitnexus=gitnexus) else None
