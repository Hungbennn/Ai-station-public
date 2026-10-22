"""Chuẩn bị một phiếu trên máy thợ (spec 3 §7.1, §7.2): worktree ở đúng `cha` (dọn rác → `chay.don_rac`), môi trường
kiểm khi phiếu cần (thiếu → `bi thieu-moi-truong-kiem`, không chạy CLI), `.tram/goi.md`, hàng đợi + settings/mcp của
phiếu (thư mục principal đọc/ghi được, KHÔNG chứa bí mật), principal + trao quyền ghi worktree (S6)."""
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tram.cau_hinh.du_an import nap_du_an
from tram.chay_cli.lenh_claude import ghi_file_phieu
from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem
from tram.phieu.mo_hinh import Phieu
from tram.tho.cau_hinh import KheCauHinh
from tram.tho.co_model import lenh_model
from tram.tho.hop_thu import HopThu
from tram.tho.ngu_canh import NguCanhTho, rid
from tram.tho.principal_khe import lenh_trao_quyen
from tram.tho.so_khe import SoKhe, TrangThaiPhieu
from tram.tho.worktree import chuan_bi_worktree, duong_dan_worktree


@dataclass
class PhieuDangChay:
    p: Phieu
    tt: TrangThaiPhieu
    k: KheCauHinh
    so: SoKhe
    hop: HopThu
    wt: Path
    thu_muc: Path                  # ~/.tram/hang-doi/<máy>/<khe>/<giao_id>/ — hàng đợi, settings.json, mcp.json
    principal: object
    settings: Path
    mcp: Path | None

    @property
    def hang_doi(self) -> Path:
        return self.thu_muc / "hang-doi.jsonl"

    def luu(self) -> None:
        self.so.luu_phieu(self.tt)


def gui_su_kien(nc: NguCanhTho, hop: HopThu, p: Phieu, loai: str, du_lieu: dict, *khoa: object):
    than = {"khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, "loai": loai, "du_lieu": du_lieu,
            "request_id": rid(p.giao_id, p.luot, loai, *khoa)}
    return hop.gui_mot(nc.khach, "/api/tho/su-kien", than)


def loai_khoi_git(wt: Path, dich: str) -> None:
    """File môi trường kiểm KHÔNG BAO GIỜ được commit/push (`tram bao` chạy `git add -A`): thêm `/<dich>` vào
    `info/exclude` chung của kho (cùng chỗ 3a-1 thêm `.tram/`)."""
    tracked = subprocess.run(["git", "-C", str(wt), "ls-files", "--error-unmatch", "--", dich],
                             capture_output=True, text=True, check=False)
    if tracked.returncode == 0:
        raise LoiMoiTruongKiem("File môi trường kiểm đã được Git theo dõi; từ chối chép bí mật")
    if tracked.returncode != 1:
        raise subprocess.CalledProcessError(tracked.returncode, "git ls-files")
    chung = Path(subprocess.run(["git", "-C", str(wt), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip())
    p = chung / "info" / "exclude"
    p.parent.mkdir(parents=True, exist_ok=True)
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
    if f"/{dich}" not in cu.splitlines():
        p.write_text(cu + ("" if not cu or cu.endswith("\n") else "\n") + f"/{dich}\n", encoding="utf-8")


def chuan_bi(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu, tt: TrangThaiPhieu) -> PhieuDangChay | str:
    """Trả `PhieuDangChay`, hoặc `ly_do` của `bao.bi` khi không chạy được (`thieu-moi-truong-kiem`, `loi-may-tho`)."""
    p = Phieu.model_validate(tt.phieu)
    try:
        lenh_model([], k.cli, k.models, p.co)
    except ValueError:
        return "sai-model"
    if nc.ch.tren_may_b:
        from tram.tho.luot_b import chuan_bi_b
        return chuan_bi_b(nc, k, so, hop, tt, p)
    try:
        wt = duong_dan_worktree(nc.goc_wt, p.du_an, p.repo.nhanh)
        kq = chuan_bi_worktree(nc.goc_kho / p.du_an, wt, nhanh=p.repo.nhanh, cha=p.repo.cha, bead_id=p.bead_id,
                               luot=p.luot, bay_gio=nc.dong_ho())
    except (ValueError, OSError, subprocess.SubprocessError):
        return "loi-may-tho"
    if kq.nhanh_rac:
        gui_su_kien(nc, hop, p, "chay.don_rac", {"nhanh_rac": kq.nhanh_rac}, kq.nhanh_rac)
    if p.can_moi_truong_kiem:
        mt = nap_du_an(p.du_an).moi_truong_kiem
        if mt is None:
            return "thieu-moi-truong-kiem"
        try:
            loai_khoi_git(wt, mt.dich)
            chep_moi_truong_kiem(mt.file, wt, mt.dich)
        except (LoiMoiTruongKiem, OSError, subprocess.SubprocessError):
            return "thieu-moi-truong-kiem"
    (wt / ".tram" / "goi.md").write_text(p.goi_ngu_canh, encoding="utf-8")
    thu_muc = so.hang_doi / p.giao_id
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "hang-doi.jsonl").touch()
    settings, mcp = ghi_file_phieu(thu_muc, p, nho=bool(nc.ch.chay.nho_url))
    pr = nc.principal(k, wt, f"{p.giao_id}-{p.luot}")
    if getattr(pr, "user", None):
        git_wt = Path(subprocess.run(["git", "-C", str(wt), "rev-parse", "--absolute-git-dir"], capture_output=True,
                                     text=True, check=True).stdout.strip())
        for lenh in lenh_trao_quyen(wt, git_wt, thu_muc, user=pr.user):
            nc.chay_lenh(lenh, check=False, capture_output=True)
    return PhieuDangChay(p, tt, k, so, hop, wt, thu_muc, pr, settings, mcp)
