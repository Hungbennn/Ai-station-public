import builtins

import pytest

from tram.cli import main
from tram.du_an.khoi import DAU


@pytest.fixture(autouse=True)
def repo_tram_tam(tmp_path, monkeypatch):
    """Lát 1a-2: `them` còn ghi du-an/<ten>.yaml vào repo trạm — test không được ghi vào repo thật."""
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "tram-repo"))


def test_khong_dong_y_thi_khong_ghi(tmp_path, monkeypatch, capsys):
    (tmp_path / "AGENTS.md").write_text("# A\n", encoding="utf-8")
    monkeypatch.setattr(builtins, "input", lambda _: "khong")
    assert main(["du-an", "them", str(tmp_path)]) == 1
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n" and not (tmp_path / "CLAUDE.md").exists()
    assert "+" + DAU in capsys.readouterr().out


def test_go_khi_khong_co_khoi_khong_hoi_khong_ghi(tmp_path, monkeypatch, capsys):
    (tmp_path / "AGENTS.md").write_bytes(b"# A")  # không có xuống dòng cuối
    monkeypatch.setattr(builtins, "input", lambda _: (_ for _ in ()).throw(AssertionError("không được hỏi")))
    assert main(["du-an", "go", str(tmp_path)]) == 0
    assert (tmp_path / "AGENTS.md").read_bytes() == b"# A" and not (tmp_path / "CLAUDE.md").exists()
    assert "Không có gì thay đổi." in capsys.readouterr().out


def test_dau_hong_o_mot_file_thi_khong_ghi_file_nao(tmp_path, capsys):
    (tmp_path / "AGENTS.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("<!-- tram:bat-dau v1 -->\nghi chú\n", encoding="utf-8")
    assert main(["du-an", "them", str(tmp_path), "--dong-y"]) == 2
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n"
    assert "CLAUDE.md" in capsys.readouterr().out


def test_giu_xuong_dong_crlf(tmp_path):
    (tmp_path / "AGENTS.md").write_bytes("# A\r\n\r\nNội dung\r\n".encode())
    assert main(["du-an", "them", str(tmp_path), "--dong-y"]) == 0
    b = (tmp_path / "AGENTS.md").read_bytes()
    assert b.count(b"\n") == b.count(b"\r\n") and DAU.encode() in b
    assert main(["du-an", "go", str(tmp_path), "--dong-y"]) == 0
    assert (tmp_path / "AGENTS.md").read_bytes() == "# A\r\n\r\nNội dung\r\n".encode()


def test_repo_khong_ton_tai(tmp_path, capsys):
    assert main(["du-an", "them", str(tmp_path / "khong-co"), "--dong-y"]) == 2
    assert not (tmp_path / "khong-co").exists()
