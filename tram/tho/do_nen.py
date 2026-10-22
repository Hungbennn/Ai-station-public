"""Phép thử hữu hạn từ chính daemon thợ; không xin phiếu, không ghi danh tính/token ra log."""
import json
import tempfile
import unicodedata
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import KhachTram, doc_token_may
from tram.tho.principal import doc_principal
from tram.tho.lenh_token_khe import boc_token
from tram.tho.san_sang_b import san_sang_b


def khong_dau(s: str) -> str:
    # Claude hay trả "SẴN-SÀNG" có dấu cho câu hỏi tiếng Việt (đo máy B 21/10).
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if not unicodedata.combining(c)).upper()


def thu_claude(ch, *, chay=chay_gioi_han):
    with tempfile.TemporaryDirectory(prefix="do-nen-", dir=Path.home() / "tram") as ten:
        goc = Path(ten)
        goc.chmod(0o755)
        for k in ch.khe:
            pr = doc_principal(k.principal)
            env = {"PATH": ch.chay.path_cli, "LANG": "C.UTF-8", "CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh)}
            argv = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--tools", "",
                    "--setting-sources", "user", "--strict-mcp-config", "--max-turns", "1"]
            kq = chay(pr.boc(boc_token(argv)), env=env, cwd=goc, kill=pr.kill_nhom, timeout=120,
                      input="Chỉ trả lời SAN-SANG. Không dùng công cụ.", text=True, capture_output=True)
            dong = [json.loads(x) for x in kq.stdout.splitlines() if x.strip()]
            dat = any(x.get("type") == "result" and x.get("is_error") is False
                      and "SAN-SANG" in khong_dau(x.get("result", "")) for x in dong)
            if kq.returncode != 0 or not dat:
                return False
    return True


def main():
    try:
        ch = nap_cau_hinh_tho()
        token = doc_token_may(tren_may_b=ch.tren_may_b)
        if not token or not san_sang_b(ch):
            print("DO-NEN: CHUA-DANG-NHAP", flush=True)
            return 2
        if KhachTram(ch.tram_api, token).ping().get("may_id") != "B":
            print("DO-NEN: TOKEN-KHONG-KHOP", flush=True)
            return 2
        if not thu_claude(ch):
            print("DO-NEN: CLAUDE-CHUA-DAT", flush=True)
            return 2
    except Exception:
        print("DO-NEN: KHONG-KET-LUAN", flush=True)
        return 2
    print("DO-NEN: DAT-HAI-KHE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
