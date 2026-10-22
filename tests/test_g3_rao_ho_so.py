"""G3.11 dùng lệnh giả hoàn toàn; không sudo/launchctl/sandbox-exec thật, không đụng ~/.tram.

ps mặc định giả hoàn toàn để chạy trong sandbox Codex. Ca ps thật chỉ dành cho Claude ngoài sandbox.
"""
import json
import os
import signal
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.g3

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs/handovers/g3-rao-ho-so.sh"
FAKE = r'''
import json, os, pathlib, subprocess, sys, time
d = pathlib.Path(os.environ["G3_GIA"])
a = sys.argv[1:]; name = pathlib.Path(sys.argv[0]).name
state = d / "jobs.json"
jobs = json.loads(state.read_text()) if state.exists() else {}
def log(s):
    with (d / "commands").open("a") as f: f.write(s + "\n")
def save(): state.write_text(json.dumps(jobs))
def receipt(label):
    assert any("job|" + label + "|" in p.read_text() for p in (d / "out").glob("*.receipt"))
def lc(a, inside=False, copied=False, owner=False):
    log(f"lc inside={inside} copy={copied} owner={owner} " + " ".join(a))
    cmd = a[0]
    if cmd == 'help':
        if copied and os.getenv('R_COPY_KILL'): return 137
        return 0
    if cmd == "print":
        if os.getenv("R_PRINT_BAD"): return 1
        target = a[1]
        late = d / "late.json"
        if late.exists() and target.endswith(json.loads(late.read_text())["label"]):
            pending = json.loads(late.read_text()); pending["count"] += 1
            if pending["count"] == 5:
                jobs[pending["target"]] = pending["entry"]; save(); late.unlink()
            else: late.write_text(json.dumps(pending))
        if target in jobs:
            print(target + " = {\n pid = " + str(jobs[target]["pid"]) + "\n}"); return 0
        print("Could not find service", file=sys.stderr); return 113
    if cmd == "bootout":
        target = a[1]; receipt(target.split("/")[-1])
        assert target.startswith(("gui/501/vn.tram.g3r.", "user/503/vn.tram.g3r."))
        if os.getenv("R_RELOAD") == "always": return 0
        if os.getenv("R_RELOAD") == "once" and not (d / "reloaded").exists():
            (d / "reloaded").touch(); return 0
        jobs.pop(target, None); save(); return 0
    if cmd == "submit": label = a[2]; args = a[4:]
    else:
        import plistlib
        p = plistlib.loads(pathlib.Path(a[2]).read_bytes())
        assert p["RunAtLoad"] is True and "KeepAlive" not in p
        label = p["Label"]; args = p["ProgramArguments"]
    receipt(label)
    if inside and os.getenv("R_PAUSE") and ".m3-copy-submit" in label:
        (d / "paused").touch(); time.sleep(2)
    if inside:
        if copied and os.getenv("R_EXEC_BAD"):
            print("cannot execute: Permission denied", file=sys.stderr); return 126
        if not (copied and cmd == "submit" and os.getenv("R_LEAK")):
            print(("launchctl: " + cmd + " failed: Operation not permitted") if copied
                  else "sandbox-exec: exec failed: Operation not permitted", file=sys.stderr)
            return 5 if copied else 71
    elif not owner and (cmd != "submit" or os.getenv("R_M2_BAD")):
        print("launchctl: " + cmd + " failed: 5: Input/output error", file=sys.stderr); return 5
    import zlib
    uid = 503 if not owner and os.getenv("R_JOB_UID") == "503" else 501
    pid = 900000 + zlib.adler32(label.encode()) % 500000; start = "birth-" + label
    target = (a[1] if cmd == "bootstrap" else ("gui/501" if uid == 501 else "user/503")) + "/" + label
    entry = {"pid":pid, "uid":uid, "start":start}; jobs[target] = entry; save()
    # Fixture probe arguments: job run-ID case output-501 output-503.
    out = pathlib.Path(args[4 if uid == 501 else 5]); out.mkdir(exist_ok=True)
    (out / (args[3] + ".txt")).write_text(
        f"RUN={args[2]} CASE={args[3]} PID={pid} UID={uid} RUID={uid} GID=20 RGID=20 GROUPS=20\nSTART={start}\n")
    if inside and os.getenv("R_LEAK") == "late":
        (d / "late.json").write_text(json.dumps({"label":label, "target":target, "entry":entry, "count":0}))
        jobs.clear(); save()
        print("launchctl: submit failed: Operation not permitted", file=sys.stderr); return 5
    return 5 if inside and os.getenv("R_LEAK") == "nonzero" else 0
if name == "id": print(503 if a == ["-u", "tram-kiem"] else 501); sys.exit(0)
if name == "ps":
    if "-p" in a:
        entry = next((j for j in jobs.values() if str(j["pid"]) == a[a.index("-p")+1]), None)
        if entry is None: sys.exit(1)
        print(f'{entry["pid"]} 1 {entry["uid"]} {entry["uid"]} {entry["start"]}'); sys.exit(0)
    print(f"{os.getppid()} 1 501 501 /bin/bash")
    if os.getenv("R_STRANGER"): print("888888 1 503 503 /untrusted/process")
    sys.exit(0)
if name == "launchctl": sys.exit(lc(a, owner=True))
assert name == "sudo", name
log("sudo " + " ".join(a)); assert a[:4] == ["-n", "-H", "-u", "tram-kiem"]
a = a[4:]; inside = False
if a[0].startswith("--preserve-env="):
    assert a[1] == "--"; a = a[2:]
if a[0] == "/usr/bin/sandbox-exec":
    assert a[1:3] == ["-f", "/usr/local/tram/tram-kiem.sb"]
    assert a[3] == "-D" and a[4].startswith("LUOT=" + str(d / "goc"))
    assert a[5] == "-D" and a[6] == a[4].replace("LUOT=", "NHA=") + ".nha"
    assert a[7] == "/usr/bin/env"; a = a[8:]; inside = True
    while a and "=" in a[0] and not a[0].startswith("/"): a = a[1:]   # bỏ mọi KEY=VAL (môi trường lượt v2)
if a[0] == str(d / "launchctl") or a[0].endswith("/launchctl-copy"):
    sys.exit(lc(a[1:], inside=inside, copied=a[0].endswith("/launchctl-copy")))
if a[0].endswith("positive.sh") and a[1] == "identity":
    print("UID=503 RUID=503 GID=20 RGID=20 GROUPS=20"); sys.exit(0)
assert a[0] in ["/bin/mkdir", "/bin/rm", "/bin/chmod", "/bin/cp", "/bin/ln", "/bin/cat",
                "/usr/bin/stat", "/bin/test", "/usr/bin/tee", "/usr/bin/cmp", "/bin/bash", "/usr/bin/id"], a
if a[0] == "/usr/bin/id": print("503"); sys.exit(0)
assert all(str(d) in p for p in a[1:] if p.startswith("/") and p not in ["/bin/bash"]), a
if a[0] in ["/bin/mkdir", "/bin/cp", "/bin/rm", "/bin/ln", "/usr/bin/tee", "/bin/chmod"]:
    import re
    assert re.search(r"(?:g3r-|tram-canary-)\d+-\d+-\d+", a[-1]), a
    assert any(any(f"{k}|{a[-1]}|tk" in p.read_text() for k in ("write", "intent", "delete"))
               for p in (d / "out").glob("*.receipt")), a
if a[0] == "/bin/cp":
    import shutil
    shutil.copyfile(a[1], a[2]); sys.exit(0)
if a[0] == "/usr/bin/cmp":
    sys.exit(0 if pathlib.Path(a[-2]).read_bytes() == pathlib.Path(a[-1]).read_bytes() else 1)
if a[0] == "/bin/mkdir" and os.getenv("R_MKDIR_BROKEN"):
    subprocess.check_call(a); sys.exit(142)
sys.exit(subprocess.call(a))
'''


