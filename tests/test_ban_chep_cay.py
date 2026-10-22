"""R7 (lát 3c, 3C-C): cây git của bản chép phải ĐÚNG cây commit gốc — CRLF/`.gitattributes`, encoding, ident, mode,
symlink. `git archive` của trạm không mang cấu hình git riêng của trạm; `git add` trong bản chép chuẩn hoá khác commit
gốc, trùng tên hoa-thường hay submodule → `CayKhacNguon`, không chạy lệnh kiểm. `git` THẬT trong `tmp_path`."""
import os
import subprocess

import pytest

from git_gia import MOI_TRUONG, git
from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec.ban_chep import CayKhacNguon, LoiBanChep, chep_ban
from tram.giao_viec.kiem_lai import kiem_lai

PHP = "* text=auto\n"
LFS = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"0" * 64 + b"\nsize 3\n"


def dung_commit(kho, tep: dict) -> str:
    """Commit con của origin/main qua lệnh nền (giữ nguyên bytes, kể cả CRLF mà `git add` thường sẽ chuẩn hoá)."""
    env = {**MOI_TRUONG, "GIT_INDEX_FILE": str(kho / ".git" / "chi-muc-tam")}
    g = lambda *a, vao=None: subprocess.run(["git", "-C", str(kho), *a], input=vao, env=env, check=True,
                                            capture_output=True).stdout.decode().strip()
    g("read-tree", "origin/main")
    for duong, (mode, nd) in tep.items():
        sha = nd if isinstance(nd, str) else g("hash-object", "-w", "--stdin", vao=nd)
        g("update-index", "--add", "--cacheinfo", f"{mode},{sha},{duong}")
    return g("commit-tree", g("write-tree"), "-p", "origin/main", "-m", "x")


def chep(tmp_path, tep: dict, boc=lambda a: a, cau_hinh_kho: tuple = ()):
    k = dung_kho(tmp_path)
    for c in cau_hinh_kho:
        git(k.kho, "config", *c.split("="))
    sha = dung_commit(k.kho, tep)
    wt = tmp_path / "kiem" / "g-1-ab"
    chep_ban(k.kho, sha, wt, boc=boc)
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")
    return wt


def test_cay_dung_nguon_va_tep_dung_nhu_checkout(tmp_path):
    thuoc_tinh = b"*.crlf eol=crlf\n*.u16 working-tree-encoding=UTF-16\n*.c ident\n*.bin filter=lfs -text\n"
    wt = chep(tmp_path, {".gitattributes": ("100644", thuoc_tinh + PHP.encode()), "a.crlf": ("100644", b"x\ny\n"),
                         "b.u16": ("100644", "xin chào\n".encode()), "c.c": ("100644", b"/* $Id$ */\n"),
                         "d.bin": ("100644", LFS), "e.dat": ("100644", b"\0\r\n"),
                         "chay.sh": ("100755", b"#!/bin/sh\n"), "lk": ("120000", b"chay.sh"),
                         "ra": ("120000", b"../x")})
    assert (wt / "a.crlf").read_bytes() == b"x\r\ny\r\n" and (wt / "e.dat").read_bytes() == b"\0\r\n"
    assert (wt / "b.u16").read_bytes().decode("utf-16") == "xin chào\n" and (wt / "d.bin").read_bytes() == LFS
    assert b"$Id: " in (wt / "c.c").read_bytes() and os.access(wt / "chay.sh", os.X_OK)
    assert os.readlink(wt / "lk") == "chay.sh" and os.readlink(wt / "ra") == "../x"


def test_crlf_khong_thuoc_tinh_giu_nguyen(tmp_path):
    assert (chep(tmp_path, {"a.txt": ("100644", b"x\r\ny\r\n")}) / "a.txt").read_bytes() == b"x\r\ny\r\n"


@pytest.mark.parametrize("bien", [{"HOME": "NHA"}, {"GIT_CONFIG_GLOBAL": "CFG"}, {"GIT_CONFIG_SYSTEM": "CFG"},
                                  {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "filter.lfs.smudge",
                                   "GIT_CONFIG_VALUE_0": "tr a-z A-Z"}, {"XDG_CONFIG_HOME": "XDG"}])
