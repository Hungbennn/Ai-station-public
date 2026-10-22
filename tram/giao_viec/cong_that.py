"""Cổng lượt THẬT của trạm (3C-D4/D5; C01, D45): ghép thu hồi + mọi quan sát vào `CongLuot`.

Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tram-kiem` đã chứng minh — không tin env/argv), rồi
`kill -KILL -1` dưới principal qua `chay_gioi_han` (hạn hữu hạn, sở hữu cây; giết mọi tiến trình cùng UID, kể cả
`setsid`). Mã thoát không là bằng chứng: TRẠM chụp bảng nhân, lọc ngoại lệ D157 tới khi hết tàn dư UID;
rồi dọn + xác nhận rỗng `DARWIN_USER_*` của `tram-kiem` (`thu_muc_he`, phần còn giữ của r47 T11).
KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
Seatbelt đúng TỪNG BYTE bản sinh từ manifest root (V2-5), tệp môi trường kiểm của mọi dự án kín (0600, của trạm),
launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>` — 3C-D7: bộ đọc CHỈ cho định dạng đo ở G3, `launchd_kiem`; lệch
hay thiếu bằng chứng G3.9 đúng ngữ cảnh thì ném, cổng giữ đóng; I1 KHÔNG bật `giao_viec.bat`)."""
import os
import stat
import subprocess
import time
from collections.abc import Callable
from functools import partial
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.launchd_kiem import doc_launchd
from tram.giao_viec.quan_sat_kiem import (HAN, cron_at, env_kin, goc_rong, launchd, mo_cong_kiem, tep_ngoai,
                                         tien_trinh)
from tram.giao_viec.thu_muc_he import don_thu_muc_he
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.ngoai_le_uid import con_uid
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.kiem_python import kiem_prefix
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, ho_so_tu_manifest

GIET = ["/bin/kill", "-KILL", "-1"]
HAN_HET = 5.0
HO_SO_TOI_DA = 65536


def cho_het_uid(uid: int, *, chup: Callable = chup_nhan, han: float = HAN_HET,
                ngu: Callable = time.sleep, loc: Callable = con_uid, ten: str | None = None) -> None:
    """Bảng nhân + D157: chờ tàn dư hết; build chưa đo hoặc ảnh lỗi → cổng đóng."""
    het = time.monotonic() + han
    while True:
        try:
            con = loc(uid, chup, ten=ten)
        except (OSError, ValueError) as e:
            raise LoiBanChep(f"không chụp được bảng tiến trình: {e}") from None
        if not con:
            return
        if time.monotonic() >= het:
            raise LoiBanChep(f"còn {len(con)} tiến trình uid {uid} sau kill -1 (setuid hoặc kẹt nhân)")
        ngu(0.2)


def thu_hoi_theo_uid(pk, *, mo_cong: Callable | None = None, cho_het: Callable[[int], None] | None = None,
                     don_he: Callable = don_thu_muc_he) -> None:
    """UID thực (3C-B) → `kill -KILL -1` dưới `tram-kiem` có hạn (P1) → ảnh chụp không còn ai → dọn `DARWIN_USER_*`.
    Lỗi bất kỳ bước nào → ném (cổng đóng)."""
    cong = mo_cong_kiem(pk, mo_cong)
    try:
        cong(pk.boc_lenh(GIET), capture_output=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:      # P1 H4: thông báo cố định, là OSError
        raise LoiBanChep(f"{pk.ten}: kill -1 không xác nhận được ({type(e).__name__})") from None
    (cho_het or partial(cho_het_uid, ten=pk.ten))(cong.uid)
    don_he(pk, cong)


def doc_tep_root(p: Path, *, chu: int = 0, lstat: Callable = os.lstat, fstat: Callable = os.fstat) -> bytes:
    """File của root: mọi thư mục cha thật, của `chu`, không ai khác ghi; mở O_NOFOLLOW, `fstat` CHÍNH fd đó."""
    try:
        for cha in reversed(p.parents):
            st = lstat(cha)
            if not stat.S_ISDIR(st.st_mode) or st.st_uid != chu or st.st_mode & 0o022:
                raise LoiBanChep(f"thư mục cha của {p.name} không do root giữ riêng — cài lại (`tram chu cai-dat-tho`)")
        fd, du_lieu = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), b""
        try:
            st = fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_uid != chu or st.st_mode & 0o022:
                raise LoiBanChep(f"{p.name} sai chủ/quyền/loại — cài lại bằng `tram chu cai-dat-tho`")
            while len(du_lieu) <= HO_SO_TOI_DA and (k := os.read(fd, 65536)):
                du_lieu += k
        finally:
            os.close(fd)
    except LoiBanChep:
        raise
    except OSError as e:
        raise LoiBanChep(f"không đọc được {p.name}: {e.strerror}") from None
    if len(du_lieu) > HO_SO_TOI_DA:
        raise LoiBanChep(f"{p.name} quá lớn — cài lại bằng `tram chu cai-dat-tho`")
    return du_lieu


def ho_so_cai(goc: Path, p: Path = HO_SO_KIEM, mf: Path = MANIFEST_KIEM, *, chu: int = 0, lstat: Callable = os.lstat,
              fstat: Callable = os.fstat) -> None:
    """V2-5 (dot7-Q04): hồ sơ đã cài ĐÚNG từng byte bản sinh lại từ manifest root (không tìm chuỗi); input manifest
    khớp cấu hình hiện hành (TRAM_HOME, gốc bản chép). Thiếu/lệch/sai chủ → `LoiBanChep`, cổng đóng, cài lại."""
    doc = partial(doc_tep_root, chu=chu, lstat=lstat, fstat=fstat)
    try:
        m, mong = ho_so_tu_manifest(doc(mf))
    except ValueError as e:
        raise LoiBanChep(str(e)) from None
    if (m["tram_home"], m["goc"]) != (str(tram_home()), str(goc)):
        raise LoiBanChep("manifest hồ sơ cài cho TRAM_HOME/gốc bản chép khác cấu hình hiện hành — cài lại")
    if doc(p) != mong:
        raise LoiBanChep(f"hồ sơ {p} khác bản đã duyệt (sinh lại từ manifest) — cài lại bằng `tram chu cai-dat-tho`")


def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
              thu_hoi: Callable[[], None] | None = None) -> CongLuot:
    goc = goc or tram_home() / "kiem"
    return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
                    quan_sat=[kiem_prefix, partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc),
                              partial(goc_rong, goc),
                              partial(cron_at, pk), partial(ho_so_cai, goc), partial(env_kin, cac_du_an),
                              partial(launchd, pk, doc=doc_launchd)])
