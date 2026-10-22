"""`tram giao tick` — vòng tick (spec 4 §10), idempotent theo ID nguồn; 4a-2 tách HAI PHA chạy ở hai luồng riêng:

- `vong_nhanh` (G5 ≤ 3 phút — không Git, không chạy lệnh): (2) `escalation.dong` · (3) `bead.dong` · chu kỳ ngân
  sách mới — chỉ ghi sự kiện, chạy cả khi estop; estop bật (hoặc `thu`) thì DỪNG ở đây. Sau đó: công việc chờ KHÔNG
  phải `xong` (bí, hết hạn mức, thu hồi), câu hỏi của agent, (1) hết ngân sách.
- `vong_git` (có thể dài — kiểm lại tới 15 phút/lệnh): `git fetch` kho kiểm (có hạn giờ) · công việc `xong` (xét
  bàn giao, QC) · kiểm lại · cột 3 · thiếu môi trường kiểm. Estop bật → không làm gì.
- `vong_deploy` (TM-3, design D-6 — một chuỗi xấu nhất ~32 phút không chặn kiểm lại): `tram.deploy.vong`. Estop bật →
  chỉ đối soát chuỗi bỏ dở và huỷ nút Deploy đang chờ.
`mot_vong_tick` = ba pha nối tiếp (lệnh `tram giao tick`, test). Một dự án lỗi không chặn dự án khác."""
import subprocess
from collections import Counter
from contextlib import closing

from tram.beads.bd import LoiBd
from tram.chu import estop
from tram.deploy.vong import bat_ghi_an_toan, buoc_deploy
from tram.de_nghi.vong import vong_de_nghi
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tick_github import buoc_github
from tram.giao_viec.tick_doc import ghi_bead_dong, ghi_escalation_dong, mo_chu_ky_con_thieu
from tram.giao_viec.tick_feature import day_feature, mo_dot_spec_con_thieu
from tram.giao_viec.tick_theo_plan import buoc_theo_plan
from tram.giao_viec.tick_pipeline import VIEC_GIT, VIEC_NHANH, day_pipeline
from tram.giao_viec.xu_ly_viec import escalation_cau_hoi, xu_ly_cong_viec
from tram.giao_viec.hang_doi import viec_cua_pha

LOI = (LoiBd, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError)
FETCH_GIAY = 120


def _nhanh(bo, kho, da, luc, dung: bool, dem: Counter) -> None:
    bd = bo.tao_bd(da)
    beads = bd.tat_ca()
    dem["escalation_dong"] += ghi_escalation_dong(kho, da.ten, beads, luc)
    dem["bead_dong"] += ghi_bead_dong(kho, da.ten, beads, luc)
    dem["chu_ky_moi"] += mo_chu_ky_con_thieu(kho, da.ten, luc)
    dem["dot_spec_moi"] += mo_dot_spec_con_thieu(kho, da.ten, luc)
    dem.update(buoc_theo_plan(kho, da, beads, None, luc))
    if dung:
        return
    for cv in viec_cua_pha(kho, da.ten, git=False):
        dem["cong_viec"] += xu_ly_cong_viec(kho, cv, du_an=da, bd=bd, kho_git=None, luc=luc)
    dem["cau_hoi"] += escalation_cau_hoi(kho, da, bd, luc)
    dem.update(day_pipeline(bo, kho, da, bd, bd.tat_ca(), bd.san_sang(), None, luc, viec=VIEC_NHANH))
    dem.update(day_feature(kho, da, bd, bd.tat_ca(), bd.san_sang(), None, luc, pha="nhanh"))


def _git(bo, kho, da, luc, dem: Counter) -> None:
    kg = bo.kho_git(da)
    if kg is None:
        return                                           # chưa có kho kiểm: công việc `xong` để nguyên (4a-1 G15)
    fetch(kg, thoi_gian_cho=FETCH_GIAY)
    bd = bo.tao_bd(da)
    for cv in viec_cua_pha(kho, da.ten, git=True):
        dem["cong_viec"] += xu_ly_cong_viec(kho, cv, du_an=da, bd=bd, kho_git=kg, luc=luc)
    dem.update(day_pipeline(bo, kho, da, bd, bd.tat_ca(), bd.san_sang(), kg, luc, viec=VIEC_GIT))
    if not estop.dang_bat():
        dem.update(buoc_github(bo, kho, da, bd, bd.tat_ca(), kg, luc))
    dem.update(day_feature(kho, da, bd, bd.tat_ca(), bd.san_sang(), kg, luc, pha="git"))
    dem.update(buoc_theo_plan(kho, da, bd.tat_ca(), kg, luc))


def _vong(bo, lam) -> dict[str, int]:
    luc, dem = bo.dong_ho(), Counter()
    with closing(bo.mo_kho()) as kho:
        for da in bo.cac_du_an():
            try:
                lam(kho, da, luc, dem)
            except LOI:
                dem["loi"] += 1
    return {k: v for k, v in dem.items() if v}


def vong_nhanh(bo, *, thu: bool = False) -> dict[str, int]:
    """`thu` = như estop: chỉ ghi sự kiện suy từ beads — không ghi beads, không chạy lệnh."""
    dung = thu or estop.dang_bat()
    dem = Counter(_vong(bo, lambda kho, da, luc, dem: _nhanh(bo, kho, da, luc, dung, dem)))
    if not dung and bo.de_nghi is not None:          # TC (design D-4): ghi đề nghị của agent, sau escalation cùng nhịp
        dem.update(vong_de_nghi(bo, bo.de_nghi, bo.dong_ho()))
    return {k: v for k, v in dem.items() if v}


def vong_git(bo) -> dict[str, int]:
    if estop.dang_bat():
        return {}
    return _vong(bo, lambda kho, da, luc, dem: _git(bo, kho, da, luc, dem))


def vong_deploy(bo, *, bat_ghi=bat_ghi_an_toan) -> dict[str, int]:
    return _vong(bo, lambda kho, da, luc, dem: dem.update(buoc_deploy(bo, kho, da, bat_ghi=bat_ghi)))


def mot_vong_tick(bo, *, thu: bool = False) -> dict[str, int]:
    dem = Counter(vong_nhanh(bo, thu=thu))
    if not thu:
        dem.update(vong_git(bo))
        dem.update(vong_deploy(bo))
    return {k: v for k, v in dem.items() if v}
