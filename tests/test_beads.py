import json
import subprocess
from pathlib import Path

import pytest

from tram.beads.bd import Bd, LoiBd, chay_bd
from tram.beads.mo_hinh import Bead

MAU = Path(__file__).parent / "du_lieu" / "beads-mau.json"


class RunnerGia:
    def __init__(self, ra: str = "[]"):
        self.goi: list[list[str]] = []
        self.ra = ra

    def __call__(self, args):
        self.goi.append(list(args))
        return self.ra


def test_bead_tu_json_mac_dinh():
    b = Bead.tu_json(json.loads(MAU.read_text())[0])
    assert b.acceptance_criteria == "" and b.labels == ("qa",) and b.phu_thuoc == ()
    assert b.nhan_cot() is None


def test_bead_nhan_cot_va_phu_thuoc():
    b = Bead.tu_json(json.loads(MAU.read_text())[2])
    assert b.nhan_cot() == "cot:ai-lam"
    assert b.phu_thuoc[0].depends_on_id == "hr-2" and b.phu_thuoc[0].loai == "blocks"
    assert "Test pass" in b.van_ban() and "docs/x.md" in b.van_ban()


def test_tat_ca_goi_dung_lenh():
    r = RunnerGia(MAU.read_text())
    ds = Bd(Path("/repo"), runner=r).tat_ca()
    assert [b.id for b in ds] == ["hr-1", "hr-2", "hr-3"]
    assert r.goi[0] == ["-C", "/repo", "list", "--json", "--all", "--limit", "0"]


def test_cap_nhat_nhan_co_actor():
    r = RunnerGia("")
    Bd(Path("/repo"), runner=r).cap_nhat_nhan(
        "hr-1", them=["cot:can-chot"], bo=["cot:ai-lam"], ghi_chu="lý do")
    assert r.goi[0] == ["-C", "/repo", "update", "hr-1", "--actor", "tram/cham-cot",
                        "--add-label", "cot:can-chot", "--remove-label", "cot:ai-lam",
                        "--append-notes", "lý do"]


def test_cap_nhat_rong_khong_goi_bd():
    r = RunnerGia("")
    Bd(Path("/repo"), runner=r).cap_nhat_nhan("hr-1")
    assert r.goi == []


@pytest.mark.parametrize("loi", [FileNotFoundError("bd"), subprocess.TimeoutExpired(["bd"], 120)])
def test_chay_bd_loi_nem_LoiBd(monkeypatch, loi):
    """Bộ chạy giả — trước đây test này để PATH rỗng nên vẫn spawn `bd` (bs-2bd.1.18: nhật ký chặn bắt được)."""
    def hong(*a, **k):
        raise loi
    monkeypatch.setattr("tram.beads.bd.subprocess.run", hong)
    with pytest.raises(LoiBd):
        chay_bd(["list"])


def _b(*nhan):
    return Bead("x", "", "", "", "", "", "open", "task", nhan, (), "2026-10-12T00:00:00Z")


def test_nhan_cot_uu_tien_cot_an_toan():
    assert _b("cot:ai-lam", "cot:can-chot").nhan_cot() == "cot:can-chot"
    assert _b("cot:ai-lam", "cot:cho-review").nhan_cot() == "cot:cho-review"
    assert _b("cot:can-chot", "cot:cho-review", "cot:ai-lam").nhan_cot() == "cot:cho-review"
    assert _b("cot:la", "cot:ai-lam").nhan_cot() == "cot:ai-lam"
    assert _b("qa", "cot:la", "cot:khac").nhan_cot() == "cot:la"


# --- Lát 2a: trường mới của Bead, đọc bd an toàn ---

def test_bead_truong_lat_2a_doc_tu_json():
    b = Bead.tu_json({"id": "hr-9", "updated_at": "2026-10-13T01:00:00Z", "priority": 1, "parent": "hr-1",
                      "assignee": "hung", "created_at": "2026-10-01T00:00:00Z", "status": "closed",
                      "close_reason": "Tính trên giá sau giảm", "closed_at": "2026-10-13T00:59:00Z"})
    assert (b.priority, b.parent, b.assignee) == (1, "hr-1", "hung")
    assert (b.created_at, b.close_reason, b.closed_at) == (
        "2026-10-01T00:00:00Z", "Tính trên giá sau giảm", "2026-10-13T00:59:00Z")


def test_bead_truong_lat_2a_thieu_co_mac_dinh():
    b = Bead.tu_json(json.loads(MAU.read_text())[0])
    assert (b.priority, b.parent, b.assignee, b.created_at, b.close_reason, b.closed_at) == (
        None, "", "", "", "", "")


@pytest.mark.parametrize("p", ["cao", None, True, 1.5])
def test_bead_priority_khong_phai_so_nguyen_thi_none(p):
    assert Bead.tu_json({"id": "x", "updated_at": "2026-10-13T00:00:00Z", "priority": p}).priority is None


def test_bead_tao_theo_vi_tri_cu_van_chay():
    assert _b("qa").close_reason == "" and _b("qa").priority is None


@pytest.mark.parametrize("ra", ["{khong phai json", '{"id": "x"}', '[{"id": "x"}]', '["chuoi"]', "null"])
def test_tat_ca_json_hong_nem_LoiBd(ra):
    with pytest.raises(LoiBd):
        Bd(Path("/repo"), runner=RunnerGia(ra)).tat_ca()


def test_phien_ban_doc_updated_at_tu_bd_show():
    r = RunnerGia('[{"id": "hr-1", "updated_at": "2026-10-13T02:00:00Z"}]')
    assert Bd(Path("/repo"), runner=r).phien_ban("hr-1") == "2026-10-13T02:00:00Z"
    assert r.goi[0] == ["-C", "/repo", "show", "hr-1", "--json"]


def test_phien_ban_nhan_ca_dang_doi_tuong():
    r = RunnerGia('{"id": "hr-1", "updated_at": "2026-10-13T02:00:00Z"}')
    assert Bd(Path("/repo"), runner=r).phien_ban("hr-1") == "2026-10-13T02:00:00Z"


@pytest.mark.parametrize("ra", ["", "[]", '[{"id": "hr-1"}]', '"chuoi"',
                                '[{"id": "hr-2", "updated_at": "2026-10-13T02:00:00Z"}]'])
def test_phien_ban_json_hong_nem_LoiBd(ra):
    with pytest.raises(LoiBd):
        Bd(Path("/repo"), runner=RunnerGia(ra)).phien_ban("hr-1")
