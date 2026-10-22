"""TM-3 (D96, D101; design D-5): trang Tự động thêm `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`; trang Phê duyệt
thêm một dòng "sẵn sàng deploy" mỗi dự án và cộng vào số đếm — phía máy chủ, GET ai cũng xem, không lộ lệnh."""
from contextlib import closing

from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doi_cai_dat, giao_dich

DU = CaiDatTuDong(lenh_deploy="/Users/Shared/tram-deploy/d.sh", lenh_kiem_song="/Users/Shared/tram-deploy/k.sh",
                  lenh_lui="/Users/Shared/tram-deploy/l.sh")


def _app(tmp_path):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    return app, pt


def _ghi(pt, ten, loai, du_lieu, bead=None, tac_nhan="tram/tu-deploy") -> int:
    with closing(pt.mo_kho()) as kho, giao_dich(kho.db):
        return ghi_trong_giao_dich(kho.db, ten, loai, du_lieu, bead_id=bead, tac_nhan=tac_nhan,
                                   luc="2026-10-18T21:52:00Z")


def _merge(pt, ten, i, mc) -> int:
    return _ghi(pt, ten, "pr.da_merge", {"commit": f"c{i}", "merge_commit": mc, "pr": i, "ma_thao_tac": f"pr-{i}"},
                f"rn-{i}", "tram/giao-viec")


def test_mac_dinh_khong_co_gi(tmp_path):
    app, _ = _app(tmp_path)
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    assert (ct["san_sang"], ct["dang_deploy"], ct["lich_su"], ct["dem_hong"]) == (None, None, [], 0)
    assert goi(app, "GET", "/api/phe-duyet").json()["so"] == 0
    tt = goi(app, "GET", "/api/tu-dong").json()["du_an"]
    assert [(d["ten"], d["san_sang"], d["dem_hong"]) for d in tt] == [("hr-codex", False, 0), ("repo-nhap", False, 0)]


def test_san_sang_o_trang_tu_dong_va_phe_duyet(tmp_path):
    """Scenario "Hiện ở trang Phê duyệt", "Ba lần merge chờ deploy" (gồm 2 việc), "Đại ca gộp tay"."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        doi_cai_dat(kho.db, "repo-nhap", lambda c: DU, tac_nhan="dai-ca/dashboard")
    bao = [_merge(pt, "repo-nhap", 11, "9be2"), _merge(pt, "repo-nhap", 12, "a41c")]
    _ghi(pt, "repo-nhap", "deploy.san_sang", {"commit": "a41c", "so_merge": 2, "bao_gom": bao, "cho": []})
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    ss = {"commit": "a41c", "so_merge": 2, "bead_ids": ["rn-11", "rn-12"], "luc": "2026-10-18T21:52:00Z",
          "commit_dang_chay": None}
    assert ct["san_sang"] == ss and ct["dang_deploy"] is None and ct["dem_hong"] == 0
    assert [x["loai"] for x in ct["lich_su"]] == ["san_sang"]       # hai merge gộp tay: nằm trong "gồm 2 việc"
    pd = goi(app, "GET", "/api/phe-duyet").json()
    assert pd["so"] == 1 and pd["muc"] == [{"loai": "san-sang-deploy", "du_an": "repo-nhap", "bead_id": None,
                                            "tieu_de": "", "uu_tien": None, "updated_at": ss["luc"],
                                            "chi_tiet": {**ss, "phien_ban": "1"}}]   # TM20 T6: nút Deploy gửi phiên bản
    tt = {d["ten"]: d for d in goi(app, "GET", "/api/tu-dong").json()["du_an"]}
    assert (tt["repo-nhap"]["san_sang"], tt["hr-codex"]["san_sang"]) == (True, False)


def test_thieu_lenh_khong_co_dong_phe_duyet(tmp_path):
    """D96: chỉ khi dự án khai đủ 3 lệnh."""
    app, pt = _app(tmp_path)
    i = _merge(pt, "hr-codex", 1, "m1")
    _ghi(pt, "hr-codex", "deploy.san_sang", {"commit": "m1", "so_merge": 1, "bao_gom": [i], "cho": []})
    assert goi(app, "GET", "/api/du-an/hr-codex/tu-dong").json()["san_sang"] is None
    assert goi(app, "GET", "/api/phe-duyet").json()["so"] == 0


def test_lich_su_va_dem_hong_khong_lo_lenh(tmp_path):
    """Scenario "Lệnh deploy in ra token": dashboard chỉ hiện "hỏng · mã thoát 1 · 42 giây"."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        doi_cai_dat(kho.db, "repo-nhap", lambda c: DU, tac_nhan="dai-ca/dashboard")
    _ghi(pt, "repo-nhap", "deploy.bat_dau", {"ma_thao_tac": "dp-1", "commit": "c0d9", "commit_truoc": "5d3e",
                                             "nguon": "tu_dong"})
    _ghi(pt, "repo-nhap", "deploy.lenh", {"ma_thao_tac": "dp-1", "buoc": "deploy", "ma_thoat": 1, "giay": 42,
                                          "het_gio": False, "digest_log": "sha256:ab"})
    assert goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["dang_deploy"]["trang_thai"] == "chay"
    _ghi(pt, "repo-nhap", "deploy.xong", {"ma_thao_tac": "dp-1", "ket_qua": "da_lui", "dem_hong": 1})
    r = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong")
    ct = r.json()
    assert ct["dem_hong"] == 1 and ct["dang_deploy"] is None
    assert ct["lich_su"] == [{"luc": "2026-10-18T21:52:00Z", "loai": "deploy_lui", "bead_id": None, "commit": "c0d9",
                              "chi_tiet": "deploy: mã thoát 1 · 42 giây (bản trước 5d3e)", "ai": "tu_deploy"}]
    assert goi(app, "GET", "/api/tu-dong").json()["du_an"][1]["dem_hong"] == 1
    assert "sha256:ab" not in r.body.decode() and "commit_truoc" not in r.body.decode()
