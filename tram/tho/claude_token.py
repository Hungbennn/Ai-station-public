"""Điểm vào stdlib sau sudo: mở token bằng UID khe rồi exec Claude; không in bí mật."""
import os
import pwd
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tram.tho.principal import BIEN_GIU
from tram.tho.tep_token import TOKEN, doc, ghi, mo

CLI = '/opt/homebrew/bin/claude'
FD_ENV = 'CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR'


def duong():
    user = pwd.getpwuid(os.geteuid())
    if user.pw_name not in ('tram-khe1', 'tram-khe2'):
        raise ValueError('Chỉ chạy dưới UID khe B')
    return Path(user.pw_dir) / 'claude/oauth-token'


def kiem():
    p = duong()
    for credential in (p.parent / '.credentials.json', p.parent.parent / '.claude/.credentials.json'):
        if credential.exists() or credential.is_symlink():
            raise ValueError('Còn credential ngoài file đã duyệt')
    doc(p)
    return p


def chay(argv, *, kiem_token=None, exec_cli=None):
    """Phụ thuộc chỉ tiêm từ Python; điểm vào CLI luôn dùng kiểm UID và exec cố định."""
    p = (kiem_token or kiem)()
    fd = mo(p)
    try:
        if not TOKEN.fullmatch(os.read(fd, 4097).decode('ascii')):
            raise ValueError('Token sai dạng')
        os.lseek(fd, 0, os.SEEK_SET)
        os.set_inheritable(fd, True)
        env = {k: v for k, v in os.environ.items() if k in BIEN_GIU}
        env.update(HOME=str(p.parent.parent), CLAUDE_CONFIG_DIR=str(p.parent))
        # Cờ thư viện được đặt bởi boc_kiem_b sau sudo, không mang bí mật.
        if os.environ.get('TRAM_KIEM_DA_CHUAN_BI') == '1':
            env['TRAM_KIEM_DA_CHUAN_BI'] = '1'
        env[FD_ENV] = str(fd)
        (exec_cli or os.execve)(CLI, [CLI, *argv], env)
    finally:
        os.close(fd)


def main():
    try:
        if sys.argv[1:] == ['ghi']:
            ghi(duong(), sys.stdin.read(4098).strip())
            kiem()
        elif sys.argv[1:] == ['kiem']:
            kiem()
        elif sys.argv[1:2] == ['chay']:
            chay(sys.argv[2:])
        else:
            raise ValueError('Sai lệnh')
    except (OSError, ValueError, KeyError):
        print('TOKEN-KHE: CHUA-XAC-NHAN', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
