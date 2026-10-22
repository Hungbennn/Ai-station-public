"""B1 + C: chọn G3, nhân pytest và log chung; mọi runner con chỉ chạy suite giả trong tmp_path."""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from test_phu_thuoc_runner import runner


def chay(sh, env, *args):
    return subprocess.run([str(sh), *args], cwd=sh.parents[2], env=env,
                          capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("co_xdist,nhan,them,doi", [
    (True, None, [], ["-n", "6"]), (True, "2", ["-n", "0"], ["-n", "2", "-n", "0"]),
    (False, None, [], []),
])
def test_runner_tu_chon_nhan_va_giu_nguyen_tham_so(tmp_path, co_xdist, nhan, them, doi):
    sh, env = runner(tmp_path, co_venv=False)
    uv = tmp_path / "bin/uv"
    uv.parent.mkdir()
    ma_uv = tmp_path / "uv_gia.py"
    ma_uv.write_text('import json, os, sys\n'
                    f'if sys.argv[1:3] == ["run", "python"]: sys.exit({0 if co_xdist else 1})\n'
                    'open(os.environ["GHI_ARGV"], "w").write(json.dumps(sys.argv[1:]))\n')
    uv.write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(ma_uv))} "$@"\n')
    uv.chmod(0o755)
    env.pop("TRAM_KIEM_DA_CHUAN_BI")
    env.pop("TRAM_TEST_NHAN", None)
    env.update(PATH=f"{uv.parent}:{env['PATH']}", GHI_ARGV=str(tmp_path / "argv"))
    if nhan is not None:
        env["TRAM_TEST_NHAN"] = nhan
    r = chay(sh, env, *them, "-q", "test có dấu.py", "-k", "a or b")
    assert r.returncode == 0, r.stdout + r.stderr
    argv = json.loads((tmp_path / "argv").read_text())
    assert argv[:4] == ["run", "pytest", "-p", "chan_host"]
    assert argv[6:] == doi + ["-q", "test có dấu.py", "-k", "a or b"]


@pytest.mark.parametrize("nhan,g3,so_chay,so_bo", [("0", "0", 1, 2), ("6", "0", 1, 2), ("6", "1", 3, 0)])
def test_g3_bo_qua_mac_dinh_bat_ro_va_chi_bao_mot_lan(tmp_path, nhan, g3, so_chay, so_bo):
    sh, env = runner(tmp_path)
    env.update(TRAM_TEST_NHAN=nhan, TRAM_TEST_G3=g3)
    (tmp_path / "tests/test_nho.py").write_text('def test_nhanh(): pass\n')
    (tmp_path / "tests/test_g3_gia.py").write_text(
        'import pytest\npytestmark = pytest.mark.g3\n'
        '@pytest.mark.parametrize("n", [1, 2])\ndef test_cham(n): pass\n')
    r = chay(sh, env, "-q", "--strict-markers", "-W", "error::pytest.PytestUnknownMarkWarning")
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"{so_chay} passed" in r.stdout
    assert r.stdout.count(f"bỏ qua {so_bo} test G3") == 1, r.stdout


