"""Duyệt / Trả về spec, đóng feature (spec 4 §7.3, §10 bước 4) — G7 (không trùng), G11 (đúng bản đang xem)."""
import pytest

from bead_gia import bead
from spec_cho_duyet_gia import DA, V, cho_duyet, ghi_spec_xong
from tram.beads.bd import LoiBd
from tram.thao_tac.duyet_spec import NguonSpec, duyet_spec
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, XungDot
from tram.thao_tac.phe_duyet import duyet, tra_ve


def d(t, ma="ma-duyet-spec-1", **kw):
    kw = {"expected_commit": t.commit, "digest_bead": t.digest, **kw}
    return duyet(t.nc, "hr-f", ma=ma, expected_version=V, nguon_spec=t.ns, **kw)


def test_duyet_tao_con_phu_thuoc_nhan_va_su_kien(tmp_path):
    t = cho_duyet(tmp_path)
    kq = d(t)
    f, t1, t2 = (t.g.beads[i] for i in ("hr-f", "hr-f.1", "hr-f.2"))
    assert f.labels == ("theo-plan",) and t.commit in f.notes
    assert (t1.parent, t1.labels, t2.priority) == ("hr-f", ("b2b",), 1)
    assert ("hr-f.1", "blocks") in [(p.depends_on_id, p.loai) for p in t2.phu_thuoc]
    s = t.nc.kho.moi_nhat(DA, "hr-f", "spec.duyet")
    assert s.tac_nhan == "tram/giao-viec" and s.du_lieu["bead_moi"] == ["hr-f.1", "hr-f.2"]
    assert (s.du_lieu["commit"], s.du_lieu["digest_bead"]) == (t.commit, t.digest)
    assert kq.ket_qua["tao_bead"] == {"t1": "hr-f.1", "t2": "hr-f.2"}
    so = len(t.g.goi)
    assert d(t).lap_lai and len(t.g.goi) == so                              # gửi lại cùng mã: không ghi gì


@pytest.mark.parametrize("sua", [{"expected_commit": "0" * 40}, {"digest_bead": "sha256:" + "0" * 64},
                                 {"expected_commit": None}])
def test_ban_khac_ban_dang_xem_thi_409_khong_ghi(tmp_path, sua):
    t = cho_duyet(tmp_path)
    with pytest.raises(XungDot if sua.get("expected_commit", 1) is not None else KhongHopLe):
        d(t, **sua)
    assert t.g.so_lan("tao") == 0 and t.g.so_lan("cap_nhat_nhan") == 0


def test_spec_moi_hon_hoac_git_khac_ban_da_kiem_thi_409(tmp_path):
    t = cho_duyet(tmp_path)
    ghi_spec_xong(t.nc.kho, "c" * 40, t.digest)                                # lượt spec mới hơn
    with pytest.raises(XungDot):
        d(t)
    t2 = cho_duyet(tmp_path / "b")
    t2.nc.kho.ghi(DA, "spec.xong", {"feature": "hr-f", "nhanh": "tram/spec-hr-f", "commit": t2.commit,
                                    "digest_bead": "sha256:" + "1" * 64, "file": [], "de_xuat": []}, bead_id="hr-f")
    with pytest.raises(XungDot):
        d(t2, digest_bead="sha256:" + "1" * 64)                               # file trên Git khác digest đã kiểm
    assert t2.g.so_lan("tao") == 0


def test_crash_giua_chung_lam_tiep_khong_tao_trung(tmp_path):
    t = cho_duyet(tmp_path, ra_loi_truoc={"tao": 2})
    with pytest.raises(LoiBd):
        d(t)
    d(t)
    assert t.g.so_lan("tao") == 2 and t.g.beads["hr-f"].labels == ("theo-plan",)
    t3 = cho_duyet(tmp_path / "c", ra_loi_truoc={"cap_nhat_nhan": 1})
    with pytest.raises(LoiBd):
        d(t3)
    d(t3, ma="ma-duyet-spec-moi")                                            # Duyệt lại bằng mã mới
    assert t3.g.so_lan("tao") == 2 and t3.g.so_lan("them_phu_thuoc") == 1


def test_khong_con_cho_duyet_hoac_chua_co_kho_kiem(tmp_path):
    t = cho_duyet(tmp_path)
    with pytest.raises(ChuaHoTro):
        duyet(t.nc, "hr-f", ma="ma-duyet-spec-2", expected_version=V, expected_commit=t.commit,
              digest_bead=t.digest, nguon_spec=NguonSpec(t.g, None))
    d(t)
    with pytest.raises(XungDot):
        d(t, ma="ma-duyet-spec-3")                                            # bead đã đổi — tải lại
    with pytest.raises(XungDot):
        duyet_spec(t.nc, t.ns, "hr-f", ma="ma-duyet-spec-4", expected_version=t.g.beads["hr-f"].updated_at,
                   expected_commit=t.commit, digest_bead=t.digest)


def test_tra_ve_spec(tmp_path):
    t = cho_duyet(tmp_path)
    tra_ve(t.nc, "hr-f", gop_y="Tách API và màn hình", ma="ma-trave-spec-1", expected_version=V, nguon_spec=t.ns)
    f = t.g.beads["hr-f"]
    assert f.labels == ("can-spec",) and "Trả về spec: Tách API và màn hình" in f.notes
    assert t.nc.kho.moi_nhat(DA, "hr-f", "spec.tra_ve").du_lieu["gop_y"] == "Tách API và màn hình"
    so = len(t.g.goi)
    tra_ve(t.nc, "hr-f", gop_y="Tách API và màn hình", ma="ma-trave-spec-1", expected_version=V, nguon_spec=t.ns)
    assert len(t.g.goi) == so


def test_dong_feature_khi_moi_con_da_dong(tmp_path):
    con = bead("hr-f.1", status="closed", parent="hr-f")
    t = cho_duyet(tmp_path, con, bead("hr-f.2", parent="hr-f"))
    t.g.beads["hr-f"] = bead("hr-f", issue_type="feature", labels=["theo-plan"])
    with pytest.raises(KhongHopLe):
        d(t, ma="ma-dong-f-1")
    t.g.dong("hr-f.2", "xong")
    d(t, ma="ma-dong-f-2")
    assert t.g.beads["hr-f"].status == "closed" and "mọi bead con đã đóng" in t.g.beads["hr-f"].close_reason

@pytest.mark.parametrize("doi", ["ref", "tra-ve"])
def test_duyet_do_khong_tiep_tuc_khi_ban_duoc_duyet_da_thay(tmp_path, doi):
    t = cho_duyet(tmp_path, ra_loi_truoc={"tao": 2})
    with pytest.raises(LoiBd):
        d(t)
    if doi == "ref":
        ghi_spec_xong(t.nc.kho, "c" * 40, t.digest)
    else:
        t.nc.kho.ghi(DA, "spec.tra_ve", {"gop_y": "Đổi hướng", "ma_thao_tac": "ma-trave-khac"}, bead_id="hr-f")
    so = len(t.g.goi)
    with pytest.raises(XungDot):
        d(t)
    # Có thể đọc Beads, tuyệt đối không tạo thêm con/phụ thuộc/nhãn từ approval cũ.
    assert t.g.so_lan("tao") == 1 and t.g.so_lan("cap_nhat_nhan") == 0
    assert t.nc.kho.moi_nhat(DA, "hr-f", "spec.duyet") is None

