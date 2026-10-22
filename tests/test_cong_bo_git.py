"""Lệnh Git công bố của trạm + hai nguồn lấy commit (spec 3 §6.4) — remote là repo bare cục bộ, không mạng."""
from cong_bo_gia import commit_tho, dung_ba_kho
from git_gia import git
from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.cong_bo.git import day_cas, la_hau_due, sha_remote, xoa_cas
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam, chon_nguon, ref_nhan, ref_tam_cua


def test_nguon_kho_tho_fetch_tu_duong_dan_kho_tho(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    sha = commit_tho(b, ref_tam_cua("hr-1", 2), {"b.txt": "x"})
    n = NguonKhoTho({"B": b.tho.parent})
    assert n.lay(b.tram, may_id="B", du_an="hr-codex", ref_tam="tram/luot/hr-1/2", giao_id="g-1", timeout=30) == sha
    assert git(b.tram, "rev-parse", ref_nhan("g-1")) == sha
    assert n.lay(b.tram, may_id="C", du_an="hr-codex", ref_tam="tram/luot/hr-1/2", giao_id="g-1", timeout=30) is None
    assert n.lay(b.tram, may_id="B", du_an="hr-codex", ref_tam="tram/luot/hr-1/9", giao_id="g-2", timeout=30) is None


def test_nguon_ref_tam_fetch_tu_origin_va_don_luot_cu(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    sha = commit_tho(b, "tram/luot/hr-1/1", {"b.txt": "x"})
    n = NguonRefTam()
    assert n.lay(b.tram, may_id="B", du_an="hr-codex", ref_tam="tram/luot/hr-1/1", giao_id="g-1", timeout=30) is None
    git(b.tho, "push", "-q", "origin", "tram/luot/hr-1/1:refs/heads/tram/luot/hr-1/1")
    assert n.lay(b.tram, may_id="B", du_an="hr-codex", ref_tam="tram/luot/hr-1/1", giao_id="g-1", timeout=30) == sha
    git(b.tho, "push", "-q", "origin", "tram/luot/hr-1/1:refs/heads/tram/luot/hr-1/2")
    assert n.don_cu(b.tram, bead_id="hr-1", luot=2, timeout=30) == ["tram/luot/hr-1/1"]
    assert sha_remote(b.tram, "tram/luot/hr-1/1", timeout=30) is None
    assert sha_remote(b.tram, "tram/luot/hr-1/2", timeout=30) == sha
    assert NguonKhoTho({}).don_cu(b.tram, bead_id="hr-1", luot=9, timeout=30) == []


def test_cas_chi_doi_khi_dung_sha_mong_doi(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    a = commit_tho(b, "tram/luot/hr-1/1", {"b.txt": "1"})
    c = commit_tho(b, "tram/luot/hr-1/2", {"c.txt": "2"}, cha=a)
    NguonKhoTho({"B": b.tho.parent}).lay(b.tram, may_id="B", du_an="hr-codex", ref_tam="tram/luot/hr-1/2",
                                        giao_id="g-2", timeout=30)
    assert la_hau_due(b.tram, b.cha, c) and not la_hau_due(b.tram, c, b.cha)
    assert day_cas(b.tram, a, "tram/hr-1", None, timeout=30) == "ok"            # ref chưa có
    assert day_cas(b.tram, c, "tram/hr-1", None, timeout=30) == "tu_choi"       # đã có → lease "chưa có" sai
    assert day_cas(b.tram, c, "tram/hr-1", b.cha, timeout=30) == "tu_choi"      # sha mong đợi sai
    assert day_cas(b.tram, c, "tram/hr-1", a, timeout=30) == "ok" and sha_remote(b.tram, "tram/hr-1", timeout=30) == c
    assert xoa_cas(b.tram, "tram/hr-1", a, timeout=30) == "tu_choi"
    assert xoa_cas(b.tram, "tram/hr-1", c, timeout=30) == "ok" and sha_remote(b.tram, "tram/hr-1", timeout=30) is None


def test_remote_hong_la_khong_ro(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    git(b.tram, "remote", "set-url", "origin", str(tmp_path / "khong-co.git"))
    assert day_cas(b.tram, b.cha, "tram/hr-1", None, timeout=30) == "khong_ro"


def test_chon_nguon_theo_cau_hinh(tmp_path):
    assert chon_nguon(CauHinhCongBo()) is None
    assert isinstance(chon_nguon(CauHinhCongBo("ref-tam")), NguonRefTam)
    assert chon_nguon(CauHinhCongBo("kho-tho", {"B": tmp_path})).kho_tho == {"B": tmp_path}