@pytest.mark.parametrize("loi", [False, True])
def test_sau_worker_ke_thua_bo_chan_va_gop_du_ba_nhat_ky(tmp_path, loi):
    pytest.importorskip("xdist", reason="xdist cục bộ là tuỳ chọn; lượt kiểm ghim lock có thể không cài")
    sh, env = runner(tmp_path)
    env.update(TRAM_TEST_NHAN="6", TRAM_TEST_G3="0", CO_LOI=str(int(loi)))
    (tmp_path / "tests/test_nhan.py").write_text('''import os, pathlib, shutil, subprocess, sys
import pytest
@pytest.mark.parametrize("n", range(12))
def test_con(tmp_path, request, n):
    assert os.environ["TRAM_CHAN_CHAY_SH"] == "1"
    assert os.environ["TRAM_TEST_NHAN"] == "6"
    assert shutil.which("git").endswith("/chan_host/bin/git")
    assert str(pathlib.Path.cwd() / "tests/chan_host") in os.environ["PYTHONPATH"].split(":")
    pathlib.Path("da-chay-" + request.config.workerinput["workerid"]).touch()
    # Chỉ stub vô hại; hook hỏng thì có dấu, không lệnh host thật nào chạy.
    cam = tmp_path / "sudo"
    cam.write_text("#!/bin/sh\\ntouch " + str(tmp_path / "lot") + "\\n")
    cam.chmod(0o755)
    with pytest.raises(PermissionError): subprocess.run([str(cam)], timeout=10)
    assert not (tmp_path / "lot").exists()
    env = dict(os.environ, LENH=str(pathlib.Path(shutil.which("git")).with_name("sudo")))
    assert subprocess.run(["/bin/sh", "-c", 'exec "$LENH"'], env=env, timeout=10).returncode == 97
    subprocess.run([sys.executable, "-E", "-c", "pass"], check=True, timeout=10)
    def git(*args):
        return subprocess.run(["git", *args], check=True, capture_output=True, timeout=20)
    nguon, dich = tmp_path / "nguon", tmp_path / "dich.git"
    git("init", "-q", "-b", "main", str(nguon))
    git("-C", str(nguon), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "a")
    git("init", "-q", "--bare", str(dich))
    git("-C", str(nguon), "push", str(dich), "HEAD:refs/heads/main")
    assert not (n == 0 and os.environ["CO_LOI"] == "1")
''')
    nk = Path(env["TRAM_CHAN_NHAT_KY"])
    nk.write_text("dòng cũ\n")
    r = chay(sh, env, "-q")
    assert r.returncode == 3, r.stdout + r.stderr
    assert ("11 passed" if loi else "12 passed") in r.stdout and "24 dòng mới" in r.stdout
    assert "bộ chặn): 12;" in r.stdout and "push thật): 12" in r.stdout
    assert {p.name for p in tmp_path.glob("da-chay-*")} == {f"da-chay-gw{i}" for i in range(6)}
    dong = nk.read_text().splitlines()
    assert dong[0] == "dòng cũ" and len(dong) == 25
    assert sum(d.startswith("audithook subprocess.Popen sudo ") for d in dong[1:]) == 12
    assert sum(d.startswith("path sudo ") for d in dong[1:]) == 12


def test_runner_thieu_xdist_thuc_su_chay_tuan_tu(tmp_path):
    sh, env = runner(tmp_path, co_venv=False)
    py = tmp_path / ".venv/bin/python"
    py.parent.mkdir(parents=True)
    py.write_text('#!/bin/sh\nif [ "$2" = "-c" ] && [ "$3" = "import xdist" ]; then exit 1; fi\n'
                  f'exec {shlex.quote(sys.executable)} "$@"\n')
    py.chmod(0o755)
    (tmp_path / "tests/test_nho.py").write_text('def test_nho(): pass\n')
    r = chay(sh, env, "-q", "-p", "no:xdist", "-p", "no:xdist.looponfail")
    assert r.returncode == 0 and "1 passed" in r.stdout, r.stdout + r.stderr
    assert "bringing up nodes" not in r.stdout


def test_ca_sau_file_g3_duoc_chon_bang_bien_moi_truong(tmp_path):
    goc = Path(__file__).resolve().parents[1]
    files = sorted(str(p.relative_to(goc)) for p in (goc / "tests").glob("test_g3*.py"))
    assert len(files) == 6
    env = dict(os.environ, TRAM_TEST_NHAN="0", TRAM_TEST_G3="0", TRAM_CHAN_NHAT_KY=str(tmp_path / "nk"))
    args = [str(goc / "tests/chan_host/chay.sh"), "--co", "-q", "--strict-markers", *files]
    bo = subprocess.run(args, env=env, cwd=goc, capture_output=True, text=True, timeout=30)
    assert bo.returncode == 5 and "no tests collected" in bo.stdout, bo.stdout + bo.stderr
    env["TRAM_TEST_G3"] = "1"
    kem = subprocess.run(args, env=env, cwd=goc, capture_output=True, text=True, timeout=30)
    assert kem.returncode == 0, kem.stdout + kem.stderr
    so_test = int(re.search(r"(\d+) tests collected", kem.stdout)[1])
    assert f"bỏ qua {so_test} test G3" in bo.stdout and so_test > 0
