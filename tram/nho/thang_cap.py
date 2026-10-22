"""Tìm cặp thăng cấp (spec 1b §8) — phép so khớp chéo dự án CHỈ chạy trong memory service, không lộ qua HTTP/MCP.

Cặp: ký ức `/du-an/A/cach-lam` và `/du-an/B/cach-lam` (A ≠ B), chưa xoá, cùng model hiện hành, cosine ≥ 0,85.
Không bao giờ xét `nghiep-vu`. Bỏ cặp đã thăng cấp (kể cả bản đã xoá mềm), đã từ chối, đã bỏ, đã xoá cứng."""
import hashlib
import json
import re
from dataclasses import dataclass
from itertools import combinations

from tram.nho.bang import COT, ky_uc_tu_hang, sql, trong
from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import KyUc
from tram.nho.nhat_ky import NhatKy
from tram.nho.pham_vi import TEN

NGUONG_THANG_CAP = 0.85
SO_UNG_VIEN_MOI_BAN = 5
_CACH_LAM = re.compile(rf"/du-an/({TEN})/cach-lam")


@dataclass(frozen=True)
class CapThangCap:
    a: KyUc                 # id nhỏ hơn
    b: KyUc
    cosine: float

    @property
    def khoa(self) -> str:
        return f"{self.a.id}|{self.b.id}"


def du_an_cach_lam(pham_vi: str) -> str | None:
    m = _CACH_LAM.fullmatch(pham_vi)
    return m.group(1) if m else None


def khoa_cap(id_1: str, id_2: str) -> str:
    return "|".join(sorted((id_1, id_2)))


def id_thang_cap(khoa: str) -> str:
    """ID ổn định của ký ức thăng cấp từ một cặp — phát lại / crash không sinh bản thứ hai (§6.4)."""
    return "m-" + hashlib.sha256(f"thang_cap:{khoa}".encode()).hexdigest()[:24]


def cac_cap_da_co(kho: KhoKyUc, nhat_ky: NhatKy) -> set[str]:
    """Cặp đã thăng cấp: mọi ký ức (KỂ CẢ đã xoá mềm) có `nguon` loại `thang_cap` — kiểm bằng `id_goc`; cộng sổ cặp
    trong nhật ký (đã từ chối, LLM bỏ, ký ức thăng cấp đã bị xoá cứng)."""
    da_co = set(nhat_ky.cac_cap())
    for h in kho.quet(cot=["nguon"]):
        goc = sorted({n["id_goc"] for n in json.loads(h["nguon"]) if n.get("loai") == "thang_cap" and n.get("id_goc")})
        da_co.update(f"{x}|{y}" for x, y in combinations(goc, 2))
    return da_co


def tim_cap(kho: KhoKyUc, mo_hinh: str, *, bo_qua: set[str], toi_da: int) -> list[CapThangCap]:
    """Cặp mới, cosine cao trước (hoà → khoá); mỗi ký ức gốc vào tối đa một cặp mỗi lượt; tối đa `toi_da` cặp."""
    dk = f"da_xoa = false AND mo_hinh_embed = {sql(mo_hinh)}"
    cl = sorted({h["pham_vi"] for h in kho.quet(dk, cot=["pham_vi"]) if du_an_cach_lam(h["pham_vi"])})
    if len(cl) < 2:
        return []
    cap: dict[str, CapThangCap] = {}
    for k in sorted((ky_uc_tu_hang(h) for h in kho.quet(f"{dk} AND pham_vi IN {trong(cl)}", cot=COT)),
                    key=lambda x: x.id):
        khac = [p for p in cl if p != k.pham_vi]
        for m, cos in kho.tim(k.vector, khac, mo_hinh=mo_hinh, gioi_han=SO_UNG_VIEN_MOI_BAN):
            if cos >= NGUONG_THANG_CAP and du_an_cach_lam(m.pham_vi) != du_an_cach_lam(k.pham_vi):
                a, b = sorted((k, m), key=lambda x: x.id)
                cap.setdefault(khoa_cap(a.id, b.id), CapThangCap(a, b, round(cos, 6)))
    chon, da_dung = [], set()
    for c in sorted(cap.values(), key=lambda c: (-c.cosine, c.khoa)):
        if c.khoa in bo_qua or {c.a.id, c.b.id} & da_dung:
            continue
        chon.append(c)
        da_dung |= {c.a.id, c.b.id}
        if len(chon) >= toi_da:
            break
    return chon


def _vai(k: KyUc) -> str | None:
    ds = {n.get("vai") for n in k.nguon}
    v = ds.pop() if len(ds) == 1 else None
    return v if isinstance(v, str) and re.fullmatch(TEN, v) else None


def dich_thang_cap(a: KyUc, b: KyUc) -> str:
    """Đích do trạm tính: hai bản gốc cùng một `nguon.vai` → `/vai/<vai>`; khác hoặc thiếu → `/chung`."""
    va = _vai(a)
    return f"/vai/{va}" if va is not None and va == _vai(b) else "/chung"
