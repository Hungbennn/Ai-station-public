"""Mẫu cấu hình MCP HTTP của memory cho Claude Code (spec 1b §9.2, §9.3) — CHỈ SINH, không ghi vào đâu.

Ghi vào `claude`/`codex` của máy thợ là việc của `tram tho dang-ky` (3b). Cách đưa vào phiên tay trên máy A —
`.mcp.json` trong repo dự án hay `claude mcp add --scope local` — CHƯA CHỐT (§13 câu 10). Giá trị `${TEN}` là biến môi
trường; Claude Code có mở rộng biến trong `url`/`headers` hay không là việc của spike N2 (chưa chạy)."""
import json

from tram.nho.pham_vi import goc_du_an

TEN_MAY_CHU = "tram-nho"


def cau_hinh_tho() -> dict:
    """CLI máy thợ: URL theo máy (`TRAM_NHO_URL`), bằng chứng là phiếu đang giữ (`TRAM_GIAO_ID`, `TRAM_MA_GIAO`)."""
    return {"type": "http", "url": "${TRAM_NHO_URL}",
            "headers": {"X-Tram-Giao-Id": "${TRAM_GIAO_ID}", "X-Tram-Ma-Giao": "${TRAM_MA_GIAO}"}}


def cau_hinh_phien_tay(du_an: str, url: str) -> dict:
    """Phiên tay của Đại ca trên máy A: mã Đại ca từ biến `TRAM_DAI_CA_MA` (không nằm trong file), dự án tĩnh."""
    goc_du_an(du_an)                                    # tên sai dạng → LoiVungCap
    if not url.startswith("https://") or not url.endswith("/nho/mcp"):
        raise ValueError("url phải dạng https://<máy B>.<tailnet>.ts.net/nho/mcp")
    return {"type": "http", "url": url, "headers": {"Authorization": "Bearer ${TRAM_DAI_CA_MA}", "X-Tram-Du-An": du_an}}


def mcp_json(may_chu: dict) -> str:
    return json.dumps({"mcpServers": {TEN_MAY_CHU: may_chu}}, ensure_ascii=False, indent=2) + "\n"
