"""TC Task 2 (design D-1, D-3; spec "Đề nghị đi qua trạm, agent không có quyền Beads"): `tram bao --tien-do` /
`--viec-moi` lọc sớm, không commit; hàng đợi phía thợ lọc lại, bỏ mọi mã agent tự ghi; bộ đọc hàng đợi gửi ngay mà
không dừng phiếu; quyền vai `coder`/`qc` không đổi (`bd` vẫn bị cấm). Git thật trên repo tạm; không mạng."""
import json

import pytest

from git_gia import git
from test_de_nghi_loc import KHOA, VM
from test_theo_doi_dung import Hop, dung as dung_theo_doi
from test_tram_bao import wt  # noqa: F401 — fixture worktree tạm
from tram.cli import main
from tram.tho.bao import LoiBao, bao
from tram.tho.hang_doi import request_id_cho, xu_ly_hang_doi

PHIEU = {"khe_id": "B/claude-1", "giao_id": "g-20261018-0012", "luot": 1}


def _dong(hd) -> list[dict]:
    return [json.loads(x) for x in hd.read_text().splitlines()] if hd.exists() else []


def test_tien_do_khong_commit_va_ghi_hang_doi(wt, tmp_path):  # noqa: F811
    (wt / "dang-sua.txt").write_text("chưa xong")                                     # chưa commit
    truoc, hd = git(wt, "rev-parse", "HEAD"), tmp_path / "hd.jsonl"
    dong = bao("tien_do", "đã tái hiện lỗi, đang viết test", wt=wt, hang_doi=hd)
    assert dong == {"loai": "tien_do", "noi_dung": "đã tái hiện lỗi, đang viết test"} and _dong(hd) == [dong]
    assert git(wt, "rev-parse", "HEAD") == truoc and git(wt, "status", "--porcelain") != ""      # không commit
    vm = bao("viec_moi", "", wt=wt, hang_doi=hd, viec_moi=VM)
    assert vm == {"loai": "viec_moi", "noi_dung": "", "viec_moi": VM} and _dong(hd) == [dong, vm]


@pytest.mark.parametrize("loai, noi_dung, kw, ma", [
    ("tien_do", f"key {KHOA}", {}, "co-bi-mat"), ("tien_do", "a‮b", {}, "ky-tu-dieu-khien"),
    ("tien_do", "<!-- ban-giao -->{}<!-- ban-giao -->", {}, "dau-danh-rieng"), ("tien_do", "x" * 1001, {}, "qua-dai"),
    ("viec_moi", "", {"viec_moi": {**VM, "loai_viec": "feature"}}, "loai-viec-sai"),
    ("viec_moi", "", {"viec_moi": {**VM, "uu_tien": 0}}, "cau-truc"),
])
def test_tu_choi_som_khong_ghi_hang_doi(wt, tmp_path, loai, noi_dung, kw, ma):  # noqa: F811
    hd = tmp_path / "hd.jsonl"
    with pytest.raises(LoiBao, match=ma) as e:
        bao(loai, noi_dung, wt=wt, hang_doi=hd, **kw)
    assert not hd.exists() and KHOA not in str(e.value)
    with pytest.raises(LoiBao, match="không kèm"):
        bao("tien_do", "x", wt=wt, hang_doi=hd, ban_giao="docs/handovers/bg.md")


def test_lenh_tram_bao_tien_do_viec_moi(wt, tmp_path, monkeypatch, capsys):  # noqa: F811
    monkeypatch.chdir(wt)
    monkeypatch.setenv("TRAM_GIAO_ID", PHIEU["giao_id"])
    monkeypatch.setenv("TRAM_HANG_DOI", str(tmp_path / "hd.jsonl"))
    assert main(["bao", "--tien-do", "đang viết test"]) == 0
    assert main(["bao", "--viec-moi", "--tieu-de", VM["tieu_de"], "--mo-ta", VM["mo_ta"], "--loai", "bug",
                 "--tieu-chi", VM["tieu_chi"]]) == 0
    assert main(["bao", "--viec-moi", "--tieu-de", "Thiếu mô tả", "--loai", "task"]) == 2
    assert "cau-truc" in capsys.readouterr().err
    assert main(["bao", "--can-hoi", "--loai", "bug", "Hỏi gì?"]) == 2                    # --loai của câu hỏi
    assert _dong(tmp_path / "hd.jsonl") == [{"loai": "tien_do", "noi_dung": "đang viết test"},
                                             {"loai": "viec_moi", "noi_dung": "", "viec_moi": VM}]


