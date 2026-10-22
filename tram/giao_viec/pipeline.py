"""Bước kế tiếp của bead bug/task/chore/spike (spec 4 §4, §6.6) — tính lúc đọc từ sự kiện (Q12), không lưu.

Sự kiện dùng (cửa sổ = kể từ `cot.tra_ve` gần nhất): `giao.nhan` (phần 3), `giao.ket_thuc` (phần 4 — kết luận
xét `bao.xong`: `ly_do` None = hợp lệ, `commit` = SHA công bố của lượt), `kiem.lai`, `qc.ket_qua`, `giao.cong_bo`
(ref công bố — mọi thời điểm, không cắt cửa sổ)."""
from dataclasses import dataclass
from typing import Literal

from tram.giao_viec.su_kien import SK, cua_so, moi_nhat, ref_cong_bo

Buoc = Literal["code", "kiem_lai", "qc", "cot_3", "cho"]


@dataclass(frozen=True)
class TrangThaiBead:
    co_phieu: bool          # phiếu hiệu lực (phần 3)
    bi_chan: bool           # phụ thuộc `blocks` chưa đóng — gồm escalation mở (fail-closed)
    cong_viec_ton: bool     # công việc chờ của phần 3 chưa xử lý xong
    cho_review: bool        # bead có `cot:cho-review`
    digest_tieu_chi: str    # digest tiêu chí HIỆN TẠI của bead
    la_spike: bool


def sha_code_hop_le(w: list[SK]) -> str | None:
    """SHA công bố của phiếu `code` mới nhất nếu `bao.xong` của nó được xét hợp lệ; ngược lại None."""
    code = moi_nhat(w, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
    if code is None:
        return None
    kt = moi_nhat(w, "giao.ket_thuc", lambda s: s.du_lieu.get("giao_id") == code.du_lieu["giao_id"])
    if kt is None or kt.du_lieu.get("ket_thuc") != "xong" or kt.du_lieu.get("ly_do") is not None:
        return None
    return kt.du_lieu.get("commit")


def _qc_chua_ket_qua(w: list[SK], kl: SK) -> bool:
    """Công bố mới nhất thuộc đúng QC mới nhất, sau kiểm lại và đã kết thúc chưa có kết luận."""
    q = moi_nhat(w, "giao.nhan", lambda s: s.id > kl.id and s.du_lieu.get("buoc") == "qc")
    cb = moi_nhat(w, "giao.cong_bo")
    if q is None or cb is None or cb.id <= q.id or cb.du_lieu.get("luot") != q.du_lieu.get("luot"):
        return False
    kt = moi_nhat(w, "giao.ket_thuc", lambda s: s.id > cb.id
                  and s.du_lieu.get("giao_id") == q.du_lieu.get("giao_id")
                  and s.du_lieu.get("luot") == q.du_lieu.get("luot"))
    return kt is not None and kt.du_lieu.get("ket_thuc") in {"thu_hoi", "het_han_muc", "bi"}


def buoc_ke_tiep(ds: list[SK], tt: TrangThaiBead) -> Buoc:
    if tt.co_phieu or tt.bi_chan or tt.cong_viec_ton or tt.cho_review:          # dòng 1, 2
        return "cho"
    w, ref = cua_so(ds), ref_cong_bo(ds)
    code = moi_nhat(w, "giao.nhan", lambda e: e.du_lieu.get("buoc") == "code")
    lai = moi_nhat(w, "co.can-code-lai")
    if code and lai and lai.id > code.id and lai.du_lieu.get("giao_id") == code.du_lieu["giao_id"]:
        return "code"
    sha = sha_code_hop_le(w)
    kl = moi_nhat(w, "kiem.lai", lambda e: code is not None
                  and e.du_lieu.get("giao_id") == code.du_lieu["giao_id"]
                  and e.du_lieu.get("luot") == code.du_lieu["luot"])
    qk = moi_nhat(w, "qc.ket_qua", lambda e: kl is not None and e.id > kl.id)
    kl_dung = (kl is not None and sha is not None and kl.du_lieu["commit"] == sha
               and kl.du_lieu["dat"] and kl.du_lieu["digest_tieu_chi"] == tt.digest_tieu_chi)
    if (kl_dung and qk is not None and qk.du_lieu["ket_luan"] == "dat"                 # dòng 3
            and qk.du_lieu["commit_code"] == kl.du_lieu["commit"] and ref == qk.du_lieu["commit_qc"]):
        return "cot_3"
    if (kl_dung and sha is not None and kl.du_lieu["commit"] == sha and ref == sha     # dòng 4
            and qk is None):
        return "cot_3" if tt.la_spike and not code.du_lieu.get("co") else "qc"
    if kl_dung and qk is None and not tt.la_spike and _qc_chua_ket_qua(w, kl):
        return "qc"
    if sha is not None and kl is None:   # dòng 5
        return "kiem_lai"
    return "code"                                                                      # dòng 6
