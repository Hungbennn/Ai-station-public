"""Thư mục riêng `DARWIN_USER_DIR/TEMP_DIR/CACHE_DIR` của `tram-kiem` (`/var/folders/…`, 0700 — trạm không đọc được):
phần còn giữ của r47 T11 (C01 hàng 6, sửa dot6-Q01). Hồ sơ Seatbelt của lượt cấm ghi ở đây; bước này dọn thứ do lệnh
NGOÀI hồ sơ (trạm chạy `kill`, `crontab -l`, `getconf` dưới `tram-kiem`) để lại, rồi xác nhận rỗng. Mỗi bước chạy dưới
`tram-kiem` qua `chay` (`CongLich` — UID đã chứng minh, có hạn): `getconf` → `ls` → gỡ cờ/quyền → `rm` → `ls` lại.
MÃ LỖI của bất kỳ bước nào (kể cả khi stdout trông hợp lệ hay rỗng), đường dẫn không đúng dạng
`/var/folders/<a>/<b>/{0,T,C}`, còn mục → `LoiBanChep`: cổng giữ đóng. Xoá TRƯỚC khi quan sát nội dung là đánh đổi có
ghi (G3.6 đo thứ hệ thống tự tạo ở đây; sau đó mới quyết "còn mục lạ → đóng cổng"). Cơ chế `sandbox`: sudoers ghim hồ sơ
cấm ghi ở đây cho MỌI lệnh dưới `tram-kiem` (kể cả `rm` của trạm) → bỏ qua, không có gì của lượt ghi được vào."""
import re
import subprocess
from collections.abc import Callable

from tram.giao_viec.ban_chep import LoiBanChep
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi

CHFLAGS, CHMOD, GETCONF, LS, RM = "/usr/bin/chflags", "/bin/chmod", "/usr/bin/getconf", "/bin/ls", "/bin/rm"
THU_MUC_HE = ("DARWIN_USER_DIR", "DARWIN_USER_TEMP_DIR", "DARWIN_USER_CACHE_DIR")
HAN = 120
DUONG = re.compile(r"/(private/)?var/folders/[\w+-]+/[\w+-]+/[0TC]")
# Đo 20/10: macOS tự tạo `com.apple.*` ở đây (data vault SIP khoá cả chủ). Lượt không ghi được vào đây (Seatbelt),
# nên mọi `com.apple.*` là của hệ thống → bỏ qua, không xoá, không xét (Đại ca: "của Apple thì bỏ qua").
APPLE = "com.apple."


def _ra(chay: Callable, argv: list[str]):
    try:
        return chay(argv, capture_output=True, text=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
        raise LoiBanChep(f"lệnh dọn DARWIN_USER_* không xác nhận được ({type(e).__name__})") from None


def _liet_ke(pk, chay, p, bien):
    x = _ra(chay, pk.boc_lenh([LS, "-1A", p]))
    if x.returncode:
        raise LoiBanChep(f"không liệt kê được {bien} của {pk.ten} (ls mã {x.returncode})")
    return [d for d in (x.stdout or "").split("\n") if d]


def don_thu_muc_he(pk, chay: Callable) -> None:
    if pk.co_che == "sandbox":
        return
    for bien in THU_MUC_HE:
        g = _ra(chay, pk.boc_lenh([GETCONF, bien]))
        p = (g.stdout or "").strip().rstrip("/")
        if g.returncode or not DUONG.fullmatch(p):
            raise LoiBanChep(f"không xác nhận được {bien} của {pk.ten} (getconf mã {g.returncode})")
        xoa = [f"{p}/{t}" for t in _liet_ke(pk, chay, p, bien) if not t.startswith(APPLE)]
        if xoa:     # đồ chỉ-đọc / cờ uchg của chính tram-kiem: gỡ trước; mã lỗi không chặn, quyết ở rm + liệt kê lại
            _ra(chay, pk.boc_lenh([CHFLAGS, "-R", "nouchg,nouappnd", "--", *xoa]))
            _ra(chay, pk.boc_lenh([CHMOD, "-R", "u+rwX", "--", *xoa]))
            x = _ra(chay, pk.boc_lenh([RM, "-rf", "--", *xoa]))
            if x.returncode:
                loi = (x.stderr or "")[-300:]
                raise LoiBanChep(f"không dọn được {bien} của {pk.ten} (rm mã {x.returncode}): {loi}")
        if any(not t.startswith(APPLE) for t in _liet_ke(pk, chay, p, bien)):
            raise LoiBanChep(f"{bien} của {pk.ten} chưa rỗng sau khi dọn")
