from tram.suy.van_phong import cac_phong, suc_khoe

HE_QUET = {"loai": "he", "du_an": "hr-codex", "bead_id": None, "chi_tiet": {"su_kien": "quet.loi"}}
HE_DAO = {"loai": "he", "du_an": "_tram", "bead_id": None,
          "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "khe_id": "B/claude-2"}}
REVIEW = {"loai": "cho-review", "du_an": "hr-codex", "bead_id": "hr-1", "chi_tiet": {}}


def test_suc_khoe_xanh_vang_do():
    assert suc_khoe(estop_bat=False, muc=[REVIEW], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": [], "muc": []}
    nv = [{"khe_id": "B/claude-1", "trang_thai": "mat_ket_noi"}, {"khe_id": "B/claude-3", "trang_thai": "lam"}]
    v = suc_khoe(estop_bat=False, muc=[HE_DAO], loi_doc={}, nhan_vat=nv)
    assert (v["mau"], v["ly_do"]) == ("vang", ["Cầu dao khe B/claude-2 đang ngắt", "Khe B/claude-1: mất kết nối"])
    r = suc_khoe(estop_bat=True, muc=[HE_QUET, HE_DAO], loi_doc={"tram": "bd lỗi <bí mật>"}, nhan_vat=[])
    assert r["mau"] == "do"
    assert r["ly_do"] == ["Estop đang bật", "Không đọc được beads của dự án tram", "hr-codex: lỗi quét beads",
                          "Cầu dao khe B/claude-2 đang ngắt"]
    assert "bí mật" not in str(r)


def test_cac_phong_co_dinh_truoc_roi_du_an():
    sk = {"mau": "xanh", "ly_do": []}
    ds = cac_phong(["hr-codex", "tram"], so_cho=3, suc_khoe=sk)
    assert [p["ma"] for p in ds] == ["dieu-phoi", "giam-doc", "may-chu", "ca-phe", "du-an:hr-codex", "du-an:tram"]
    assert ds[0] == {"ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": None}
    assert ds[1]["so_cho"] == 3 and ds[2]["suc_khoe"] == sk
    assert ds[4] == {"ma": "du-an:hr-codex", "loai": "du_an", "ten": "hr-codex", "du_an": "hr-codex"}
