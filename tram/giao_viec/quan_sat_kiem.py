"""Quan sát bổ trợ sau mỗi lượt kiểm (3C-D3; C01) — TRẠM tự chạy, không qua sudo, không tin lời `tram-kiem`.

Không phải ranh giới cách ly (ranh giới là hồ sơ Seatbelt của lượt, 3C-D1); là dây báo: thấy tàn dư hoặc không quan
sát được thì ném, `CongLuot` đóng cổng. `tep_ngoai` tìm tệp của `tram-kiem` ở MỌI độ sâu trong vùng ghi-chung (sửa lỗ
`_sot -maxdepth 1` mà Codex nêu: tệp con trong thư mục cha 0777 của user khác), cắt nhánh thư mục user khác mà trạm
không đọc được; `goc_rong` đòi gốc bản chép trống (bản chép, nhà lượt, thứ dời đi đều phải đã dọn); `cron_at` đòi
không có crontab/việc `at` (KHÔNG gỡ — gỡ là việc của Đại ca sau khi xem). Thư mục ghi qua nhóm `staff` ngoài
`GOC_CHUNG` không quan sát — chỉ hồ sơ Seatbelt chặn; `DARWIN_USER_*` dọn ở thu hồi (`thu_muc_he.py`).
3C-D5 (hợp đồng P1 H3): lệnh dưới `tram-kiem` của quan sát đi qua `CongLich` (`mo_cong_kiem` — UID thực đã chứng minh,
`chay_gioi_han` có hạn); không chứng minh được danh tính → `LoiBanChep`, không chạy lệnh lịch nào. Cơ chế `sandbox`:
sudoers ghim hồ sơ cấm exec `crontab`/`atq` cho MỌI lệnh dưới `tram-kiem` — cách quan sát lịch chưa đo (G3) → ném."""
import os
import pwd
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cache_apple import find_quan_sat_duoc
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.ngoai_le_uid import con_uid
from tram.kiem.cong_lich import CongLich, mo_cong_lich
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.principal import USER_RE
FIND = "/usr/bin/find"
GOC_CHUNG = ("/private/tmp", "/private/var/tmp", "/Users/Shared", "/Library/Caches")
HAN = 120


def _ten(ten: str) -> str:
    if not USER_RE.fullmatch(ten):
        raise ValueError(f"tên user không hợp lệ: {ten!r}")
    return ten


def mo_cong_kiem(pk, mo: Callable | None = None) -> CongLich:
    """`CongLich` của `tram-kiem` (P1 H3/H4): lỗi danh tính/thu hồi cây dò → `LoiBanChep` thông báo cố định."""
    try:
        return (mo or mo_cong_lich)(pk.ten, pk.boc_lenh, pk.kill_nhom)
    except (LoiDanhTinh, LoiThuHoi) as e:
        raise LoiBanChep(f"{pk.ten}: không xác minh được UID thực ({type(e).__name__})") from None


def tien_trinh(ten: str, *, chup: Callable = chup_nhan, loc: Callable = con_uid,
               tim: Callable = pwd.getpwnam) -> None:
    """UID lấy từ tài khoản hệ thống; bảng nhân và ngoại lệ D157 chung với thu hồi."""
    _ten(ten)
    try:
        con = loc(tim(ten).pw_uid, chup, ten=ten)
    except (OSError, ValueError, KeyError) as e:
        raise LoiBanChep(f"{ten}: không quan sát được tiến trình: {e}") from None
    if con:
        raise LoiBanChep(f"{ten} còn {len(con)} tiến trình")


