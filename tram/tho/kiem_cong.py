"""Kiểm đăng nhập và cách ly khe bằng thăm dò đúng principal; lỗi đối chứng không tính đạt."""
import json
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.kiem import danh_tinh
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.don_uid import con_lai
from tram.tho.khach import DichKiemAm, LoiKhachTram
from tram.tho.kiem_am import HUONG_DAN_SUDO, KetQuaThamDo, ThamDo, chay_tham_do, tham_do_api_db, tham_do_khe
from tram.tho.kiem_may import DauDo, MucKiem
from tram.tho.principal import ChuaCoPrincipal
from tram.tho.principal_khe import principal_cua
from tram.tho.lenh_token_khe import boc_token

LENH_DANG_NHAP = ("auth", "status")  # B qua helper FD; S2 vẫn cần đo daemon thật
KEYCHAIN_CAM = ("tram-tho-token", "tram-noi-bo-token", "tram-anthropic-api-key")
def _uid(p, xac_minh) -> tuple[int | None, str | None]:
    """Lỗi UID/thu hồi: không chạy thêm; chỉ hướng dẫn có điều kiện, không chép ngoại lệ."""
    try:
        return xac_minh(p.user, p.boc, p.kill_nhom), None
    except (danh_tinh.LoiDanhTinh, LoiThuHoi) as e:
        ly = ("UID: không xác nhận thu hồi tiến trình dò — kiểm principal" if isinstance(e, LoiThuHoi)
              else "UID thực của principal chưa chứng minh — không chạy thăm dò")
        return None, ly + HUONG_DAN_SUDO


def dang_nhap(ch: CauHinhTho, k: KheCauHinh, *, goc: Path, goc_wt: Path, chay=chay_gioi_han,
              xac_minh=danh_tinh.xac_minh_uid) -> tuple[str, str]:
    try:
        p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
    except ChuaCoPrincipal as e:
        return "do", str(e)
    if (ly_do := _uid(p, xac_minh)[1]) is not None:
        return "do", ly_do
    env = {"CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh), "PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}
    argv = boc_token([k.cli, *LENH_DANG_NHAP]) if ch.tren_may_b else [k.cli, *LENH_DANG_NHAP]
    try:
        kq = chay(p.boc(argv), kill=p.kill_nhom, capture_output=True, text=True, timeout=30,
                  env=env)
    except LoiThuHoi:
        return "do", "không xác nhận thu hồi tiến trình lệnh trạng thái — kiểm principal" + HUONG_DAN_SUDO
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return "do", f"không chạy được lệnh trạng thái: {type(e).__name__}" + HUONG_DAN_SUDO
    try:
        co = json.loads(kq.stdout).get("loggedIn") is True
    except (ValueError, AttributeError):
        co = False
    return ("xanh", "đã đăng nhập") if kq.returncode == 0 and co else (
        "do", "chưa xác nhận đăng nhập / dạng phản hồi không khớp S2" + HUONG_DAN_SUDO)


def _tan_du(uid: int, chup, *, ten: str | None = None) -> list[KetQuaThamDo]:
    try:
        n = con_lai(uid, chup, ten=ten)
    except (OSError, ValueError):
        return [KetQuaThamDo("tàn dư", False, "không kết luận: không đọc được bảng tiến trình sau thăm dò")]
    return [KetQuaThamDo("tàn dư", False, f"còn {n} tiến trình của principal sau thăm dò — chưa chứng minh thu hồi "
                                          "(dừng `tram tho chay` rồi kiểm lại)")] if n else []


def _api_db(ch: CauHinhTho, dich: Callable[[], DichKiemAm]) -> tuple[list[ThamDo], list[KetQuaThamDo]]:
    """(thăm dò API Duyệt + DB nghiệp vụ, lỗi) — đích lấy MỘT lần từ trạm cho mọi khe. Đích (loopback, DB của trạm)
    theo máy B: thợ máy khác chưa có ánh xạ đích đã chứng minh, 403 qua proxy không chứng minh kênh ghi tách → bỏ."""
    if not ch.tren_may_b:
        ly = "không kết luận: thợ không ở máy B (tram_api không phải loopback) — D54 lát này chỉ kiểm trên máy B"
        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False, ly)]
    try:
        d = dich()
    except LoiKhachTram as e:
        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False,
                                 f"không kết luận: không lấy được đích từ tram-api ({type(e).__name__})")]
    return tham_do_api_db(api=ch.tram_api, dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu)), []


def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, dich: Callable[[], DichKiemAm],
            chay_td=chay_tham_do, xac_minh=danh_tinh.xac_minh_uid, chup=chup_nhan) -> list[MucKiem]:
    ra, (them, loi_dich) = [], _api_db(ch, dich)
    for k in ch.khe:
        kid = ch.khe_id(k)
        try:
            p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
        except ChuaCoPrincipal as e:
            ra.append(MucKiem(f"{kid} cách ly", "do", str(e)))
            continue
        uid, ly_do = _uid(p, xac_minh)
        if ly_do is not None:
            ra.append(MucKiem(f"{kid} cách ly", "do", ly_do))
            continue
        khac = [x for x in ch.khe if x.ten != k.ten]
        kho = [goc_wt.parent / "kho" / d / ".git" for d in du_an]
        ds = tham_do_khe(keychain=list(KEYCHAIN_CAM),
                         doc_cam=[goc / "tho" / ch.may_id / k.ten / "phieu.json", Path.home() / "Library/Keychains",
                                  *([ch.chay.thu_muc_tram / "su-kien.db"] if ch.chay.thu_muc_tram else [])],
                         ghi_cam=[*(goc / "hang-doi" / ch.may_id / x.ten for x in khac),
                                  *(x.thu_muc_cau_hinh for x in khac), *(g / "hooks" for g in kho)],
                         ghi_duoc=goc / "hang-doi" / ch.may_id / k.ten, ghi_tep_cam=[g / "config" for g in kho])
        kq = chay_td(ds + them, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
        hong = [x for x in kq if not x.dat] + loi_dich + _tan_du(
            uid, chup, ten=p.user if ch.tren_may_b and p.co_che == 'user' else None)
        ra.append(MucKiem(f"{kid} cách ly", "do" if hong else "xanh",
                          "; ".join(f"{x.ten}: {x.chi_tiet}" for x in hong) or f"{len(kq)} thăm dò đạt"))
    return ra


def dau_do_that(ch: CauHinhTho, khach, *, du_an: tuple[str, ...] = ()) -> DauDo:
    """Đầu đo của `tram tho kiem` có mục chờ cổng chạy THẬT (3a-2)."""
    from tram.duong_dan import tram_home
    goc, goc_wt = tram_home(), Path.home() / "tram" / "worktrees"
    ds = khach.du_an() if du_an else None
    if du_an and not set(du_an) <= set(ds):
        raise ValueError("Dự án kiểm không có ở trạm")
    lay = (lambda: list(du_an)) if du_an else khach.du_an
    return DauDo(ping=khach.ping, du_an=lay,
                 dang_nhap=lambda k: dang_nhap(ch, k, goc=goc, goc_wt=goc_wt),
                 cach_ly=lambda: cach_ly(ch, lay(), goc=goc, goc_wt=goc_wt, dich=khach.kiem_am))
