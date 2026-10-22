"""bs-2bd.1.18: bộ chặn host trong repo. Mỗi đường vòng được thử bằng file giả VÔ HẠI trong tmp_path (tên `sudo`, chỉ
`touch` một dấu) — lớp chặn hỏng thì file giả chạy và để dấu, không lệnh thật nào chạy. Kho git chỉ trong tmp_path;
`git push` thật KHÔNG BAO GIỜ chạy (AGENT_RULES §11): git "thật" của bộ chặn là bản ghi từ chối mọi push."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

GOC = Path(__file__).resolve().parent / "chan_host"
LENH = ("sudo", "crontab", "at", "atq", "atrm", "batch", "launchctl", "security", "dscl", "sysadminctl", "pkill",
        "killall", "sandbox-exec", "createhomedir", "visudo", "dseditgroup", "bd", "gh")
CON = """import os, subprocess, sys
G = os.environ["GIA"]
DUONG = {
    "tuyet-doi": lambda: subprocess.run([G]),
    "os-system-giua": lambda: os.system("true; " + G),
    "sh-c": lambda: subprocess.run(["/bin/sh", "-c", G + " -l"]),
    "shell-true": lambda: subprocess.run(G, shell=True),
    "boc-env": lambda: subprocess.run(["/usr/bin/env", G]),
    "posix-spawn": lambda: os.waitpid(os.posix_spawn(G, [G], dict(os.environ)), 0),
    "python-chau": lambda: subprocess.run([sys.executable, "-c",
        "import os, subprocess\\ntry:\\n    subprocess.run([os.environ['GIA']])\\nexcept PermissionError:\\n"
        "    print('chan')"], capture_output=True, text=True).stdout.strip(),
}
try:
    kq = DUONG[sys.argv[1]]()
except PermissionError:
    print("chan")
else:
    print(kq if sys.argv[1] == "python-chau" else "LOT")
