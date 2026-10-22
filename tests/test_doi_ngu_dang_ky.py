import yaml
import pytest
from tram.tho.dang_ky_b import dang_ky_b
from tram.tho.khach import LoiKhachTram


def ung_vien(p):
    p.write_text(yaml.safe_dump({"may_id": "B", "tram_api": "http://127.0.0.1:7700",
        "chay": {"day": "kho-tho"}, "khe": [{"ten": f"claude-{n}", "cli": "claude",
        "principal": f"user:tram-khe{n}", "thu_muc_cau_hinh": f"/Users/tram-khe{n}/claude",
        "ten_goi_nho": f"Tho {n}", "vai_uu_tien": ["coder"]} for n in (1, 2)]}))
    return p


class Khach:
    def __init__(self, ma=200):
        self.ma, self.gui = ma, []
    def ping(self):
        return {"may_id": "B"}
    def goi(self, method, url, than):
        self.gui.append((method, url, than))
        return self.ma, {"loi": "khong-duoc-in"}


def test_http_hong_khong_thay_file(tmp_path):
    p, dich = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml"
    dich.write_text("cu")
    with pytest.raises(LoiKhachTram, match="HTTP 503"):
        dang_ky_b(p, dich, Khach(503))
    assert dich.read_text() == "cu" and not list(tmp_path.glob("tho-truoc-*"))


def test_thanh_cong_retry_giu_ban_sao(tmp_path):
    p, dich, khach = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", Khach()
    dich.write_text("cu")
    for _ in range(2):
        assert dang_ky_b(p, dich, khach) == ["B/claude-1", "B/claude-2"]
    assert dich.read_bytes() == p.read_bytes() and dich.stat().st_mode & 0o777 == 0o600
    assert len(list(tmp_path.glob("tho-truoc-*"))) == 1
    assert khach.gui[0] == khach.gui[1]
    assert "principal" not in khach.gui[0][2]["khe"][0]


def test_token_sai_may_khong_post(tmp_path):
    khach = Khach()
    khach.ping = lambda: {"may_id": "C"}
    with pytest.raises(ValueError, match="Token"):
        dang_ky_b(ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", khach)
    assert khach.gui == []



def test_api_retry_khong_tu_bat_khe(tmp_path):
    from contextlib import closing
    from tho_api_gia import tao_tram, KHE
    from tram.phieu.khe import khe_dang_bat
    t = tao_tram(tmp_path, dang_ky=False)
    than = {"may_id": "B", "khe": KHE}
    for _ in range(2):
        assert t.goi("POST", "/api/tho/dang-ky", json_body=than).status == 200
    assert t.goi("POST", "/api/tho/dang-ky", may="C", json_body=than).status == 403
    with closing(t.kho()) as kho:
        assert kho.db.execute("SELECT COUNT(*) FROM su_kien WHERE loai='khe.dang_ky'").fetchone()[0] == 2
        assert not khe_dang_bat(kho, "B/claude-1") and not khe_dang_bat(kho, "B/claude-2")


def test_ghi_file_hong_sau_post_giu_cu_retry_duoc(tmp_path, monkeypatch):
    from tram.tho import dang_ky_b as module
    p, dich, khach = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", Khach()
    dich.write_text("cu")
    replace = module.os.replace
    monkeypatch.setattr(module.os, "replace", lambda *a: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        dang_ky_b(p, dich, khach)
    assert dich.read_text() == "cu" and len(khach.gui) == 1
    assert not list(tmp_path.glob(".tho-*"))
    monkeypatch.setattr(module.os, "replace", replace)
    assert dang_ky_b(p, dich, khach) == ["B/claude-1", "B/claude-2"]
