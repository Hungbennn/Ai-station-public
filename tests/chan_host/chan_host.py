"""Bộ chặn host cho test (bs-2bd.1.18, AGENT_RULES §11, §13) — lưới an toàn, KHÔNG phải sandbox.

Nạp vào MỌI tiến trình Python mang `PYTHONPATH` chứa thư mục này: pytest qua `-p chan_host`, Python con/cháu qua
`sitecustomize.py`. Audithook xét mọi lời spawn (`subprocess.Popen`, `os.system`, `os.exec*`, `os.posix_spawn*`,
`os.spawn*`): chặn khi BẤT KỲ đối số nào có tên cuối thuộc `CHAN` (đường tuyệt đối, bọc qua `env`/`nohup`…), khi chuỗi
lệnh của shell (`sh -c`, `shell=True`, `os.system`) chứa từ như vậy, và khi `git` đẩy / chạy alias / có tuỳ chọn chung
lạ mà KHÔNG phân giải ra lệnh giả `bin/git` (`git_chan.py`) — lệnh giả không bao giờ chạy `git push` thật: nó giả lập
(`day_gia.py`) hoặc chặn. Bị chặn → ghi `audithook <sự kiện> <tên> <test>` (không chép đối số) vào
`$TRAM_CHAN_NHAT_KY` rồi PermissionError. Điểm mù (ghi `mu …` vào `$TRAM_CHAN_MU`, không chặn): Python con chạy môi
trường dọn sạch hoặc `-I`/`-E`; chương trình không phải Python tự spawn bên trong (script, binary — kể cả hook, alias
`!`, `--exec` do chính git chạy: git đặt thư mục git-core của nó lên đầu PATH). Chạy như script:
`chan_host.py git <đối số>` — lệnh giả `bin/git` gọi khi không tự cho qua được."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from git_chan import (DAY, GIT_THAT, GOC, NHAT_KY, can_qua_gia, dung_san, ghi, la_git_gia,  # noqa: E402
                      phan_tich_git)

CHAN = frozenset({"sudo", "crontab", "at", "atq", "atrm", "batch", "launchctl", "security", "dscl", "sysadminctl",
                  "pkill", "killall", "sandbox-exec", "createhomedir", "visudo", "dseditgroup", "bd", "gh",
                  "git-send-pack", "git-http-push", "git-push"})
SHELL = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
MU = os.environ.get("TRAM_CHAN_MU") or os.devnull
_TACH = re.compile(r"[\s;&|()<>`$'\"]+")


def _ten(x) -> str:
    try:
        return os.path.basename(os.fsdecode(x))
    except (TypeError, ValueError):
        return ""


def _xet(ev: str, tu: list[str], env=None) -> None:
    if tu and _ten(tu[0]) in SHELL and "-c" in tu:
        tu = tu + _TACH.split(" ".join(tu[tu.index("-c") + 1:]))
    ten = [_ten(t) for t in tu]
    cam = next((t for t in ten if t in CHAN), None)
    for k in (k for k, t in enumerate(ten) if t == "git" and cam is None):
        if can_qua_gia(tu[k:]) and not la_git_gia(tu[k], env):
            cam = "git-push"
    if cam:
        ghi(NHAT_KY, f"audithook {ev} {cam}")
        raise PermissionError(f"chan_host: cấm spawn {cam}")
    la_python = bool(ten) and (re.fullmatch(r"python[0-9.]*", ten[0]) is not None
                               or os.path.realpath(tu[0]) == os.path.realpath(sys.executable))
    mat = env is not None and GOC not in str(env.get("PYTHONPATH", "")).split(os.pathsep)
    if la_python and (mat or "-I" in tu or "-E" in tu):
        ghi(MU, "mu python-khong-mang-bo-chan")


def _hook(ev: str, args: tuple) -> None:
    if ev == "subprocess.Popen":
        exe, argv, _, env = args
        tu = [os.fsdecode(argv)] if isinstance(argv, (str, bytes)) else [os.fsdecode(a) for a in argv]
        _xet(ev, ([os.fsdecode(exe)] if exe and _ten(exe) != _ten(tu[0]) else []) + tu, env)
    elif ev == "os.system":
        _xet(ev, ["/bin/sh", "-c", os.fsdecode(args[0])])
    elif ev in ("os.exec", "os.posix_spawn"):
        _xet(ev, [os.fsdecode(args[0]), *map(os.fsdecode, args[1])], args[2])
    elif ev == "os.spawn":
        _xet(ev, [os.fsdecode(args[1]), *map(os.fsdecode, args[2])], args[3])


sys.addaudithook(_hook)

if __name__ == "__main__" and sys.argv[1:2] == ["git"]:          # lệnh giả bin/git gọi khi không tự cho qua được
    from day_gia import gia_day
    tu = ["git", *sys.argv[2:]]
    lenh = phan_tich_git(tu)[1]
    if lenh == "push":
        sys.exit(gia_day(tu))
    if lenh is None or (lenh != "send-pack" and lenh in dung_san()):
        os.execv(GIT_THAT, [GIT_THAT, *sys.argv[2:]])
    ghi(NHAT_KY, f"path git-{'push' if lenh in DAY else 'khong-ro'}")
    sys.exit(97)
