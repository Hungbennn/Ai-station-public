"""`tram giao kiem` — các mục principal kiểm lại (lát 3c; 3C-D6, hợp đồng P1 H7). Chạy DƯỚI khoá kiểm lại và chỉ khi
cổng lượt chưa đóng (`mo`/`chua-mo`) và không còn dấu hạn tổng `kiem-lai.dong`. Danh tính: `xac_minh_uid` (UID nhân ghi
cho tiến trình dò dưới đúng `boc`; không so `id -un` với `getpass`) — sai thì KHÔNG lệnh nào khác chạy dưới
`tram-kiem`. Rồi thu hồi theo UID (3C-D5) TRƯỚC probe, rồi mọi probe — kể cả tạo/xoá lượt tạm — qua `boc_luot` của MỘT
lượt tạm (cùng đường `chep_ban`/`don_ban` của lượt thật): giữ APP_ENV, không đọc kho trạm, ghi được trong `LUOT`, ghi ra
gốc ngoài `LUOT` bị từ chối (gốc thuộc `tram-kiem`: chỉ hồ sơ chặn được); mục "bị chặn" chỉ xanh khi mục ghi được xanh
(chứng minh wrapper chạy). Lệnh có hạn qua `chay_gioi_han` (H1); "dừng được" gọi thẳng, xanh khi `het_gio and
da_thu_hoi`. BẤT KỲ mục probe nào ĐỎ (danh tính, thu hồi, lượt tạm, hồ sơ không chặn, lệnh không dừng/không thu hồi
được, dọn) → `cong.dong` (fail-closed: lượt sau bị chặn tới khi Đại ca xem). `sudo -n -l` của trạm chạy trước khi UID
được chứng minh nên chỉ kill cục bộ, không gửi gì dưới `tram-kiem`."""
import os
import subprocess
from collections.abc import Callable
from functools import partial
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
from tram.giao_viec.kiem_goc import kiem_sudoers_khong_root, kiem_thu_muc_goc, uid_that
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.han_tong import cong_dong, gop_kill
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.kiem_may import MucKiem

THU_MUC_THU = "tram-giao-kiem-thu"
LOI = (OSError, subprocess.SubprocessError, ValueError, LoiDanhTinh, LoiThuHoi)   # LoiBanChep là OSError


def _muc(ten: str, dat: bool, chi_tiet: str) -> MucKiem:
    return MucKiem(ten, "xanh" if dat else "do", chi_tiet[:200])


def _ra(chay: Callable, argv: list[str], **kw):
    return chay(argv, capture_output=True, text=True, timeout=30, **kw)


def _luot_tam(pk, wt: Path, chay: Callable, chay_lenh: Callable) -> list[MucKiem]:
    nha, ngoai, b = f"{wt}.nha", wt.with_name(wt.name + ".ngoai"), pk.boc_luot(wt)
    if any(_ra(chay, b(a)).returncode for a in (["/bin/mkdir", str(wt)], ["/bin/mkdir", "-m", "700", nha,
                                                                           f"{nha}/tmp"])):
        raise ValueError("tram-kiem không tạo được lượt tạm dưới thu_muc_kiem (qua boc_luot)")
    env = _ra(chay, b(["/usr/bin/env"]), env=moi_truong_kiem({}))
    ghi = all(_ra(chay, b(a)).returncode == 0 for a in (["/bin/mkdir", str(wt / "con")],
                                                         ["/usr/bin/touch", str(wt / "con" / "x")]))
    ghi = ghi and (wt / "con" / "x").is_file()
    doc = _ra(chay, b(["/bin/ls", str(tram_home())]))
    r = _ra(chay, b(["/usr/bin/touch", str(ngoai)]))
    kq = chay_lenh("sleep 30", ["/bin/sleep", "30"], cwd=wt, env=moi_truong_kiem({}), thoi_gian_cho=1, boc=b,
                   log=tram_home() / "log" / "giao-kiem-dung.log", cho_kill=2, kill=pk.kill_nhom)
    return [_muc("principal: giữ APP_ENV", "APP_ENV=testing" in env.stdout.splitlines(), "lệnh kiểm thấy APP_ENV"),
            _muc("principal: ghi bản chép kiểm", ghi, "ghi được trong LUOT (đối chứng dương của hai mục sau)"),
            _muc("principal: không đọc kho trạm", ghi and doc.returncode != 0, f"ls {tram_home()} phải bị từ chối"),
            _muc("principal: hồ sơ chặn ghi ngoài lượt", ghi and r.returncode != 0 and not os.path.lexists(ngoai),
                 "touch ra gốc (thuộc tram-kiem) ngoài LUOT phải bị hồ sơ từ chối"),
            _muc("principal: dừng được lệnh quá hạn", kq.het_gio and kq.da_thu_hoi, "quá hạn → thu hồi cả cây")]


