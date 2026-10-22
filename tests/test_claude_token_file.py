import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace

import pytest


def api():
    assert importlib.util.find_spec('tram.tho.claude_token'), 'Thiếu wrapper FD dưới UID khe'
    from tram.tho import claude_token
    return claude_token


def test_wrapper_fd_khong_token_trong_argv_env(tmp_path, monkeypatch):
    m = api()
    monkeypatch.setattr(m.pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='tram-khe1', pw_dir=str(tmp_path)))
    from tram.tho.tep_token import ghi
    p = tmp_path / 'claude/oauth-token'; ghi(p, 'oauth-gia-lap')
    monkeypatch.setenv('CLAUDE_CODE_OAUTH_TOKEN', 'token-cu')
    monkeypatch.setenv('CLAUDE_CODE_REMOTE', '1')
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'key-cu')
    monkeypatch.setenv('CLAUDE_CONFIG_DIR', '/sai')
    monkeypatch.setenv('TRAM_THO_TOKEN', 'may-cu')
    da = []
    def execve(cli, argv, env):
        fd = int(env['CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR'])
        da.append(fd)
        assert os.get_inheritable(fd) and os.read(fd, 4096) == b'oauth-gia-lap'
        assert env['CLAUDE_CONFIG_DIR'] == str(p.parent)
        assert env['HOME'] == str(tmp_path)
        assert not {'CLAUDE_CODE_OAUTH_TOKEN', 'CLAUDE_CODE_REMOTE', 'ANTHROPIC_API_KEY', 'TRAM_THO_TOKEN'} & env.keys()
        assert cli == '/opt/homebrew/bin/claude' and argv == [cli, 'auth', 'status']
        assert all('oauth-gia-lap' not in str(x) for x in (argv, env))
    monkeypatch.setattr(os, 'execve', execve)
    m.chay(['auth', 'status'])
    with pytest.raises(OSError):
        os.fstat(da[0])


@pytest.mark.parametrize('loi', ['thieu', 'credential', 'uid', 'sai-mode'])
def test_wrapper_dong_khi_kho_hong(tmp_path, monkeypatch, loi):
    m = api()
    monkeypatch.setattr(m.pwd, 'getpwuid', lambda uid: SimpleNamespace(
        pw_name='tram-tho' if loi == 'uid' else 'tram-khe2', pw_dir=str(tmp_path)))
    from tram.tho.tep_token import ghi
    p = tmp_path / 'claude/oauth-token'; ghi(p, 'gia-lap')
    if loi == 'thieu': p.unlink()
    if loi == 'credential': (p.parent / '.credentials.json').touch()
    if loi == 'sai-mode': p.chmod(0o644)
    monkeypatch.setattr(os, 'execve', lambda *a: pytest.fail('exec khi kho hong'))
    with pytest.raises((ValueError, OSError)):
        m.chay(['auth', 'status'])


def test_boc_nam_sau_sudo_va_env_khong_bi_mat(tmp_path):
    from test_doi_ngu_nen import ch
    from tram.tho.kiem_cong import dang_nhap
    from tram.tho.deps_b import boc_kiem_b
    from tram.tho.principal import Principal, BIEN_GIU
    c = ch(); da = []
    def run(argv, **kw):
        da.append((argv, kw)); return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}')
    assert dang_nhap(c, c.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=run, xac_minh=lambda *a: 600)[0] == 'xanh'
    a, kw = da[0]
    assert any(x.endswith('/claude_token.py') for x in a), 'auth status chưa qua wrapper'
    assert a.index('-u') < a.index('-I') and a[-3:] == ['chay', 'auth', 'status']
    assert not any('OAUTH' in x for x in BIEN_GIU) and not any('TOKEN' in x for x in kw['env'])
    pc = SimpleNamespace(p=SimpleNamespace(du_an='ben-station'), principal=Principal('user', 'tram-khe1'))
    a = boc_kiem_b(pc)(['claude', '-p'])
    assert a.index('--') < a.index('TRAM_KIEM_DA_CHUAN_BI=1') < a.index('-I')
    assert a[-2:] == ['chay', '-p']


def test_do_nen_cung_wrapper(tmp_path, monkeypatch):
    from test_doi_ngu_nen import ch
    from tram.tho.do_nen import thu_claude
    monkeypatch.setattr(Path, 'home', lambda: tmp_path); (tmp_path / 'tram').mkdir()
    def run(argv, **kw):
        assert any(x.endswith('/claude_token.py') for x in argv), 'do-nen chưa qua wrapper'
        return SimpleNamespace(returncode=0, stdout='{"type":"result","is_error":false,"result":"SAN-SANG"}')
    assert thu_claude(ch(), chay=run)
