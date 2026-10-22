"""Bộ đọc launchd của `tram-kiem` (3C-D7; C01 hàng 20–22) CHỈ cho bố cục đo ở G3 (`launchd_dinh_dang`); lệch bố cục,
mã lạ, thiếu mốc hay thiếu bằng chứng cho ngữ cảnh hiện hành → ném, cổng đóng. Dây báo, không phải ranh giới
(Seatbelt, G4). `user/<uid>`: miền RIÊNG của tram-kiem — dịch vụ ngoài mốc, khối trạng thái có dòng → ném; thiếu
khối bắt buộc = không quan sát được. `gui/<uid>`: chỉ mã 125 đã đo là sạch. `login/<asid>` là phiên của NGƯỜI GỌI
sudo (G3: phiên Aqua của người vận hành, uid 501), không ghi uid từng mục → không quy được → KHÔNG in; chỉ đi tiếp
khi `BANG_CHUNG_LOGIN` có ĐÚNG ngữ cảnh hiện hành (`ngu_canh_kiem`, G3.9 — launchd từ chối tram-kiem ghi vào đó),
kiểm TRƯỚC mọi lệnh. Mốc (D45: chỉ hỗ trợ, không là bằng chứng) theo build. G3 ghi `2>&1` → đọc gộp stdout+stderr."""
import re
import subprocess
from collections.abc import Callable

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.launchd_dinh_dang import BAT_BUOC_USER, DONG_DV, tach
from tram.giao_viec.ngu_canh_kiem import NguCanh, ngu_canh_hien_hanh
from tram.giao_viec.launchd_moc import DONG_ENDPOINT, MAU_USER, MOC_USER  # noqa: F401 — mốc D68, D157
from tram.giao_viec.quan_sat_kiem import HAN, mo_cong_kiem
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi

LAUNCHCTL = "/bin/launchctl"
GUI_KHONG = "Could not print domain: 125: Domain does not support specified action"
PHAI_RONG = ("unmanaged processes", "endpoints", "externally-hosted endpoints", "environment", "disabled services")
BANG_CHUNG_LOGIN: frozenset[NguCanh] = frozenset()             # ngữ cảnh đã đạt G3.9 — chưa đo


def xet_user(van_ban: str, uid: int, moc: frozenset[str], *, bat_job: bool = True) -> None:
    ten = f"user/{uid}"
    try:
        k = tach(van_ban, ten)
        if any(x not in k for x in BAT_BUOC_USER):
            raise ValueError("thiếu khối/khoá bắt buộc")
        ports = (rf"\t\t\t +0x[0-9a-f]+ 4 +bootstrap  com\.apple\.xpc\.launchd\.domain\.user\.{uid}\n"
                 r"\t\t\t +0x[0-9a-f]+ 9 +access  \(unknown\)")
        if not re.fullmatch(ports, "\n".join(k["task-special ports"])):
            raise ValueError("task-special ports khác bản đã đo")
        dv = [DONG_DV.fullmatch(d) for d in k["services"]]
        if (k["type"], k["handle"], k["session"]) != ("user", str(uid), "Background") or not all(dv) or \
                not re.fullmatch(rf"\t\tuid = {uid}\n\t\tasid = \d+", "\n".join(k["security context"])):
            raise ValueError("danh tính miền")
    except ValueError:
        raise LoiBanChep(f"{ten}: định dạng launchctl print khác bản đã đo — không quan sát được, cổng đóng") from None
    # Đại ca 20/10: dịch vụ ngoài mốc (macOS tự bật, đổi theo bản cập nhật) loại ra; chặn job là việc của Seatbelt
    # (`deny job-creation`, đối chứng G4 đạt). Cổng thật gọi `bat_job=False`; kịch bản đo G3 giữ mặc định.
    la = [m[1] for m in dv if m[1] not in moc and not MAU_USER.fullmatch(m[1])] if bat_job else []
    if la:
        raise LoiBanChep(f"{ten}: {len(la)} dịch vụ launchd ngoài mốc — tram-kiem có job (C01 hàng 20)")
    for x in PHAI_RONG:
        if x == "endpoints" and all(DONG_ENDPOINT.fullmatch(d) for d in k.get(x, ())):
            continue
        if k.get(x):
            raise LoiBanChep(f"{ten}: khối '{x}' có {len(k[x])} dòng — tram-kiem để lại trạng thái launchd")


def _ra(cong: Callable, argv: list[str]) -> tuple[int, str]:
    try:
        r = cong(argv, capture_output=True, text=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
        raise LoiBanChep(f"launchctl print dưới tram-kiem không xác nhận được ({type(e).__name__})") from None
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _ngu_canh(pk, ngu_canh: Callable[[str], NguCanh]) -> NguCanh:
    try:
        return ngu_canh(pk.ten)
    except (KeyError, OSError, ValueError, AttributeError):
        raise LoiBanChep("không xác định được ngữ cảnh vận hành (bản macOS, máy, UID, phiên) — cổng đóng") from None


def doc_launchd(pk, *, chay: Callable | None = None, ngu_canh: Callable[[str], NguCanh] = ngu_canh_hien_hanh,
                moc: dict | None = None, bang_chung: frozenset | None = None) -> None:
    """Bộ đọc cho `quan_sat_kiem.launchd(pk, doc=…)`: sạch thì trả; thấy, lệch hay không chắc → `LoiBanChep`."""
    if pk.co_che == "sandbox":
        raise LoiBanChep(f"{pk.ten}: cơ chế sandbox cấm exec launchctl (G3.2) — không quan sát được launchd, cổng đóng")
    nc = _ngu_canh(pk, ngu_canh)
    moc_user = (MOC_USER if moc is None else moc).get(nc.ban)
    if moc_user is None:
        raise LoiBanChep(f"chưa có mốc launchd cho macOS {nc.ban} — đo lại (G3.3, G3.8) rồi ghi mốc")
    if nc not in (BANG_CHUNG_LOGIN if bang_chung is None else bang_chung):
        raise LoiBanChep("login/<asid>: chưa có bằng chứng G3.9 cho ngữ cảnh này (bản macOS, máy, UID, phiên) — không "
                         "quy được mục nào về tram-kiem, cổng đóng")
    cong = chay or mo_cong_kiem(pk)
    if cong.uid != nc.uid_kiem:
        raise LoiBanChep(f"{pk.ten}: UID đã chứng minh khác UID của ngữ cảnh — cổng đóng")
    ma, ra = _ra(cong, pk.boc_lenh([LAUNCHCTL, "print", f"user/{cong.uid}"]))
    if ma:
        raise LoiBanChep(f"user/{cong.uid}: launchctl print mã {ma} — không quan sát được")
    xet_user(ra, cong.uid, moc_user, bat_job=False)
    ma, ra = _ra(cong, pk.boc_lenh([LAUNCHCTL, "print", f"gui/{cong.uid}"]))
    if ma == 0:
        raise LoiBanChep(f"gui/{cong.uid}: tram-kiem có miền GUI — chưa đo, không được có (cổng đóng)")
    if ma != 125 or ra.strip() != GUI_KHONG:                          # chỉ dạng "không có miền" đã đo là sạch
        raise LoiBanChep(f"gui/{cong.uid}: launchctl print mã {ma} — không quan sát được")
