import os
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tram.bao_tin.telegram import KEYCHAIN_TELEGRAM
from tram.chu.dich_vu_tram import DICH_VU_TRAM, HAN_LENH_GIAY, bien_nhan, canh_bao_quet, chon, tep_dich_vu
from tram.chu.launchd import NHAN_BAO_TIN
from tram.chu.siet_quyen import siet
from tram.duong_dan import tram_home
from tram.keychain import LoiKeychain, co_muc
from tram.llm.claude import KEYCHAIN_DICH_VU

LENH_TAILSCALE_SERVE = ["tailscale", "serve", "--bg", "--https=443", "http://127.0.0.1:7700"]


@dataclass
class KeHoach:
    tep: dict[Path, bytes]
    lenh: list[list[str]]
    canh_bao: list[str]
    buoc: list[tuple[str, Callable[[], None]]] = field(default_factory=list)   # chạy trước các lệnh
    han_lenh: float | None = None                      # bs-2bd.1.23: hạn mỗi lệnh (None: như cũ, không hạn)
    han_rieng: dict[tuple[str, ...], float] = field(default_factory=dict)   # tiền tố lệnh → hạn riêng (tải mô hình…)


def _co_keychain(dich_vu: str) -> bool:
    """Ném `LoiKeychain` khi không kiểm được — `tao_token_nho` không tạo khoá khi chưa biết đã có hay chưa."""
    return co_muc(dich_vu)


def _thieu_keychain(dich_vu: str) -> bool:
    try:
        return not _co_keychain(dich_vu)
    except LoiKeychain:                     # Keychain khoá/treo: cảnh báo như thiếu, Đại ca kiểm lại sau đăng nhập
        return True


def _canh_bao() -> list[str]:
    cb = []
    if not shutil.which("tailscale") and not Path("/Applications/Tailscale.app").exists():
        cb.append("Chưa thấy Tailscale — Đại ca cài và đăng nhập trước (#5, chưa duyệt).")
    if _thieu_keychain(KEYCHAIN_DICH_VU):
        cb.append(f"Chưa có API key trong Keychain. Đại ca tự chạy: "
                  f"security add-generic-password -s {KEYCHAIN_DICH_VU} -a tram -w")
    thieu_tin = _thieu_keychain(KEYCHAIN_TELEGRAM)
    if thieu_tin:
        cb.append(f"Chưa có token bot Telegram. Đại ca tự tạo bot (@BotFather) rồi chạy: "
                  f"security add-generic-password -s {KEYCHAIN_TELEGRAM} -a tram -w")
    if not (tram_home() / "cau-hinh.yaml").exists():
        thieu_tin = True
        cb.append("Chưa có ~/.tram/cau-hinh.yaml (dai_ca_logins, ten_may_b, telegram.chat_id, dashboard_url) — "
                  "dashboard chỉ đọc, không báo tin.")
    if thieu_tin:
        cb.append("tram-bao-tin thoát ngay (mã 0) khi chưa có token / chat_id và launchd không tự bật lại. Cấu hình "
                  f"xong, Đại ca chạy: launchctl kickstart -k gui/{os.getuid()}/{NHAN_BAO_TIN}")
    try:
        ngu = subprocess.run(["pmset", "-g"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        ngu, cb = "", cb + ["Không đọc được `pmset -g` trong 10 giây — Đại ca tự kiểm chế độ ngủ."]
    if any(l.split()[:1] == ["sleep"] and l.split()[1] != "0" for l in ngu.splitlines() if l.strip()):
        cb.append("Máy đang bật chế độ ngủ — Đại ca tắt trong System Settings → Energy.")
    if not shutil.which("bd"):
        cb.append("Không thấy `bd` trong PATH.")
    cb.append("Mở dashboard trong tailnet — Đại ca tự chạy khi #5 được duyệt (kiểm cú pháp với bản Tailscale "
              "trên máy B): " + " ".join(LENH_TAILSCALE_SERVE))
    return cb


def lap_ke_hoach(*, uv: str, repo: Path, dich_vu: list[str] | None) -> KeHoach:
    """bs-2bd.1.23: chỉ dịch vụ Đại ca chọn, không mặc định; siết quyền ~/.tram trước khi nạp; mỗi lệnh có hạn."""
    ds, la, log = chon(dich_vu), Path(os.environ["HOME"]) / "Library/LaunchAgents", tram_home() / "log"
    cb = canh_bao_quet() if "quet" in ds else []           # LoiCaiDat: dừng trước khi lập kế hoạch
    tep = {la / f"{DICH_VU_TRAM[t]}.plist": tep_dich_vu(t, uv=uv, repo=repo, log=log) for t in ds}
    plist = list(tep)
    tep.update(bien_nhan(p.stem, p, tep[p]) for p in plist)   # bs-2bd.1.17: chứng cứ sở hữu cho go-dich-vu
    mien = f"gui/{os.getuid()}"
    lenh = [["mkdir", "-p", str(log)]]
    for p in plist:
        lenh += [["launchctl", "bootout", f"{mien}/{p.stem}"], ["launchctl", "bootstrap", mien, str(p)]]
    buoc = [("Siết quyền ~/.tram của trạm chủ về 700/600 (bs-2bd.1.4)", lambda: siet(tram_home()) and None)]
    return KeHoach(tep=tep, lenh=lenh, canh_bao=_canh_bao() + cb, buoc=buoc, han_lenh=HAN_LENH_GIAY)


def in_ke_hoach(kh: KeHoach) -> str:
    dong = ["Sẽ ghi các file:"] + [f"  - {p}" for p in kh.tep]
    if kh.buoc:
        dong += ["Sẽ làm trước các lệnh:"] + [f"  - {mo_ta}" for mo_ta, _ in kh.buoc]
    dong += ["Sẽ chạy các lệnh:"] + [f"  - {' '.join(c)}" for c in kh.lenh]
    dong += ["Cảnh báo (Đại ca tự xử lý, trạm không đổi cài đặt hệ thống):"]
    dong += [f"  - {c}" for c in kh.canh_bao or ["không có"]]
    dong += ["Trạm không tự cập nhật. Lúc chạy chỉ gọi ra ngoài tới: Claude API, api.telegram.org, GitHub (Q15)."]
    return "\n".join(dong)


BO_QUA_LOI = (("launchctl", "bootout"), ("pkill",))      # lệnh dọn: "không có gì để dọn" không phải lỗi


def bo_qua_loi(c: list[str]) -> bool:
    """`launchctl bootout` (dịch vụ chưa nạp) và `pkill` (không có tiến trình) — kể cả khi chạy qua `sudo` (lát 3c)."""
    c = c[1:] if c[:1] == ["sudo"] else c
    return any(tuple(c[:len(t)]) == t for t in BO_QUA_LOI)


def thuc_hien(kh: KeHoach, *, chay=subprocess.run) -> None:
    for p, noi_dung in kh.tep.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(noi_dung)
    for _, ham in kh.buoc:
        ham()
    for c in kh.lenh:                      # quá hạn → subprocess.TimeoutExpired: dừng, lệnh sau không chạy
        han = next((h for t, h in kh.han_rieng.items() if tuple(c[:len(t)]) == t), kh.han_lenh)
        chay(c, check=not bo_qua_loi(c), **({"timeout": han} if han else {}))
