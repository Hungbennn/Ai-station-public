from pathlib import Path
import subprocess
import pytest
from tram.tho.quyen_cay_b import lenh_quyen_b, trao_quyen_b


def test_chi_cay_ma_va_hang_doi(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / ".git").write_text("gitdir: /private/git/worktrees/wt")
    hd = tmp_path / "hang-doi.jsonl"
    ds = lenh_quyen_b(wt, hd, user="tram-khe1")
    assert any("deny write" in " ".join(a) and a[-1] == str(wt / ".git") for a in ds)
    find = next(a for a in ds if a[0] == "/usr/bin/find")
    assert "-prune" in find and str(wt / ".tram") in find
    assert all("delete_child" not in " ".join(a) for a in ds if "user:tram-khe1" in " ".join(a))
    assert not any("/private/git" in " ".join(a) for a in ds)
    assert any(a[-1] == str(hd) and "allow read,append" in a[-2] for a in ds)


def test_acl_hong_dung_ngay(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /g")
    da = []
    def hong(argv, **kw):
        da.append(argv)
        raise subprocess.CalledProcessError(1, argv)
    with pytest.raises(subprocess.CalledProcessError):
        trao_quyen_b(tmp_path, tmp_path / "hd", user="tram-khe1", chay=hong)
    assert len(da) == 1


def test_khe_khac_khong_doc_cay_va_settings_duoc_doc_khong_duoc_ghi(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /g")
    hd = tmp_path / "phieu/hang-doi.jsonl"
    hd.parent.mkdir()
    (hd.parent / "settings.json").touch()
    ds = lenh_quyen_b(tmp_path, hd, user="tram-khe1")
    assert ["/bin/chmod", "700", str(tmp_path)] in ds
    assert ["/bin/chmod", "700", str(hd.parent)] in ds
    assert any(a[-1] == str(hd.parent) and "allow list,search" in a[-2] for a in ds)
    assert any(a[-1] == str(hd.parent / "settings.json") and "allow read," in a[-2] for a in ds)


def test_quan_ly_co_quyen_ke_thua_doc_va_don_file_uid_khe(tmp_path):
    (tmp_path / '.git').write_text('gitdir: /g')
    ds = lenh_quyen_b(tmp_path, tmp_path / 'phieu/hang-doi.jsonl', user='tram-khe1')
    import pwd
    manager = f'user:{pwd.getpwuid(tmp_path.stat().st_uid).pw_name} allow '
    assert any(manager in ' '.join(a) and 'delete_child' in ' '.join(a)
               and 'file_inherit,directory_inherit' in ' '.join(a) for a in ds)
    assert any(a[-1] == str(tmp_path) and 'only_inherit' in a[-2] and manager in a[-2] for a in ds)
    assert not any('chown' == x for a in ds for x in a)
    assert any(a[-1] == str(tmp_path / '.tram') and 'file_inherit' in a[-2] and 'write' not in a[-2] for a in ds)


def test_cu_phap_acl_that_chi_trong_tmp(tmp_path):
    # Chỉ kiểm cú pháp macOS, không đổi UID/không sudo; nobody không phải hai tài khoản khe thật.
    wt, hd = tmp_path / 'cay', tmp_path / 'phieu/hang-doi.jsonl'
    (wt / '.tram').mkdir(parents=True)
    (wt / '.git').write_text('gitdir: /khong-dung')
    (wt / '.tram/goi.md').write_text('goi-gia')
    (wt / 'src').mkdir()
    (wt / 'src/a.py').write_text('x=1')
    hd.parent.mkdir()
    hd.touch()
    (hd.parent / 'settings.json').write_text('{}')
    trao_quyen_b(wt, hd, user='nobody', chay=subprocess.run)
    # File sinh sau còn đọc/dọn được; chủ quản lý không bị ACL của nobody chặn.
    (wt / 'src/moi').write_text('x')
    (wt / 'src/moi').unlink()
