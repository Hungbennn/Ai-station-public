import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from bead_gia import bead

from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cli import main
from tram.danh_gia import danh_gia
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "")
VAI = ("1", "V")


class ClientLuonCot1:
    """Luôn trả 'ai-lam' — cùng dạng `beta.messages.create` mà tram/llm/claude.py gọi. Lát 1a-2: lần gọi chế độ
    rút gọn (schema không có `cot`) nhận một câu hỏi, như mô hình thật tuân schema."""

    def __init__(self):
        self.so_goi = 0
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.so_goi += 1
        tra = {"cot": "ai-lam", "ly_do": "x", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}
        if "cot" not in kw["output_config"]["format"]["schema"]["properties"]:
            tra = {"cau_hoi_can_chot": ["Hoa hồng tính trên giá nào?"]}
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(tra))],
                  usage=NS(input_tokens=1, output_tokens=1, cache_read_input_tokens=0))


def test_danh_gia(tmp_path):
    beads = [bead("hr-1", title="Sửa nút"), bead("hr-2", title="hoa hồng"), bead("hr-3", title="Việc mơ hồ")]
    mau = [{"id": "hr-1", "cot": "ai-lam", "cham_rao": False},
           {"id": "hr-2", "cot": "can-chot", "cham_rao": True},
           {"id": "hr-3", "cot": "can-chot", "cham_rao": False}]
    kq = danh_gia(DU_AN, mau, beads=beads, kho=KhoSuKien(tmp_path / "s.db"), client=ClientLuonCot1(), vai=VAI)
    assert kq.tong == 3 and kq.khop == 2 and abs(kq.ti_le - 2 / 3) < 1e-9
    assert kq.vi_pham_t1 == []
    assert kq.lech == [("hr-3", "can-chot", "ai-lam")]


def test_bead_mau_khong_ton_tai(tmp_path):
    with pytest.raises(KeyError, match="hr-x"):
        danh_gia(DU_AN, [{"id": "hr-x", "cot": "ai-lam", "cham_rao": False}], beads=[],
                 kho=KhoSuKien(tmp_path / "s.db"), client=ClientLuonCot1(), vai=VAI)


@pytest.fixture
def repo_tam(tmp_path, monkeypatch):
    goc = tmp_path / "goc"
    (goc / "du-an").mkdir(parents=True)
    (goc / "bo-mau").mkdir()
    (goc / "du-an" / "hr.yaml").write_text(
        "ten: hr\nduong_dan: /r\nhang_rao:\n  tien:\n    tu_khoa: [hoa hồng]\n", encoding="utf-8")
    monkeypatch.setenv("TRAM_REPO", str(goc))
    return goc


def cam_api(monkeypatch):
    def tao_client():
        raise AssertionError("không được gọi API")
    monkeypatch.setattr("tram.llm.claude.tao_client", tao_client)


def test_cli_thieu_file_bo_mau(repo_tam, monkeypatch, capsys):
    cam_api(monkeypatch)
    assert main(["danh-gia", "hr"]) == 2
    assert "bo-mau" in capsys.readouterr().out


@pytest.mark.parametrize("noi_dung", ["mau: []\n", "du_an: hr\n", "mau:\n  - {id: hr-1, cot: , cham_rao: }\n"])
def test_cli_mau_rong_hoac_chua_dien(repo_tam, monkeypatch, capsys, noi_dung):
    cam_api(monkeypatch)
    (repo_tam / "bo-mau" / "hr.yaml").write_text(noi_dung, encoding="utf-8")
    assert main(["danh-gia", "hr"]) == 2
    assert "bo-mau/hr.yaml" in capsys.readouterr().out


def test_cli_chay_that(repo_tam, monkeypatch, capsys, tram_home_tam):
    (repo_tam / "bo-mau" / "hr.yaml").write_text(
        "mau:\n  - {id: hr-1, cot: ai-lam, cham_rao: false}\n  - {id: hr-2, cot: can-chot, cham_rao: true}\n",
        encoding="utf-8")
    client = ClientLuonCot1()

    class BdGia:
        def __init__(self, repo):
            pass

        def tat_ca(self):
            return [bead("hr-1", title="Sửa nút"), bead("hr-2", title="hoa hồng")]

    monkeypatch.setattr("tram.beads.bd.Bd", BdGia)
    monkeypatch.setattr("tram.llm.claude.tao_client", lambda: client)
    monkeypatch.setattr("tram.cham_cot.prompt.nap_vai", lambda ten: VAI)
    assert main(["danh-gia", "hr"]) == 0
    ra = capsys.readouterr().out
    assert "Khớp 2/2" in ra and "không có" in ra
    assert client.so_goi == 2
    assert (tram_home_tam / "su-kien-danh-gia.db").exists() and not (tram_home_tam / "su-kien.db").exists()
