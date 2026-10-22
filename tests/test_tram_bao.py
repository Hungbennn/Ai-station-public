import json

import pytest

from git_gia import git, ghi, tao_repo
from tram.ban_giao.cau_truc import LoiCauTruc
from tram.cli import main
from tram.tho.bao import LoiBao, bao

FILE = "docs/handovers/bg.md"


def khoi(**ghi_de) -> dict:
    d = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 7, "file_ban_giao": FILE, "nhanh": "agent-ghi-bay",
         "commit": "deadbee", "doi_chieu_nghiem_thu": [{"tieu_chi": "A", "dat": True, "bang_chung": "t::a"}],
         "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [],
         "thay_doi_vung_nhay_cam": []}
    d.update(ghi_de)
    return d


@pytest.fixture
def wt(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    r = tao_repo(tmp_path / "wt")
    ghi(r, {"a.txt": "a"})
    git(r, "switch", "-q", "-c", "tram/hr-1")
    return r


def _viet_ban_giao(wt, k: dict):
    (wt / "docs/handovers").mkdir(parents=True, exist_ok=True)
    (wt / FILE).write_text(f"# Bàn giao\n<!-- ban-giao -->\n{json.dumps(k, ensure_ascii=False)}\n<!-- ban-giao -->\n")


def test_xong_dien_nhanh_commit_luot_roi_commit_va_ghi_hang_doi(wt, tmp_path):
    _viet_ban_giao(wt, khoi())
    hd = tmp_path / "hang-doi.jsonl"
    dong = bao("xong", "xong bước code", wt=wt, hang_doi=hd, ban_giao=FILE)
    head = git(wt, "rev-parse", "HEAD")
    assert git(wt, "status", "--porcelain") == "" and git(wt, "log", "-1", "--format=%s") == "xong: xong bước code"
    assert dong["commit"] == head and dong["ban_giao"]["commit"] == head
    assert dong["ban_giao"]["nhanh"] == "tram/hr-1" and dong["ban_giao"]["luot"] == 0
    assert [json.loads(l) for l in hd.read_text().splitlines()] == [dong]


def test_moc_khong_thay_doi_thi_khong_commit_va_noi_tiep_hang_doi(wt, tmp_path):
    hd = tmp_path / "hd.jsonl"
    truoc = git(wt, "rev-parse", "HEAD")
    bao("moc", "mốc 1", wt=wt, hang_doi=hd)
    bao("can_hoi", "Xoá cột cũ được không?", wt=wt, hang_doi=hd, loai_hoi="thao_tac_nguy_hiem")
    ds = [json.loads(l) for l in hd.read_text().splitlines()]
    assert [d["loai"] for d in ds] == ["moc", "can_hoi"] and ds[0]["commit"] == truoc == git(wt, "rev-parse", "HEAD")
    assert ds[1]["loai_hoi"] == "thao_tac_nguy_hiem" and "ban_giao" not in ds[1]


@pytest.mark.parametrize("loai, nd, kw", [
    ("xong", "x", {}), ("can_hoi", "hỏi", {}), ("can_hoi", "", {"loai_hoi": "can_quyet_dinh"}),
    ("bi", "  ", {}), ("ngu", "x", {}), ("moc", "x" * 4001, {}),
    ("can_hoi", "hỏi", {"loai_hoi": "can_quyet_dinh", "ban_giao": FILE}),
])
def test_tham_so_sai(wt, tmp_path, loai, nd, kw):
    with pytest.raises(LoiBao):
        bao(loai, nd, wt=wt, hang_doi=tmp_path / "hd", **kw)
    assert not (tmp_path / "hd").exists()


@pytest.mark.parametrize("k", [khoi(loai="tam", buoc_tiep=[]), khoi(la="x"), khoi(file_ban_giao=""),
                               khoi(vuong_mac=["x" * 70_000])])
def test_khoi_sai_cau_truc_khong_ghi_gi(wt, tmp_path, k):
    _viet_ban_giao(wt, k)
    with pytest.raises(LoiCauTruc):
        bao("xong", "x", wt=wt, hang_doi=tmp_path / "hd", ban_giao=FILE)
    assert not (tmp_path / "hd").exists() and git(wt, "status", "--porcelain") != ""


def test_file_ban_giao_ngoai_worktree_hoac_khong_co_khoi(wt, tmp_path):
    (tmp_path / "ngoai.md").write_text("x")
    with pytest.raises(LoiBao):
        bao("moc", "x", wt=wt, hang_doi=tmp_path / "hd", ban_giao="../ngoai.md")
    (wt / "docs").mkdir()
    (wt / "docs/k.md").write_text("không có khối")
    with pytest.raises(LoiBao):
        bao("moc", "x", wt=wt, hang_doi=tmp_path / "hd", ban_giao="docs/k.md")


def test_tram_chi_nhan_bao_khi_co_tram_giao_id(wt, tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("TRAM_GIAO_ID", raising=False)
    monkeypatch.chdir(wt)
    assert main(["bao", "--moc", "x"]) == 2 and "TRAM_GIAO_ID" in capsys.readouterr().err
    monkeypatch.setenv("TRAM_GIAO_ID", "g-20261013-0001")
    monkeypatch.setenv("TRAM_HANG_DOI", str(tmp_path / "hd.jsonl"))
    for lenh in (["quet"], ["chu", "estop"], ["api"], ["nho", "tim", "x"], []):
        assert main(lenh) == 2
    assert "chỉ được chạy" in capsys.readouterr().err
    assert main(["bao", "--moc", "mốc"]) == 0 and json.loads((tmp_path / "hd.jsonl").read_text())["loai"] == "moc"
    assert main(["bao", "--bi", ""]) == 2