def setup(tmp_path, **env):
    fake = tmp_path / "fake.py"
    fake.write_text("import sys; sys.argv = sys.argv[1:]\n" + FAKE)
    for name in ("sudo", "launchctl", "ps", "id"):
        p = tmp_path / name
        p.write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(fake))} "$0" "$@"\n')
        p.chmod(0o755)
    (tmp_path / "goc").mkdir()
    (tmp_path / "home").mkdir()
    return {**os.environ, "G3_GIA": str(tmp_path), "G3_PY": sys.executable, **env}


def run(tmp_path, **env):
    r = subprocess.run(["/bin/bash", str(SCRIPT)], env=setup(tmp_path, **env),
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=100)
    return r, commands(tmp_path)


def commands(d):
    return (d / "commands").read_text() if (d / "commands").exists() else ""


def clean(d):
    assert not (d / "jobs.json").exists() or not json.loads((d / "jobs.json").read_text())
    assert not list((d / "goc").iterdir()) and not list((d / "home").iterdir())
    assert not (d / "out/g3b.khoa").exists()


def test_dat_va_argv_thuc_tu_boc_luot(tmp_path):
    r, log = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RÀO LAUNCHD ỨNG VIÊN ĐẠT" in r.stdout
    assert "ĐỌC NHÀ ĐẠI CA: ngoài hồ sơ có, trong hồ sơ có" in r.stdout
    assert "UID=501" in r.stdout and "DỌN: XONG" in r.stdout
    assert log.count("inside=True copy=True owner=False submit") == 1
    assert "sandbox-exec -f /usr/local/tram/tram-kiem.sb -D LUOT=" in log
    assert "procinfo" not in log and "sudo -n -H -u tram-kiem" in log
    clean(tmp_path)


