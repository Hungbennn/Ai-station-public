"""Gói ngữ cảnh lớp 1–5 (spec 4 §11; lớp 5 + luồng gitnexus từ 4c) — markdown, cố định trước, hay đổi sau.
Lớp 3, 4 là dữ liệu không tin cậy: bọc bằng `boc_khong_tin_cay` của 1a. Vượt ngân sách 60.000 token (ước 2,5 ký
tự/token): cắt lớp 4 — bỏ `doi_chieu_nghiem_thu`, `lenh_kiem` của các bàn giao → bỏ bàn giao phụ thuộc cũ nhất →
cắt diff QC theo file → bỏ phần tuỳ chọn của 4c (luồng gitnexus, lớp 5)."""
import json
from dataclasses import dataclass, replace

from tram.beads.mo_hinh import Bead
from tram.cham_cot.prompt import boc_khong_tin_cay
from tram.giao_viec.lop_5 import Lop5, van_ban_lop_5

TOKEN_TOI_DA = 60_000
KY_TU_MOI_TOKEN = 2.5
BO_KHI_GON = ("doi_chieu_nghiem_thu", "lenh_kiem")
HUONG_DAN_CHUNG = """### Hướng dẫn chung của trạm
- Báo trạm bằng `tram bao --moc | --can-hoi --loai can_quyet_dinh|thao_tac_nguy_hiem | --bi | --xong --ban-giao <file>`.
- Ghi tiến độ vào `.tram/tien-do.md` (không commit) sau mỗi bước đáng kể.
- Bàn giao đúng schema khối `<!-- ban-giao -->` (phien_ban 1, loai `chinh-thuc`, `file_ban_giao` dưới `docs/handovers/`).
- Chép NGUYÊN VĂN từng dòng "Tiêu chí của phiếu" ở lớp 3 vào `doi_chieu_nghiem_thu[].tieu_chi` — trạm so từng ký tự.
- Phiếu `qc`: thêm khối `<!-- qc -->` có `commit_code` đúng như lớp 4."""


@dataclass(frozen=True)
class Lop4:
    ban_giao_phu_thuoc: tuple[tuple[str, dict], ...] = ()     # (bead_id, khối) — cũ → mới
    ban_giao_tam: dict | None = None
    ban_giao_code: dict | None = None                         # phiếu qc: bàn giao của bước code
    loi_ban_giao: tuple[str, ...] = ()
    kiem_lai: dict | None = None
    phat_hien_qc: tuple[dict, ...] = ()
    gop_y: tuple[str, ...] = ()
    tra_loi: tuple[str, ...] = ()
    commit_code: str | None = None
    diff_qc: tuple[tuple[str, str], ...] = ()
    da_cat: int = 0


@dataclass(frozen=True)
class DauVaoGoi:
    tai_lieu: tuple[tuple[str, str], ...]     # lớp 1: (đường dẫn, nội dung) tại origin/<nhanh_chinh>
    vai: tuple[str, str, str]                 # (tên vai, phiên bản, thân)
    bead: Bead
    buoc: str
    tieu_chi: tuple[str, ...]
    lenh_kiem: tuple[str, ...]
    lop_4: Lop4
    lop_5: Lop5 | None = None                 # None: chưa bật (trước 4c)
    luong: str = ""                           # lớp 1: luồng liên quan từ gitnexus, đã bọc dữ liệu không tin cậy
    de_nghi: str = ""                         # lớp 2: hướng dẫn tự cập nhật việc (TC) — rỗng khi tắt


def _gon(bg: dict | None) -> dict | None:
    return None if bg is None else {k: v for k, v in bg.items() if k not in BO_KHI_GON}


