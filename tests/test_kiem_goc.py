"""`tram giao kiem` — thư mục gốc bản chép của `tram-kiem` và sudoers không NOPASSWD root (D22, lát 3c). `lstat`
thật trên `tmp_path`, `uid_cua`/`chay` giả — KHÔNG sudo, không đọc người dùng thật."""
import os
from types import SimpleNamespace

import pytest

from tram.giao_viec.kiem_goc import kiem_sudoers_khong_root, kiem_thu_muc_goc
from tram.giao_viec.principal_kiem import tu_cach_ly

PK = tu_cach_ly("user:tram-kiem")
TOI = lambda ten: os.getuid()                                          # noqa: E731 — "tram-kiem" = user đang test


def test_thu_muc_goc_cua_tram_kiem_la_xanh(tmp_path):
    (tmp_path / "kiem").mkdir(mode=0o755)
    assert kiem_thu_muc_goc(PK, tmp_path / "kiem", uid_cua=TOI).muc_do == "xanh"


@pytest.mark.parametrize("ca", ["symlink", "tep", "chu-khac", "nhom-ghi", "khong-di-qua", "khong-co-user", "chua-dat"])
def test_thu_muc_goc_sai_la_do(tmp_path, ca):
    d = tmp_path / "kiem"
    d.mkdir(mode=0o755)
    kw = {"uid_cua": TOI}
    if ca == "symlink":
        (tmp_path / "lk").symlink_to(d)
        d = tmp_path / "lk"
    elif ca == "tep":
        d = tmp_path / "f"
        d.write_text("x")
    elif ca == "nhom-ghi":
        d.chmod(0o775)
    kw.update({"chu-khac": {"uid_cua": lambda ten: os.getuid() + 1}, "khong-di-qua": {"di_qua": lambda p: False},
               "khong-co-user": {"uid_cua": lambda ten: pwd_loi()}}.get(ca, {}))
    assert kiem_thu_muc_goc(PK, None if ca == "chua-dat" else d, **kw).muc_do == "do"


def pwd_loi():
    raise KeyError("getpwnam(): name not found: 'tram-kiem'")


@pytest.mark.parametrize("ra, muc_do", [
    ((0, "    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"), "xanh"),
    ((0, "    (tram-kiem) NOPASSWD: SETENV: ALL\n    (root) NOPASSWD: /usr/local/tram/x /k/*\n"), "do"),
    ((0, "    (ALL : ALL) NOPASSWD: ALL\n"), "do"),
    ((1, "sudo: a password is required\n"), "do")])
def test_sudoers_nopasswd_root_la_do(ra, muc_do):
    goi = []
    m = kiem_sudoers_khong_root(chay=lambda a, **kw: goi.append(a) or SimpleNamespace(returncode=ra[0], stdout=ra[1]))
    assert m.muc_do == muc_do and goi == [["/usr/bin/sudo", "-n", "-l"]]