@pytest.mark.parametrize("leak", ["1", "nonzero", "late"])
def test_lot_ban_chep_dung_khong_chay_ca_sau(tmp_path, leak):
    r, log = run(tmp_path, R_LEAK=leak)
    assert r.returncode == 4 and "LỌT" in r.stdout, r.stdout
    assert "m3-copy-gui" not in log and "m3-copy-user" not in log
    clean(tmp_path)


@pytest.mark.parametrize("env", [{"R_M2_BAD": "1"}, {"R_EXEC_BAD": "1"}])
def test_thieu_doi_chung_khong_ket_luan(tmp_path, env):
    r, _ = run(tmp_path, **env)
    assert r.returncode == 1 and "KHÔNG KẾT LUẬN" in r.stdout, r.stdout
    assert "ỨNG VIÊN ĐẠT" not in r.stdout
    clean(tmp_path)


@pytest.mark.parametrize("reload,code", [("once", 0), ("always", 3)])
def test_nap_lai_phai_don_lap_huu_han(tmp_path, reload, code):
    r, log = run(tmp_path, R_RELOAD=reload)
    assert r.returncode == code, r.stdout
    assert log.count("bootout gui/501/vn.tram.g3r.") >= 2
    if code == 0:
        clean(tmp_path)
    else:
        assert "DỌN: CHƯA XÁC NHẬN" in r.stdout
        assert list((tmp_path / "goc").iterdir()) and (tmp_path / "out/g3b.khoa").exists()


@pytest.mark.parametrize("sig,code", [(signal.SIGINT, 130), (signal.SIGTERM, 143),
                                     (signal.SIGHUP, 143), (signal.SIGALRM, 142)])
