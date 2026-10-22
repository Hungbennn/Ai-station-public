"""Registry được tạo tại 3b; 3a-2 chỉ có ChayClaude, chưa có BoCLI."""
from pathlib import Path
from typing import Protocol, runtime_checkable

from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.lenh_claude import argv_claude
from tram.chay_cli.codex.bo import BoCodex
from tram.han_muc.claude import NguonHanMucClaude


@runtime_checkable
class BoCLI(Protocol):
    cli: str
    bien_thu_muc: str
    chu_ky_han_muc_ranh_giay: int | None
    def lenh(self, *, worktree: Path, thu_muc_phieu: Path, vai: str, lenh_cho_phep: list[str],
             settings: Path | None = None, mcp: Path | None = None) -> list[str]: ...
    def tao_chay(self, boc, **kw): ...
    def tao_nguon(self, **kw): ...
    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio, principal, path): ...


class BoClaude:
    cli, bien_thu_muc, chu_ky_han_muc_ranh_giay = "claude", "CLAUDE_CONFIG_DIR", None

    def lenh(self, *, worktree, thu_muc_phieu, vai, lenh_cho_phep, settings=None, mcp=None):
        if settings is None:
            raise ValueError("Claude cần settings của phiếu")
        return argv_claude(settings=settings, mcp=mcp)

    def tao_chay(self, boc, **kw):
        return ChayClaude(boc, **kw)

    def tao_nguon(self, **kw):
        return NguonHanMucClaude(**kw)

    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio, principal, path):
        return None


BO_CLI: dict[str, BoCLI] = {"claude": BoClaude(), "codex": BoCodex()}
