"""Lệnh kiểm do THỢ chạy sau `--xong`, khi CLI đã thoát và worktree đã sạch (spec 3 §7.5):
1. diff từ gốc nhánh chạm `duong_dan_cam` → KHÔNG chạy lệnh nào, lỗi vào `loi_ban_giao`;
2. chạy MỌI lệnh bắt buộc (`can_lenh_kiem`) — không khớp `lenh_cho_phep` là fail; lệnh agent đề xuất khớp thì chạy
   và ghi lại, không thay được lệnh bắt buộc; không khớp thì bỏ, ghi vào `vuong_mac`;
3. GHI ĐÈ `lenh_kiem[]`, `luot`, `commit` của khối bằng kết quả thật;
4. luật `chinh-thuc` chặt (bản QC cho phiếu qc). Trượt vẫn trả nguyên kết quả + `loi_ban_giao` — thợ không tự đổi
   thành `bi`; phần 4 quyết."""
import subprocess
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tram.ban_giao.schema import BanGiao, kiem_ban_giao
from tram.cau_hinh.lenh import khop_bat_ky
from tram.kiem.chay_lenh import chay_mot_lenh
from tram.kiem.diff import diff_cham_cam
from tram.kiem.vong_doi import LoiThuHoi
from tram.phieu.mo_hinh import Phieu

GIT = ("git", "-c", "core.hooksPath=/dev/null")


@dataclass(frozen=True)
class KetQuaKiemTho:
    ban_giao: BanGiao            # khối gửi kèm `bao.xong` (đã ghi đè)
    loi_ban_giao: list[str]      # nằm trong thân `bao`, không trong khối
    cham_cam: list[str]


def _git(wt: Path, *args: str) -> str:
    return subprocess.run([*GIT, "-C", str(wt), *args], capture_output=True, text=True, check=True).stdout.strip()


def kiem_sau_xong(wt: Path, phieu: Phieu, ban_giao: BanGiao, *, thu_muc_log: Path,
                  boc: Callable[[list[str]], list[str]], env: Mapping[str, str], them_cam: Iterable[str] = (),
                  cho_phep_cam: Iterable[str] = (), bat_buoc: Iterable[str] = (), thoi_gian_cho: float = 900,
                  loi_cam: str | None = None,
                  ket_luan_qc: str | None = None, kill: Callable[[int, int], None] | None = None) -> KetQuaKiemTho:
    if _git(wt, "status", "--porcelain"):
        raise ValueError("Worktree còn thay đổi chưa commit — thợ commit `wip: sau xong` trước khi kiểm")
    commit = _git(wt, "rev-parse", "HEAD")
    cham = diff_cham_cam(wt, f"origin/{phieu.repo.nhanh_chinh}", commit, them=them_cam,
                          cho_phep=cho_phep_cam, bat_buoc=bat_buoc)
    ket_qua, vuong = [], list(ban_giao.vuong_mac)
    if not cham and not loi_cam:
        de_xuat = list(dict.fromkeys(l.lenh for l in ban_giao.lenh_kiem if l.lenh not in phieu.lenh_kiem))
        vuong += [f"Lệnh đề xuất không khớp lenh_cho_phep, không chạy: {l}" for l in de_xuat
                  if khop_bat_ky(l, phieu.lenh_cho_phep) is None]
        ds = [(l, khop_bat_ky(l, phieu.lenh_cho_phep)) for l in (phieu.lenh_kiem if phieu.can_lenh_kiem else [])]
        ds += [(l, a) for l in de_xuat if (a := khop_bat_ky(l, phieu.lenh_cho_phep)) is not None]
        for i, (lenh, argv) in enumerate(ds, 1):
            kq = chay_mot_lenh(lenh, argv, cwd=wt, env=env, boc=boc, thoi_gian_cho=thoi_gian_cho,
                               log=thu_muc_log / f"{phieu.giao_id}-{phieu.luot}-{i}.log",
                               **({"kill": kill} if kill else {}))
            if not kq.da_thu_hoi:           # P1: tiến trình lệnh kiểm có thể còn sống dưới principal → dừng khe
                raise LoiThuHoi("Không dọn được nhóm lệnh kiểm; dừng khe để kiểm principal")
            ket_qua.append(kq.sang_lenh_kiem())
    bg = BanGiao.model_validate({**ban_giao.model_dump(), "lenh_kiem": ket_qua, "luot": phieu.luot,
                                 "commit": commit, "vuong_mac": vuong})
    loi = [f"Diff chạm đường dẫn cấm: {', '.join(cham)}"] if cham else []
    loi += [loi_cam] if loi_cam else []
    loi += kiem_ban_giao(bg, phieu.tieu_chi, wt, lenh_bat_buoc=phieu.lenh_kiem, can_lenh_kiem=phieu.can_lenh_kiem,
                         commit=commit, la_qc=phieu.buoc == "qc", ket_luan_qc=ket_luan_qc)
    return KetQuaKiemTho(bg, loi, cham)