def test_cau_hinh_git_cua_tram_khong_doi_noi_dung_ban_chep(tmp_path, monkeypatch, bien):
    nha, xdg = tmp_path / "nha", tmp_path / "xdg"
    (xdg / "git").mkdir(parents=True)
    (xdg / "git" / "attributes").write_text("* text eol=crlf\n")
    nha.mkdir()
    (nha / ".gitconfig").write_text('[core]\n\tautocrlf = true\n[filter "lfs"]\n\tsmudge = tr a-z A-Z\n\tclean = cat\n')
    for k, v in bien.items():
        monkeypatch.setenv(k, {"NHA": str(nha), "CFG": str(nha / ".gitconfig"), "XDG": str(xdg)}.get(v, v))
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.bin filter=lfs -text\n"), "a.txt": ("100644", b"x\ny\n"),
                         "d.bin": ("100644", b"abc\n")})
    assert (wt / "a.txt").read_bytes() == b"x\ny\n" and (wt / "d.bin").read_bytes() == b"abc\n"


def test_cau_hinh_rieng_cua_kho_kiem_khong_doi_noi_dung_ban_chep(tmp_path):
    wt = chep(tmp_path, {".gitattributes": ("100644", b"*.txt text\n"), "a.txt": ("100644", b"x\n"),
                         "b.md": ("100644", b"y\n")}, cau_hinh_kho=("core.autocrlf=true", "core.eol=crlf"))
    assert (wt / "a.txt").read_bytes() == b"x\n" and (wt / "b.md").read_bytes() == b"y\n"


@pytest.mark.parametrize("tep", [
    {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\ny\r\n")},
    {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\ny\n")},
    {".gitattributes": ("100644", b"*.txt eol=crlf\n"), "a.txt": ("100644", b"x\r\ny\r\n")},
    {".gitattributes": ("100644", b"*.c ident\n"), "c.c": ("100644", b"/* $Id: abc $ */\n")},
    {"sub": ("160000", "1" * 40)}], ids=["crlf-text-auto", "lan-dong", "crlf-eol-crlf", "ident-da-mo", "submodule"])
def test_cay_lech_nguon_thi_fail_closed(tmp_path, tep):
    with pytest.raises(CayKhacNguon, match="khác cây commit gốc"):
        chep(tmp_path, tep)


def test_trung_ten_hoa_thuong_tren_o_khong_phan_biet(tmp_path):
    (tmp_path / "Hoa").touch()
    if not (tmp_path / "hoa").exists():
        pytest.skip("ổ phân biệt hoa-thường: không có ca trùng tên")
    with pytest.raises(CayKhacNguon):
        chep(tmp_path, {"A.txt": ("100644", b"1"), "a.txt": ("100644", b"2")})


@pytest.mark.parametrize("thay", [["/usr/bin/false"], ["/bin/echo", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]])
def test_khong_doc_duoc_hoac_doc_sai_cay_ban_chep_thi_fail_closed(tmp_path, thay):
    with pytest.raises(LoiBanChep, match="rev-parse|khác cây commit gốc"):
        chep(tmp_path, {"a.txt": ("100644", b"x\n")}, boc=lambda a: thay if "rev-parse" in a else a)


def test_kiem_lai_cay_lech_khong_chay_lenh_va_van_don(m):
    k, da, tmp = m
    sha = dung_commit(k.kho, {".gitattributes": ("100644", PHP.encode()), "a.txt": ("100644", b"x\r\n"),
                              "kiem.sh": ("100644", f"touch {tmp}/DA_CHAY\n".encode())})
    kq = kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"],
                  chay_lenh=True, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
                  env_goc=os.environ)
    assert (kq.dat, kq.loi) == (False, "cay-khac-nguon") and not (tmp / "DA_CHAY").exists() and ban_chep(m) == []
