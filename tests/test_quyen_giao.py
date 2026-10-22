"""`phien_ban_quyen` thật trong khoá chống trùng (spec 4 §5.1 điều kiện 7; 4a-1 G14 → 4a-2)."""
from pathlib import Path

from bead_gia import bead
from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.chon import UngVien
from tram.giao_viec.de_xuat import dung_de_xuat
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen

DA = DuAn("hr-codex", Path("/r"), None, {}, lenh_cho_phep=("sh kiem.sh",),
          moi_truong_kiem=MoiTruongKiem(Path("/env"), ".env.testing"), giao=CauHinhGiao(lenh_kiem_mac_dinh=("sh kiem.sh",)))


def test_phien_ban_theo_noi_dung_file(tmp_path):
    assert phien_ban_quyen("coder", goc=tmp_path) == KHONG_CO
    (tmp_path / "coder.json").write_text('{"cho_phep": ["Read"]}')
    a = phien_ban_quyen("coder", goc=tmp_path)
    (tmp_path / "coder.json").write_text('{"cho_phep": ["Read", "Edit"]}')
    b = phien_ban_quyen("coder", goc=tmp_path)
    assert a.startswith("sha256:") and a != b and phien_ban_quyen("qc", goc=tmp_path) == KHONG_CO


def test_khoa_chong_trung_doi_khi_file_quyen_doi(tmp_path, monkeypatch):
    k = dung_kho(tmp_path)
    fetch(k.kho)
    goc = tmp_path / "repo-tram"
    (goc / "vai" / "quyen").mkdir(parents=True)
    monkeypatch.setattr("tram.giao_viec.quyen.goc_repo", lambda: goc)
    b = bead("hr-1", labels=["cot:ai-lam"], acceptance_criteria="- Tên kết thúc 'ỷ'", issue_type="bug")
    uv = UngVien(DA, b, "code", False, frozenset())
    k1 = dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung
    (goc / "vai" / "quyen" / "coder.json").write_text('{"cho_phep": ["Read"]}')
    k2 = dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung
    (goc / "vai" / "quyen" / "qc.json").write_text('{"cho_phep": ["Bash"]}')
    assert k1 != k2 == dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung   # đổi quyền vai khác: không đổi
