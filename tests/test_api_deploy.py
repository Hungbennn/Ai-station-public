"""TM-3: nút Deploy của Đại ca `POST /api/du-an/{ten}/tu-dong/deploy` (tu-deploy "Nút Deploy của Đại ca";
dieu-khien-tu-dong "Estop dừng cả tự merge và tự deploy", "Deploy tay khi dự án tạm dừng", "Cửa ghi còn tạm"; D87,
D97 luật 3, D116, D129 — cùng tuyến cho nút ở trang Tự động và ở dòng Phê duyệt; Codex Q7). Chỉ ghi yêu cầu — không
lệnh nào chạy trong tram-api."""
import json
from contextlib import closing

import pytest

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.su_kien.kho import KhoSuKien
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung, giao_dich

M4, M5 = "4" * 40, "5" * 40
DP = "/api/du-an/repo-nhap/tu-dong/deploy"
DU = CaiDatTuDong(lenh_deploy="/Users/Shared/tram-deploy/d.sh", lenh_kiem_song="/Users/Shared/tram-deploy/k.sh",
                  lenh_lui="/Users/Shared/tram-deploy/l.sh")


@pytest.fixture(autouse=True)
def dinh_gia(monkeypatch):
    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten, db: M5)
    monkeypatch.setattr("tram.thao_tac.deploy.cong_mo", lambda: True)
    monkeypatch.setattr("tram.thao_tac.deploy.can_duong", lambda *a: None)


def _app(tmp_path, *, unix=True, cd=DU, san_sang=True):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    with closing(pt.mo_kho()) as kho:
        for ten in ("repo-nhap", "hr-codex"):
            doi_cai_dat(kho.db, ten, lambda c: cd, tac_nhan="dai-ca/dashboard")
            if san_sang:
                i = _ghi(kho, ten, "pr.da_merge", {"commit": "c7", "merge_commit": M5, "ma_thao_tac": "pr-7"}, "rn-7")
                _ghi(kho, ten, "deploy.san_sang", {"commit": M5, "so_merge": 1, "bao_gom": [i], "cho": []})
    if unix:
        app.state.kenh_ghi = "unix-socket"
        client = KenhUnix(app)
        client.state = app.state
        return client, pt
    return app, pt


def _ghi(kho, ten, loai, du_lieu, bead=None) -> int:
    with giao_dich(kho.db):
        return ghi_trong_giao_dich(kho.db, ten, loai, du_lieu, bead_id=bead, tac_nhan="tram/tu-deploy",
                            luc="2026-10-18T10:00:00Z")


def _than(ma="ma-api-dp-001", commit=M5):
    return {"ma_thao_tac": ma, "expected_version": "1", "expected_commit": commit}


def _yeu_cau(pt) -> list[dict]:
    with closing(pt.mo_kho()) as kho:
        return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai='deploy.yeu_cau'")]


def test_dai_ca_bam_deploy_mot_lan_theo_ma(tmp_path):
    """Scenario "Đại ca bấm Deploy": ghi yêu cầu cho `m5`, hàng "sẵn sàng" chuyển "đang deploy"; gửi lại cùng mã."""
    app, pt = _app(tmp_path)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 200 and r.json() == {"ket_qua": {"deploy.yeu_cau": {"commit": M5}}, "lap_lai": False}
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    assert ct["san_sang"] is None and ct["dang_deploy"]["trang_thai"] == "cho" and ct["dang_deploy"]["commit"] == M5
    assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).json()["lap_lai"] is True
    assert _yeu_cau(pt) == [{"ma_thao_tac": "ma-api-dp-001", "commit": M5, "nguon": "dai_ca", "phien_ban": "1"}]
    r = goi(app, "POST", DP, json_body=_than("ma-api-dp-002"), headers=DAI_CA)       # đã có yêu cầu chờ
    assert r.status == 422 and "Đang có một lần deploy" in r.json()["loi"]


