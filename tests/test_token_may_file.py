import io
import os
from types import SimpleNamespace

import pytest

from tram.tho import khach, lenh_chay, token_may


def nha(tmp_path, monkeypatch):
    import pwd
    monkeypatch.setattr(pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='tram-tho', pw_dir=str(tmp_path)))
    return tmp_path / '.tram/token-may'


def test_b_ghi_doc_file_khong_keychain(tmp_path, monkeypatch):
    p = nha(tmp_path, monkeypatch)
    token_may.ghi_token_may('B', 't' * 43, tren_may_b=True,
                            chay=lambda *a, **kw: pytest.fail('đụng Keychain'))
    assert khach.doc_token_may(tren_may_b=True) == 't' * 43
    assert p.stat().st_mode & 0o777 == 0o600
    p.chmod(0o644)
    assert khach.doc_token_may(tren_may_b=True) is None


def test_b_thieu_file_khong_lui_keychain(tmp_path, monkeypatch):
    nha(tmp_path, monkeypatch)
    monkeypatch.setattr(khach, 'doc_muc', lambda *a, **kw: pytest.fail('fallback'))
    assert khach.doc_token_may(tren_may_b=True) is None


def test_nhan_token_b_truoc_co_yaml(tmp_path, monkeypatch, capsys):
    p = nha(tmp_path, monkeypatch)
    monkeypatch.setattr(lenh_chay.sys, 'stdin', io.StringIO('t' * 43 + '\n'))
    luu = lenh_chay.luu_token_may
    monkeypatch.setattr(lenh_chay, 'luu_token_may', lambda token, **kw: luu(
        token, chay=lambda *a, **k: pytest.fail('nhan-token B vẫn gọi Keychain'), doc=lambda: None, **kw))
    assert lenh_chay._nhan_token(SimpleNamespace(may_b=True)) == 0
    assert p.read_text() == 't' * 43
    assert 't' * 43 not in str(capsys.readouterr())


def test_khong_duoc_gia_home_de_ghi_duoi_user_khac(tmp_path, monkeypatch):
    import pwd
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setattr(pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='khac', pw_dir=str(tmp_path)))
    with pytest.raises(ValueError):
        token_may.ghi_token_may('B', 't' * 43, tren_may_b=True)
    assert not (tmp_path / '.tram').exists()


def test_tu_xa_giu_keychain(monkeypatch):
    monkeypatch.setattr(khach, 'doc_muc', lambda *a, **kw: 'gia-keychain')
    assert khach.doc_token_may(tren_may_b=False) == 'gia-keychain'


def test_nhan_token_tu_chon_b_theo_cau_hinh(tmp_path, monkeypatch):
    from tram.tho import cau_hinh
    from tram.duong_dan import tram_home
    tram_home().mkdir(parents=True, exist_ok=True)
    (tram_home() / "tho.yaml").touch()
    p = nha(tmp_path, monkeypatch)
    monkeypatch.setattr(cau_hinh, 'nap_cau_hinh_tho', lambda: SimpleNamespace(tren_may_b=True))
    monkeypatch.setattr(lenh_chay.sys, 'stdin', io.StringIO('t' * 43))
    monkeypatch.setattr(lenh_chay, 'luu_token_may', lambda token, **kw: (
        token_may.ghi_token_may('B', token, tren_may_b=kw.get('tren_may_b', False),
                               chay=lambda *a, **kw: pytest.fail('không dùng Keychain cho B'))))
    assert lenh_chay._nhan_token(SimpleNamespace(may_b=False)) == 0
    assert p.exists()
