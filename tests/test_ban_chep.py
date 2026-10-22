"""Bản chép kiểm do `tram-kiem` sở hữu (D22, lát 3c) — các ca F01 còn áp dụng: đổi cây sau khi kiểm, symlink trong
archive, tiến trình tram-kiem tái sinh, dọn lỗi thì fail-closed, hai lần kiểm lại đồng thời. `git archive`, `tar`,
`rm` THẬT dưới user đang chạy test (`boc` đồng nhất thay cho `sudo -u tram-kiem`) trong `tmp_path` — không sudo."""
import os
import shutil
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, chay, m  # noqa: F401 — fixture `m` dùng chung
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.ban_chep import KiemLaiDangBan, LoiBanChep, chep_ban, giu_khoa, nhan_moi_truong
from tram.giao_viec.git_kiem import fetch
from tram.kiem.moi_truong import LoiMoiTruongKiem

KIEM = ('test -f tests/a.txt && grep -q "Format:" v.txt && grep -q DB_DATABASE=test .env.testing && git ls-files '
        '--error-unmatch tests/a.txt >/dev/null && ! git ls-files --error-unmatch .env.testing 2>/dev/null\n')


def test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau(m):
    (m[0].kho / "kiem.sh").write_text("exit 1\n")              # thư mục làm việc của kho kiểm bị sửa: không ảnh hưởng
    kq = chay(m, {"kiem.sh": KIEM, "tests/a.txt": "x", "v.txt": "$Format:%H$\n",
                  ".gitattributes": "/tests export-ignore\nv.txt export-subst\n"})
    assert kq.dat and ban_chep(m) == []


def test_cay_bi_doi_sau_khi_chep_thi_moi_truong_khong_ra_ngoai(tmp_path):
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"config/app.php": "x"}, tu=k.main)
    fetch(k.kho)
    wt, ngoai, env = tmp_path / "kiem" / "g-1-ab", tmp_path / "ngoai", tmp_path / "env.testing"
    ngoai.mkdir()
    env.write_text("DB_DATABASE=test\n")
    chep_ban(k.kho, sha, wt, boc=lambda a: a)
    shutil.rmtree(wt / "config")
    (wt / "config").symlink_to(ngoai)                          # tiến trình lạ đổi cây SAU khi chép
    with pytest.raises(LoiMoiTruongKiem):
        nhan_moi_truong(k.kho, sha, wt, env, "config/.env.testing", boc=lambda a: a)
    assert list(ngoai.iterdir()) == []


def test_symlink_trong_archive_khong_bi_di_theo(m):
    ngoai = m[2] / "ngoai"
    (ngoai / "thu-muc").mkdir(parents=True)
    (ngoai / "bi-mat").write_text("goc")
    (ngoai / "thu-muc" / "x").write_text("goc")
    os.symlink(ngoai / "bi-mat", m[0].dev / "lk")
    os.symlink(ngoai / "thu-muc", m[0].dev / "lkdir")
    assert chay(m, {"kiem.sh": "test -L lk && test -L lkdir\n"}).dat and ban_chep(m) == []
    assert (ngoai / "bi-mat").read_text() == "goc" and (ngoai / "thu-muc" / "x").read_text() == "goc"
    os.symlink(ngoai / "thu-muc", m[0].dev / "config")             # đích môi trường đi qua symlink trong commit
    da = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(m[2] / "env.testing",
                                                                            "config/.env.testing"))
    kq = chay((m[0], da, m[2]), {"kiem.sh": "exit 0\n"})
    assert kq.loi == "thieu-moi-truong-kiem" and sorted(os.listdir(ngoai / "thu-muc")) == ["x"]


def test_tien_trinh_tai_sinh_luc_don_thi_khong_tra_ket_qua(m):
    lan = []

    def don_sach():
        lan.append(1)
        if len(lan) == 2:
            raise LoiBanChep("tram-kiem vẫn còn tiến trình sau 5 lần giết")
    with pytest.raises(LoiBanChep, match="vẫn còn"):
        chay(m, {"kiem.sh": "exit 0\n"}, don_sach=don_sach)
    assert ban_chep(m) == []                                       # vẫn dọn thư mục, nhưng không trả kết quả


@pytest.mark.parametrize("hong", ["/bin/rm", "/usr/bin/tar"])
def test_tar_hoac_rm_loi_thi_fail_closed(m, hong):
    boc = lambda a: ["/usr/bin/false"] if a[0] == hong else a
    with pytest.raises(LoiBanChep):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, boc=boc)
    assert not (m[2] / "DA_CHAY").exists() or hong == "/bin/rm"
    assert (ban_chep(m) == []) == (hong == "/usr/bin/tar")


def test_hai_lan_kiem_lai_dong_thoi(m):
    with giu_khoa():
        with pytest.raises(KiemLaiDangBan):
            chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"})
    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []
    assert chay(m, {"kiem.sh": "exit 0\n"}).dat                       # nhả khoá → chạy được
