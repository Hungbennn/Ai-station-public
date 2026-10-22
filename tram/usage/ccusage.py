"""Bộ đọc `ccusage` (MIT — spec 2 §8, §11) cho màn Usage. CHỜ CHẠY THẬT: ccusage chưa cài trên máy B; cờ lệnh
và dạng JSON dưới đây chưa kiểm với phiên bản thật (plan 2b G6) — test chỉ dùng bản giả. Chỉ cho màn Usage,
KHÔNG dùng để chặn giao việc (spec 3 §8.1).

Chạy bản cài cố định `usage.ccusage` (không `npx`, không tự cập nhật — Q15); `--version` phải khớp
`usage.ccusage_phien_ban`, lệch thì không chạy. Lệnh: `<ccusage> daily --json --offline --since YYYYMMDD
--until YYYYMMDD` (`--offline`: bảng giá đóng gói sẵn, không gọi mạng). Môi trường tối thiểu: không khoá, không
token nào đi theo."""
import json
import math
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tram.suy.lam_sach import lam_sach

PHIEN_BAN_RE = re.compile(r"\d+\.\d+\.\d+")
NGAY_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TRUONG = {"inputTokens": "token_vao", "outputTokens": "token_ra", "cacheReadTokens": "token_cache_doc",
          "cacheCreationTokens": "token_cache_ghi", "totalCost": "chi_phi_usd"}


@dataclass(frozen=True)
class KetQuaCcusage:
    trang_thai: str                       # "ok" | "chua_cau_hinh" | "loi"
    theo_ngay: tuple[dict, ...] = ()      # {ngay, token_vao, token_ra, token_cache_doc, token_cache_ghi, chi_phi_usd}
    loi: str | None = None
    phien_ban: str | None = None


def doc_json_ccusage(van_ban: str) -> list[dict]:
    """`{"daily": [{"date": "YYYY-MM-DD", "inputTokens": n, …, "totalCost": x}]}` → dòng chuẩn hoá.
    Dạng lạ → ValueError (không đoán); trường thiếu = 0, trường lạ bỏ qua."""
    try:
        raw = json.loads(van_ban)
    except ValueError:
        raise ValueError("ccusage không trả JSON") from None
    ds = raw.get("daily") if isinstance(raw, dict) else None
    if not isinstance(ds, list):
        raise ValueError("JSON ccusage thiếu mảng 'daily'")
    ra = []
    for x in ds:
        if not isinstance(x, dict) or not isinstance(x.get("date"), str) or not NGAY_RE.fullmatch(x["date"]):
            raise ValueError("dòng 'daily' thiếu 'date' dạng YYYY-MM-DD")
        date.fromisoformat(x["date"])
        dong: dict = {"ngay": x["date"]}
        for khoa, ten in TRUONG.items():
            v = x.get(khoa, 0)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise ValueError(f"'{khoa}' không phải số ≥ 0")
            dong[ten] = round(float(v), 4) if ten == "chi_phi_usd" else int(v)
        ra.append(dong)
    return ra


@dataclass
class DocCcusage:
    lenh: Path
    phien_ban: str
    chay: Callable = subprocess.run
    thoi_gian_cho: float = 60.0

    def _goi(self, *doi_so: str) -> subprocess.CompletedProcess:
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path.home()), "LANG": "C.UTF-8",
               "TZ": "Asia/Ho_Chi_Minh"}
        return self.chay([str(self.lenh), *doi_so], capture_output=True, text=True, timeout=self.thoi_gian_cho,
                         env=env)

    def theo_ngay(self, tu: date, den: date) -> KetQuaCcusage:
        try:
            v = self._goi("--version")
            thay = PHIEN_BAN_RE.search(v.stdout or "")
            if v.returncode != 0 or thay is None or thay.group(0) != self.phien_ban:
                return KetQuaCcusage("loi", loi=f"Phiên bản ccusage lệch (cần {self.phien_ban}, thấy "
                                                f"{thay.group(0) if thay else '?'}) — không chạy")
            kq = self._goi("daily", "--json", "--offline", "--since", f"{tu:%Y%m%d}", "--until", f"{den:%Y%m%d}")
            if kq.returncode != 0:
                return KetQuaCcusage("loi", loi=f"ccusage thoát mã {kq.returncode}")
            return KetQuaCcusage("ok", tuple(doc_json_ccusage(kq.stdout)), phien_ban=self.phien_ban)
        except (OSError, subprocess.TimeoutExpired, ValueError) as e:
            return KetQuaCcusage("loi", loi=f"ccusage không đọc được ({type(e).__name__})")
