"""Nhập token tại Terminal; thăm dò quyền chỉ mở/đóng, không trả nội dung bí mật."""
import getpass
import json
import re
import sys
import warnings

from doi_ngu_chuan_bi import PYTHON, RUNTIME, THO, can_tat
from doi_ngu_io import Dung

# Token setup-token thật dài 108 ký tự; Terminal 80 cột từng cắt mất đuôi khi dán (21/10).
DANG_TOKEN = re.compile(r'sk-ant-oat01-[A-Za-z0-9_-]{80,}')
HELPER = str(RUNTIME / 'tram/tho/claude_token.py')
MO_THU = '''import os, sys
try:
    fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOFOLLOW)
    os.close(fd)
except PermissionError:
    print('Permission denied', file=sys.stderr)
    sys.exit(1)
'''


def dang_nhap(c, n):
    can_tat(c)
    if n not in (1, 2) or not sys.stdin.isatty():
        raise Dung('can-Terminal.app-khe-hop-le')
    u = f'tram-khe{n}'
    dau = ['sudo', '-H', '-u', u]
    c.tuong_tac('setup-token', [*dau, '/usr/bin/env', f'CLAUDE_CONFIG_DIR=/Users/{u}/claude',
                              '/opt/homebrew/bin/claude', 'setup-token'])
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        try:
            token = getpass.getpass('Dán token Claude vừa tạo (ẩn): ').strip()
        except (getpass.GetPassWarning, EOFError):
            raise Dung('khong-co-o-nhap-an') from None
    if not DANG_TOKEN.fullmatch(token):
        dai = len(token)
        token = None
        raise Dung(f'token-sai-dang (dai {dai} ky tu, can sk-ant-oat01-... >= 93) — dan lai bang Terminal.app')
    # Bỏ ACL cũ trước ghi: mode 0700 không tự xoá ACL của bước chuẩn bị cũ.
    c.goi('bo-acl-claude', [*dau, 'chmod', '-N', f'/Users/{u}/claude'], han=30)
    c.goi('kin-claude', [*dau, 'chmod', '700', f'/Users/{u}/claude'], han=30)
    try:
        c.goi('ghi-token-khe', [*dau, PYTHON, '-I', HELPER, 'ghi'], input=token, han=30)
    finally:
        token = None
    c.goi('kiem-token-khe', [*dau, PYTHON, '-I', HELPER, 'kiem'], han=30)
    r = c.goi('auth-status-fd', [*dau, PYTHON, '-I', HELPER, 'chay', 'auth', 'status'], han=30)
    try:
        dat = json.loads(r.stdout).get('loggedIn') is True
    except (ValueError, AttributeError):
        dat = False
    if not dat:
        raise Dung('S2-chua-dang-nhap-qua-FD')
    c.ghi('S2-file', 'DAT-CHO-DO-NEN')


def kiem_token_s6(c):
    from tram.tho.cham_tham_do import cham
    # Đối chứng dưới chủ file; helper kiểm chủ, mode, loại, không trả token.
    for n in (1, 2):
        c.goi('token-khe-doi-chung', ['sudo', '-H', '-u', f'tram-khe{n}', PYTHON, '-I', HELPER, 'kiem'], han=30)
    script = ('import sys; sys.path.insert(0, sys.argv[1]); '
              'from tram.tho.token_may_file import doc_token_b; sys.exit(0 if doc_token_b() else 2)')
    c.goi('token-may-doi-chung', ['sudo', '-H', '-u', 'tram-tho', PYTHON, '-I', '-c', script, str(RUNTIME)], han=30)
    for n in (1, 2):
        dich = f'/Users/tram-khe{n}/claude/oauth-token'
        for user, p in ((f'tram-khe{3-n}', dich), ('tram-tho', dich),
                        (f'tram-khe{n}', str(THO / '.tram/token-may'))):
            r = c.goi('token-bi-chan', ['sudo', '-H', '-u', user, PYTHON, '-I', '-c', MO_THU, p],
                      check=False, han=30)
            if cham('doc', r.returncode, '', r.stderr)[0] != 'dat':
                raise Dung('token-file-chua-chung-minh-bi-chan')
