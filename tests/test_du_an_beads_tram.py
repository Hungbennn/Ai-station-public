"""Lát 1a-2: `tram du-an them` bước (3) — chỉ kiểm điều kiện, in lệnh dự kiến, chờ cổng spike §4.6."""
from tram.du_an.beads_tram import xet_beads


def repo_beads(tmp_path):
    r = tmp_path / "HR Codex"
    (r / ".beads").mkdir(parents=True)
    return r


def spike(goc, noi_dung):
    (goc / "docs" / "spikes").mkdir(parents=True)
    (goc / "docs" / "spikes" / "2026-10-20-beads-tu-xa.md").write_text(noi_dung, encoding="utf-8")


def test_repo_khong_dung_beads(tmp_path):
    (tmp_path / "r").mkdir()
    b = xet_beads(tmp_path / "r", goc=tmp_path, may_b="may-b")
    assert b.trang_thai == "khong_dung_beads" and b.lenh_du_kien == ()


def test_chua_co_spike_thi_cho_cong(tmp_path):
    b = xet_beads(repo_beads(tmp_path), goc=tmp_path / "tram", may_b=None)
    assert b.trang_thai == "cho_cong" and "bs-g28.4" in b.ly_do
    assert b.lenh_du_kien == (f"bd -C '{tmp_path / 'HR Codex'}' dolt set host <ten_may_b>",)


def test_spike_chua_dat_van_cho_cong(tmp_path):
    spike(tmp_path / "tram", "# Spike\nKết luận: chưa đạt — claim đôi thắng cả hai\n")
    assert xet_beads(repo_beads(tmp_path), goc=tmp_path / "tram", may_b="may-b").trang_thai == "cho_cong"


def test_spike_dat_van_khong_thuc_thi(tmp_path):
    spike(tmp_path / "tram", "# Spike\n\nKết luận: đạt\n")
    b = xet_beads(repo_beads(tmp_path), goc=tmp_path / "tram", may_b="may-b")
    assert b.trang_thai == "cho_lat_sau" and "2026-10-20-beads-tu-xa.md" in b.ly_do
    assert b.lenh_du_kien[0].endswith("dolt set host may-b") and "ten_may_b" not in b.ly_do


def test_spike_dat_thieu_may_b(tmp_path):
    spike(tmp_path / "tram", "Kết luận: đạt\n")
    assert "chưa có ten_may_b" in xet_beads(repo_beads(tmp_path), goc=tmp_path / "tram", may_b=None).ly_do