def test_ngat_giua_m3_don_receipt(tmp_path, sig, code):
    p = subprocess.Popen(["/bin/bash", str(SCRIPT)], env=setup(tmp_path, R_PAUSE="1"),
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        end = time.monotonic() + 60
        while not (tmp_path / "paused").exists():
            assert time.monotonic() < end and p.poll() is None
            time.sleep(0.02)
        p.send_signal(sig)
        out, _ = p.communicate(timeout=40)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
    assert p.returncode == code and "DỌN: XONG" in out, out
    clean(tmp_path)
    assert "m3-copy-gui" not in commands(tmp_path)
    rc = next((tmp_path / "out").glob("*.receipt")).read_text()
    assert "m3-copy-submit|trong" in rc and "delete|" in rc and "tram-canary-" in rc and ".nha|tk" in rc


def test_khoa_co_san_khong_sudo(tmp_path):
    env = setup(tmp_path)
    (tmp_path / "out/g3b.khoa").mkdir(parents=True)
    r = subprocess.run(["/bin/bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=10)
    assert r.returncode == 2 and commands(tmp_path) == "", r.stdout
    assert (tmp_path / "out/g3b.khoa").exists()


def test_tien_trinh_la_dung_truoc_lenh_ghi(tmp_path):
    r, log = run(tmp_path, R_STRANGER="1")
    assert r.returncode == 1 and "không giết" in r.stdout, r.stdout
    assert log == "" and not list((tmp_path / "goc").iterdir())


def test_khong_terminal_khong_chay():
    env = {k: v for k, v in os.environ.items() if not k.startswith("G3_")}
    r = subprocess.run(["/bin/bash", str(SCRIPT)], env=env, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 2 and "Terminal" in r.stdout


def test_uid_503_van_la_kenh_ngoai_ho_so(tmp_path):
    r, log = run(tmp_path, R_JOB_UID="503")
    assert r.returncode == 0 and "UID=503" in r.stdout, r.stdout
    assert "owner=False bootout user/503/vn.tram.g3r." in log
    clean(tmp_path)


def test_han_don_khong_ke_thua_bo_qua_alarm():
    helper = SCRIPT.with_name("g3-rao-ho-so-probe.sh")
    code = '''. "$1" --thu-vien
HET_CA=$((SECONDS+30)); HET_TONG=$((SECONDS+30)); DANG_DON=1; HET_DON=$((SECONDS+1))
trap '' ALRM
han /bin/sleep 3
echo "ma=$?"
'''
    start = time.monotonic()
    r = subprocess.run(["/bin/bash", "-c", code, "g3r-test", str(helper)], capture_output=True,
                       text=True, timeout=5)
    assert "ma=142" in r.stdout and time.monotonic() - start < 2.8, r.stdout + r.stderr


def test_het_han_tong_van_co_ngan_sach_don_rieng(tmp_path):
    helper = SCRIPT.with_name("g3-rao-ho-so-probe.sh")
    code = '''. "$1" --thu-vien
HET_CA=60; HET_TONG=0; DANG_DON=1; HET_DON=60
han /usr/bin/touch "$2"
echo "ma=$?"
'''
    marker = tmp_path / "da-don"
    r = subprocess.run(["/bin/bash", "-c", code, "g3r-test", str(helper), str(marker)],
                       capture_output=True, text=True, timeout=5)
    assert "ma=0" in r.stdout and marker.exists(), r.stdout + r.stderr


def test_ban_sao_bi_kill_van_do_canary_sau_don(tmp_path):
    r, log = run(tmp_path, R_COPY_KILL='1')
    assert r.returncode == 1, r.stdout
    assert 'shell_rc=137' in r.stdout and 'M3: CHƯA ĐO' in r.stdout
    assert 'ĐỌC NHÀ ĐẠI CA: ngoài hồ sơ có, trong hồ sơ có' in r.stdout
    assert 'm3-copy' not in log and 'ỨNG VIÊN ĐẠT' not in r.stdout
    clean(tmp_path)


def test_mkdir_tao_roi_bi_ngat_khong_duoc_bao_sach(tmp_path):
    r, _ = run(tmp_path, R_MKDIR_BROKEN="1")
    assert r.returncode == 3 and "CHƯA XÁC NHẬN intent" in r.stdout, r.stdout
    assert "DỌN: XONG" not in r.stdout and (tmp_path / "out/g3b.khoa").exists()
    assert list((tmp_path / "goc").iterdir())