def tep_ngoai(ten: str, goc: Path, *, chay: Callable = subprocess.run) -> None:
    """Không còn mục nào của `ten` trong `GOC_CHUNG` (mọi độ sâu, không qua ổ khác); find lỗi → không quan sát được."""
    cat = ["(", "-path", str(goc), "-o", "-type", "d", "!", "-user", _ten(ten), "!", "-perm", "-0005", ")", "-prune"]
    r = chay([FIND, "-x", *GOC_CHUNG, *cat, "-o", "-user", ten, "-print"], capture_output=True, text=True, timeout=HAN)
    muc = [x for x in r.stdout.splitlines() if x.strip()]
    if not find_quan_sat_duoc(r) or (r.stdout and not muc):
        raise LoiBanChep(f"find vùng ghi-chung mã {r.returncode} — không quan sát được tệp của {ten}")
    if muc:
        raise LoiBanChep(f"{ten} còn {len(muc)} mục ngoài bản chép (vùng ghi-chung, kể cả thư mục cha khác owner)")


def goc_rong(goc: Path) -> None:
    """Gốc bản chép không còn mục nào: lượt trước đã dọn cả bản chép lẫn nhà của lượt, không dời gì sang chỗ khác."""
    try:
        con = os.listdir(goc)
    except OSError as e:
        raise LoiBanChep(f"không đọc được gốc bản chép {goc}: {e.strerror}") from e
    if con:
        raise LoiBanChep(f"gốc bản chép còn {len(con)} mục của lượt trước — chưa dọn")


def _ra_lich(chay: Callable, argv: list[str]):
    try:
        return chay(argv, capture_output=True, text=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
        raise LoiBanChep(f"lệnh quan sát lịch không xác nhận được ({type(e).__name__})") from None


def cron_at(pk, *, chay: Callable | None = None) -> None:
    """`tram-kiem` không có crontab (`crontab -l` mã 1, "no crontab for") và không có việc `at` (`atq` rỗng; trạm tự
    tìm tệp của nó trong `/usr/lib/cron/jobs`). Thấy hay không chắc → ném; không tự gỡ để quan sát không bị xoá dấu."""
    if pk.co_che == "sandbox":
        raise LoiBanChep(f"{pk.ten}: cơ chế sandbox cấm exec crontab/atq — chưa đo cách quan sát lịch (G3), cổng đóng")
    chay = chay or mo_cong_kiem(pk)
    r = _ra_lich(chay, pk.boc_lenh(["/usr/bin/crontab", "-l"]))
    if r.returncode != 1 or "no crontab for" not in r.stderr:
        raise LoiBanChep(f"{pk.ten}: crontab -l mã {r.returncode} — có crontab hoặc không xác nhận được")
    for argv in (pk.boc_lenh(["/usr/bin/atq"]), [FIND, "/usr/lib/cron/jobs", "-user", _ten(pk.ten)]):
        r = _ra_lich(chay, argv)
        if r.returncode or r.stdout.strip():
            raise LoiBanChep(f"{pk.ten}: {argv[-1] if argv[0] == FIND else 'atq'} mã {r.returncode} — có việc at "
                             "hoặc không xác nhận được")


def launchd(pk, *, doc: Callable | None = None) -> None:
    """Khung quan sát launchd của `tram-kiem` (3C-D6; C01 hàng 20–22: `user/<uid>`, `gui/<uid>`, `login/<asid>`).
    Không có bộ đọc `doc(pk)` thì ném — cổng giữ đóng. Bộ đọc đã đo: `launchd_kiem.doc_launchd` (3C-D7, fixture là đầu
    ra thật G3.3), `cong_that.dung_cong` truyền vào; không viết parser đoán."""
    if doc is None:
        raise LoiBanChep("quan sát launchd user/gui/login của tram-kiem chưa có — G3 chưa đo định dạng launchctl print")
    doc(pk)


def env_kin(cac_du_an: Callable[[], list]) -> None:
    for da in cac_du_an():
        mt = da.moi_truong_kiem
        if mt is None:
            continue
        try:
            st = mt.file.stat()
        except OSError as e:
            raise LoiBanChep(f"{da.ten}: không đọc được tệp môi trường kiểm: {e.strerror}") from e
        if st.st_uid != os.getuid() or st.st_mode & 0o077:
            raise LoiBanChep(f"{da.ten}: tệp môi trường kiểm phải 0600 của trạm (tram-kiem đọc được env lượt khác)")
