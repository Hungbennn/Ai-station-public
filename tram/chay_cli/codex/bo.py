"""Bộ CLI của khe Codex (spec 3 §7.2, lát 3b) cho vòng `tram tho chay` (3a-2) — đăng ký `BO_CLI["codex"]`.

Lệnh (cờ theo hiểu biết hiện tại — chờ spike S5): `codex exec --json --cd <worktree> --sandbox workspace-write`,
`approval_policy="never"` (không hỏi — thao tác ngoài sandbox bị từ chối, agent phải `tram bao --can-hoi`), mạng tắt
(`sandbox_workspace_write.network_access=false`), thêm chỗ ghi: thư mục phiếu (hàng đợi `tram bao`) — chưa mở git
common-dir (chờ giải pháp S6). Prompt qua stdin (`-`). KHÔNG BAO GIỜ dùng chế độ bỏ qua sandbox/quyền (Q6).
Codex không có file quyền theo vai như Claude: `vai`, `lenh_cho_phep` không vào lệnh — lớp bổ sung là prompt vai và kiểm
diff của phần 4; hàng rào thật là sandbox + principal của khe (S6)."""
import subprocess
from datetime import datetime
from pathlib import Path

from tram.chay_cli.codex.app_server import CHU_KY_RANH_GIAY, doc_han_muc_ranh, hoi_app_server
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.mo_hinh import HanMuc


def _kiem(p: Path) -> Path:
    p = Path(p)
    if not p.is_absolute() or ".." in p.parts or p == Path("/") or p == Path.home():
        raise ValueError(f"đường dẫn ghi của sandbox phải tuyệt đối, cụ thể: {p}")
    return p


def lenh_codex(*, worktree: Path, ghi_them: list[Path], codex: str = "codex") -> list[str]:
    argv = [codex, "exec", "--json", "--cd", str(_kiem(worktree)), "--sandbox", "workspace-write",
            "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=false"]
    for d in ghi_them:
        argv += ["--add-dir", str(_kiem(d))]
    return [*argv, "-"]


class BoCodex:
    cli = "codex"
    bien_thu_muc = "CODEX_HOME"
    chu_ky_han_muc_ranh_giay = CHU_KY_RANH_GIAY

    def __init__(self, *, codex: str = "codex", chay=subprocess.run, hoi=hoi_app_server):
        self.codex, self.chay, self.hoi = codex, chay, hoi

    def lenh(self, *, worktree: Path, thu_muc_phieu: Path, vai: str, lenh_cho_phep: list[str],
             settings: Path | None = None, mcp: Path | None = None) -> list[str]:
        # S6 chưa giải quyết quyền Git: không mở cả common-dir để làm commit chạy được.
        return lenh_codex(worktree=worktree, ghi_them=[thu_muc_phieu], codex=self.codex)

    def tao_chay(self, boc=lambda a: a, **kw) -> ChayCodex:
        return ChayCodex(boc, **kw)

    def tao_nguon(self, **kw) -> NguonHanMucCodex:
        return NguonHanMucCodex()

    def doc_han_muc_ranh(self, khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, principal,
                         path: str) -> HanMuc | None:
        return doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, bay_gio=bay_gio, principal=principal, path=path,
                                codex=self.codex, hoi=self.hoi)
