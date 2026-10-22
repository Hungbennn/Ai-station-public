"""Bảng sẵn sàng chạy thật cho trang Cài đặt (D19, D38/Q13; khảo sát §1.10 A2). CHỈ ĐỌC.

Hai nguồn: (b) bead của REPO TRẠM có nhãn `san-sang` (`Bd(goc_repo()).tat_ca()`, bộ đệm 60 giây) — closed → dat; mở
và bị `blocks` bởi bead chưa đóng → cho ("cần <id>"); còn lại → thieu; chỉ trả tiêu đề đã làm sạch, KHÔNG mô tả/notes.
(a) tự kiểm rẻ: lệnh trong PATH (`shutil.which`), dịch vụ đã cài, Keychain (`DocHeThong`, có bộ đệm riêng).
KHÔNG BAO GIỜ gọi `tram tho kiem` / `tram giao kiem` (có sudo, touch, sleep — khảo sát §1.10 mục 5)."""
import shutil
import subprocess
import threading
import time
from collections.abc import Callable, Sequence

from tram.beads.bd import Bd, LoiBd
from tram.beads.mo_hinh import Bead
from tram.chu.launchd import NHAN_API, NHAN_BAO_TIN, NHAN_NHO, NHAN_QUET
from tram.duong_dan import bay_gio, goc_repo
from tram.suy.he_thong import GIAY_CHO, DocHeThong
from tram.suy.lam_sach import lam_sach

NHAN_SAN_SANG = "san-sang"
LENH = ("bd", "tailscale", "gh", "codex", "claude", "gitnexus", "uv", "ollama")
DICH_VU_CAN = (NHAN_API, NHAN_QUET, NHAN_NHO, NHAN_BAO_TIN)
GIAY_BEAD = 60
LOI_BEAD = "Không đọc được bead của repo trạm (bd) — bảng chỉ còn phần tự kiểm"
GHI_KEYCHAIN = {"co": ("dat", ""), "chua": ("thieu", "chưa có trong Keychain"),
                "khong_ro": ("thieu", "không kiểm được (Keychain khoá?)")}


def _chay_bd(args: Sequence[str]) -> str:
    """Runner chỉ đọc cho `Bd`: timeout 3 giây; câu lỗi cố định, không mang stderr."""
    try:
        kq = subprocess.run(["bd", *args], capture_output=True, text=True, timeout=GIAY_CHO, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        raise LoiBd("bd không chạy được") from None
    if kq.returncode != 0:
        raise LoiBd("bd trả mã lỗi")
    return kq.stdout


def doc_bead_tram() -> list[Bead]:
    return Bd(goc_repo(), runner=_chay_bd).tat_ca()


def _muc(ma: str, ten: str, tt: str, ghi_chu: str, nguon: str) -> dict:
    return {"ma": ma, "ten": ten, "trang_thai": tt, "ghi_chu": ghi_chu, "nguon": nguon}


def tu_bead(ds: list[Bead]) -> list[dict]:
    dong = {b.id for b in ds if b.status == "closed"}
    ra = []
    for b in ds:
        if NHAN_SAN_SANG not in b.labels:
            continue
        # phụ thuộc `blocks` vào bead chưa đóng (kể cả mã không còn trong danh sách) → chưa tới lượt
        can = [lam_sach(p.depends_on_id, 64) for p in b.phu_thuoc if p.loai == "blocks" and p.depends_on_id not in dong]
        if b.status == "closed":
            tt, ghi = "dat", ""
        elif can:
            tt, ghi = "cho", "cần " + ", ".join(can[:3])
        else:
            tt, ghi = "thieu", ""
        ra.append(_muc(lam_sach(b.id, 64), lam_sach(b.title, 120), tt, ghi, "bead"))
    return ra


def _ghi_dich_vu(d: dict) -> str:
    if not d["da_cai"]:
        return "chưa có plist trong ~/Library/LaunchAgents"
    if d["dang_chay"]:
        return ""
    return "đã cài, chưa chạy" if d["kiem_duoc"] else "không kiểm được launchctl"


def tu_kiem(he: DocHeThong, which: Callable[[str], object] = shutil.which) -> list[dict]:
    ra = []
    for l in LENH:
        co = bool(which(l))
        ra.append(_muc(f"lenh:{l}", f"Có lệnh {l} trong PATH", "dat" if co else "thieu",
                       "" if co else "không thấy trong PATH của tram-api", "tu_kiem"))
    for d in he.dich_vu():
        if d["nhan"] in DICH_VU_CAN:
            ra.append(_muc(f"dich-vu:{d['nhan']}", f"Đã cài {d['nhan']}", "dat" if d["da_cai"] else "thieu",
                           _ghi_dich_vu(d), "tu_kiem"))
    for k in he.keychain():
        ra.append(_muc(f"keychain:{k['ten']}", f"Keychain có {k['ten']}", *GHI_KEYCHAIN[k["trang_thai"]], "tu_kiem"))
    return ra


class BangSanSang:
    def __init__(self, *, doc_bead: Callable[[], list[Bead]] = doc_bead_tram,
                 which: Callable[[str], object] = shutil.which, dong_ho: Callable[[], float] = time.monotonic):
        self._doc_bead, self._which, self._dong_ho = doc_bead, which, dong_ho
        self._nho: tuple[float, list[dict], str | None, str] | None = None
        self._khoa = threading.Lock()

    def _bead(self) -> tuple[list[dict], str | None, str]:
        with self._khoa:
            bay = self._dong_ho()
            if self._nho is None or bay - self._nho[0] >= GIAY_BEAD:
                try:
                    muc, loi = tu_bead(self._doc_bead()), None
                except Exception:                          # không đưa câu lỗi bd ra ngoài
                    muc, loi = [], LOI_BEAD
                self._nho = (bay, muc, loi, bay_gio())
            return [dict(m) for m in self._nho[1]], self._nho[2], self._nho[3]

    def lay(self, he: DocHeThong) -> dict:
        muc, loi, luc = self._bead()
        muc += tu_kiem(he, self._which)
        return {"muc": muc, "dem": {k: sum(m["trang_thai"] == k for m in muc) for k in ("dat", "thieu", "cho")},
                "doc_luc": luc, "loi": loi}


CHUNG = BangSanSang()                                       # dùng chung cả tiến trình; test thay bằng monkeypatch
