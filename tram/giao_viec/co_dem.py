"""Chấm thuần: hợp khai báo + diff trạm, nhãn chỉ nâng; không đọc filesystem/LLM."""
from tram.giao_viec.co_bao_ve import nguy_hiem as cham_nguy_hiem
from tram.giao_viec.tieu_chi import tach_tieu_chi

CO = ("nho", "vua", "lon")
MO, DONG = "<!-- pham-vi-co:v1 -->", "<!-- /pham-vi-co -->"


def pham_vi(design):
    if design.count(MO) != 1 or design.count(DONG) != 1:
        return None
    a, b = design.index(MO) + len(MO), design.index(DONG)
    if b < a:
        return None
    files = []
    for dong in design[a:b].splitlines():
        if not dong.strip():
            continue
        if not dong.strip().startswith("- "):
            return None
        p = dong.strip()[2:].strip()
        while p.startswith("./"):
            p = p[2:]
        if not p or p.startswith("/") or any(x in ("", ".", "..") for x in p.split("/")):
            return None
        if any(c in p for c in "*?[\\\x00\r\n"):
            return None
        files.append(p)
    return tuple(sorted(set(files))) or None


def cham_co(bead, ch, theo_id, *, diff=(), ben=False, nguy_hiem=False, phu_thuoc_ro=True, them_cam=()):
    khai = pham_vi(bead.design)
    files = sorted(set(khai or ()) | set(diff))
    thieu = [] if khai else ["pham-vi"]
    nhom = set()
    for p in files:
        if p.startswith(("tests/", "docs/", "openspec/")):
            continue
        tien_to = sorted((k for k in ch["nhom"] if p.startswith(k)), key=len, reverse=True)
        if tien_to:
            nhom.add(ch["nhom"][tien_to[0]])
        elif not p.startswith(("tests/", "docs/", "openspec/")):
            thieu.append("nhom")
    tc = len(tach_tieu_chi(bead.acceptance_criteria))
    if not tc:
        thieu.append("tieu-chi")
    if not phu_thuoc_ro:
        thieu.append("phu-thuoc")
    dem = {"file": len(files), "nhom": len(nhom), "tieu_chi": tc}
    nguy = nguy_hiem or cham_nguy_hiem(files, bead.labels, (*ch["nguy_hiem"], *them_cam), ben=ben)
    ly = []
    lon = nguy or len(nhom) >= 3 or any(v > ch["vua_" + k] for k, v in dem.items())
    nho = not thieu and all(v <= ch["nho_" + k] for k, v in dem.items())
    tu = "lon" if lon else "nho" if nho else "vua"
    if nguy:
        ly.append("nguy-hiem")
    if len(nhom) >= 3:
        ly.append("ba-nhom")
    ly.append("nguong-" + tu)
    san = "lon" if "co:lon" in bead.labels else "vua" if "co:vua" in bead.labels else "nho"
    co = CO[max(CO.index(tu), CO.index(san))]
    return {"tu_dong": tu, "san_nhan": san, "san_nguy_hiem": "lon" if nguy else None,
            "co": co, "dem": dem, "thieu": sorted(set(thieu)), "ly_do": ly, "ban_luat": ch["ban_luat"],
            "model": ch["model_nho" if co == "nho" else "model_lon"],
            "effort": ch["effort_" + co],
            "quy_trinh": {"nho": "thang", "vua": "plan-ngan", "lon": "plan-day-du"}[co],
            "pham_vi": files, "model_thuc": None, "ket_qua_test": None, "ket_qua_qc": None,
            "thoi_gian_ms": None, "lam_lai": None}
