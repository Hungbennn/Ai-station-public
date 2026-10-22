"""Bằng chứng plan do tài khoản trạm ghi sau quy trình duyệt/review hiện có; không nhận từ thợ."""
from tram.giao_viec.su_kien import su_kien_bead, moi_nhat

CO = ("nho", "vua", "lon")


def _plan(ds, ma):
    p = moi_nhat(ds, "co.plan")
    if p is None or p.id != ma:
        raise ValueError("Plan không còn hiện hành")
    return p


def ghi_plan(kho, da, bead, commit, file, digest, khe, q, luc):
    d = {"commit": commit, "file": file, "digest": digest, "khe": khe,
         "co": q["co"], "pham_vi": q["pham_vi"], "ban_luat": q["ban_luat"], "yeu_cau": q.get("yeu_cau")}
    with kho.giao_dich():
        cu = moi_nhat(su_kien_bead(kho, da, bead), "co.plan")
        if cu and cu.du_lieu == d:
            return cu.id
        return kho.ghi_su_kien(da, "co.plan", d, bead_id=bead, luc=luc, tac_nhan="dai-ca")


def duyet(kho, da, bead, plan, luc):
    with kho.giao_dich():
        ds = su_kien_bead(kho, da, bead)
        _plan(ds, plan)
        if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == plan for s in ds):
            kho.ghi_su_kien(da, "co.duyet", {"plan": plan}, bead_id=bead, luc=luc, tac_nhan="dai-ca")


def review(kho, da, bead, plan, khe, ket_luan, ma, luc, *, commit=None):
    with kho.giao_dich():
        ds = su_kien_bead(kho, da, bead)
        d = {"plan": plan, "khe": khe, "ket_luan": ket_luan, "ma": ma}
        if commit is not None:
            d["commit"] = commit
        cu = next((s for s in ds if s.loai == "co.review" and s.du_lieu["ma"] == ma), None)
        if cu:
            if cu.du_lieu != d:
                raise ValueError("Mã review đã dùng với nội dung khác")
            return
        p = _plan(ds, plan)
        if khe == p.du_lieu["khe"] or ket_luan not in ("dat", "tra-ve"):
            raise ValueError("Review phải khác khe viết và có kết luận hợp lệ")
        if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == plan for s in ds):
            raise ValueError("Chưa duyệt plan")
        rs = [s for s in ds if s.loai == "co.review"]
        if len(rs) >= 3 or any(s.du_lieu["plan"] == plan and s.du_lieu["ket_luan"] == "dat" for s in rs):
            raise ValueError("Đã dừng review")
        kho.ghi_su_kien(da, "co.review", d, bead_id=bead, luc=luc, tac_nhan="dai-ca")


def cong_plan(ds, q):
    if q["thieu"]:
        return "lam-ro-du-lieu"
    if q["co"] == "nho":
        return None
    p = moi_nhat(ds, "co.plan")
    if p is None or CO.index(p.du_lieu["co"]) < CO.index(q["co"]) or not set(q["pham_vi"]) <= set(
            p.du_lieu["pham_vi"]) or p.du_lieu["ban_luat"] != q["ban_luat"]:
        return "cho-plan"
    if p.du_lieu.get("yeu_cau") != q.get("yeu_cau"):
        return "cho-plan"
    if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == p.id for s in ds):
        return "cho-duyet-plan"
    if q["co"] == "vua":
        return None
    rs = [s for s in ds if s.loai == "co.review"]
    if any(s.du_lieu["plan"] == p.id and s.du_lieu["ket_luan"] == "dat" for s in rs):
        return None
    return "hoi-dai-ca-ba-vong" if len(rs) >= 3 else "cho-review-plan"
