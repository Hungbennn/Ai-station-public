"""Luồng feature (spec 4 §4, §6.6 "Với feature", §7, §8 đợt sửa spec) — tính lúc đọc từ sự kiện (Q12).

Feature đi `can-spec` → bước `spec` → (trạm xét `bao.xong`) → `cho-duyet-spec` → Đại ca Duyệt (`theo-plan`, tạo bead
con) hoặc Trả về (`spec.tra_ve`, lại `can-spec`). Cửa sổ của một vòng spec = sự kiện sau `spec.tra_ve` gần nhất.
Đợt sửa spec: đếm `spec.tra_ve` sau `ngan_sach.dot_spec_moi` gần nhất; đạt `TRA_VE_SPEC_TOI_DA` thì không giao
`spec` nữa — vòng tick tạo escalation `spec-tra-ve-nhieu`; Đại ca trả lời escalation đó mới mở đợt mới."""
from typing import Literal

from tram.beads.mo_hinh import Bead
from tram.giao_viec.phieu_yeu_cau import doc_phieu
from tram.giao_viec.pipeline import TrangThaiBead
from tram.giao_viec.su_kien import SK, moi_nhat

NHAN_CAN_SPEC, NHAN_CHO_DUYET, NHAN_THEO_PLAN = "can-spec", "cho-duyet-spec", "theo-plan"
TRA_VE_SPEC_TOI_DA = 2
BuocFeature = Literal["spec", "chuyen_duyet", "cho"]


def cua_so_spec(ds: list[SK]) -> list[SK]:
    tv = moi_nhat(ds, "spec.tra_ve")
    return [s for s in ds if tv is None or s.id > tv.id]


def spec_xong_hop_le(w: list[SK]) -> SK | None:
    """`giao.ket_thuc` của phiếu `spec` mới nhất trong cửa sổ nếu trạm đã xét `bao.xong` là hợp lệ."""
    n = moi_nhat(w, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "spec")
    kt = n and moi_nhat(w, "giao.ket_thuc", lambda s: s.du_lieu.get("giao_id") == n.du_lieu["giao_id"])
    if not kt or kt.du_lieu.get("ket_thuc") != "xong" or kt.du_lieu.get("ly_do") is not None:
        return None
    return kt if kt.du_lieu.get("commit") else None


def buoc_feature(ds: list[SK], tt: TrangThaiBead) -> BuocFeature:
    """Feature đang `can-spec`: `cho` (phiếu hiệu lực, bị chặn, công việc tồn) · `chuyen_duyet` (spec vừa xong hợp lệ
    — tick ghi `spec.xong` rồi đổi nhãn) · `spec` (chưa có, hoặc lượt trước lỗi/bí/thu hồi, hoặc sau trả về)."""
    if tt.co_phieu or tt.bi_chan or tt.cong_viec_ton:
        return "cho"
    return "chuyen_duyet" if spec_xong_hop_le(cua_so_spec(ds)) else "spec"


def bat_dau_dot(ds: list[SK]) -> int:
    s = moi_nhat(ds, "ngan_sach.dot_spec_moi")
    return s.id if s else 0


def dem_tra_ve_dot(ds: list[SK]) -> int:
    tu = bat_dau_dot(ds)
    return sum(1 for s in ds if s.loai == "spec.tra_ve" and s.id > tu)


def con_dot_spec(ds: list[SK]) -> bool:
    return dem_tra_ve_dot(ds) < TRA_VE_SPEC_TOI_DA


def ly_do_khong_giao_spec(bead: Bead, san_sang: set[str], du_an: str) -> str | None:
    """Spec 4 §5.1 "Bead feature": `can-spec`, phiếu yêu cầu hợp lệ, `open`, nằm trong `bd ready` (escalation chặn
    feature thì không giao lại). Điều kiện 5–7 (phiếu hiệu lực, ngân sách, khoá) kiểm ở bộ chọn và phần 3."""
    if bead.issue_type != "feature":
        return "loai-khong-giao"
    if any(n.startswith("cot:") for n in bead.labels):
        return "nhan-lech"                       # feature trong luồng không mang nhãn cột (spec 2 §5.1)
    if NHAN_CAN_SPEC not in bead.labels or {NHAN_CHO_DUYET, NHAN_THEO_PLAN} & set(bead.labels):
        return "khong-can-spec"
    if bead.status != "open":
        return "trang-thai"
    if bead.id not in san_sang:
        return "bi-chan"
    if doc_phieu(bead.description, du_an)[0] is None:
        return "phieu-thieu"
    return None
