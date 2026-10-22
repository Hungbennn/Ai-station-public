"""Mỗi phiếu/lượt B có cổng 0700 do quản lý giữ; không dùng lại cây giữa hai khe."""
import os
import shutil
import subprocess
from pathlib import Path

from tram.kiem.moi_truong import LoiMoiTruongKiem
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.ngu_canh import rid
from tram.tho.worktree import GIT, duong_dan_worktree


def git(kho, *args):
    return subprocess.run([*GIT, '-C', str(kho), *args], check=True, capture_output=True, text=True, timeout=600)


def dong_cong(cong, nc):
    if cong.is_symlink() or cong.stat().st_uid != os.getuid():
        raise ValueError('Cổng lượt không thuộc quản lý')
    nc.chay_lenh(['/bin/chmod', '-N', str(cong)], check=True, capture_output=True, timeout=30)
    cong.chmod(0o700)


def xoa_cay(cong, kho):
    # Cổng đã đóng, UID đã dọn. Không chmod/chown file của khe; rmtree không theo symlink.
    (cong / 'san-sang').unlink(missing_ok=True)
    wt = cong / 'cay'
    if wt.exists():
        shutil.rmtree(wt)
    # --force nhận cả worktree thiếu thư mục; chỉ gỡ registration của đúng lượt.
    ds = git(kho, 'worktree', 'list', '--porcelain').stdout.splitlines()
    if f'worktree {wt}' in ds:
        git(kho, 'worktree', 'remove', '--force', str(wt))
    shutil.rmtree(cong)


def chuan_bi_b(nc, k, so, hop, tt, p):
    from tram.tho.chuan_bi import PhieuDangChay
    from tram.tho.chuan_bi_b import tao_noi_dung
    duong_dan_worktree(nc.goc_wt, p.du_an, p.repo.nhanh)  # Giữ kiểm tên dự án/nhánh cũ.
    cong = nc.goc_wt / rid(p.giao_id, p.luot, p.khe_id)
    kho, wt, hd = nc.goc_kho / p.du_an, cong / 'cay', cong / 'phieu'
    pr = nc.principal(k, wt, f'{p.giao_id}-{p.luot}')
    try:
        if cong.exists():
            dong_cong(cong, nc)
            if not (cong / 'san-sang').is_file():
                xoa_cay(cong, kho)
        if not cong.exists():
            cong.mkdir(parents=True, mode=0o700)
            dong_cong(cong, nc)
            git(kho, 'fetch', '-q', 'origin')
            git(kho, 'worktree', 'add', '--detach', str(wt), p.repo.cha)
            try:
                tao_noi_dung(nc, p, wt, hd, pr)
            except LoiMoiTruongKiem:
                # CLI chưa chạy, khe chưa được trao quyền: dọn rồi báo bi theo luồng cũ.
                dong_cong(cong, nc)
                xoa_cay(cong, kho)
                return 'thieu-moi-truong-kiem'
            (cong / 'san-sang').touch(mode=0o600)
        if getattr(pr, 'user', None):
            nc.chay_lenh(['/bin/chmod', '+a', f'user:{pr.user} allow search', str(cong)],
                         check=True, capture_output=True, timeout=30)
        return PhieuDangChay(p, tt, k, so, hop, wt, hd, pr, hd / 'settings.json',
                            hd / 'mcp.json' if (hd / 'mcp.json').is_file() else None)
    except (OSError, ValueError, subprocess.SubprocessError):
        if cong.exists():
            dong_cong(cong, nc)
        raise LoiThuHoi('Chuẩn bị lượt B lỗi; giữ phiếu và cổng đóng để đối soát') from None


def don_luot_b(pc, nc):
    cong = pc.wt.parent
    try:
        dong_cong(cong, nc)
        nc.don_khe(pc.k)
        xoa_cay(cong, nc.goc_kho / pc.p.du_an)
    except (OSError, ValueError, subprocess.SubprocessError):
        raise LoiThuHoi('Dọn lượt B lỗi; giữ phiếu, không nhận lượt mới') from None


def don_phieu_cu_b(nc, k, tt):
    from types import SimpleNamespace
    from tram.phieu.mo_hinh import Phieu
    p = Phieu.model_validate(tt.phieu)
    cong = nc.goc_wt / rid(p.giao_id, p.luot, p.khe_id)
    if cong.exists():
        don_luot_b(SimpleNamespace(wt=cong / 'cay', p=p, k=k), nc)
