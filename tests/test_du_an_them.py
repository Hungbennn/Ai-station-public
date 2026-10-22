"""Lát 1a-2: `tram du-an them` đủ ba bước theo spec 0+1a §4.7 — repo dự án và repo trạm đều là thư mục tạm."""
import builtins
import subprocess

import pytest

from tram.cau_hinh.bat_ghi import bat_ghi
from tram.cau_hinh.du_an import nap_du_an
from tram.cli import main
from tram.du_an.khoi import DAU


@pytest.fixture
def moi_truong(tmp_path, monkeypatch):
    tram = tmp_path / "tram-repo"
    repo = tmp_path / "HR Codex"
    repo.mkdir()
    monkeypatch.setenv("TRAM_REPO", str(tram))

    def cam(*a, **kw):
        raise AssertionError("du-an them không được chạy lệnh ngoài")
    monkeypatch.setattr(subprocess, "run", cam)
    monkeypatch.setattr(subprocess, "Popen", cam)
    return repo, tram / "du-an" / "hr-codex.yaml"


def khong_hoi(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: (_ for _ in ()).throw(AssertionError("không được hỏi")))


def test_dong_y_thi_tao_yaml_va_chen_khoi(moi_truong, capsys):
    repo, yaml = moi_truong
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    da = nap_du_an("hr-codex", thu_muc=yaml.parent)
    assert da.duong_dan == repo.resolve() and DAU in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert bat_ghi("hr-codex", thu_muc=yaml.parent) is False          # D31: dự án mới chỉ đọc + quét thử
    ra = capsys.readouterr().out
    assert '+ten: "hr-codex"' in ra and "+" + DAU in ra and "Bước 3" in ra and "khong_dung_beads" in ra


def test_khong_dong_y_thi_khong_ghi_gi(moi_truong, monkeypatch, capsys):
    repo, yaml = moi_truong
    monkeypatch.setattr(builtins, "input", lambda _: "khong")
    assert main(["du-an", "them", str(repo)]) == 1
    assert not yaml.exists() and not (repo / "AGENTS.md").exists()
    assert "bat_ghi: false — trạm chỉ đọc và quét thử" in capsys.readouterr().out


def test_chay_lai_khong_doi_gi_khong_hoi(moi_truong, monkeypatch, capsys):
    repo, _ = moi_truong
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    khong_hoi(monkeypatch)
    assert main(["du-an", "them", str(repo)]) == 0
    assert capsys.readouterr().out.rstrip().endswith("Không có gì thay đổi.")


def test_yaml_da_co_thi_giu_nguyen(moi_truong, capsys):
    repo, yaml = moi_truong  # yaml hợp lệ trỏ đúng repo; yaml lỗi/trỏ repo khác: tests/test_du_an_them_yaml_cu.py
    yaml.parent.mkdir(parents=True)
    yaml.write_text(f'ten: "hr-codex"\nduong_dan: "{repo.resolve()}"\nboi_canh: "viết tay"\n', encoding="utf-8")
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    assert "viết tay" in yaml.read_text(encoding="utf-8")
    ra = capsys.readouterr().out
    assert "đã có — giữ nguyên" in ra and "bat_ghi" not in ra and DAU in (repo / "AGENTS.md").read_text()


def test_ghi_de_cau_hinh_khi_co_co(moi_truong, capsys):
    repo, yaml = moi_truong
    yaml.parent.mkdir(parents=True)
    yaml.write_text('ten: "hr-codex"\nduong_dan: "/khac"\n', encoding="utf-8")
    assert main(["du-an", "them", str(repo), "--ghi-de-cau-hinh", "--dong-y"]) == 0
    assert nap_du_an("hr-codex", thu_muc=yaml.parent).duong_dan == repo.resolve()
    assert '-duong_dan: "/khac"' in capsys.readouterr().out


def test_ten_va_gitnexus_tuy_chon(moi_truong):
    repo, yaml = moi_truong
    assert main(["du-an", "them", str(repo), "--ten", "hr", "--gitnexus", "hr-interview-copilot", "--dong-y"]) == 0
    assert nap_du_an("hr", thu_muc=yaml.parent).gitnexus_repo == "hr-interview-copilot" and not yaml.exists()


def test_ten_sai_thi_khong_ghi_gi(moi_truong, capsys):
    repo, yaml = moi_truong
    assert main(["du-an", "them", str(repo), "--ten", "HR Codex", "--dong-y"]) == 2
    assert not yaml.parent.exists() and not (repo / "AGENTS.md").exists()
    assert "không hợp lệ" in capsys.readouterr().out


def test_dau_khoi_hong_thi_khong_ghi_yaml(moi_truong, capsys):
    repo, yaml = moi_truong
    (repo / "CLAUDE.md").write_text("<!-- tram:bat-dau v1 -->\nghi chú\n", encoding="utf-8")
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 2
    assert not yaml.exists() and not (repo / "AGENTS.md").exists() and "CLAUDE.md" in capsys.readouterr().out


def test_repo_co_beads_thi_chi_in_buoc_3(moi_truong, capsys):
    repo, _ = moi_truong
    (repo / ".beads").mkdir()
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    ra = capsys.readouterr().out
    assert "Bước 3 — trỏ beads về trạm chủ: cho_cong" in ra and "KHÔNG chạy" in ra and "dolt set host" in ra


def test_cau_hinh_tram_hong_van_lap_ke_hoach(moi_truong, tram_home_tam, capsys):
    repo, _ = moi_truong
    (repo / ".beads").mkdir()
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("ten_may_b: 'a b'\n", encoding="utf-8")
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    assert "cau-hinh.yaml lỗi" in capsys.readouterr().out


def test_go_khong_xoa_yaml(moi_truong, capsys):
    repo, yaml = moi_truong
    assert main(["du-an", "them", str(repo), "--dong-y"]) == 0
    assert main(["du-an", "go", str(repo), "--dong-y"]) == 0
    assert yaml.exists() and DAU not in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "không xoá du-an/<ten>.yaml" in capsys.readouterr().out
