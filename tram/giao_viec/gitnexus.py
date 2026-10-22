"""Adapter gitnexus CLI cho lát 4c (kiến trúc Q3, §5.1 lớp 1; spec 4 §6.4 mục 3, §11): `detect-changes` cho cờ
đỏ, `query` cho "luồng liên quan" ở lớp 1. Chỉ đọc index có sẵn — KHÔNG `analyze`/`index`/`clean`.
Hình dạng đầu ra CLI (JSON hay văn bản, tên trường) CHƯA XÁC MINH — chờ spike GN; vì vậy đọc khoan dung: mọi
chuỗi dưới khoá đường dẫn ở bất kỳ độ sâu nào là file bị chạm; `partial`/`truncated`/không đọc được → không chắc."""
import json
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

KHOA_TEP = frozenset({"filePath", "file_path", "file", "path"})
LENH_DUOC_PHEP = frozenset({"detect-changes", "query"})
Chay = Callable[[list[str], Path | None], tuple[int, str]]


class LoiGitnexus(RuntimeError):
    """gitnexus lỗi, quá hạn hoặc trả dữ liệu không đọc được."""


@dataclass(frozen=True)
class ThayDoi:
    tep: frozenset[str]          # file của symbol đổi + của các luồng bị ảnh hưởng (tương đối gốc worktree)
    khong_chac: bool             # partial/truncated — không được coi là sạch


def chay_gitnexus(argv: list[str], cwd: Path | None) -> tuple[int, str]:
    try:
        kq = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=120,
                            env={**os.environ, "NO_COLOR": "1"})
    except (OSError, subprocess.TimeoutExpired) as e:
        raise LoiGitnexus(f"không chạy được gitnexus: {type(e).__name__}") from None
    return kq.returncode, kq.stdout


def _json(ra: str) -> dict:
    for tho in (ra, ra[ra.find("{"):ra.rfind("}") + 1]):
        try:
            d = json.loads(tho)
        except ValueError:
            continue
        if isinstance(d, dict) and "error" not in d:
            return d
    raise LoiGitnexus("gitnexus không trả JSON object đọc được")


def _tep(x: object, goc: str, ra: set[str]) -> set[str]:
    if isinstance(x, dict):
        for k, v in x.items():
            if k in KHOA_TEP and isinstance(v, str) and v:
                ra.add(v[len(goc):].lstrip("/") if v.startswith(goc) else v)
            else:
                _tep(v, goc, ra)
    elif isinstance(x, list):
        for v in x:
            _tep(v, goc, ra)
    return ra


class GitnexusCli:
    def __init__(self, chay: Chay = chay_gitnexus):
        self._chay = chay

    def _gn(self, lenh: str, *args: str, cwd: Path | None = None) -> dict:
        if lenh not in LENH_DUOC_PHEP:
            raise LoiGitnexus(f"gitnexus {lenh}: không được phép")
        ma, ra = self._chay(["gitnexus", lenh, *args], cwd)
        if ma != 0:
            raise LoiGitnexus(f"gitnexus {lenh} lỗi {ma}")
        return _json(ra)

    def thay_doi(self, worktree: Path, base: str, repo: str) -> ThayDoi:
        """Diff `base`..worktree (worktree tách rời tại commit cần xét) → file bị chạm theo symbol và luồng."""
        d = self._gn("detect-changes", "--scope", "compare", f"--base-ref={base}", f"--repo={repo}",
                     "--limit=500", cwd=worktree)
        # Adapter chưa được spike: object lạ/rỗng không đồng nghĩa không có ảnh hưởng.
        if not all(isinstance(d.get(k), list) for k in ("changed_symbols", "affected_processes")):
            raise LoiGitnexus("detect-changes sai dạng")
        return ThayDoi(frozenset(_tep(d, str(worktree) + "/", set())),
                       bool(d.get("partial")) or bool(d.get("truncated")))

    def luong(self, truy_van: str, repo: str, toi_da: int = 5) -> list[tuple[str, tuple[str, ...]]]:
        """[(tên luồng, file thuộc luồng)] liên quan tới `truy_van` (văn bản bead — dữ liệu không tin cậy)."""
        q = " ".join(truy_van.split())[:300]
        d = self._gn("query", f"--query={q}", f"--repo={repo}", f"--limit={toi_da}")
        ds, ky_hieu = d.get("processes"), d.get("process_symbols") or []
        if not isinstance(ds, list) or not isinstance(ky_hieu, list):
            raise LoiGitnexus("gitnexus query sai dạng")
        ra = []
        for p in [p for p in ds if isinstance(p, dict)][:toi_da]:
            ten = str(p.get("name") or p.get("label") or p.get("id") or "?")[:200]
            tep = sorted({r.get("filePath") for r in ky_hieu if isinstance(r, dict) and r.get("process_id") ==
                          p.get("id") and isinstance(r.get("filePath"), str)})
            ra.append((ten, tuple(tep[:8])))
        return ra
