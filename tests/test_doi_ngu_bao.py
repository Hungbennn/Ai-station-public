import json
from tram.tho.bao import bao
from test_tram_bao import khoi, FILE


def test_bao_b_khong_goi_git(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_GIT_QUA_QUAN_LY", "1")
    monkeypatch.setenv("TRAM_NHANH", "tram/bs-thu")
    p = tmp_path / FILE
    p.parent.mkdir(parents=True)
    p.write_text("<!-- ban-giao -->" + json.dumps(khoi()) + "<!-- ban-giao -->")
    def cam(*a, **kw):
        raise AssertionError("Khe không được chạy Git để báo")
    dong = bao("xong", "xong", wt=tmp_path, hang_doi=tmp_path / "hd", ban_giao=FILE, chay=cam)
    assert dong["commit"] is None and dong["ban_giao"]["commit"] is None
    assert dong["ban_giao"]["nhanh"] == "tram/bs-thu"
    assert json.loads((tmp_path / "hd").read_text()) == dong
