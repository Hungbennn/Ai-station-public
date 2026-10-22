"""Cấu hình memory MCP (spec 1b §9.2) cho CLI của khe trên máy thợ — `tram tho dang-ky` (3b). Chỉ SINH nội dung/lệnh;
ghi thật ở bước thực hiện sau khi Đại ca gõ `dong-y`. Hình dạng cấu hình của CLI chưa kiểm bằng chạy thật
(spike N2, S5).

- Claude: qua lệnh của CLI (`claude mcp add-json --scope user`, `CLAUDE_CONFIG_DIR` của khe) với `cau_hinh_tho()` của
  1b-2 — trạm không mở file cấu hình/đăng nhập của Claude. Biến `${TRAM_NHO_URL}`… do vòng `tram tho chay` đặt (3a-2).
- Codex: khối có dấu mốc ở CUỐI `$CODEX_HOME/config.toml`: `url` ghi thẳng (Codex không mở rộng biến trong url — chờ
  S5), header lấy từ biến môi trường qua `env_http_headers`. Chạy lại thay khối cũ; trùng tên ngoài khối → từ chối."""
import json
import re
import tomllib
from pathlib import Path

from tram.nho.cau_hinh_mcp import TEN_MAY_CHU, cau_hinh_tho

DAU = f"# >>> {TEN_MAY_CHU} (tram tho dang-ky — đừng sửa tay) >>>"
CUOI = f"# <<< {TEN_MAY_CHU} <<<"
URL_RE = re.compile(r"https://[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+(:\d{2,5})?")


def url_nho(tram_chu: str) -> str:
    """`tailscale serve` đưa đường `/nho` → memory 7710 (spec 1b §9; kiểm ở N2)."""
    goc = tram_chu.rstrip("/")
    if not URL_RE.fullmatch(goc):
        raise ValueError("tram chủ phải dạng https://<máy B>.<tailnet>.ts.net")
    return goc + "/nho/mcp"


def _bien_header() -> dict[str, str]:
    """{header: TÊN_BIẾN} từ `cau_hinh_tho()` (`${TÊN}`) — một nguồn với bên kiểm của memory 1b-2."""
    return {h: re.fullmatch(r"\$\{([A-Z_]+)\}", v).group(1) for h, v in cau_hinh_tho()["headers"].items()}


def khoi_codex(url: str) -> str:
    hdr = ", ".join(f'"{h}" = "{b}"' for h, b in _bien_header().items())
    return f'{DAU}\n[mcp_servers.{TEN_MAY_CHU}]\nurl = "{url}"\nenv_http_headers = {{ {hdr} }}\n{CUOI}\n'


def _bo_khoi(cu: str) -> str:
    if cu.count(DAU) != cu.count(CUOI) or cu.count(DAU) > 1:
        raise ValueError("config.toml có dấu mốc tram-nho hỏng — Đại ca sửa tay trước")
    if DAU not in cu:
        return cu
    dau, cuoi = cu.index(DAU), cu.index(CUOI) + len(CUOI)
    return cu[:dau] + cu[cuoi:].lstrip("\n")


def ghep_codex_toml(cu: str, url: str) -> str:
    goc = _bo_khoi(cu)
    try:
        if TEN_MAY_CHU in tomllib.loads(goc).get("mcp_servers", {}):
            raise ValueError(f"config.toml đã có mcp_servers.{TEN_MAY_CHU} ngoài khối của trạm — Đại ca gỡ tay trước")
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"config.toml hiện tại không đọc được: {e}") from None
    moi = (goc if not goc or goc.endswith("\n") else goc + "\n") + ("\n" if goc.strip() else "") + khoi_codex(url)
    tomllib.loads(moi)
    return moi


def lenh_claude_mcp(claude: str, thu_muc: Path) -> list[tuple[list[str], dict[str, str]]]:
    """(argv, biến môi trường thêm). Lệnh xoá được phép lỗi (chưa có); lệnh thêm phải thành công."""
    env = {"CLAUDE_CONFIG_DIR": str(thu_muc)}
    goc = [claude, "mcp"]
    return [([*goc, "remove", "--scope", "user", TEN_MAY_CHU], env),
            ([*goc, "add-json", "--scope", "user", TEN_MAY_CHU, json.dumps(cau_hinh_tho(), ensure_ascii=False)], env)]
