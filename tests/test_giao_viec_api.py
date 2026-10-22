"""Dashboard 4a (spec 4 §5.1, §6.4 mục 4): lý do không giao + lệnh/link tạo PR — `GET /api/giao-viec`."""
from dataclasses import replace

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from git_gia import git
from giao_viec_gia import bug, du_an_gia, dung
from tram.api.app import tao_app
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.git_kiem import fetch
from tram.su_kien.kho import KhoSuKien
from tram.suy.giao_viec import VAN_BAN, ly_do_hien, thong_tin_pr


def test_ly_do_hien(tmp_path):
    da = du_an_gia(tmp_path)
    ds = [bug("a", acceptance_criteria=""), bug("b", labels=["cot:ai-lam", "cot:can-chot"]),
          bug("c", parent="f-1"), bug("d", issue_type="feature"), bug("e", labels=["cot:can-chot"]),
          bug("f", chan_boi=["x"]), bug("g"), bug("h", status="in_progress", assignee="hung")]
    theo_id = {b.id: b for b in ds}
    assert [ly_do_hien(b, theo_id, da, True) for b in ds] == [
        "thieu-tieu-chi", "nhan-lech", "cho-merge-spec", "loai-khong-giao", None, None, None, "nguoi-khac-nhan"]
    assert ly_do_hien(bug("g"), theo_id, da, False) == "chua-co-kho-kiem"
    khong_lenh = replace(da, giao=CauHinhGiao())
    assert ly_do_hien(bug("g"), theo_id, khong_lenh, True) == "thieu-lenh-kiem"
    assert ly_do_hien(bug("s", issue_type="spike"), theo_id, khong_lenh, True) is None
    assert ly_do_hien(bug("g"), theo_id, du_an_gia(tmp_path, env=False), True) == "thieu-moi-truong-kiem"


def test_thong_tin_pr_github_va_lech(tmp_path):
    t = dung(tmp_path, bug(labels=["cot:cho-review"]))
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    fetch(t.k.kho)
    b = t.g.beads["hr-1"]
    pr = thong_tin_pr(t.da, b, {"commit_ban_giao": c}, t.k.kho)
    assert (pr["nhanh"], pr["commit"], pr["tu_xa"], pr["lech"], pr["link"]) == ("tram/hr-1", c, c, False, None)
    assert pr["lenh"] == "gh pr create --base main --head tram/hr-1 --fill"
    git(t.k.kho, "remote", "set-url", "origin", "https://github.com/hung/hr-codex.git")
    t.k.day("tram/hr-1", {"src/la.py": "x\n"}, tu=c)
    git(t.k.kho, "fetch", "-q", str(t.k.origin), "+refs/heads/*:refs/remotes/origin/*")
    pr = thong_tin_pr(t.da, b, {"commit_ban_giao": c}, t.k.kho)
    assert pr["lech"] and pr["link"] == "https://github.com/hung/hr-codex/compare/main...tram/hr-1?expand=1"
    assert pr["lenh"].startswith("gh pr create --repo hung/hr-codex ")
    assert thong_tin_pr(t.da, b, {"commit_ban_giao": "khong-phai-sha"}, t.k.kho) is None
    assert thong_tin_pr(t.da, bug(), {"commit_ban_giao": c}, t.k.kho) is None              # không ở cột 3


def test_api_giao_viec(tmp_path):
    t = dung(tmp_path, bug("hr-1", acceptance_criteria=""), bug("hr-2", labels=["cot:cho-review"]))
    c = t.k.day("tram/hr-2", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    fetch(t.k.kho)
    pt = tao_pt(tmp_path, {"hr-codex": t.g})
    pt.bo_giao = t.bo
    KhoSuKien(tmp_path / "sk.db").ghi("hr-codex", "bead.vao_cot_3", {"commit_ban_giao": c}, bead_id="hr-2")
    r = goi(tao_app(pt), "GET", "/api/giao-viec?du_an=hr-codex")
    assert r.status == 200 and r.json()["bat"] is False
    g = r.json()["giao"]
    assert g["hr-codex/hr-1"] == {"khong_giao": VAN_BAN["thieu-tieu-chi"], "pr": None}
    assert g["hr-codex/hr-2"]["pr"]["commit"] == c and g["hr-codex/hr-2"]["khong_giao"] is None
    assert goi(tao_app(pt), "GET", "/api/giao-viec?du_an=khong-co").status == 404


def test_api_khi_chua_noi_bo_giao_viec(tmp_path):
    r = goi(tao_app(tao_pt(tmp_path, {"hr-codex": BdGia([bug()])})), "GET", "/api/giao-viec")
    assert r.status == 200 and r.json() == {"bat": False, "giao": {}}
