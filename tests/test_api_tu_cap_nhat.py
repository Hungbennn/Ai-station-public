"""TC Task 9 (spec cong-tac-de-nghi-viec, design D-8, D-9; D108, D110, D113): tuyến đọc/ghi nút "agent tự cập nhật
việc" — GET ai cũng xem (khoá nút theo `la_dai_ca`, `chi_tat`); POST qua cửa ghi: thiếu/giả danh tính → 403; cùng mã
thao tác → kết quả lần đầu, một dòng lịch sử; màn hình cũ → 409; `bat_ghi: false` → 422; kênh `header` chỉ TẮT được;
dấu vết đề nghị của một việc (Scenario "Xem dấu vết của một phiếu")."""
import json
from contextlib import closing

import pytest

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.api.kenh_ghi import KenhUnix
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, doi_cai_dat
from tram.su_kien.kho import KhoSuKien

DUONG = "/api/du-an/repo-nhap/tu-cap-nhat"
BAT = {"bat": True, "tien_do": True, "viec_moi": True, "bi_chan": True}


def _app(tmp_path, *, unix=True):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    if unix:
        app.state.kenh_ghi = "unix-socket"
        client = KenhUnix(app)
        client.state = app.state
        return client, pt
    return app, pt


def _than(ma="ma-api-tc-0001", ev="0", **nut):
    return {"ma_thao_tac": ma, "expected_version": ev, "cai_dat": {**BAT, **nut}}


def _xem(app, ten="repo-nhap", **kw):
    return goi(app, "GET", f"/api/du-an/{ten}/tu-cap-nhat", **kw).json()


def test_xem_mac_dinh_ai_cung_xem_duoc(tmp_path):
    """Scenario "Dự án chưa từng chỉnh", "Xem khi không phải Đại ca" (phía máy chủ: `la_dai_ca` false)."""
    app, _ = _app(tmp_path, unix=False)
    x = _xem(app)
    assert x == {"du_an": "repo-nhap", "bat_ghi": True, "cai_dat": {**BAT, "bat": False}, "phien_ban": "0",
                 "kenh_ghi": "header", "chi_tat": False, "la_dai_ca": False, "lich_su_doi": []}
    assert _xem(app, headers=DAI_CA)["la_dai_ca"] is True and _xem(app, "hr-codex")["bat_ghi"] is False
    assert goi(app, "GET", "/api/du-an/khong-co/tu-cap-nhat").status == 404


@pytest.mark.parametrize("h", [{}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
                               {k: v for k, v in DAI_CA.items() if k != "X-Tram"},
                               {**DAI_CA, "Origin": "https://evil.example"}])
def test_thieu_hoac_gia_danh_tinh_bi_403(tmp_path, h):
    """Scenario "Thiếu danh tính": 403, nút không đổi — cả qua kênh unix-socket."""
    app, _ = _app(tmp_path)
    assert goi(app, "POST", DUONG, json_body=_than(), headers=h).status == 403
    assert _xem(app)["phien_ban"] == "0"


def test_luu_gui_lai_man_hinh_cu_va_lich_su(tmp_path):
    """Scenario "Gửi lại cùng mã thao tác", "Màn hình cũ", "Khởi động lại trạm" (lịch sử ai đổi, trước → sau)."""
    app, _ = _app(tmp_path)
    r = goi(app, "POST", DUONG, json_body=_than(), headers=DAI_CA)
    pb = r.json()["ket_qua"]["tu_cap_nhat.cai_dat"]["phien_ban"]
    assert r.status == 200 and r.json()["lap_lai"] is False and pb != "0"
    lai = goi(app, "POST", DUONG, json_body=_than(), headers=DAI_CA).json()
    assert lai == {"ket_qua": {"tu_cap_nhat.cai_dat": {"phien_ban": pb}}, "lap_lai": True}
    cu = goi(app, "POST", DUONG, json_body=_than("ma-api-tc-0002", "0", viec_moi=False), headers=DAI_CA)
    assert cu.status == 409 and "tải lại" in cu.json()["loi"]
    x = _xem(app)
    assert x["cai_dat"] == BAT and x["phien_ban"] == pb and len(x["lich_su_doi"]) == 1
    assert x["lich_su_doi"][0]["tac_nhan"] == "dai-ca/dashboard" and x["lich_su_doi"][0]["doi"] == [
        {"truong": "bat", "truoc": False, "sau": True}]


def test_du_an_chi_quet_thu_khong_bat_duoc(tmp_path):
    """Scenario "Dự án chỉ quét thử": bật → 422; tắt / chỉnh nút con khi tắt vẫn được."""
    app, _ = _app(tmp_path)
    duong = "/api/du-an/hr-codex/tu-cap-nhat"
    r = goi(app, "POST", duong, json_body=_than(), headers=DAI_CA)
    assert r.status == 422 and "chỉ quét thử" in r.json()["loi"]
    ok = goi(app, "POST", duong, json_body=_than("ma-api-tc-0003", bat=False, viec_moi=False), headers=DAI_CA)
    assert ok.status == 200 and _xem(app, "hr-codex")["cai_dat"]["viec_moi"] is False


