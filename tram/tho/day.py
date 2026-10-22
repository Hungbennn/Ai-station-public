"""Thợ lưu commit và đưa lên ref tạm của lượt, rồi báo `da-push` (spec 3 §6.4 bước 1–3, 6; §7.4, §7.6). Agent không
push. Phương án (§14, chốt sau S7) theo `chay.day` của `tho.yaml`: nhánh cục bộ `tram/luot/<bead>/<luot>` LUÔN được
đặt trong kho thợ (đủ cho `kho-tho`); `ref-tam` thì thêm `git push --force` ref đó lên origin (credential của tài
khoản quản lý thợ — chỉ được `tram/luot/*`). Kết quả `da-push` tạm (`dang-cong-bo`, `khong-ro`…) thì gửi lại cùng
request_id tới hạn chót."""
import hashlib
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

from tram.cong_bo.nguon import ref_tam_cua
from tram.phieu.mo_hinh import Phieu
from tram.tho.khach import KhachTram, LoiKhachTram
from tram.tho.worktree import DANH_TINH, GIT

KET_QUA_DUT_KHOAT = {"khong-phai-hau-due": "khong-cong-bo", "nhanh-bi-day-ngoai-luong": "ngoai-luong"}


def _git(wt: Path, *args: str, timeout: float = 60, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([*GIT, "-C", str(wt), *args], capture_output=True, text=True, timeout=timeout, check=check)


def luu_wip(wt: Path, thong_diep: str) -> str:
    """Commit mọi thay đổi còn lại (hook tắt) — trả HEAD."""
    if _git(wt, "status", "--porcelain").stdout.strip():
        co_ten = _git(wt, "config", "user.email", check=False).stdout.strip()
        _git(wt, "add", "-A")
        _git(wt, *(() if co_ten else DANH_TINH), "commit", "-q", "-m", thong_diep)
    return _git(wt, "rev-parse", "HEAD").stdout.strip()


def dua_len_ref_tam(wt: Path, phieu: Phieu, commit: str, *, phuong_an: str, timeout: float = 60) -> bool:
    ref = ref_tam_cua(phieu.bead_id, phieu.luot)
    _git(wt, "update-ref", f"refs/heads/{ref}", commit)
    if phuong_an != "ref-tam":
        return True
    try:
        return _git(wt, "push", "--force", "--quiet", "origin", f"{commit}:refs/heads/{ref}", timeout=timeout,
                    check=False).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def giu_nhanh_rac(wt: Path, ten: str, commit: str) -> None:
    """Giữ WIP cục bộ khi không công bố kịp (§7.6) — nhánh `rac/…`, không push."""
    _git(wt, "branch", "-f", ten, commit)


def xoa_ref_tam(wt: Path, phieu: Phieu) -> None:
    _git(wt, "update-ref", "-d", f"refs/heads/{ref_tam_cua(phieu.bead_id, phieu.luot)}", check=False)


def than_da_push(phieu: Phieu, commit: str) -> dict:
    rid = "r-" + hashlib.sha256(f"{phieu.giao_id}:{phieu.luot}:da-push:{commit}".encode()).hexdigest()[:32]
    return {"khe_id": phieu.khe_id, "giao_id": phieu.giao_id, "luot": phieu.luot, "commit": commit,
            "ref_tam": ref_tam_cua(phieu.bead_id, phieu.luot), "request_id": rid}


def day_va_cong_bo(wt: Path, phieu: Phieu, commit: str, *, khach: KhachTram, phuong_an: str, han: float,
                   cho: float = 5.0, ngu: Callable[[float], None] = time.sleep,
                   dung: threading.Event | None = None) -> str:
    """Trả `cong_bo` | `khong-cong-bo` | `ngoai-luong` | `luot-cu` | `chua-cong-bo` (tới `han` — giờ monotonic —
    vẫn chưa xác nhận: trạm giữ snapshot cũ, thợ KHÔNG ghi "đã lưu toàn bộ"). `dung` đặt (luồng đọc hàng đợi đang
    dừng, bs-863.16) → thôi thử lại ngay sau lần đang dở, trả `chua-cong-bo`."""
    than = than_da_push(phieu, commit)
    while True:
        if dung is not None and dung.is_set():
            return "chua-cong-bo"
        if dua_len_ref_tam(wt, phieu, commit, phuong_an=phuong_an, timeout=max(1.0, min(60.0, han - time.monotonic()))):
            try:
                ma, kq = khach.goi("POST", "/api/tho/da-push", than)
            except LoiKhachTram:
                ma, kq = 0, {}
            if ma == 200 and kq.get("cong_bo"):
                return "cong_bo"
            if ma == 200 and kq.get("ly_do") in KET_QUA_DUT_KHOAT:
                return KET_QUA_DUT_KHOAT[kq["ly_do"]]
            if ma in (403, 409):
                return "luot-cu"
        if time.monotonic() + cho >= han:
            return "chua-cong-bo"
        if dung is None:
            ngu(cho)
        else:
            dung.wait(cho)
