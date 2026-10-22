"""Đo M6 (spec 1b §2, §16.3): recall p95 trên kho N ký ức sinh giả, GỒM embed truy vấn qua embedder thật.

Kho đo nằm ở thư mục tạm riêng — không đụng ~/.tram/nho. Vector kho sinh ngẫu nhiên (chuẩn hoá L2) gắn đúng
`mo_hinh` của embedder để qua bộ lọc model; phạm vi trải 40 dự án + vai + chung như spike N1."""
import random
import time
from pathlib import Path

from tram.nho.embed import Embedder
from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import KyUc, chuan_hoa_l2
from tram.nho.nho_lai import nho_lai

LUC = "2026-10-01T00:00:00Z"


def _pham_vi(i: int) -> str:
    if i % 50 == 0:
        return "/chung"
    if i % 50 == 1:
        return "/vai/coder"
    return f"/du-an/da{i % 40}/{'nghiep-vu' if i % 2 else 'cach-lam'}"


def sinh_kho(thu_muc: Path, embedder: Embedder, so_ban: int, *, lo: int = 1000, hat: int = 7) -> KhoKyUc:
    r = random.Random(hat)
    kho = KhoKyUc(thu_muc, so_chieu=embedder.so_chieu)
    mo_hinh = embedder.mo_hinh
    for dau in range(0, so_ban, lo):
        hang = [KyUc(f"m-{i:06d}", f"ký ức giả {i}", _pham_vi(i), (), 0.5, ({"loai": "agent"},), False, LUC, LUC,
                     mo_hinh, chuan_hoa_l2([r.gauss(0, 1) for _ in range(embedder.so_chieu)]))
                for i in range(dau, min(so_ban, dau + lo))]
        kho.them_lo(hang)
    return kho


def do_tre(kho: KhoKyUc, embedder: Embedder, truy_van: list[str], *, so_lan: int) -> dict[str, float]:
    """Mỗi lần: một recall đầy đủ (embed + 3 nhóm × 50 ứng viên + chấm). Trả p50/p95/max (ms)."""
    vung = ["/du-an/da7", "/vai/coder", "/chung"]
    ms = []
    for i in range(so_lan):
        bat_dau = time.perf_counter()
        nho_lai(kho, embedder, truy_van[i % len(truy_van)], vung)
        ms.append((time.perf_counter() - bat_dau) * 1000)
    ms.sort()
    return {"p50": ms[len(ms) // 2], "p95": ms[min(len(ms) - 1, int(len(ms) * 0.95))], "max": ms[-1]}
