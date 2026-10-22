import pytest
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.san_sang_b import san_sang_b
from tram.tho.do_nen import thu_claude


def ch():
    return CauHinhTho("B", "http://127.0.0.1:7700", tuple(KheCauHinh(f"claude-{n}", "claude",
        f"user:tram-khe{n}", Path(f"/Users/tram-khe{n}/claude"), f"Tho {n}", ("coder",))
        for n in (1, 2)), CauHinhChay(day="kho-tho"))


def test_thieu_auth_khong_san_sang():
    assert not san_sang_b(ch(), do=lambda *a, **kw: ("do", "khoa"))
    assert san_sang_b(ch(), do=lambda *a, **kw: ("xanh", "ok"))


def test_hai_luot_nen_khong_token_khong_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / "tram").mkdir()
    da = []
    def run(argv, **kw):
        da.append((argv, kw))
        return SimpleNamespace(returncode=0, stdout='{"type":"result","is_error":false,"result":"SAN-SANG"}')
    assert thu_claude(ch(), chay=run)
    assert len(da) == 2 and all(x[1]["timeout"] == 120 for x in da)
    assert [x[1]["env"]["CLAUDE_CONFIG_DIR"] for x in da] == ["/Users/tram-khe1/claude", "/Users/tram-khe2/claude"]
    assert all("--tools" in x[0] and "CLAUDE_CODE_OAUTH_TOKEN" not in x[1]["env"] for x in da)


def test_het_han_auth_giu_tat_khong_lap_daemon(monkeypatch):
    from tram.tho import cau_hinh, khoi_dong, lenh_chay, san_sang_b as module
    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", ch)
    monkeypatch.setattr(lenh_chay, "doc_token_may", lambda **kw: "token-gia")
    monkeypatch.setattr(khoi_dong, "HAN_KHOI_DONG", 0)
    monkeypatch.setattr(module, "san_sang_b", lambda c: False)
    monkeypatch.setattr(lenh_chay, "chay_may", lambda *a: (_ for _ in ()).throw(AssertionError("nhan viec")))
    assert lenh_chay._chay(SimpleNamespace()) == 0



def test_exit_0_nhung_chua_dang_nhap_khong_xanh(tmp_path):
    from test_kiem_cong import cau_hinh
    from tram.tho.kiem_cong import dang_nhap
    c = cau_hinh(tmp_path)
    for out in ('{"loggedIn":false}', '{}', '[]', 'khong-phai-json'):
        def run(*a, **kw):
            return SimpleNamespace(returncode=0, stdout=out)
        assert dang_nhap(c, c.khe[0], goc=tmp_path, goc_wt=tmp_path,
                        chay=run, xac_minh=lambda *a: 600)[0] == "do"


def test_yaml_hong_thoat_sach_khong_goi_keychain(monkeypatch):
    import yaml
    from tram.tho import cau_hinh, lenh_chay
    def hong():
        raise yaml.YAMLError("noi-dung-khong-duoc-in")
    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", hong)
    monkeypatch.setattr(lenh_chay, "doc_token_may", lambda: (_ for _ in ()).throw(AssertionError()))
    assert lenh_chay._chay(SimpleNamespace()) == 0


def test_het_han_ghi_token_khong_in_dau_ra(monkeypatch, capsys):
    import io
    import subprocess
    from tram.tho import lenh_chay
    monkeypatch.setattr(lenh_chay.sys, "stdin", io.StringIO("t" * 43))
    def hong(token):
        raise subprocess.TimeoutExpired(["security", "-i"], 10, output="bi-mat", stderr="bi-mat")
    monkeypatch.setattr(lenh_chay, "luu_token_may", hong)
    assert lenh_chay._nhan_token(SimpleNamespace()) == 2
    assert "bi-mat" not in capsys.readouterr().err


@pytest.mark.parametrize("tra_loi", ["SẴN-SÀNG", "SAN-SANG.", "sẵn-sàng"])
def test_tra_loi_co_dau_van_dat(tmp_path, monkeypatch, tra_loi):
    # Máy B 21/10: Claude thật trả "SẴN-SÀNG" (câu hỏi tiếng Việt) → so chuỗi không dấu chấm sai CLAUDE-CHUA-DAT.
    import json
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / "tram").mkdir()
    dong = json.dumps({"type": "result", "is_error": False, "result": tra_loi}, ensure_ascii=False)
    assert thu_claude(ch(), chay=lambda argv, **kw: SimpleNamespace(returncode=0, stdout=dong))


def test_loi_xac_thuc_van_khong_dat(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / "tram").mkdir()
    dong = json.dumps({"type": "result", "is_error": True, "result": "Failed to authenticate. API Error: 401"})
    assert not thu_claude(ch(), chay=lambda argv, **kw: SimpleNamespace(returncode=1, stdout=dong))
