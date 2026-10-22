"""Vòng tick — luồng feature (spec 4 §7.2, §8, §9, §10): phieu-thieu, spec.xong → cho-duyet-spec, đợt sửa spec."""
from bead_gia import bead
from feature_gia import ke_hoach_json
from giao_viec_gia import dung
from kho_phieu_gia import dat_phieu
from su_kien_gia import DA, cong_bo, ds, nhan, sk
from test_phieu_yeu_cau import mo_ta
from test_xet_spec import TC, bg_spec, tep_spec
from tram.chu import estop
from tram.giao_viec.feature import con_dot_spec
from tram.giao_viec.ke_hoach import digest_ke_hoach
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick
from xu_ly_gia import ket_thuc_bang


def feat(**kw):
    kw.setdefault("description", mo_ta())
    return bead("hr-f", title="Hoa hồng", issue_type="feature", labels=["can-spec"], **kw)


def loai(t, l, bead_id="hr-f"):
    return [s for s in ds(t.kho, bead_id) if s.loai == l]


def esc(t, ly_do):
    return [b for b in t.g.beads.values() if b.issue_type == "decision" and f"ly_do: {ly_do}" in b.description]


def test_phieu_thieu_mot_escalation_mo_va_tao_lai_khi_dong_ma_van_sai(tmp_path):
    t = dung(tmp_path, feat(description="Chưa có phiếu"))
    assert mot_vong_tick(t.bo)["phieu_thieu"] == 1 and "phieu_thieu" not in mot_vong_tick(t.bo)
    [e] = esc(t, "phieu-thieu")
    assert loai(t, "phieu.loi")[0].du_lieu["loi"] and "không có khối" in e.description
    t.g.dong(e.id, "Đã sửa")
    assert mot_vong_tick(t.bo)["phieu_thieu"] == 1 and len(esc(t, "phieu-thieu")) == 2


def spec_xong(t):
    sha = t.k.day("tram/spec-hr-f", tep_spec(), tu=t.k.main)
    p = dat_phieu(t.kho, bead_id="hr-f", buoc="spec", tieu_chi=[TC], cha=t.k.main)
    nhan(t.kho, p.giao_id, p.luot, buoc="spec", bead_id="hr-f")
    cong_bo(t.kho, p.luot, sha, bead_id="hr-f")
    ket_thuc_bang(t.kho, p, "xong", commit=sha, ban_giao=bg_spec(sha))
    return sha


def test_spec_xong_hop_le_chuyen_cho_duyet_trong_cung_vong(tmp_path):
    t = dung(tmp_path, feat())
    sha = spec_xong(t)
    r = mot_vong_tick(t.bo)
    assert r["cong_viec"] == 1 and r["spec_xong"] == 1 and t.g.beads["hr-f"].labels == ("cho-duyet-spec",)
    [x] = loai(t, "spec.xong")
    assert (x.du_lieu["commit"], x.du_lieu["digest_bead"]) == (sha, digest_ke_hoach(ke_hoach_json()))
    assert [b["khoa"] for b in x.du_lieu["de_xuat"]] == ["t1", "t2"] and x.du_lieu["nhanh"] == "tram/spec-hr-f"
    assert "spec_xong" not in mot_vong_tick(t.bo) and len(loai(t, "spec.xong")) == 1


def test_estop_khong_doi_nhan(tmp_path):
    t = dung(tmp_path, feat())
    spec_xong(t)
    estop.bat("thử")
    try:
        assert "spec_xong" not in mot_vong_tick(t.bo) and t.g.beads["hr-f"].labels == ("can-spec",)
    finally:
        estop.tat()


def test_dot_sua_spec_du_tra_ve_thi_escalation_tra_loi_thi_dot_moi(tmp_path):
    t = dung(tmp_path, feat())
    for i in range(2):
        sk(t.kho, "spec.tra_ve", {"gop_y": f"lần {i}"}, bead_id="hr-f")
    r = mot_vong_tick(t.bo)
    assert r["spec_tra_ve_nhieu"] == 1 and r["chu_ky_moi"] == 2 and "spec_tra_ve_nhieu" not in mot_vong_tick(t.bo)
    [e] = esc(t, "spec-tra-ve-nhieu")
    t.g.dong(e.id, "Làm tiếp, gộp hai màn")
    r = mot_vong_tick(t.bo)
    assert r["escalation_dong"] == 1 and r["dot_spec_moi"] == 1 and con_dot_spec(ds(t.kho, "hr-f"))
    assert "spec_tra_ve_nhieu" not in mot_vong_tick(t.bo)


def test_het_ngan_sach_spec_thi_escalation(tmp_path):
    t = dung(tmp_path, feat())
    for i in range(5):
        nhan(t.kho, f"g-{i}", i + 1, buoc="spec", bead_id="hr-f", ngan_sach={"so_lan_chay": 2, "phut": 45,
                                                                            "token_ra": 1})
        sk(t.kho, "giao.ket_thuc", {"giao_id": f"g-{i}", "luot": i + 1, "buoc": "spec", "ket_thuc": "thu_hoi",
                                    "ly_do": "mat-nhip", "commit": None, "loi": []}, bead_id="hr-f")
    assert mot_vong_tick(t.bo)["het_ngan_sach"] == 1 and len(esc(t, "het-ngan-sach")) == 1
    assert moi_nhat(ds(t.kho, "hr-f"), "escalation.tao").du_lieu["ly_do"] == "het-ngan-sach"

def test_pha_nhanh_feature_khong_goi_git(tmp_path):
    from tram.giao_viec.tick import vong_nhanh
    t = dung(tmp_path, feat(description="Chưa có phiếu"))
    def cam_git(da):
        raise AssertionError("Pha nhanh không gọi Git")
    t.bo.kho_git = cam_git
    assert vong_nhanh(t.bo)["phieu_thieu"] == 1

