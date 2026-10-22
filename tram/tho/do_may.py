"""Dò máy thợ — CHỈ ĐỌC, không đổi gì (spec 3 §9.2, §9.3; kiến trúc §7 "Mac thợ").

- CLI: đường dẫn + `--version` (không đụng credential). Đăng nhập CHỈ dò DƯỚI principal của khe (bs-863.17):
  `dang_nhap_codex` — `codex login status` qua `boc`/`kill` của principal, env dựng mới PATH/LANG/CODEX_HOME (không
  HOME/token của quản lý; mã 0 = đã đăng nhập — chờ spike S5). Claude: lệnh trạng thái chốt ở S2 (`kiem_cong`). Không
  bao giờ mở file đăng nhập, không chép đầu ra lệnh trạng thái (có thể chứa email tài khoản).
- Tailscale: Mac thợ phải là thiết bị GẮN TAG (#3) — đọc `tailscale status --json` → `Self.Tags`. Trạm không tự gắn tag,
  không chạy `tailscale up`; chưa gắn thì Đại ca làm trong trang quản trị Tailscale."""
import json
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han

TAG_THO = "tag:tram-tho"
DUONG_TAILSCALE_APP = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
BIEN_THU_MUC = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME"}


@dataclass(frozen=True)
class KetQuaDo:
    cli: str
    duong_dan: str | None
    phien_ban: str
    dang_nhap: bool | None          # None = chưa kiểm được
    chi_tiet: str


def do_cli(cli: str, thu_muc: Path, *, which=shutil.which, chay=subprocess.run) -> KetQuaDo:
    duong = which(cli)
    if duong is None:
        return KetQuaDo(cli, None, "", None, f"không thấy `{cli}` trong PATH")
    v = chay([duong, "--version"], capture_output=True, text=True, timeout=20)
    phien = ((v.stdout or v.stderr or "").strip().splitlines() or [""])[0][:80]
    return KetQuaDo(cli, duong, phien, None, "đăng nhập chỉ dò dưới principal của khe (`tram tho kiem`) — không dò "
                    f"dưới tài khoản quản lý; thư mục đăng nhập của khe: {BIEN_THU_MUC[cli]}={thu_muc}")


def dang_nhap_codex(pr, codex: str, thu_muc: Path, *, path: str, chay: Callable = chay_gioi_han
                    ) -> tuple[bool | None, str]:
    """(True | False | None = không kết luận, chi tiết) — `pr` là principal ĐÃ xác minh UID (người gọi). `LoiThuHoi`
    NỔI LÊN (review vòng 1 A05): người gọi phải thôi mọi thăm dò khác dưới principal này."""
    env = {"PATH": path, "LANG": "C.UTF-8", "CODEX_HOME": str(thu_muc)}
    try:
        s = chay(pr.boc([codex, "login", "status"]), kill=pr.kill_nhom, capture_output=True, text=True, timeout=20,
                 env=env)
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, f"không kết luận: không chạy được `codex login status` dưới principal ({type(e).__name__})"
    if s.returncode == 0:
        return True, "đã đăng nhập (`codex login status` mã 0, dưới principal của khe)"
    return False, (f"chưa đăng nhập (`codex login status` mã {s.returncode}) — Đại ca đăng nhập tay dưới principal "
                   f"của khe với CODEX_HOME={thu_muc}")


def kiem_tag(*, which=shutil.which, chay=subprocess.run, tag: str = TAG_THO) -> tuple[bool, str]:
    duong = which("tailscale") or which(DUONG_TAILSCALE_APP)
    if duong is None:
        return False, "không thấy Tailscale — Đại ca cài, rồi đưa máy vào tailnet như thiết bị gắn tag"
    kq = chay([duong, "status", "--json"], capture_output=True, text=True, timeout=20)
    try:
        tu = json.loads(kq.stdout) if kq.returncode == 0 else {}
        tags = ((tu.get("Self") or {}).get("Tags") or []) if isinstance(tu, dict) else []
    except (ValueError, AttributeError):
        tags = []
    if isinstance(tags, list) and tag in tags:
        return True, f"máy gắn {tag}"
    return False, (f"máy chưa gắn {tag} (hoặc không đọc được `tailscale status`) — Đại ca gắn tag trong trang quản "
                   "trị Tailscale (máy không đăng nhập bằng tài khoản Đại ca); trạm không tự đổi cài đặt")
