"""Trao quyền ghi worktree cho principal phía thợ (3a-2 G20; sửa ở lát 3c): `chmod -R +a` của macOS ĐI THEO symlink,
nên lệnh phải duyệt bằng `find` (không theo symlink). Test thật trên macOS cấp ACL cho CHÍNH user đang chạy (vô hại,
xoá cùng `tmp_path`) — không sudo, không user khác."""
import getpass
import subprocess
import sys

import pytest

from tram.tho.principal_khe import FIND, QUYEN_GHI, lenh_trao_quyen


def test_lenh_duyet_bang_find_chi_thu_muc_va_file_thuong(tmp_path):
    assert lenh_trao_quyen(tmp_path, user="tram-k-1") == [[
        FIND, str(tmp_path), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "/bin/chmod", "+a",
        f"user:tram-k-1 allow {QUYEN_GHI}", "{}", "+"]]


@pytest.mark.skipif(sys.platform != "darwin", reason="ACL macOS")
def test_that_khong_dat_acl_len_dich_cua_symlink(tmp_path):
    wt, ngoai, toi = tmp_path / "wt", tmp_path / "ngoai", getpass.getuser()
    (wt / "a").mkdir(parents=True)
    (wt / "a" / "x").write_text("x")
    ngoai.mkdir()
    (ngoai / "token").write_text("bí mật của tiến trình quản lý")
    (wt / "lk").symlink_to(ngoai / "token")
    (wt / "lkdir").symlink_to(ngoai)
    acl = lambda p: subprocess.run(["/bin/ls", "-led", str(p)], capture_output=True, text=True).stdout
    for lenh in lenh_trao_quyen(wt, user=toi):
        subprocess.run(lenh, check=True, capture_output=True)
    assert f"user:{toi} allow" in acl(wt / "a" / "x") and f"user:{toi} allow" in acl(wt)
    assert "allow" not in acl(ngoai / "token") and "allow" not in acl(ngoai)
    for lenh in lenh_trao_quyen(wt, user=toi, thu=True):
        subprocess.run(lenh, check=True, capture_output=True)
    assert "allow" not in acl(wt / "a" / "x")