def _lop_4(l: Lop4) -> str:
    phan = {k: v for k, v in (
        ("ban_giao_phu_thuoc", [{"bead": i, "ban_giao": bg} for i, bg in l.ban_giao_phu_thuoc]),
        ("ban_giao_tam_gan_nhat", l.ban_giao_tam), ("ban_giao_buoc_code", l.ban_giao_code),
        ("loi_ban_giao_lan_truoc", list(l.loi_ban_giao)), ("ket_qua_kiem_lai", l.kiem_lai),
        ("phat_hien_qc", list(l.phat_hien_qc)), ("gop_y_tra_ve", list(l.gop_y)),
        ("tra_loi_escalation", list(l.tra_loi)), ("commit_code", l.commit_code)) if v}
    van_ban = json.dumps(phan, ensure_ascii=False, indent=1) if phan else "(không có)"
    if l.diff_qc or l.da_cat:
        van_ban += "\n\nDiff tới commit_code:\n" + "\n".join(d for _, d in l.diff_qc)
        van_ban += f"\n(đã cắt {l.da_cat} file diff vì vượt ngân sách gói)" if l.da_cat else ""
    return boc_khong_tin_cay(van_ban)


def _ghep(d: DauVaoGoi, l4: Lop4) -> str:
    b, (ten, pb, than) = d.bead, d.vai
    lop1 = "\n\n".join(f"### {p}\n{nd.strip()}" for p, nd in d.tai_lieu) or "(không có tài liệu dự án)"
    lop1 += f"\n\n### Luồng liên quan (gitnexus)\n{d.luong}" if d.luong else ""
    lenh = "\n".join(f"- `{x}`" for x in d.lenh_kiem) or "- (không có — phiếu này không chạy lệnh kiểm)"
    task = json.dumps({"id": b.id, "loai": b.issue_type, "tieu_de": b.title, "mo_ta": b.description,
                       "acceptance_criteria": b.acceptance_criteria, "design": b.design}, ensure_ascii=False,
                      indent=1)
    tieu_chi = "\n".join(f"- {t}" for t in d.tieu_chi)
    return "\n\n".join([
        f"# Gói ngữ cảnh — {b.id}, bước {d.buoc}", f"## Lớp 1 — Dự án (tại nhánh chính)\n{lop1}",
        f"## Lớp 2 — Vai {ten} (phiên bản {pb})\n{than.strip()}\n\n{HUONG_DAN_CHUNG}\n\n"
        + (f"{d.de_nghi}\n\n" if d.de_nghi else "") + f"### Lệnh bắt buộc của phiếu (trạm chạy lại)\n{lenh}",
        f"## Lớp 3 — Task\n{boc_khong_tin_cay(task)}\n\n### Tiêu chí của phiếu\n{boc_khong_tin_cay(tieu_chi)}",
        f"## Lớp 4 — Đầu vào tường minh\n{_lop_4(l4)}", van_ban_lop_5(d.lop_5)])


class GoiQuaLon(ValueError):
    """Phần ngữ cảnh bắt buộc vẫn vượt ngân sách sau khi đã rút phần được phép."""


def dung_goi(d: DauVaoGoi, toi_da_ky_tu: int = int(TOKEN_TOI_DA * KY_TU_MOI_TOKEN)) -> str:
    l4 = d.lop_4
    goi = _ghep(d, l4)
    if len(goi) > toi_da_ky_tu:
        l4 = replace(l4, ban_giao_phu_thuoc=tuple((i, _gon(bg)) for i, bg in l4.ban_giao_phu_thuoc),
                     ban_giao_tam=_gon(l4.ban_giao_tam), ban_giao_code=_gon(l4.ban_giao_code))
        goi = _ghep(d, l4)
    while len(goi) > toi_da_ky_tu and l4.ban_giao_phu_thuoc:
        l4 = replace(l4, ban_giao_phu_thuoc=l4.ban_giao_phu_thuoc[1:])
        goi = _ghep(d, l4)
    while len(goi) > toi_da_ky_tu and l4.diff_qc:
        l4 = replace(l4, diff_qc=l4.diff_qc[:-1], da_cat=l4.da_cat + 1)
        goi = _ghep(d, l4)
    if len(goi) > toi_da_ky_tu and (d.luong or (d.lop_5 is not None and not d.lop_5.da_cat)):
        d = replace(d, luong="", lop_5=None if d.lop_5 is None else Lop5(da_cat=True))
        goi = _ghep(d, l4)
    if len(goi) > toi_da_ky_tu:
        raise GoiQuaLon("Gói ngữ cảnh vượt ngân sách; không cấp phiếu")
    return goi