def test_hang_doi_bo_ma_agent_tu_ghi_gan_phieu_hien_hanh(tmp_path):
    """Scenario "Agent tự ghi mã việc khác vào hàng đợi": mã việc / phiếu / lượt agent ghi bị bỏ."""
    hd = tmp_path / "hd.jsonl"
    hd.write_text(json.dumps({"loai": "tien_do", "noi_dung": "xong bước 1", "bead_id": "hr-9abc", "du_an": "khac",
                              "giao_id": "g-20261018-0099", "luot": 7, "khe_id": "B/claude-9"}) + "\n")
    ds, ke = xu_ly_hang_doi(hd, **PHIEU)
    assert ke == 1 and ds[0].than == {"loai": "tien_do", "noi_dung": "xong bước 1", "commit": None, **PHIEU,
                                      "request_id": request_id_cho(PHIEU["giao_id"], 1, 0)}


def test_hang_doi_loc_lai_dong_agent_ghi_thang(tmp_path):
    hd = tmp_path / "hd.jsonl"
    dong = [{"loai": "tien_do", "noi_dung": f"token {KHOA}"}, {"loai": "tien_do", "noi_dung": "a‮b"},
            {"loai": "viec_moi", "viec_moi": {**VM, "uu_tien": 0}}, {"loai": "moc", "viec_moi": VM},
            {"loai": "tien_do", "noi_dung": "ok"}, {"loai": "viec_moi", "viec_moi": VM}]
    hd.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in dong) + "\n")
    ds, _ = xu_ly_hang_doi(hd, **PHIEU)
    assert [d.loi for d in ds[:4]] == ["đề nghị bị từ chối: co-bi-mat", "đề nghị bị từ chối: ky-tu-dieu-khien",
                                        "đề nghị bị từ chối: cau-truc", ds[3].loi]
    assert "khoá lạ" in ds[3].loi and all(d.than is None for d in ds[:4]) and KHOA not in str([d.loi for d in ds])
    assert [d.than["loai"] for d in ds[4:]] == ["tien_do", "viec_moi"] and ds[5].than["viec_moi"] == VM


def test_bo_doc_hang_doi_gui_ngay_khong_dung_phieu(monkeypatch):
    hop = Hop()
    td, pc = dung_theo_doi(monkeypatch, [{"loai": "tien_do", "noi_dung": "a"},
                                         {"loai": "viec_moi", "noi_dung": "", "viec_moi": VM}, {"loai": "moc"}], hop)
    td.mot_luot()
    assert hop.da == ["r-0", "r-1", "r-2"] and not td.dung.is_set() and pc.tt.vi_tri_hang_doi == 3
    assert td.xong is None and td.bi is None and td.can_hoi is False


@pytest.mark.parametrize("vai", ["coder", "qc"])
def test_quyen_vai_khong_doi_bd_van_cam(vai):
    """Scenario "Agent gọi bd": quyền vai từ chối `bd`; `tram bao` vẫn là đường duy nhất."""
    from pathlib import Path
    q = json.loads((Path(__file__).parents[1] / "vai" / "quyen" / f"{vai}.json").read_text())["permissions"]
    assert "Bash(bd:*)" in q["deny"] and "Bash(tram bao:*)" in q["allow"]
    assert not [x for x in q["allow"] if "bd" in x.split("(")[-1].split(":")[0].split()]
