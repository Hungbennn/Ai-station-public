import re
from pathlib import Path
from typing import Literal

from pydantic import ValidationError, field_validator

from tram.ban_giao.file_ban_giao import loi_duong_dan, loi_tai_commit, loi_tren_dia
from tram.ban_giao.mo_hinh import DoiChieu, HuongDaBo, LenhKiem, Nghiem

GIOI_HAN_BYTE = 64 * 1024
KHOI_RE = re.compile(r"<!-- ban-giao -->\s*(\{.*?\})\s*<!-- ban-giao -->", re.S)
PR_RE = re.compile(r"https?://[^\s/]+/\S+")


class BanGiao(Nghiem):
    phien_ban: Literal[1]
    loai: Literal["chinh-thuc", "tam"]
    luot: int
    file_ban_giao: str
    nhanh: str
    commit: str | None
    pr: str | None = None  # URL PR hoặc null; bàn giao cũ không có trường này vẫn hợp lệ
    doi_chieu_nghiem_thu: list[DoiChieu]
    lenh_kiem: list[LenhKiem]
    quyet_dinh: list[str]
    huong_da_bo: list[HuongDaBo]
    vuong_mac: list[str]
    buoc_tiep: list[str]
    cau_hoi_mo: list[str]
    thay_doi_vung_nhay_cam: list[str]

    @field_validator("pr")
    @classmethod
    def _pr_la_url(cls, v: str | None) -> str | None:
        if v is not None and not PR_RE.fullmatch(v):
            raise ValueError("pr phải là URL http(s) có đường dẫn, hoặc null")
        return v


def _loi_file(bg: BanGiao, goc: Path, commit: str | None) -> str | None:
    loi = loi_duong_dan(bg.file_ban_giao)
    if loi is None:
        loi = loi_tai_commit(goc, commit, bg.file_ban_giao) if commit else loi_tren_dia(goc, bg.file_ban_giao)
    return loi


def _loi_doi_chieu(bg: BanGiao, tieu_chi: list[str], la_qc: bool, ket_luan_qc: str | None) -> list[str]:
    loi = []
    for t in dict.fromkeys(tieu_chi):
        dong = [d for d in bg.doi_chieu_nghiem_thu if d.tieu_chi.strip().removeprefix("- ") == t]
        if len(dong) != 1:
            loi.append(f"{'Thiếu' if not dong else 'Trùng'} đối chiếu tiêu chí: {t}")
            continue
        if not dong[0].bang_chung.strip():
            loi.append(f"Tiêu chí '{t}' không có bằng chứng")
        if not dong[0].dat and not (la_qc and ket_luan_qc == "tra_ve"):
            loi.append(f"Tiêu chí '{t}' chưa đạt" + (" mà khối QC không kết luận tra_ve" if la_qc else ""))
    return loi


def _loi_lenh(bg: BanGiao, lenh_bat_buoc: list[str]) -> list[str]:
    if not lenh_bat_buoc:
        return ["Phiếu cần lệnh kiểm nhưng không có lệnh bắt buộc nào"]
    loi = []
    for l in dict.fromkeys(lenh_bat_buoc):
        kq = [x.ket_qua for x in bg.lenh_kiem if x.lenh == l]
        if not kq:
            loi.append(f"Thiếu lệnh bắt buộc: {l}")
        elif any(k != "pass" for k in kq):
            loi.append(f"Lệnh bắt buộc không pass: {l}")
    return loi


def kiem_ban_giao(bg: BanGiao, tieu_chi: list[str], goc_repo_du_an: Path, *, lenh_bat_buoc: list[str],
                  can_lenh_kiem: bool, commit: str | None = None, la_qc: bool = False,
                  ket_luan_qc: str | None = None) -> list[str]:
    """Luật chặt (spec 0+1a §4.3, 13/10). `commit` có → kiểm file trong cây Git của commit; None → trên đĩa.
    `la_qc` + `ket_luan_qc`: bản QC — `dat: false` chỉ được phép khi khối QC kết luận `tra_ve`."""
    loi: list[str] = []
    if len(bg.model_dump_json().encode()) > GIOI_HAN_BYTE:
        loi.append("Khối bàn giao vượt 64 KB")
    if bg.loai == "tam":
        if not bg.nhanh:
            loi.append("Bàn giao tạm thiếu nhanh")
        if not bg.buoc_tiep:
            loi.append("Bàn giao tạm thiếu buoc_tiep")
        return loi
    loi_file = _loi_file(bg, goc_repo_du_an, commit)
    loi += [loi_file] if loi_file else []
    loi += _loi_doi_chieu(bg, tieu_chi, la_qc, ket_luan_qc)
    return loi + (_loi_lenh(bg, lenh_bat_buoc) if can_lenh_kiem else [])


def doc_khoi_ban_giao(notes: str) -> BanGiao | None:
    khop = KHOI_RE.findall(notes or "")
    if not khop:
        return None
    try:
        return BanGiao.model_validate_json(khop[-1])
    except ValidationError:
        return None