"""


def moi_truong(tmp_path, **them):
    return {**os.environ, "PYTHONPATH": str(GOC), "TRAM_CHAN_NHAT_KY": str(tmp_path / "nk.log"),
            "TRAM_CHAN_MU": str(tmp_path / "mu.log"), **them}


@pytest.fixture
def gia(tmp_path):
    g, dau = tmp_path / "sudo", tmp_path / "da-chay"
    g.write_text(f"#!/bin/sh\ntouch {dau}\n")
    g.chmod(0o755)
    return g, dau


@pytest.mark.parametrize("ten", LENH)
def test_lenh_gia_ghi_nhat_ky_va_thoat_97(tmp_path, ten):
    kq = subprocess.run(["/bin/sh", "-c", 'exec "$LENH" -l bi-mat'], capture_output=True, text=True, timeout=10,
                        env=moi_truong(tmp_path, LENH=str(GOC / "bin" / ten)))      # đường qua biến: hook ngoài không
    assert kq.returncode == 97                                                        # chặn nhầm chính lệnh giả
    assert (tmp_path / "nk.log").read_text().split()[:2] == ["path", ten]             # không chép đối số


@pytest.mark.parametrize("duong", ["tuyet-doi", "os-system-giua", "sh-c", "shell-true", "boc-env", "posix-spawn",
                                   "python-chau"])
def test_duong_vong_deu_bi_chan(tmp_path, gia, duong):
    g, dau = gia
    kq = subprocess.run([sys.executable, "-c", CON, duong], capture_output=True, text=True, timeout=60,
                        env=moi_truong(tmp_path, GIA=str(g)))                       # sitecustomize nạp bộ chặn
    assert kq.stdout.split() == ["chan"] and not dau.exists(), kq.stderr[-500:]
    assert (tmp_path / "nk.log").read_text().split()[:3][-1] == "sudo"


def test_python_con_moi_truong_sach_la_diem_mu_duoc_ghi(tmp_path):
    ma = "import subprocess, sys\nsubprocess.run([sys.executable, '-c', 'pass'], env={})\n"
    subprocess.run([sys.executable, "-c", ma], timeout=60, env=moi_truong(tmp_path), check=True)
    assert (tmp_path / "mu.log").read_text().split()[:2] == ["mu", "python-khong-mang-bo-chan"]


def git_that() -> str:
    """git thật ngoài thư mục lệnh giả — chỉ để dựng kho tạm (init/commit/đọc), KHÔNG BAO GIỜ push."""
    duong = os.pathsep.join(d for d in os.environ.get("PATH", "").split(os.pathsep)
                            if d and os.path.realpath(d) != os.path.realpath(GOC / "bin"))
    return os.environ.get("TRAM_CHAN_GIT") or shutil.which("git", path=duong)


@pytest.fixture
def kho(tmp_path):
    """Kho nguồn + kho đích trần trong gốc tạm `duoc/`, một kho trần NGOÀI gốc tạm. `git_ghi` (tên `git`) thay git
    thật cho bộ chặn: ghi mọi lời gọi; gặp `push`/`send-pack`/alias thử nghiệm → ghi PUSH-THAT, thoát 99, KHÔNG chạy —
    lớp chặn hỏng thì test thấy dấu mà không lệnh push thật nào chạy."""
    that, ghi = git_that(), tmp_path / "git-that.log"
    (tmp_path / "that").mkdir()
    git_ghi = tmp_path / "that" / "git"
    git_ghi.write_text(f'#!/bin/sh\nfor a in "$@"; do\n  case "$a" in push|send-pack|dua|alias.*) '
                       f'echo "PUSH-THAT $*" >> "{ghi}"; exit 99 ;; esac\ndone\necho "$*" >> "{ghi}"\n'
                       f'exec "{that}" "$@"\n')
    git_ghi.chmod(0o755)
    sach = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}

    def g(*a):
        return subprocess.run([that, "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True,
                              text=True, timeout=30, env={**os.environ, **sach}, check=True).stdout.strip()
    nguon = tmp_path / "duoc" / "nguon"
    nguon.mkdir(parents=True)
    g("init", "-q", "-b", "main", str(nguon))
    g("-C", str(nguon), "commit", "-q", "--allow-empty", "-m", "a")
    for b in ("duoc/dich.git", "ngoai.git"):
        g("init", "-q", "--bare", str(tmp_path / b))
    env = moi_truong(tmp_path, **{**sach, "TRAM_CHAN_GIT": str(git_ghi), "TRAM_CHAN_GOC_TAM": str(tmp_path / "duoc"),
                                  "TRAM_CHAN_GIA": str(tmp_path / "gia.log"),
                                  "PATH": f"{GOC / 'bin'}{os.pathsep}{os.environ['PATH']}"})
    return NS(g=g, nguon=nguon, dich=tmp_path / "duoc/dich.git", ngoai=tmp_path / "ngoai.git", ghi=ghi,
              git_ghi=git_ghi, tmp=tmp_path, env=env)


def qua_gia(k, *a, **them):
    return subprocess.run([str(GOC / "bin" / "git"), *a], capture_output=True, text=True, timeout=60, cwd=k.tmp,
                          env={**k.env, **them})


def khong_push_that(k):
    return "PUSH-THAT" not in (k.ghi.read_text() if k.ghi.exists() else "")


def test_git_gia_gia_lap_push_vao_kho_tam_khong_goi_push_that(kho):
    """`git push` qua lệnh giả: KHÔNG chạy `git push` thật (§11) — giả lập bằng fetch chạy TRONG kho đích tạm."""
    k, dau = kho, kho.g("-C", str(kho.nguon), "rev-parse", "HEAD")
    r = qua_gia(k, "-C", str(k.nguon), "push", "-q", str(k.dich), "HEAD:refs/heads/main")
    assert r.returncode == 0, r.stderr
    k.g("-C", str(k.nguon), "remote", "add", "origin", str(k.dich))
    assert qua_gia(k, "-C", str(k.nguon), "push", "-q", "origin", "main:refs/heads/khac").returncode == 0
    assert k.g("--git-dir", str(k.dich), "rev-parse", "main", "khac") == f"{dau}\n{dau}"
    assert khong_push_that(k) and len((k.tmp / "gia.log").read_text().splitlines()) == 2


@pytest.mark.parametrize("dang", ["gitfile", "lien-ket", "commondir"])
def test_dich_trong_goc_nhung_git_dir_o_ngoai_phai_chan(kho, dang):
    k = kho
    dich = k.tmp / "duoc" / "vo"
    dich.mkdir()
    if dang == "gitfile":
        (dich / ".git").write_text(f"gitdir: {k.ngoai}\n")
    elif dang == "lien-ket":
        (dich / ".git").symlink_to(k.ngoai, target_is_directory=True)
    else:
        k.g("--git-dir", str(k.ngoai), "fetch", str(k.nguon), "HEAD:refs/heads/main")
        k.g("--git-dir", str(k.ngoai), "worktree", "add", "--detach", str(dich), "main")
        gitdir = Path((dich / ".git").read_text().strip().removeprefix("gitdir: "))
        trong = k.tmp / "duoc" / "quan-ly-worktree"
        shutil.copytree(gitdir, trong)
        (trong / "commondir").write_text(str(k.ngoai) + "\n")
        (dich / ".git").write_text(f"gitdir: {trong}\n")
    truoc = k.g("--git-dir", str(k.ngoai), "for-each-ref")
    r = qua_gia(k, "-C", str(k.nguon), "push", str(dich), "HEAD:refs/heads/khac")
    assert r.returncode == 97 and khong_push_that(k)
    assert k.g("--git-dir", str(k.ngoai), "for-each-ref") == truoc
    assert not (k.tmp / "gia.log").exists()


def test_cong_bo_that_qua_git_gia_dung_ngu_nghia_lease(kho, monkeypatch):
    """Đường công bố thật của trạm (`tram.cong_bo.git`: --porcelain, --force-with-lease, xoá) qua lệnh giả."""
    from tram.cong_bo.git import day_cas, sha_remote, xoa_cas
    k = kho
    for ten, gt in k.env.items():
        monkeypatch.setenv(ten, gt)
    k.g("-C", str(k.nguon), "remote", "add", "origin", str(k.dich))
    c1 = k.g("-C", str(k.nguon), "rev-parse", "HEAD")
    assert day_cas(k.nguon, c1, "x", None, timeout=30) == "ok"
    assert day_cas(k.nguon, c1, "x", None, timeout=30) == "tu_choi"                    # lease: mong chưa có
    k.g("-C", str(k.nguon), "commit", "-q", "--allow-empty", "-m", "b")
    c2 = k.g("-C", str(k.nguon), "rev-parse", "HEAD")
    assert day_cas(k.nguon, c2, "x", "0" * 40, timeout=30) == "tu_choi"
    assert day_cas(k.nguon, c2, "x", c1, timeout=30) == "ok" and sha_remote(k.nguon, "x", timeout=30) == c2
    assert xoa_cas(k.nguon, "x", c1, timeout=30) == "tu_choi" and xoa_cas(k.nguon, "x", c2, timeout=30) == "ok"
    assert sha_remote(k.nguon, "x", timeout=30) is None and khong_push_that(k)
    k.g("-C", str(k.nguon), "remote", "set-url", "origin", str(k.tmp / "duoc/khong-co.git"))
    assert day_cas(k.nguon, c2, "x", None, timeout=30) == "khong_ro"                  # như git: kho không có → 128
    assert not (k.tmp / "nk.log").exists()                                              # không phải lần chặn


@pytest.mark.parametrize("dang", ["ngoai-goc-tam", "git-dir", "alias-dong-lenh", "alias-cau-hinh", "env-git-dir",
                                  "tuy-chon-la", "send-pack"])
def test_push_ra_ngoai_hay_dang_khong_gia_lap_duoc_thi_chan(kho, dang):
    k, n, them = kho, str(kho.nguon), {}
    lenh = {"ngoai-goc-tam": ["-C", n, "push", str(k.ngoai), "HEAD:refs/heads/main"],
            "git-dir": ["--git-dir", f"{n}/.git", "push", str(k.dich), "HEAD:refs/heads/main"],
            "alias-dong-lenh": ["-c", "alias.dua=push", "-C", n, "dua", str(k.dich), "HEAD:refs/heads/main"],
            "alias-cau-hinh": ["-C", n, "dua", str(k.dich), "HEAD:refs/heads/main"],
            "env-git-dir": ["push", str(k.dich), "HEAD:refs/heads/main"],
            "tuy-chon-la": ["-C", n, "push", "--mirror", str(k.dich)],
            "send-pack": ["-C", n, "send-pack", str(k.dich), "main"]}[dang]
    if dang == "alias-cau-hinh":
        k.g("-C", n, "config", "alias.dua", "push")
    if dang == "env-git-dir":
        them = {"GIT_DIR": f"{n}/.git"}
    r = qua_gia(k, *lenh, **them)
    assert r.returncode == 97 and "path git-" in (k.tmp / "nk.log").read_text() and khong_push_that(k)
    assert k.g("--git-dir", str(k.dich), "for-each-ref") == "" == k.g("--git-dir", str(k.ngoai), "for-each-ref")


CON_GIT = """import json, subprocess, sys
try:
    print(subprocess.run(json.loads(sys.argv[1]), capture_output=True).returncode)
