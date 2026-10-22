"""`git push` GIẢ của bộ chặn host (bs-2bd.1.18, AGENT_RULES §11): KHÔNG BAO GIỜ chạy `git push` thật.

Giả lập dạng hẹp test và mã trạm dùng — `git [-C d]… [-c k=v]… push [-q|--quiet|--porcelain|-f|--force|
--force-with-lease=<ref>:<sha>|--no-verify]… <kho|remote> [+]<nguồn>:<đích>…` — vào kho cục bộ TRONG
`TRAM_CHAN_GOC_TAM`: đọc SHA ở kho nguồn → kiểm lease/fast-forward/nhánh đang checkout → `fetch` chạy TRONG kho đích →
`update-ref <đích> <mới> <cũ>`; in như git ở chỗ trạm đọc (`[rejected]`, `stale info`, mã 1). Không chạy hook phía
nhận. Dạng khác, `GIT_DIR`…, URL mạng, đích ngoài gốc tạm → `path git-push`, thoát 97; đích trong gốc tạm mà không
phải kho → lỗi như git (128). Mỗi lần giả lập ghi `gia-push` vào `$TRAM_CHAN_GIA`."""
import os
import re
import subprocess
import sys

from git_chan import GIT_THAT, NHAT_KY, KhongGiaLap, ghi, phan_tich_day

KHONG = "0" * 40


class KhongCoKho(Exception):
    pass


def _git(*a: str, kho: str, co: list[str] = ()) -> subprocess.CompletedProcess:
    return subprocess.run([GIT_THAT, *co, "-C", kho, *a], capture_output=True, text=True, timeout=60)


def _sha(kho: str, ref: str, co: list[str] = ()) -> str | None:
    kq = _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", kho=kho, co=co)
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def _dich(nguon: str, co: list[str], kho: str) -> str:
    url = kho
    if "/" not in kho and not kho.startswith("."):
        kq = _git("remote", "get-url", "--push", "--all", kho, kho=nguon, co=co)
        ds = kq.stdout.split()
        if kq.returncode != 0 or len(ds) != 1:
            raise KhongGiaLap
        url = ds[0]
    url = url.removeprefix("file://")
    if "://" in url or re.match(r"^[^/]+@[^/]+:", url):
        raise KhongGiaLap
    that = os.path.realpath(os.path.join(nguon, url))
    goc = os.path.realpath(os.environ.get("TRAM_CHAN_GOC_TAM") or os.environ.get("TMPDIR") or "/tmp")
    if not that.startswith(goc.rstrip("/") + "/"):
        raise KhongGiaLap
    if not os.path.isdir(that) or _git("rev-parse", "--git-dir", kho=that).returncode != 0:
        raise KhongCoKho(url)
    # Worktree trong gốc tạm chưa đủ: gitfile/commondir có thể trỏ ra kho thật bên ngoài.
    for co_dd in ("--absolute-git-dir", "--git-common-dir"):
        kq = _git("rev-parse", co_dd, kho=that)
        dd = os.path.realpath(os.path.join(that, kq.stdout.strip()))
        if kq.returncode or not kq.stdout.strip() or not dd.startswith(goc.rstrip("/") + "/"):
            raise KhongGiaLap
    return that


def _mot_ref(nguon: str, co: list[str], dich: str, rs: str, lease: dict, ep: bool) -> tuple[str, str, bool]:
    """(cờ porcelain, tóm tắt, bị từ chối) cho một refspec."""
    ep, (src, dst) = ep or rs.startswith("+"), rs.lstrip("+").split(":", 1)
    dst = dst if dst.startswith("refs/") else f"refs/heads/{dst}"
    moi, cu = (_sha(nguon, src, co) if src else None), _sha(dich, dst)
    if src and moi is None:
        raise KhongGiaLap
    if dst in lease and lease[dst] != cu:
        return "!", "[rejected] (stale info)", True
    if not moi and not cu:
        return "!", "[remote rejected] (remote ref does not exist)", True
    if moi == cu:
        return "=", "[up to date]", False
    if moi and _git("rev-parse", "--is-bare-repository", kho=dich).stdout.strip() != "true" and \
            _git("symbolic-ref", "-q", "HEAD", kho=dich).stdout.strip() == dst:
        return "!", "[remote rejected] (branch is currently checked out)", True
    if moi and _git("-c", "uploadpack.allowAnySHA1InWant=true", "fetch", "--no-tags", "--quiet",
                    "--no-write-fetch-head", nguon, moi, kho=dich).returncode != 0:
        return "!", "[remote rejected] (fetch failed)", True
    if moi and cu and not ep and dst not in lease and \
            _git("merge-base", "--is-ancestor", cu, moi, kho=dich).returncode != 0:
        return "!", "[rejected] (non-fast-forward)", True
    doi = ["update-ref", dst, moi, cu or KHONG] if moi else ["update-ref", "-d", dst, cu or KHONG]
    if _git(*doi, kho=dich).returncode != 0:
        return "!", "[remote rejected] (failed to update ref)", True
    if not moi:
        return "-", "[deleted]", False
    return ("*", "[new branch]", False) if not cu else ("+" if ep else " ", f"{cu[:7]}..{moi[:7]}", False)


def gia_day(tu: list[str]) -> int:
    try:
        nguon, co, lease, tuy, refspec, kho = phan_tich_day(tu)
        dich = _dich(nguon, co, kho)
        kq = [(rs, *_mot_ref(nguon, co, dich, rs, lease, bool(tuy & {"-f", "--force"}))) for rs in refspec]
    except KhongCoKho as e:
        print(f"fatal: '{e}' does not appear to be a git repository\nfatal: Could not read from remote repository.",
              file=sys.stderr)
        return 128
    except (KhongGiaLap, OSError, subprocess.SubprocessError):
        ghi(NHAT_KY, "path git-push")
        return 97
    ghi(os.environ.get("TRAM_CHAN_GIA") or os.devnull, "gia-push")
    dong = [f"{c}\t{rs.lstrip('+')}\t{tt}" for rs, c, tt, _ in kq]
    if "--porcelain" in tuy:
        print("\n".join([f"To {dich}", *dong, "Done"]))
    elif any(tc for *_, tc in kq) or not tuy & {"-q", "--quiet"}:
        print("\n".join([f"To {dich}", *dong]), file=sys.stderr)
    if any(tc for *_, tc in kq):
        print(f"error: failed to push some refs to '{dich}'", file=sys.stderr)
        return 1
    return 0
