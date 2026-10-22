"""Bước tự merge của vòng tick (spec `tu-merge`; design D-1, D-2, D-11): chen giữa mở PR và xác minh merge trong
`buoc_github`. Công tắc tự merge của dự án tắt → không đọc GitHub, không ghi gì (hành vi như trước TM-2). Bật → đọc
PR + CI, tính lại mọi điều kiện từ sự kiện, Beads, kho kiểm (không tin nhãn hay notes), đọc lại cài đặt / TẠM DỪNG
/ estop / `bat_ghi` và tập file cấm từ ba lệnh hiện hành (D89, `tu_merge_rao`) ngay trước lệnh (`tu_merge_gui`).
Sau khi merge, `kiem_merge` (bead) hay điều kiện 8 của spec 4 §5.1 (`spec_merge`, PR spec) xác minh như cũ."""
from datetime import datetime
from pathlib import Path

import yaml

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.bat_ghi import bat_ghi
from tram.cau_hinh.du_an import DuAn
from tram.chu import estop
from tram.giao_viec.gh import GhCli, PrInfo
from tram.giao_viec.git_kiem import la_to_tien
from tram.giao_viec.pr_bang_chung import bang_chung_hien_hanh
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.giao_viec.tu_merge_gui import gui_merge
from tram.giao_viec.tu_merge_tuoi import doc_hien_hanh, spec_con_nguyen
from tram.giao_viec.tu_merge_rao import cham_file_lenh, cham_rao, doc_tep
from tram.giao_viec.tu_merge_xet import DuKien, kiem_lai_qc, ly_do_chua_merge, ly_do_chua_merge_spec
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.luu import TrangThaiTuDong, doc_trang_thai

NHAN_KHOA_COT = "cot-khoa"


def _bat_ghi(ten: str) -> bool:
    try:
        return bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False                                        # INV-005: đọc lỗi = chỉ quét thử


def _khoa(kho: KhoPhieu, da: DuAn) -> tuple[TrangThaiTuDong, bool, bool]:
    return doc_trang_thai(kho.db, da.ten), _bat_ghi(da.ten), estop.dang_bat()


def _dung_pr(pr: PrInfo, mo: dict, nhanh: str, da: DuAn) -> bool:
    return (pr.so, pr.url, pr.nhanh, pr.base, pr.ngoai_repo) == (mo["pr"], mo["url"], nhanh, da.nhanh_chinh, False)


def xet_tu_merge(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
                 luc: datetime) -> str | None:
    """Bead ở cột 3 đã có `pr.mo` cho `commit_ban_giao` hiện hành."""
    if not doc_trang_thai(kho.db, da.ten).cai_dat.tu_merge or (v := bang_chung_hien_hanh(b, ds)) is None:
        return None
    c = v.du_lieu["commit_ban_giao"]
    if (mo := moi_nhat(cua_so(ds), "pr.mo", lambda s: s.du_lieu["commit"] == c)) is None:
        return None
    tep = doc_tep(kg, da, c)

    def ly_do(pr: PrInfo) -> list[str]:
        tt, _, _ = _khoa(kho, da)                           # đọc ba lệnh SAU `gh pr view` (D89)
        cam = cham_file_lenh(tt.cai_dat, kg, da, c, tep)
        if (hien := doc_hien_hanh(bd, kho, da, b.id)) is None:
            return ["du_lieu_loi"]
        bead, sk = hien
        seal = bang_chung_hien_hanh(bead, sk)
        if seal is None or seal != v:
            return ["kiem_lai"]
        if moi_nhat(cua_so(sk), "pr.mo") != mo:
            return ["pr_khac"]
        qc_dat, kl_dat = kiem_lai_qc(sk, seal)
        schema, rao = cham_rao(da, bead, seal, tep)
        moi, bg, es = _khoa(kho, da)                        # sau cả Beads; từ đây không gọi lệnh đọc chậm
        cam = cam if moi.cai_dat == tt.cai_dat else ("file_lenh_loi",)
        dk = DuKien(qc_dat, kl_dat, _dung_pr(pr, mo.du_lieu, f"tram/{b.id}", da), pr.head == c, schema,
                    pr.ci or "do", NHAN_KHOA_COT not in bead.labels, rao, cam)
        return ly_do_chua_merge(moi, dk, bat_ghi=bg, estop_bat=es)
    return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="code", ly_do=ly_do,
                     luc=luc)


def tu_merge_spec(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
                  luc: datetime) -> str | None:
    """Feature `theo-plan` đã được Đại ca duyệt spec, trạm đã mở PR `tram/spec-<feature>` (D95, design D-11)."""
    dy = moi_nhat(ds, "spec.duyet")
    if dy is None or b.status == "closed" or not doc_trang_thai(kho.db, da.ten).cai_dat.tu_merge:
        return None
    c = dy.du_lieu["commit"]
    mo = moi_nhat(ds, "pr.mo", lambda s: s.du_lieu["commit"] == c and s.du_lieu.get("loai") == "spec")
    gui = moi_nhat(ds, "tu_merge.bat_dau", lambda s: s.du_lieu.get("commit") == c)
    if mo is None or (gui is None and la_to_tien(kg, c, f"origin/{da.nhanh_chinh}")):
        return None                                     # đã vào nhánh chính mà trạm chưa gửi lệnh: Đại ca gộp tay
    tep = doc_tep(kg, da, c)

    def ly_do(pr: PrInfo) -> list[str]:
        tt, bg, es = _khoa(kho, da)
        cam = ("diff_loi",) if tep is None else cham_file_lenh(tt.cai_dat, kg, da, c, tep)      # D89, như mã
        if (hien := doc_hien_hanh(bd, kho, da, b.id)) is None:
            return ["du_lieu_loi"]
        bead, sk = hien
        if not spec_con_nguyen(b, bead, sk, dy, mo):
            return ["du_lieu_doi"]
        moi, bg, es = _khoa(kho, da)
        cam = cam if moi.cai_dat == tt.cai_dat else ("file_lenh_loi",)
        return ly_do_chua_merge_spec(moi, dung_pr=_dung_pr(pr, mo.du_lieu, f"tram/spec-{b.id}", da),
                                     dau_pr_dung=pr.head == c, bat_ghi=bg, estop_bat=es,
                                     file_lenh=cam + (() if pr.ci == "xanh" else ("ci_do",)))
    return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="spec", ly_do=ly_do,
                     luc=luc)