def _don(pk, wt: Path, chay: Callable, thu_hoi: Callable[[], None]) -> MucKiem:
    ngoai, ten = wt.with_name(wt.name + ".ngoai"), "principal: dọn lượt tạm + thu hồi theo UID"
    try:
        r = _ra(chay, pk.boc_luot(wt)(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]))
        if os.path.lexists(ngoai):                     # chỉ có khi hồ sơ KHÔNG chặn: xoá ngoài lượt, vẫn ĐỎ
            _ra(chay, pk.boc_lenh(["/bin/rm", "-f", str(ngoai)]))
        thu_hoi()
    except LOI as e:
        return _muc(ten, False, f"{type(e).__name__}: {e}")
    sach = r.returncode == 0 and not any(map(os.path.lexists, (wt, f"{wt}.nha", ngoai)))
    return _muc(ten, sach, "tram-kiem tự xoá lượt tạm; không còn tiến trình")


def _probe(pk, thu_muc: Path | None, chay, chay_lenh, xac_minh, thu_hoi) -> list[MucKiem]:
    try:
        uid = xac_minh(pk.ten, pk.boc_lenh, pk.kill_nhom)
        thu_hoi()                                       # tàn dư trước probe (cổng `chua-mo`) không lẫn vào probe
    except LOI as e:
        return [_muc("principal: danh tính (UID thực) + thu hồi trước probe", False, f"{type(e).__name__}: {e}")]
    ra = [_muc("principal: danh tính (UID thực) + thu hồi trước probe", True, f"{pk.ten} uid {uid}")]
    if thu_muc is None or not thu_muc.is_dir():
        return ra + [_muc("principal: lượt tạm", False, f"thu_muc_kiem không có: {thu_muc}")]
    wt = thu_muc / ten_ban_chep(THU_MUC_THU)
    try:
        ra += _luot_tam(pk, wt, chay, chay_lenh)
    except LOI as e:
        ra.append(_muc("principal: lượt tạm", False, f"{type(e).__name__}: {e}"))
    return ra + [_don(pk, wt, chay, thu_hoi)]


def kiem_principal(pk, thu_muc: Path | None, *, chay: Callable | None = None, chay_lenh: Callable = chay_mot_lenh,
                   xac_minh: Callable = xac_minh_uid, thu_hoi: Callable[[], None] | None = None, cong=None,
                   uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
    if pk is None:
        return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
    sud_chay = chay or partial(chay_gioi_han, kill=kill_cuc_bo)
    cong = cong or dung_cong(pk, thu_muc, cac_du_an=cac_du_an_quan_sat)
    chay = chay or partial(chay_gioi_han, kill=gop_kill(pk.kill_nhom, kill_cuc_bo))
    try:
        sud = kiem_sudoers_khong_root(chay=sud_chay)
    except LOI as e:
        sud = _muc("principal: sudoers không NOPASSWD root", False, f"sudo -n -l: {type(e).__name__}")
    ra, ten = [kiem_thu_muc_goc(pk, thu_muc, uid_cua=uid_cua), sud], "principal: probe"
    try:
        with giu_khoa():
            tt = cong.trang_thai()["trang_thai"]
            if tt not in ("mo", "chua-mo") or cong_dong(tram_home() / "kiem-lai.dong"):
                return ra + [_muc(ten, False, f"cổng kiểm lại {tt} hoặc còn dấu kiem-lai.dong — không chạy probe "
                                              "dưới tram-kiem; Đại ca xem rồi `tram giao mo-cong-kiem`")]
            ket = _probe(pk, thu_muc, chay, chay_lenh, xac_minh, thu_hoi or partial(thu_hoi_theo_uid, pk))
            if do := [m.muc for m in ket if m.muc_do == "do"]:
                cong.dong(f"tram giao kiem: {', '.join(do)}"[:300])
            return ra + ket
    except KiemLaiDangBan:
        return ra + [_muc(ten, False, "đang có lần kiểm lại chạy — chạy lại `tram giao kiem` sau")]