def test_bam_tren_man_hinh_cu_409(tmp_path):
    """Scenario "Bấm trên màn hình cũ": commit mới nhất `m5`, Đại ca bấm với `m4` → 409, không ghi gì."""
    app, pt = _app(tmp_path)
    r = goi(app, "POST", DP, json_body=_than(commit=M4), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại") and "đã đổi" in r.json()["loi"]
    assert _yeu_cau(pt) == []
    assert goi(app, "POST", DP, json_body=_than("ma-api-dp-fresh"), headers=DAI_CA).status == 200
    # Payload khác dùng mã mới; passkey ràng toàn bộ thân kể cả commit kỳ vọng.


def test_co_merge_moi_chua_vao_ban_cho_thi_409(tmp_path):
    """Codex Q7: hàng "sẵn sàng" đang là m5 nhưng m6 đã merge mà vòng deploy chưa kịp ghi nhận → bấm với m5 → 409
    "Có bản mới hơn — tải lại", không ghi yêu cầu (không lặng lẽ nhận bản đã cũ)."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        _ghi(kho, "repo-nhap", "pr.da_merge", {"commit": "c8", "merge_commit": "6" * 40, "ma_thao_tac": "pr-8"}, "rn-8")
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại") and "đã đổi" in r.json()["loi"]
    assert _yeu_cau(pt) == []


@pytest.mark.parametrize("h", [{}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
                               {k: v for k, v in DAI_CA.items() if k != "X-Tram"},
                               {**DAI_CA, "Origin": "https://evil.example"}])
def test_thieu_hoac_gia_danh_tinh_403(tmp_path, h):
    """Scenario "Yêu cầu không mang danh tính Đại ca": 403, không ghi yêu cầu."""
    app, pt = _app(tmp_path)
    assert goi(app, "POST", DP, json_body=_than(), headers=h).status == 403 and _yeu_cau(pt) == []


def test_kenh_header_khong_cookie_403(tmp_path):
    """D138: header thiếu phiên không được Deploy."""
    app, pt = _app(tmp_path, unix=False)
    r = goi(app, "POST", DP, json_body=_than(), headers={**DAI_CA,"Cookie":""})
    assert r.status == 403 and r.json()["detail"] == "Cần phiên passkey" and _yeu_cau(pt) == []


def test_estop_va_khoa_chung_422(tmp_path):
    """Scenario "Estop bật" (nút Deploy bị khoá), "Dự án chưa khai lệnh lùi", D116 `bat_ghi: false`."""
    app, pt = _app(tmp_path)
    estop.bat("thử")
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Estop đang bật")
    estop.tat()
    r = goi(app, "POST", "/api/du-an/hr-codex/tu-dong/deploy", json_body=_than("ma-deploy-hr-codex"), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Dự án chỉ quét thử (bat_ghi: false)")
    (tmp_path / "b").mkdir()
    app2, pt2 = _app(tmp_path / "b", cd=CaiDatTuDong(lenh_deploy="d.sh", lenh_kiem_song="k.sh"))
    r = goi(app2, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Chưa khai đủ 3 lệnh") and _yeu_cau(pt) == _yeu_cau(pt2) == []
    assert goi(app2, "GET", "/api/du-an/repo-nhap/tu-dong").json()["san_sang"] is None


def test_khong_co_gi_cho_va_than_sai(tmp_path):
    app, _ = _app(tmp_path, san_sang=False)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Không có bản mới nào chờ deploy")
    r = goi(app, "POST", DP, json_body={**_than("ma-deploy-invalid"), "expected_commit": "HEAD; rm -rf /"}, headers=DAI_CA)
    assert r.status == 422 and r.json() == {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]}
    assert goi(app, "POST", "/api/du-an/khong-co/tu-dong/deploy", json_body=_than("ma-deploy-unknown"), headers=DAI_CA).status == 404


def test_deploy_tay_khi_du_an_tam_dung(tmp_path):
    """Scenario "Deploy tay khi dự án tạm dừng" (D97 luật 3) — cả khi toàn trạm tạm dừng."""
    app, pt = _app(tmp_path)
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        ghi_tam_dung(kho.db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard")
        ghi_tam_dung(kho.db, "_tram", tam_dung=True, tac_nhan="dai-ca/dashboard")
    assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).status == 200 and len(_yeu_cau(pt)) == 1


def test_dinh_that_doi_chua_co_su_kien_409(tmp_path, monkeypatch):
    app, pt = _app(tmp_path)
    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten, db: "6" * 40)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại")
    assert _yeu_cau(pt) == []
