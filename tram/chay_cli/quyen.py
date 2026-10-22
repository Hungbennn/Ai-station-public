"""File quyền theo vai `vai/quyen/<vai>.json` (spec 3 §7.2) — có phiên bản; thợ sinh file settings CỦA PHIẾU từ mẫu
cộng `lenh_cho_phep` của phiếu và hook `PreCompact`. Là LỚP BỔ SUNG, không phải hàng rào (§7.3 mục 3): hàng rào thật
là principal thực thi (S6). Cú pháp quy tắc (`Bash(<mẫu>)`, `*`), `defaultMode: dontAsk`, hook — CHỜ SPIKE S4, S8."""
import hashlib
import json
from pathlib import Path

from tram.duong_dan import goc_repo
from tram.phieu.mo_hinh import Phieu

VAI = ("spec", "coder", "qc")
KHOA_MAU = {"phien_ban", "vai", "ghi_chu", "permissions"}
CONG_CU_NHO = ("mcp__tram-nho__nho_lai", "mcp__tram-nho__ghi_nho")      # 1b-2: máy chủ MCP `tram-nho`
HOOK_PRE_COMPACT = 'tram bao --moc "Tự lưu trước khi nén ngữ cảnh (PreCompact)"'    # S8


def thu_muc_quyen() -> Path:
    return goc_repo() / "vai" / "quyen"


def doc_mau(vai: str, thu_muc: Path | None = None) -> dict:
    if vai not in VAI:
        raise ValueError(f"Vai lạ: {vai!r}")
    m = json.loads(((thu_muc or thu_muc_quyen()) / f"{vai}.json").read_text(encoding="utf-8"))
    q = m.get("permissions") if isinstance(m, dict) else None
    if (set(m) - KHOA_MAU or m.get("vai") != vai or not isinstance(m.get("phien_ban"), str) or not isinstance(q, dict)
            or q.get("defaultMode") != "dontAsk" or q.get("disableBypassPermissionsMode") != "disable"
            or not isinstance(q.get("allow"), list) or not isinstance(q.get("deny"), list)):
        raise ValueError(f"vai/quyen/{vai}.json sai khuôn: cần phien_ban, vai, permissions.defaultMode=dontAsk và "
                         "disableBypassPermissionsMode=disable (Q6: không bỏ qua quyền)")
    return m


def phien_ban_quyen(vai: str, thu_muc: Path | None = None) -> str:
    """`<phien_ban>+<12 hex sha256 của mẫu>` — đổi mẫu là đổi khoá chống trùng của phần 4 (§5.1 điều kiện 7)."""
    m = doc_mau(vai, thu_muc)
    bam = hashlib.sha256(json.dumps(m, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]
    return f"{m['phien_ban']}+{bam}"


def sinh_settings(phieu: Phieu, *, nho: bool, thu_muc: Path | None = None) -> dict:
    """Settings của phiếu: mẫu vai + `Bash(<mẫu lenh_cho_phep>)` + công cụ memory (khi bật) + hook PreCompact."""
    m = doc_mau(phieu.vai, thu_muc)
    q = m["permissions"]
    allow = [*q["allow"], *(f"Bash({l})" for l in phieu.lenh_cho_phep), *(CONG_CU_NHO if nho else ())]
    return {"permissions": {**q, "allow": list(dict.fromkeys(allow)), "deny": list(q["deny"])},
            "hooks": {"PreCompact": [{"matcher": "", "hooks": [{"type": "command", "command": HOOK_PRE_COMPACT}]}]}}