def test_than_la_bi_422_khong_vong_lai(tmp_path):
    app, _ = _app(tmp_path)
    for than in (_than(ma="ma-schema-001", uu_tien=0), {**_than(ma="ma-schema-002"), "la": 1}, {"ma_thao_tac": "ma-api-tc-0004", "expected_version": "0",
                                                         "cai_dat": {"bat": True}}):
        r = goi(app, "POST", DUONG, json_body=than, headers=DAI_CA)
        assert r.status == 422 and "uu_tien" not in r.body.decode()


def test_kenh_header_moi_cong_tac_can_phien(tmp_path):
    app, _ = _app(tmp_path, unix=False)
    for doi in ({}, {"bat":False}, {"bat":False,"tien_do":False}):
        r = goi(app, "POST", DUONG, json_body=_than(**doi), headers={**DAI_CA,"Cookie":""})
        assert r.status == 403 and r.json()["detail"] == "Cần phiên passkey"
    assert goi(app,"POST",DUONG,json_body=_than(),headers=DAI_CA).status == 200


def _sk(kho, loai, d, tac_nhan="tho/B/claude-1", du_an="repo-nhap"):
    kho.ghi(du_an, loai, d, bead_id="rn-12", tac_nhan=tac_nhan)


def test_dau_vet_de_nghi_cua_mot_viec(tmp_path):
    """Scenario "Xem dấu vết của một phiếu": loại, lúc nhận, kết quả, lý do; không lộ lý do bí gốc."""
    app, _ = _app(tmp_path)
    g = {"giao_id": "g-20261018-0001", "luot": 1}
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        _sk(kho, "bao.tien_do", {**g, "noi_dung": "đang viết test", "ma_de_nghi": "dn-1", "request_id": "r-1"})
        _sk(kho, "de_nghi.da_ghi", {"ma_de_nghi": "dn-1", "loai": "tien_do", "bead_id": "rn-12"}, "tram/de-nghi")
        _sk(kho, "bao.viec_moi", {**g, "viec_moi": {"tieu_de": "Việc A", "mo_ta": "m", "loai_viec": "bug"},
                                  "ma_de_nghi": "dn-2", "request_id": "r-2"})
        _sk(kho, "de_nghi.bo", {"ma_de_nghi": "dn-2", "loai": "viec_moi", "ly_do": "luot-khong-dat"}, "tram/de-nghi")
        _sk(kho, "de_nghi.tu_choi", {**g, "loai": "tien_do", "ly_do": "co-bi-mat", "nhom": {"khoa_da_biet": 1}},
            "tram/api")
        _sk(kho, "bao.bi", {**g, "ly_do": "agent", "noi_dung": "BÍ MẬT GỐC", "ma_de_nghi": "dn-3", "request_id": "r-3"})
        _sk(kho, "bao.moc", {**g, "noi_dung": "mốc"})
    r = goi(app, "GET", "/api/du-an/repo-nhap/bead/rn-12/de-nghi")
    ds = r.json()["de_nghi"]
    assert [(d["loai"], d["ket_qua"], d.get("ly_do")) for d in ds] == [
        ("bi_chan", "cho", None), ("tien_do", "tu_choi", "co-bi-mat"), ("viec_moi", "bo", "luot-khong-dat"),
        ("tien_do", "da_ghi", None)]
    assert ds[3]["noi_dung"] == "đang viết test" and ds[3]["khe"] == "B/claude-1" and ds[3]["luot"] == 1
    assert ds[2]["tieu_de"] == "Việc A" and "BÍ MẬT GỐC" not in json.dumps(ds, ensure_ascii=False)
    assert goi(app, "GET", "/api/du-an/repo-nhap/bead/-x/de-nghi").status == 422


def test_dau_vet_cho_vi_khoa_ghi(tmp_path):
    """D134 — Scenario "Khoá ghi giữa chừng" (phần xem): dự án đang khoá ghi → đề nghị còn chờ hiện lý do "khoa-ghi"
    (mở khoá thì ghi bù); đề nghị đã có kết quả giữ nguyên; dự án không khoá → chờ không kèm lý do."""
    app, _ = _app(tmp_path)
    g, vm = {"giao_id": "g-20261018-0001", "luot": 1}, {"tieu_de": "Việc A", "mo_ta": "m", "loai_viec": "bug"}
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        for da in ("hr-codex", "repo-nhap"):
            _sk(kho, "bao.viec_moi", {**g, "viec_moi": vm, "ma_de_nghi": f"dn-{da}", "request_id": "r-1"}, du_an=da)
        _sk(kho, "bao.tien_do", {**g, "noi_dung": "x", "ma_de_nghi": "dn-2", "request_id": "r-2"}, du_an="hr-codex")
        _sk(kho, "de_nghi.da_ghi", {"ma_de_nghi": "dn-2", "loai": "tien_do", "bead_id": "rn-12"}, "tram/de-nghi",
            du_an="hr-codex")
    khoa = goi(app, "GET", "/api/du-an/hr-codex/bead/rn-12/de-nghi").json()["de_nghi"]
    assert [(d["loai"], d["ket_qua"], d.get("ly_do")) for d in khoa] == [
        ("tien_do", "da_ghi", None), ("viec_moi", "cho", "khoa-ghi")]
    mo = goi(app, "GET", "/api/du-an/repo-nhap/bead/rn-12/de-nghi").json()["de_nghi"]
    assert [(d["ket_qua"], d.get("ly_do")) for d in mo] == [("cho", None)]
