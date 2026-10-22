"""TM-1: tuyến tự merge / tự deploy (dieu-khien-tu-dong, design D-5). GET xem được cho mọi người; POST qua cửa ghi
(`yeu_cau_ghi`) + mã thao tác; kênh `header` (tạm) chỉ nhận TẠM DỪNG (D87); thân yêu cầu không có chỗ cho QC/kiểm
lại/cấu trúc DB (D71, D76); lỗi thân không vọng lại lệnh."""
import pytest

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from passkey_phien_gia import headers_r
from bd_gia import BdGia
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop

LENH = {"deploy": "/Users/Shared/tram-deploy/repo-nhap/deploy.sh", "kiem_song": "", "lui": ""}
CAI_DAT = {"tu_merge": True, "tu_deploy": False, "dieu_kien": {"ci": True, "cot": True, "hang_rao": True},
           "lenh": LENH}
CD = "/api/du-an/repo-nhap/tu-dong/cai-dat"


def _app(tmp_path, *, unix=True):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    if unix:
        app.state.kenh_ghi = "unix-socket"
        client = KenhUnix(app)
        client.state = app.state
        return client, pt
    return app, pt


def _than(ma="ma-api-td-001", ev="0", **cai_dat):
    return {"ma_thao_tac": ma, "expected_version": ev, "cai_dat": {**CAI_DAT, **cai_dat}}


def _xem(app, ten="repo-nhap", **kw):
    return goi(app, "GET", f"/api/du-an/{ten}/tu-dong", **kw).json()


def test_xem_mac_dinh_ai_cung_xem_duoc(tmp_path):
    app, _ = _app(tmp_path, unix=False)
    tt = goi(app, "GET", "/api/tu-dong").json()
    assert tt["chi_tam_dung"] is False and tt["kenh_ghi"] == "header" and tt["la_dai_ca"] is False
    assert tt["tam_dung_tram"] is None and tt["estop"] is False
    tm3 = {"san_sang": False, "dem_hong": 0}                          # TM-3 thêm hai khoá (hợp đồng TM-4)
    assert tt["du_an"] == [
        {"ten": "hr-codex", "bat_ghi": False, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None,
         **tm3},
        {"ten": "repo-nhap", "bat_ghi": True, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None,
         **tm3}]
    ct = _xem(app)
    assert ct["cai_dat"] == {"tu_merge": False, "tu_deploy": False, "dieu_kien": {"ci": True, "cot": True,
                             "hang_rao": True}, "lenh": {"deploy": "", "kiem_song": "", "lui": ""}}
    assert ct["phien_ban"] == "0" and ct["khoa_cung"] == ["qc", "kiem_lai", "schema"] and ct["lich_su_doi"] == []
    assert _xem(app, headers=DAI_CA)["la_dai_ca"] is True
    estop.bat("thử")
    assert _xem(app)["estop"] is True
    assert goi(app, "GET", "/api/du-an/khong-co/tu-dong").status == 404


@pytest.mark.parametrize("h", [{}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
                               {k: v for k, v in DAI_CA.items() if k != "X-Tram"},
                               {**DAI_CA, "Origin": "https://evil.example"}])
def test_thieu_hoac_gia_danh_tinh_bi_403(tmp_path, h):
    """Scenario "Thiếu danh tính": 403, cài đặt không đổi — cả qua kênh unix-socket."""
    app, _ = _app(tmp_path)
    g = {"ma_thao_tac": "ma-td-danh-tinh", "expected_version": ""}
    for duong, than in ((CD, _than()), ("/api/du-an/repo-nhap/tu-dong/tam-dung", g), ("/api/tu-dong/tam-dung", g)):
        assert goi(app, "POST", duong, json_body=than, headers=h).status == 403
    assert _xem(app)["phien_ban"] == "0" and _xem(app)["tam_dung"] is None


def test_kenh_header_can_phien_tam_dung_van_duoc(tmp_path):
    app, _ = _app(tmp_path, unix=False)
    h = {**DAI_CA, "Cookie": ""}
    r = goi(app, "POST", CD, json_body=_than(), headers=h)
    assert r.status == 403 and r.json()["detail"] == "Cần phiên passkey"
    g = {"ma_thao_tac": "ma-td-header1", "expected_version": ""}
    for i, duong in enumerate(("/api/du-an/repo-nhap/tu-dong/tam-dung", "/api/tu-dong/tam-dung")):
        assert goi(app, "POST", duong, json_body={**g,"ma_thao_tac":f"ma-stop-00{i}"}, headers=h).status == 200
    for duong in ("/api/du-an/repo-nhap/tu-dong/tiep-tuc", "/api/tu-dong/tiep-tuc"):
        assert goi(app, "POST", duong, json_body=g, headers=h).status == 403
        assert goi(app, "POST", duong, json_body={**g,"ma_thao_tac":"ma-continue-"+str(len(duong))},
                   headers=DAI_CA).status == 200


