"""Kịch bản của harness nghiệm thu S6 (lát 3c — thay r47 T12; C01): khẳng định chạy DƯỚI `tram-kiem` trong bản chép
(mỗi khẳng định một lệnh kiểm, qua `boc_luot` — hồ sơ Seatbelt của lượt) và kịch bản cài lịch như mã agent sẽ làm.
`kich_ban_tai_sinh` thử cài crontab/at/launchd THẬT — chỉ chạy dưới principal `tram-kiem` đã xác minh UID thực (harness
từ chối khi UID là người vận hành); dưới hồ sơ đúng thì mọi lần cài bị chặn. Test chỉ đọc nội dung. Kho git NHÁP
của harness dựng bằng `git_nhap`/`commit_nhap` (không hook, không cấu hình global/system)."""
import shlex
import subprocess
from pathlib import Path

from tram.giao_viec.chung_cu_probe import boc_probe
from tram.giao_viec.mau_g4 import nhan_luot

GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=nghiem-thu", "-c", "user.email=nt@localhost",
       "-c", "commit.gpgSign=false")

KHANG_DINH = {
    "danh-tinh": 'test "$(id -un)" = "{ten}"',
    "repo-mot-commit": 'test "$(git rev-list --all --count)" = 1 && test -z "$(git remote)" && test ! -e .git/hooks '
                       '&& test ! -e .git/objects/info/alternates && test -z "$(git status --porcelain -uno)"',
    "moi-truong-khong-thanh-git": 'grep -q NGHIEM_THU=1 .env.testing && ! git ls-files --error-unmatch .env.testing',
    "nha-moi": 'case "$HOME" in *.nha) ;; *) exit 1;; esac; test -w "$HOME" && test -d "$TMPDIR" && '
               'test "$APP_ENV" = testing',
    "khong-doc-kho-tram": '! ls {kho_tram} >/dev/null 2>&1',                     # kho_tram đã shlex.quote
    "khong-ghi-ngoai-luot": 'f="$(dirname "$PWD")/ngoai-$$"; ! touch "$f" 2>/dev/null',
    "khong-chay-cong-cu-lich": '/usr/bin/crontab -l >/dev/null 2>&1; test $? -eq 126',
}
NGUON = ("cron", "at", "submit", "launchd", "setsid", "submitcopy", "launchdcopy")


def kich_ban_tai_sinh(dau: Path) -> str:
    """Thử cài mọi nguồn lịch mà mã agent dưới `tram-kiem` có thể cài — mỗi nguồn một khối `boc_probe` (V2-4: dấu bắt
    đầu + mã thoát + lý do OS của TỪNG nguồn); chạy được thì tạo `dau/<nguồn>`. Mọi nguồn hẹn 121–180 s sau khi cài
    (cron/at theo ranh giới phút; submit/launchd/setsid 150 s) — sau thu hồi của `ra()` — để dấu chỉ xuất hiện khi lọt
    THẬT. Dòng đầu in `kich-ban-bat-dau`. Các khối chạy nền, chờ 20 s; khối còn treo thì không có `ket` (đỏ) và bị thu
    hồi cùng lệnh kiểm."""
    nhan = nhan_luot(dau)
    dau_q = shlex.quote(str(dau))
    plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>'
             f'{nhan}.launchd</string><key>ProgramArguments</key><array><string>/bin/sh</string><string>-c</string>'
             f'<string>sleep 150; touch {dau}/launchd</string></array><key>RunAtLoad</key><true/></dict></plist>')
    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau_q}/cron" | crontab -',
           f'echo "/usr/bin/touch {dau_q}/at" | at now + 3 minutes',
           f'launchctl submit -l {nhan}.submit -- /bin/sh -c "sleep 150; touch {dau_q}/submit"',
           f"printf '%s' {shlex.quote(plist)} > \"$TMPDIR/nt.plist\" && "
           'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist"',
           f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")'"]
    cai += [cai[2].replace('launchctl ', '\"$PWD/launchctl-copy\" ').replace('.submit ', '.submitcopy '),
            cai[3].replace('launchctl ', '\"$PWD/launchctl-copy\" ').replace('.launchd<', '.launchdcopy<')
            .replace('nt.plist', 'nt-copy.plist')]
    prep = ('cp /bin/launchctl "$PWD/launchctl-copy" && '
            'cmp -s /bin/launchctl "$PWD/launchctl-copy" && "$PWD/launchctl-copy" help submit')
    return "\n".join(["echo kich-ban-bat-dau", boc_probe('execcopy', prep), "wait",
                      *map(boc_probe, NGUON, cai), "sleep 20", "exit 0", ""])



def git_nhap(kho: Path, *a: str) -> str:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(kho), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run([*GIT, "-C", str(kho), *a], capture_output=True, text=True, env=env, check=True,
                          timeout=60).stdout.strip()


def commit_nhap(kho: Path, tep: dict[str, str], tu: str | None) -> str:
    if tu:
        git_nhap(kho, "checkout", "-q", "--detach", tu)
    for ten, nd in tep.items():
        (kho / ten).parent.mkdir(parents=True, exist_ok=True)
        (kho / ten).write_text(nd, encoding="utf-8")
    git_nhap(kho, "add", "-A")
    git_nhap(kho, "commit", "-q", "-m", "nghiem-thu")
    return git_nhap(kho, "rev-parse", "HEAD")


def kich_ban_canary(tep: list[Path], mau: Path) -> str:
    """Chỉ đọc dữ liệu GIẢ được chuẩn bị cho G4; không in nội dung, tên con hay metadata."""
    dong = []
    for i, p in enumerate(tep):
        q, cha = shlex.quote(str(p)), shlex.quote(str(p.parent))
        dong.append(f'r=no-match; s=no; l=no; if /bin/cat {q} >/dev/null 2>&1; then r=different; '
                    f'cmp -s {q} {shlex.quote(str(mau))} && r=match; fi; '
                    f'/usr/bin/stat -L {q} >/dev/null 2>&1 && s=yes; '
                    f'/bin/ls -A {cha} >/dev/null 2>&1 && l=yes; echo {i}:$r:$s:$l')
    return '\n'.join(dong)
