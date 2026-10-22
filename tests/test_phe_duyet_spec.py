"""Phê duyệt — "Spec chờ duyệt" theo commit (spec 2 §5.2, spec 4 §7.3) và "Feature xong, chờ đóng" (§10 bước 4)."""
from bead_gia import bead
from tram.su_kien.kho import KhoSuKien
from tram.suy.phe_duyet import gom_phe_duyet

C1, C2 = "c1" * 20, "c2" * 20
DE_XUAT = [{"khoa": "t1", "tieu_de": "Việc ‮t1", "loai": "task", "uu_tien": 2, "phu_thuoc": [], "nhan": ["b2b"]}]


def xong(k, commit, digest="sha256:" + "d" * 64):
    k.ghi("hr", "spec.xong", {"feature": "hr-f", "nhanh": "tram/spec-hr-f", "commit": commit, "digest_bead": digest,
                              "file": ["docs/specs/a.md", "docs/plans/a.md", "docs/plans/hr-f.beads.json"],
                              "de_xuat": DE_XUAT, "giao_id": "g-1"}, bead_id="hr-f", tac_nhan="tram/giao-viec")


def muc(k, *beads):
    return {(m["loai"], m["bead_id"]): m for m in gom_phe_duyet(["hr"], {"hr": list(beads)}, k)}


F = bead("hr-f", issue_type="feature", labels=["cho-duyet-spec"])


def test_spec_cho_duyet_hien_ban_moi_nhat_da_lam_sach(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    xong(k, C1)
    xong(k, C2)
    ct = muc(k, F)[("spec", "hr-f")]["chi_tiet"]
    assert (ct["commit"], ct["nhanh"], ct["loi"]) == (C2, "tram/spec-hr-f", [])
    assert ct["de_xuat"][0]["tieu_de"] == "Việc t1" and ct["file"][2] == "docs/plans/hr-f.beads.json"


def test_chua_co_spec_xong_hoac_da_tra_ve(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert muc(k, F)[("spec", "hr-f")]["chi_tiet"]["commit"] is None
    xong(k, C1)
    k.ghi("hr", "spec.tra_ve", {"gop_y": "x", "ma_thao_tac": "m"}, bead_id="hr-f", tac_nhan="dai-ca/dashboard")
    ct = muc(k, F)[("spec", "hr-f")]["chi_tiet"]
    assert ct["commit"] is None and ct["loi"]


def test_feature_xong_cho_dong(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    f = bead("hr-f", issue_type="feature", labels=["theo-plan"])
    con = [bead("hr-f.1", status="closed", parent="hr-f"), bead("hr-f.2", status="closed", parent="hr-f")]
    m = muc(k, f, *con)
    assert m[("feature-xong", "hr-f")]["chi_tiet"] == {"so_con": 2}
    assert ("feature-xong", "hr-f") not in muc(k, f, con[0], bead("hr-f.2", parent="hr-f"))
    assert ("feature-xong", "hr-f") not in muc(k, f)                                  # chưa có con
    assert ("feature-xong", "hr-f") not in muc(k, bead("hr-f", issue_type="feature", labels=["theo-plan"],
                                                       status="closed"), *con)
    g = bead("hr-g", issue_type="feature", labels=["cho-duyet-spec"])
    assert [x["loai"] for x in gom_phe_duyet(["hr"], {"hr": [f, *con, g]}, k)] == ["spec", "feature-xong"]
