"""Lát 1a-2, review Codex đợt 4 (F09/R1): YAML cũ lỗi hoặc trỏ repo khác → lỗi trước khi ghi bất kỳ file nào."""
import pytest


@pytest.mark.parametrize("noi_dung", ["[", "ten: hr\nduong_dan: /repo-khac\nhang_rao: {}\n"])
def test_yaml_cu_sai_khong_ghi_khoi(tmp_path, monkeypatch, noi_dung):
    from tram.du_an.ke_hoach import lap_ke_hoach
    tram = tmp_path / "tram"
    repo = tmp_path / "du-an-that"
    repo.mkdir()
    (tram / "du-an").mkdir(parents=True)
    p = tram / "du-an/hr.yaml"
    p.write_text(noi_dung)
    monkeypatch.setenv("TRAM_REPO", str(tram))
    with pytest.raises(ValueError):
        lap_ke_hoach(repo, them=True, ten="hr")
    assert p.read_text() == noi_dung
    assert not (repo / "AGENTS.md").exists()
    assert not (repo / "CLAUDE.md").exists()
