"""Principal thực thi của khe và của `tram-kiem` (spec 3 §7.3). CƠ CHẾ CHƯA CHỐT — đề xuất §14, Đại ca chốt sau
spike S6; mã hỗ trợ cả hai, chọn bằng chuỗi `principal` trong `tho.yaml` (khe) / `cach_ly.tram_kiem` (trạm):
- `user:<tên>`    — một user macOS riêng cho mỗi khe (quyền file/ACL của hệ điều hành tách khe);
- `sandbox:<tên>` — một user thực thi chung + hồ sơ `sandbox-exec` riêng mỗi lần chạy (`tram/tho/sandbox.py`).
Cả hai chạy qua `sudo -n` (không hỏi mật khẩu; sudoers do `tram chu cai-dat-tho` liệt kê, chờ `dong-y`) và chỉ
giữ các biến trong `BIEN_GIU` — giá trị biến KHÔNG BAO GIỜ nằm trong argv (`ps` của user khác thấy argv)."""
import re
import signal
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from tram.kiem.lenh_ngan import chay_ngan

SUDO = "/usr/bin/sudo"
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
BIEN_GIU = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "TRAM_MA_GIAO", "TRAM_NHO_URL",
            "PATH", "LANG", "APP_ENV", "TMPDIR", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
            "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1", "TRAM_GIT_QUA_QUAN_LY", "TRAM_NHANH")
USER_RE = re.compile(r"[a-z_][a-z0-9_-]{0,30}")


class ChuaCoPrincipal(ValueError):
    """Khe chưa có principal hợp lệ → không chạy mã repo nào (chờ S6)."""


@dataclass(frozen=True)
class Principal:
    co_che: Literal["user", "sandbox"]
    user: str
    ho_so: Path | None = None          # hồ sơ sandbox của LẦN CHẠY (cơ chế sandbox)

    def voi_ho_so(self, ho_so: Path) -> "Principal":
        return replace(self, ho_so=ho_so)

    def boc(self, argv: list[str]) -> list[str]:
        """Đối số `boc` của `chay_mot_lenh`/`kiem_sau_xong`/`ChayClaude` (3a-1 G26)."""
        dau = [SUDO, "-n", "-H", "-u", self.user, f"--preserve-env={','.join(BIEN_GIU)}", "--"]
        if self.co_che == "sandbox":
            if self.ho_so is None:
                raise ChuaCoPrincipal("Cơ chế sandbox cần hồ sơ của lần chạy")
            dau += [SANDBOX_EXEC, "-f", str(self.ho_so)]
        return [*dau, *argv]


    def kill_nhom(self, pgid: int, sig: int) -> None:
        """Gửi tín hiệu cho cả nhóm tiến trình DƯỚI QUYỀN principal (tiến trình quản lý khác user không kill được
        con cháu của principal). Cách sudo xếp nhóm tiến trình (`use_pty`) — CHỜ S6."""
        chay_ngan([SUDO, "-n", "-u", self.user, "/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
                   "--", f"-{pgid}"], timeout=5)                     # P1: có hạn tuyệt đối, không wait() trần


def doc_principal(chuoi: str | None) -> Principal:
    if not chuoi:
        raise ChuaCoPrincipal("Khe chưa khai principal (user:<tên> | sandbox:<tên>) — chờ spike S6")
    co_che, _, user = chuoi.partition(":")
    if co_che not in ("user", "sandbox") or not USER_RE.fullmatch(user):
        raise ChuaCoPrincipal(f"principal {chuoi!r} sai dạng: user:<tên> hoặc sandbox:<tên>")
    return Principal(co_che, user)
