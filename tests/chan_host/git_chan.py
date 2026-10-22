"""Phần `git` của bộ chặn host (bs-2bd.1.18, AGENT_RULES §11): đọc tuỳ chọn chung như git, nhận diện lời gọi chỉ được
chạy qua lệnh giả `bin/git` (đẩy, lệnh con không dựng sẵn — alias, kể cả alias trong cấu hình kho —, tuỳ chọn chung
lạ), và kiểm `git` của một lời spawn có phân giải ra CHÍNH lệnh giả không (theo PATH của lời spawn). Dùng chung cho
audithook (`chan_host.py`) và bản đẩy giả (`day_gia.py`, đọc dạng push hẹp ở `phan_tich_day`). `ghi`: một dòng
nhật ký, không chép đối số."""
import os
import subprocess

GOC = os.path.dirname(os.path.abspath(__file__))
GIT_GIA = os.path.join(GOC, "bin", "git")
GIT_THAT = os.environ.get("TRAM_CHAN_GIT") or "/usr/bin/git"
NHAT_KY = os.environ.get("TRAM_CHAN_NHAT_KY") or os.devnull
DAY = frozenset({"push", "send-pack"})
CO_GIA_TRI = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env",
                        "--attr-source"})
CO_DON = frozenset({"-p", "-P", "--paginate", "--no-pager", "--bare", "--no-replace-objects", "--no-lazy-fetch",
                    "--no-optional-locks", "--no-advice", "--literal-pathspecs", "--glob-pathspecs",
                    "--noglob-pathspecs", "--icase-pathspecs", "--version", "-v", "--help", "-h", "--html-path",
                    "--man-path", "--info-path", "--exec-path"})
CO_PUSH = {"-q", "--quiet", "--porcelain", "-f", "--force", "--no-verify"}
ENV_KHO = ("GIT_DIR", "GIT_WORK_TREE", "GIT_NAMESPACE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
           "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_INDEX_FILE")
_dung_san: frozenset | None = None


class KhongGiaLap(Exception):
    pass


def ghi(tep: str, dong: str) -> None:
    # Một write với O_APPEND: các worker/Python con dùng chung log không ghi đè hay xé dòng nhau.
    fd = os.open(tep, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, f"{dong} {os.environ.get('PYTEST_CURRENT_TEST', '-')}\n".encode("utf-8"))
    finally:
        os.close(fd)


def phan_tich_git(tu: list[str]) -> tuple[list[tuple[str, str | None]], str | None, list[str]]:
    """(tuỳ chọn chung, lệnh con, đối số sau lệnh con) của `git …`; tuỳ chọn chung lạ → lệnh con "?"."""
    i, chung = 1, []
    while i < len(tu):
        a, k = tu[i], tu[i].split("=", 1)[0]
        if a in CO_GIA_TRI:
            if i + 1 >= len(tu):
                return chung, "?", []
            chung.append((a, tu[i + 1]))
            i += 2
        elif a.startswith("--") and "=" in a and k in CO_GIA_TRI | {"--exec-path", "--list-cmds"}:
            chung.append((k, a.split("=", 1)[1]))
            i += 1
        elif a in CO_DON:
            chung.append((a, None))
            i += 1
        elif a.startswith("-"):
            return chung, "?", tu[i:]
        else:
            return chung, a, tu[i + 1:]
    return chung, None, []


def dung_san() -> frozenset:
    """Lệnh con dựng sẵn của git (alias không đè được tên dựng sẵn), trừ đẩy; `chay.sh` đọc sẵn một lần vào
    `TRAM_CHAN_DUNG_SAN`. Không đọc được → rỗng: mọi lệnh con đều phải qua lệnh giả."""
    global _dung_san
    if _dung_san is None and os.environ.get("TRAM_CHAN_DUNG_SAN"):
        _dung_san = frozenset(os.environ["TRAM_CHAN_DUNG_SAN"].split()) - DAY
    if _dung_san is None:
        try:
            kq = subprocess.run([GIT_THAT, "--list-cmds=builtins"], capture_output=True, text=True, timeout=10)
            _dung_san = frozenset(kq.stdout.split()) - DAY if kq.returncode == 0 else frozenset()
        except (OSError, subprocess.SubprocessError):
            _dung_san = frozenset()
    return _dung_san


def can_qua_gia(tu: list[str]) -> bool:
    """Lời gọi git này chỉ được chạy qua lệnh giả: đẩy, alias/lệnh lạ, tuỳ chọn chung lạ."""
    lenh = phan_tich_git(tu)[1]
    return lenh is not None and (lenh in DAY or lenh not in dung_san())


def la_git_gia(x: str, env) -> bool:
    if os.sep in x:
        return os.path.realpath(x) == os.path.realpath(GIT_GIA)
    path = (env if env is not None else os.environ).get("PATH", os.defpath)
    for d in os.fsdecode(path).split(os.pathsep):
        p = os.path.join(d or ".", x)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return os.path.realpath(p) == os.path.realpath(GIT_GIA)
    return False


def phan_tich_day(tu: list[str]) -> tuple[str, list[str], dict, set, list[str], str]:
    """(kho nguồn, `-c` cho lệnh đọc, lease, tuỳ chọn, refspec, kho đích) của dạng push hẹp; khác → `KhongGiaLap`."""
    chung, lenh, sau = phan_tich_git(tu)
    if lenh != "push" or any(k not in ("-C", "-c") for k, _ in chung) or any(os.environ.get(e) for e in ENV_KHO):
        raise KhongGiaLap
    nguon, co = os.getcwd(), [x for k, v in chung if k == "-c" for x in ("-c", v)]
    for k, v in chung:
        nguon = os.path.join(nguon, v) if k == "-C" else nguon
    lease, tuy, vt = {}, set(), [a for a in sau if not a.startswith("-")]
    for a in (a for a in sau if a.startswith("-")):
        if a.startswith("--force-with-lease=") and ":" in a:
            ref, sha = a.split("=", 1)[1].split(":", 1)
            lease[ref if ref.startswith("refs/") else f"refs/heads/{ref}"] = sha or None
        elif a in CO_PUSH:
            tuy.add(a)
        else:
            raise KhongGiaLap
    if len(vt) < 2 or any(":" not in r for r in vt[1:]):
        raise KhongGiaLap
    return nguon, co, lease, tuy, vt[1:], vt[0]
