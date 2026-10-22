import os

import pytest

from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem


@pytest.fixture
def ds(tmp_path):
    nguon = tmp_path / "env-test"
    nguon.write_text("DB_DATABASE=hr_test\n")
    wt = tmp_path / "wt"
    (wt / "erp").mkdir(parents=True)
    return nguon, wt


def test_chep_dung_dich_quyen_600(ds):
    nguon, wt = ds
    p = chep_moi_truong_kiem(nguon, wt, "erp/.env.testing")
    assert p.read_text() == "DB_DATABASE=hr_test\n" and oct(p.stat().st_mode & 0o777) == "0o600"
    (wt / "erp/.env.testing").write_text("cũ")
    assert chep_moi_truong_kiem(nguon, wt, "erp/.env.testing").read_text().startswith("DB_")


@pytest.mark.parametrize("dich", ["/etc/x", "../x", "erp/../../x", "erp//x", "./x", "", "erp\\x", "erp/."])
def test_dich_sai_dang(ds, dich):
    with pytest.raises(LoiMoiTruongKiem):
        chep_moi_truong_kiem(*ds, dich)


def test_dich_qua_symlink_ra_ngoai_bi_tu_choi(ds, tmp_path):
    nguon, wt = ds
    (tmp_path / "ngoai").mkdir()
    os.symlink(tmp_path / "ngoai", wt / "thoat")
    with pytest.raises(LoiMoiTruongKiem, match="thoát worktree"):
        chep_moi_truong_kiem(nguon, wt, "thoat/.env")
    assert not (tmp_path / "ngoai/.env").exists()


def test_dich_la_symlink_bi_tu_choi(ds, tmp_path):
    nguon, wt = ds
    os.symlink(tmp_path / "bi-ghi-de", wt / "erp/.env.testing")
    with pytest.raises(LoiMoiTruongKiem, match="symlink"):
        chep_moi_truong_kiem(nguon, wt, "erp/.env.testing")
    assert not (tmp_path / "bi-ghi-de").exists()


def test_thieu_nguon_hoac_thu_muc_dich(ds, tmp_path):
    nguon, wt = ds
    with pytest.raises(LoiMoiTruongKiem):
        chep_moi_truong_kiem(tmp_path / "khong-co", wt, "erp/.env")
    with pytest.raises(LoiMoiTruongKiem):
        chep_moi_truong_kiem(nguon, wt, "khong/.env")