def _luu_r(app, than, duong=CD):
    return goi(app, "POST", duong, json_body=than, headers=headers_r(app, duong, than))


def test_luu_qua_unix_socket_gui_lai_va_lich_su(tmp_path):
    app, _ = _app(tmp_path)
    r = _luu_r(app, _than())
    assert r.status == 200 and r.json()["lap_lai"] is False
    r2 = _luu_r(app, _than())                    # cùng mã thao tác
    assert r2.json() == {**r.json(), "lap_lai": True}
    pb = r.json()["ket_qua"]["tu_dong.cai_dat"]["phien_ban"]
    xem = _xem(app)
    assert xem["cai_dat"] == CAI_DAT and xem["phien_ban"] == pb and len(xem["lich_su_doi"]) == 1
    tat = _luu_r(app, _than("ma-api-td-002", pb, tu_merge=False))
    assert tat.status == 200
    ls = _xem(app)["lich_su_doi"]
    assert [(d["tac_nhan"], d["doi"][0]["truong"], d["doi"][0]["sau"]) for d in ls] == [
        ("dai-ca/dashboard", "tu_merge", False), ("dai-ca/dashboard", "tu_merge", True)]


def test_ma_loi_409_422(tmp_path):
    app, _ = _app(tmp_path)
    _luu_r(app, _than())
    r = _luu_r(app, _than("ma-api-td-003", "0", tu_merge=False))
    assert r.status == 409 and "đã đổi" in r.json()["loi"]                          # Scenario "Màn hình cũ"
    pb = _xem(app)["phien_ban"]
    qc = _than("ma-api-td-004", pb)
    qc["cai_dat"]["dieu_kien"] = {**CAI_DAT["dieu_kien"], "qc": False}                # D71: không có trường QC
    assert goi(app, "POST", CD, json_body=qc, headers=DAI_CA).status == 422
    assert goi(app, "POST", CD, json_body={**_than("ma-api-td-005", pb), "kiem_lai": False},
               headers=DAI_CA).status == 422
    r = _luu_r(app, _than("ma-api-td-006"), "/api/du-an/hr-codex/tu-dong/cai-dat")
    assert r.status == 422 and "chỉ quét thử" in r.json()["loi"]                    # Scenario "Dự án chỉ quét thử"
    assert goi(app, "POST", "/api/du-an/khong-co/tu-dong/cai-dat", json_body=_than("ma-api-td-007"),
               headers=DAI_CA).status == 404
    g = {"ma_thao_tac": "ma-api-td-008", "expected_version": ""}
    assert goi(app, "POST", "/api/du-an/_tram/tu-dong/tam-dung", json_body=g, headers=DAI_CA).status == 404
    assert goi(app, "GET", "/api/tu-dong").json()["tam_dung_tram"] is None           # không tạm dừng toàn trạm
    assert _xem(app)["phien_ban"] == pb and _xem(app, "hr-codex")["phien_ban"] == "0"


def test_lenh_co_bi_mat_bi_tu_choi_khong_vong_lai(tmp_path):
    """Scenario "Dán token vào lệnh kiểm còn sống": 422, câu hằng; phản hồi không chứa token, không lưu."""
    app, _ = _app(tmp_path)
    token = "ghp_" + "Zq7" * 12
    for i, lenh in enumerate((f"curl -H 'Authorization: token {token}' https://x.vn", f"{token}" + "x" * 2000)):
        r = _luu_r(app, _than(ma=f"ma-secret-{i}", lenh={**LENH, "kiem_song": lenh}))
        assert r.status == 422 and token.encode() not in r.body
    r = goi(app, "POST", CD, json_body=_than(ma="ma-secret-last", lenh={**LENH, "kiem_song": f"curl -u a:{token} https://x.vn"}),
            headers=headers_r(app, CD, _than(ma="ma-secret-last", lenh={**LENH, "kiem_song": f"curl -u a:{token} https://x.vn"})))
    assert r.json()["loi"] == "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
    assert _xem(app)["phien_ban"] == "0"