except PermissionError:
    print("chan")
"""


@pytest.mark.parametrize("cach, ra", [("qua-gia", "0"), ("git-tuyet-doi", "chan"), ("env-boc-khong-gia", "chan"),
                                      ("alias-tuyet-doi", "chan")])
def test_python_con_git_push_chi_di_qua_git_gia(kho, cach, ra):
    """Audithook trong Python con: `git push`/alias chỉ được spawn khi `git` phân giải ra CHÍNH lệnh giả."""
    k, n, d = kho, str(kho.nguon), str(kho.dich)
    argv = {"qua-gia": ["git", "-C", n, "push", "-q", d, "HEAD:refs/heads/main"],
            "git-tuyet-doi": [str(k.git_ghi), "-C", n, "push", d, "HEAD:refs/heads/main"],
            "env-boc-khong-gia": ["/usr/bin/env", "git", "-C", n, "push", d, "HEAD:refs/heads/main"],
            "alias-tuyet-doi": [str(k.git_ghi), "-c", "alias.dua=push", "-C", n, "dua", d, "HEAD:refs/heads/main"]}
    env = {**k.env, "PATH": f"{k.git_ghi.parent}{os.pathsep}/usr/bin{os.pathsep}/bin"} if cach == "env-boc-khong-gia" \
        else k.env
    kq = subprocess.run([sys.executable, "-c", CON_GIT, json.dumps(argv[cach])], capture_output=True, text=True,
                        timeout=60, env=env)
    assert kq.stdout.split() == [ra], kq.stderr[-500:]
    assert khong_push_that(k) and (k.g("--git-dir", d, "for-each-ref") != "") == (ra == "0")


def test_git_gia_lenh_thuong_chay_thang(kho):
    k = kho
    r = qua_gia(k, "-C", str(k.nguon), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
                "-m", "push", TRAM_CHAN_GIT=git_that())                          # "push" không phải lệnh con
    assert r.returncode == 0 and qua_gia(k, "--version").returncode == 0


def test_chay_sh_bao_so_dong_moi(tmp_path):
    nk = tmp_path / "nk.log"
    nk.write_text("dòng cũ của lượt trước\n")
    kq = subprocess.run([str(GOC / "chay.sh"), "--version"], env={**os.environ, "TRAM_CHAN_NHAT_KY": str(nk)},
                        capture_output=True, text=True, timeout=120)
    assert kq.returncode == 0 and "0 dòng mới" in kq.stdout


@pytest.mark.parametrize("thieu", ["bien-runner", "plugin", "git-gia", "ca-bo"])
def test_pytest_khong_qua_chay_sh_thi_tu_choi(tmp_path, thieu):
    """D61 (bs-2bd.1.26): thiếu MỘT dấu của runner (biến `TRAM_CHAN_CHAY_SH`, plugin `chan_host`, `git` giả đầu PATH)
    → pytest thoát 4 kèm lệnh đúng, trước khi thu thập — kể cả không chỉ file (`testpaths`, "ca-bo"). `--co`: lớp chặn
    hỏng thì cũng chỉ thu thập, không chạy test."""
    env = moi_truong(tmp_path, TRAM_CHAN_CHAY_SH="1", PATH=f"{GOC / 'bin'}{os.pathsep}{os.environ['PATH']}")
    argv = [sys.executable, "-m", "pytest", "-p", "chan_host", "-p", "no:cacheprovider", "--co", "-q",
            "tests/test_chan_host.py::test_chay_sh_bao_so_dong_moi"]
    if thieu in ("bien-runner", "ca-bo"):
        del env["TRAM_CHAN_CHAY_SH"]
        argv = argv[:-1] if thieu == "ca-bo" else argv
    elif thieu == "plugin":
        argv[3:5] = []
    else:
        env["PATH"] = os.pathsep.join(d for d in env["PATH"].split(os.pathsep)
                                      if d and os.path.realpath(d) != os.path.realpath(GOC / "bin"))
    kq = subprocess.run(argv, cwd=GOC.parent.parent, env=env, capture_output=True, text=True, timeout=120)
    assert kq.returncode == 4, kq.stdout[-500:]
    assert "tests/chan_host/chay.sh -q" in kq.stdout + kq.stderr and "collected" not in kq.stdout


def test_chay_sh_van_chay_duoc_qua_cong_d61(tmp_path):
    kq = subprocess.run([str(GOC / "chay.sh"), "-p", "no:cacheprovider", "--co", "-q",
                         "tests/test_chan_host.py::test_chay_sh_bao_so_dong_moi"], cwd=GOC.parent.parent,
                        env={**os.environ, "TRAM_CHAN_NHAT_KY": str(tmp_path / "nk.log")}, capture_output=True,
                        text=True, timeout=120)
    assert kq.returncode == 0 and "1 test collected" in kq.stdout, kq.stdout[-500:]
