"""Xét `bao.xong` tại SHA trạm đã công bố (spec 4 §6.1, §6.3). Đường dẫn cấm kiểm TRƯỚC (§6.2 bước 0); bàn giao
theo luật `chinh-thuc` chặt (`kiem_ban_giao` của 3a-1, G2); QC chỉ được thêm `docs/handovers/**` (G10)."""
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from tram.ban_giao.schema import BanGiao, kiem_ban_giao
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import doc_file, la_to_tien
from tram.giao_viec.khoi_qc import doc_khoi_qc
from tram.kiem.diff import diff_cham_cam, tep_doi
from tram.kiem.duong_dan_cam import khop_mau
from tram.phieu.mo_hinh import Phieu

QC_DUOC_DOI = "docs/handovers/**"


@dataclass(frozen=True)
class KetLuan:
    ly_do: str | None              # None = hợp lệ
    loi: tuple[str, ...]
    commit: str | None             # SHA công bố của lượt (khi đã xác minh)
    cham_cam: tuple[str, ...] = ()


@dataclass(frozen=True)
class KetQuaQC:
    ket_luan: str | None           # dat | tra_ve | khong_cong_nhan; None = chưa có QC hợp lệ để ghi (QC lại)
    phat_hien: tuple[dict, ...]
    ly_do: str | None
    commit_qc: str | None


def _cong_bo(bao: dict, sha: str | None) -> KetLuan | None:
    if sha is None:
        return KetLuan("chua-cong-bo", ("Lượt này chưa có commit trạm công bố",), None)
    if bao.get("commit") != sha:
        return KetLuan("commit-khong-cong-bo", (f"bao.xong mang {bao.get('commit')}, ref công bố của lượt là {sha}",),
                       None)
    return None


def _ban_giao(bao: dict) -> BanGiao | None:
    try:
        return BanGiao.model_validate(bao.get("ban_giao"))
    except ValidationError:
        return None


def xet_xong_code(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn, *,
                  them_cam: tuple[str, ...] = ()) -> KetLuan:
    """`them_cam` (TM-3, D89): mẫu cấm từ ba lệnh deploy của dự án, cộng vào đường dẫn cấm."""
    if (kl := _cong_bo(bao, sha)) is not None:
        return kl
    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                         cho_phep=du_an.giao.duong_dan_cam_cho_phep)
    if cham:
        return KetLuan("dong-file-cau-hinh", (f"Diff chạm đường dẫn cấm: {', '.join(cham)}",), sha, tuple(cham))
    if (bg := _ban_giao(bao)) is None:
        return KetLuan("ban-giao-loi", ("Khối bàn giao sai schema",), sha)
    loi = list(bao.get("loi_ban_giao") or [])
    loi += kiem_ban_giao(bg, list(phieu.tieu_chi), kho_git, lenh_bat_buoc=list(phieu.lenh_kiem),
                         can_lenh_kiem=phieu.can_lenh_kiem, commit=sha)
    if bg.commit != sha:
        loi.append("commit trong khối bàn giao khác SHA công bố")
    return KetLuan("ban-giao-loi" if loi else None, tuple(dict.fromkeys(loi)), sha)


def xet_xong_qc(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None) -> KetQuaQC:
    if (kl := _cong_bo(bao, sha)) is not None:
        return KetQuaQC(None, (), kl.ly_do, None)
    code = phieu.repo.cha                                     # phiếu qc được cấp với cha = commit code
    if not la_to_tien(kho_git, code, sha) or any(not khop_mau(p, QC_DUOC_DOI) for p in tep_doi(kho_git, code, sha)):
        return KetQuaQC("khong_cong_nhan", (), "qc-doi-ma", sha)
    bg = _ban_giao(bao)
    khoi = doc_khoi_qc(doc_file(kho_git, sha, bg.file_ban_giao)) if bg else None
    if khoi is None or khoi.commit_code != code:
        return KetQuaQC("tra_ve", (), "khoi-qc-loi", sha)
    phat_hien = tuple(p.model_dump() for p in khoi.phat_hien)
    loi = list(bao.get("loi_ban_giao") or []) + kiem_ban_giao(
        bg, list(phieu.tieu_chi), kho_git, lenh_bat_buoc=[], can_lenh_kiem=False, commit=sha, la_qc=True,
        ket_luan_qc=khoi.ket_luan)
    if bg.commit != sha:
        loi.append("commit trong khối bàn giao QC khác SHA công bố")
    if loi or (khoi.ket_luan == "dat" and any(not d.dat for d in bg.doi_chieu_nghiem_thu)):
        them = tuple({"muc": "chan", "noi_dung": l, "vi_tri": ""} for l in loi)
        return KetQuaQC("tra_ve", phat_hien + them, "ban-giao-qc-loi", sha)
    return KetQuaQC(khoi.ket_luan, phat_hien, None, sha)
