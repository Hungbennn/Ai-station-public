"""Lát 1a-2 (D31): khoá `bat_ghi` của du-an/<ten>.yaml — dự án chưa bật ghi chỉ được đọc và quét thử.
bs-2bd.1.22 (Đại ca chốt 17/10, INV-005): THIẾU khoá = tắt ghi; dự án muốn ghi phải khai rõ `bat_ghi: true`."""
from pathlib import Path

import pytest
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead

from tram.cau_hinh.bat_ghi import bat_ghi
from tram.cli import main
from tram.giao_viec.noi_that import cac_du_an_that

CU = 'ten: "{ten}"\nduong_dan: "/r/{ten}"\nhang_rao: {{}}\n'   # yaml viết trước lát 1a-2: không có khoá


def yaml_du_an(thu_muc, ten, them=""):
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / f"{ten}.yaml").write_text(CU.format(ten=ten) + them, encoding="utf-8")


def test_du_an_mau_duoc_khoa_theo_d40():
    thu_muc = Path(__file__).resolve().parents[1] / "du-an"
    assert bat_ghi("vi-du", thu_muc=thu_muc) is False


@pytest.mark.parametrize("them, bat", [("", False), ("bat_ghi: true\n", True), ("bat_ghi: false\n", False)])
def test_thieu_khoa_la_tat_ghi(tmp_path, them, bat):
    yaml_du_an(tmp_path, "x", them)
    assert bat_ghi("x", thu_muc=tmp_path) is bat


@pytest.mark.parametrize("them", ['bat_ghi: "khong"\n', "bat_ghi: 1\n", "bat_ghi:\n"])
def test_gia_tri_la_thi_loi(tmp_path, them):
    yaml_du_an(tmp_path, "x", them)
    with pytest.raises(ValueError, match="bat_ghi"):
        bat_ghi("x", thu_muc=tmp_path)


@pytest.fixture
def hai_du_an(tmp_path, monkeypatch):
    """Repo trạm tạm: `bat` (bat_ghi: true), `cu` (không khoá = tắt) và `moi` (bat_ghi: false). Vá mọi phụ thuộc ngoài
    của `tram quet`."""
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "tram-repo"))
    yaml_du_an(tmp_path / "tram-repo" / "du-an", "bat", "bat_ghi: true\n")
    yaml_du_an(tmp_path / "tram-repo" / "du-an", "cu")
    yaml_du_an(tmp_path / "tram-repo" / "du-an", "moi", "bat_ghi: false\n")
    goi_quet = []
    monkeypatch.setattr("tram.llm.claude.tao_client", lambda: object())
    monkeypatch.setattr("tram.cham_cot.prompt.nap_vai", lambda ten: ("3", "VAI"))
    monkeypatch.setattr("tram.nho.khach.tao_nho_lai", lambda: None)
    monkeypatch.setattr("tram.cham_cot.quet.quet", lambda du_an, **kw: goi_quet.append((du_an.ten, kw["thu"])))
    return goi_quet


def test_quet_ghi_bo_qua_du_an_chua_bat_ghi(hai_du_an, capsys):
    assert main(["quet", "--ghi"]) == 0
    assert hai_du_an == [("bat", False)]
    out = capsys.readouterr().out
    assert "moi: bỏ qua --ghi — du-an/moi.yaml chưa khai bat_ghi: true" in out
    assert "cu: bỏ qua --ghi — du-an/cu.yaml chưa khai bat_ghi: true" in out


def test_quet_thu_van_doc_du_an_chua_bat_ghi(hai_du_an):
    assert main(["quet"]) == 0
    assert hai_du_an == [("bat", True), ("cu", True), ("moi", True)]


def test_giao_viec_bo_qua_du_an_chua_bat_ghi(tmp_path, capsys):
    yaml_du_an(tmp_path, "bat", "bat_ghi: true\n")
    yaml_du_an(tmp_path, "cu")
    yaml_du_an(tmp_path, "moi", "bat_ghi: false\n")
    yaml_du_an(tmp_path, "hong", 'bat_ghi: "co"\n')
    assert [d.ten for d in cac_du_an_that(tmp_path)] == ["bat"]
    assert "bỏ qua dự án hong" in capsys.readouterr().err


def test_api_tu_choi_ghi_nhung_van_cho_doc(tmp_path):
    bd = BdGia([bead("hr-1", labels=["cot:ai-lam"])])
    app, pt = tao_app_gia(tmp_path, {"hr": bd})
    pt.bat_ghi = lambda ten: False
    than = {"ma_thao_tac": "ma-api-00001", "expected_version": "2026-10-13T01:00:00Z", "cot": "can-chot"}
    r = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=than, headers=DAI_CA)
    assert r.status == 422 and "chưa bật ghi" in r.json()["loi"] and bd.so_lan("cap_nhat_nhan") == 0
    assert goi(app, "GET", "/api/cong-viec?du_an=hr").status == 200


def test_api_du_an_tra_bat_ghi(tmp_path):
    """D37: 2f hiện chip "chỉ quét thử" theo `du_an[].bat_ghi` của GET /api/du-an."""
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia(), "moi": BdGia(), "hong": BdGia()})

    def bat(ten):
        if ten == "hong":
            raise ValueError("bat_ghi phải là true hoặc false")
        return ten == "hr"
    pt.bat_ghi = bat
    ds = {d["ten"]: d["bat_ghi"] for d in goi(app, "GET", "/api/du-an").json()["du_an"]}
    assert ds == {"hr": True, "moi": False, "hong": False}


def test_phu_thuoc_that_doc_bat_ghi_tu_yaml(hai_du_an, monkeypatch):
    import subprocess

    from tram.api.phu_thuoc import phu_thuoc_that
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    pt = phu_thuoc_that()
    assert pt.bat_ghi("bat") is True and pt.bat_ghi("cu") is False and pt.bat_ghi("moi") is False
