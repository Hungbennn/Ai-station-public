"""Phê duyệt — phần luồng feature (spec 2 §5.2 "Spec chờ duyệt"; spec 4 §7.3, §10 bước 4), tính lúc đọc (Q12).

"Spec chờ duyệt" hiện ĐÚNG bản trạm đã kiểm: sự kiện `spec.xong` mới nhất của feature, chỉ khi không có `spec.tra_ve`
nào mới hơn. Đại ca Duyệt gửi lại `commit` + `digest_bead` của bản này; bản khác → 409 (G11).
"Feature xong, chờ đóng": feature `theo-plan` còn mở, có con và mọi con đã đóng — trạm không tự đóng (#16)."""
from tram.beads.mo_hinh import Bead
from tram.suy.cot import TRANG_THAI_HIEN
from tram.suy.lam_sach import lam_sach

NHAN_THEO_PLAN = "theo-plan"
CHUA_CO = {"commit": None, "nhanh": None, "digest_bead": None, "file": [], "de_xuat": [],
           "loi": ["Chưa có spec.xong của lượt hiện tại — chờ vòng tick của trạm"]}


def spec_hien_hanh(kho, du_an: str, feature: str) -> dict | None:
    """Dữ liệu `spec.xong` hiện hành (đọc qua `KhoSuKien`); None nếu chưa có hoặc đã bị trả về."""
    x = kho.moi_nhat(du_an, feature, "spec.xong")
    tv = kho.moi_nhat(du_an, feature, "spec.tra_ve")
    if x is None or (tv is not None and tv.id > x.id):
        return None
    return x.du_lieu


def _de_xuat(d: dict) -> dict:
    return {"khoa": lam_sach(d.get("khoa"), 20), "tieu_de": lam_sach(d.get("tieu_de"), 200),
            "loai": lam_sach(d.get("loai"), 10), "uu_tien": d.get("uu_tien"),
            "phu_thuoc": [lam_sach(x, 20) for x in d.get("phu_thuoc") or []][:30],
            "nhan": [lam_sach(x, 50) for x in d.get("nhan") or []][:10]}


def chi_tiet_spec(kho, du_an: str, feature: str) -> dict:
    d = spec_hien_hanh(kho, du_an, feature)
    if d is None:
        return dict(CHUA_CO)
    return {"commit": lam_sach(d.get("commit"), 64), "nhanh": lam_sach(d.get("nhanh"), 100),
            "digest_bead": lam_sach(d.get("digest_bead"), 80),
            "file": [lam_sach(f, 200) for f in d.get("file", [])][:5],
            "de_xuat": [_de_xuat(x) for x in d.get("de_xuat", [])][:30], "loi": []}


def con_cua(beads: list[Bead], feature: str) -> list[Bead]:
    return [b for b in beads if b.parent == feature]


def feature_xong(b: Bead, beads: list[Bead]) -> bool:
    con = con_cua(beads, b.id)
    return (b.issue_type == "feature" and NHAN_THEO_PLAN in b.labels and b.status in TRANG_THAI_HIEN and bool(con)
            and all(c.status == "closed" for c in con))


def _muc_feature_xong(du_an: str, b: Bead, so_con: int) -> dict:
    return {"loai": "feature-xong", "du_an": du_an, "bead_id": b.id, "tieu_de": lam_sach(b.title, 200),
            "uu_tien": b.priority, "updated_at": b.updated_at, "chi_tiet": {"so_con": so_con}}


def bo_sung_spec(du_an: str, muc: list[dict], beads: list[Bead], kho) -> list[dict]:
    """Điền chi tiết cho mục `spec` (gom từ nhãn `cho-duyet-spec` ở 2a) và thêm các mục `feature-xong`."""
    ra = [{**m, "chi_tiet": chi_tiet_spec(kho, du_an, m["bead_id"])} if m["loai"] == "spec" else m for m in muc]
    return ra + [_muc_feature_xong(du_an, b, len(con_cua(beads, b.id))) for b in beads if feature_xong(b, beads)]
