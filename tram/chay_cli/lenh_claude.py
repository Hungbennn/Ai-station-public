"""Lệnh và môi trường của MỘT lần chạy Claude Code headless (spec 3 §7.2). Cờ chính xác CHỜ SPIKE S4: dưới đây là
bản tốt nhất theo tài liệu Claude Code, gom một chỗ để S4 sửa một nơi. Không bao giờ dùng chế độ bỏ qua quyền (Q6).

Môi trường CLI tối thiểu: KHÔNG token máy, KHÔNG credential push. `TRAM_MA_GIAO`/`TRAM_NHO_URL` chỉ khi memory MCP
bật (1b-2). Hook Git tắt và `safe.directory` = worktree qua `GIT_CONFIG_*` (principal khác chủ worktree — S6)."""
import json
from pathlib import Path

from tram.chay_cli.quyen import sinh_settings
from tram.nho.cau_hinh_mcp import cau_hinh_tho, mcp_json
from tram.phieu.mo_hinh import Phieu

CO_HEADLESS = ("-p", "--output-format", "stream-json", "--verbose")
CO_CHI_NAP_VAI = ("--setting-sources", "user")            # không nạp settings của repo (project/local) — S4
CO_MCP_CHAT = ("--strict-mcp-config",)                    # bỏ `.mcp.json` của repo — S4


def argv_claude(*, settings: Path, mcp: Path | None, cli: str = "claude") -> list[str]:
    argv = [cli, *CO_HEADLESS, *CO_CHI_NAP_VAI, "--settings", str(settings)]
    return argv + (["--mcp-config", str(mcp), *CO_MCP_CHAT] if mcp else [*CO_MCP_CHAT])


def env_cli(*, thu_muc_cau_hinh: Path, giao_id: str, hang_doi: Path, wt: Path, path: str, lang: str = "C.UTF-8",
            ma_giao: str | None = None, nho_url: str | None = None) -> dict[str, str]:
    env = {"CLAUDE_CONFIG_DIR": str(thu_muc_cau_hinh), "TRAM_GIAO_ID": giao_id, "TRAM_HANG_DOI": str(hang_doi),
           "PATH": path, "LANG": lang, "GIT_CONFIG_COUNT": "2",
           "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": "/dev/null",
           "GIT_CONFIG_KEY_1": "safe.directory", "GIT_CONFIG_VALUE_1": str(wt)}
    if nho_url:
        if not ma_giao:
            raise ValueError("Memory MCP bật mà phiếu không có ma_giao")
        env |= {"TRAM_NHO_URL": nho_url, "TRAM_MA_GIAO": ma_giao}
    return env


def ghi_file_phieu(thu_muc: Path, phieu: Phieu, *, nho: bool) -> tuple[Path, Path | None]:
    """`settings.json` (+ `mcp.json` khi memory bật) trong thư mục của phiếu — thuộc tiến trình quản lý, chỉ đọc
    với principal (S6). Trả (settings, mcp | None)."""
    thu_muc.mkdir(parents=True, exist_ok=True)
    s = thu_muc / "settings.json"
    s.write_text(json.dumps(sinh_settings(phieu, nho=nho), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not nho:
        return s, None
    m = thu_muc / "mcp.json"
    m.write_text(mcp_json(cau_hinh_tho()), encoding="utf-8")
    return s, m
