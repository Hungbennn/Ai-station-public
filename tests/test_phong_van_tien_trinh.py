"""Script máy A (plan 4d 4D-3b): chạy được với python3 3.9 + `-I`, chỉ thư viện chuẩn, không `bd`/subprocess/Keychain/
mã; tiến trình thật chỉ chạm loopback bị từ chối và thư mục tạm."""
import ast
import os
import subprocess
import sys

import pytest
from phong_van_gia import THU_MUC, nhap_day_du

SCRIPT = ("nhap.py", "khach.py", "yeu_cau.py")
CAM = ("subprocess", "os.system", "Popen", '"bd"', "'bd'", "Authorization", "Tailscale-User-Login",
       "find-generic-password", "TRAM_DAI_CA_MA", "TRAM_DIEU_PHOI_MA", "ssh")


def test_script_python_3_9_khong_chu_thich_kieu_khong_goi_bd_hay_bi_mat():
    for ten in SCRIPT:
        van_ban = (THU_MUC / ten).read_text(encoding="utf-8")
        cay = ast.parse(van_ban, feature_version=(3, 9))
        for n in ast.walk(cay):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert n.returns is None and all(a.annotation is None for a in n.args.args), (ten, n.name)
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                goc = {n.module} if isinstance(n, ast.ImportFrom) else {a.name for a in n.names}
                assert {x.split(".")[0] for x in goc} <= {"argparse", "http", "json", "os", "re", "secrets", "sys",
                                                          "urllib", "pathlib", "khach", "nhap"}, (ten, goc)
        for cam in CAM:
            assert cam not in van_ban, (ten, cam)
        assert max(len(d) for d in van_ban.split("\n")) <= 120 and van_ban.count("\n") <= 120


PY_39 = "/Library/Developer/CommandLineTools/usr/bin/python3"         # python3 của macOS (3.9) nếu máy có sẵn
TRINH = [sys.executable] + ([PY_39] if os.path.exists(PY_39) else [])


def _chay(tmp_path, py, *argv):
    env = {"HOME": str(tmp_path / "home"), "PATH": "/usr/bin:/bin", "PHONG_VAN_NHAP": str(tmp_path / "nhap")}
    return subprocess.run([py, "-I", str(THU_MUC / "yeu_cau.py"), *argv], capture_output=True, text=True,
                          timeout=60, env=env, cwd=str(tmp_path))


@pytest.mark.parametrize("py", TRINH)
def test_tien_trinh_that_python_I_khong_voi_toi_tram_thi_dung_dung_ma(tmp_path, py):
    r = _chay(tmp_path, py, "moi", "--du-an", "hr-codex")
    assert r.returncode == 0 and r.stdout.startswith("NHÁP MỚI " + str(tmp_path / "nhap")) and r.stderr == ""
    p = nhap_day_du(tmp_path)
    r = _chay(tmp_path, py, "xem", str(p), "--tram", "https://127.0.0.1:9")
    assert (r.returncode, r.stdout.strip(), r.stderr) == (2, "LỖI: không với tới trạm", "")
    r = _chay(tmp_path, py, "gui", str(p), "--tram", "https://127.0.0.1:9", "--dau-xem", "0" * 16)
    assert r.returncode == 3 and r.stdout.startswith("CHƯA RÕ") and r.stderr == ""
    r = _chay(tmp_path, py, "xem", str(p))
    assert r.returncode == 2 and "TRAM_DIEU_PHOI_URL" in r.stdout
    assert not (tmp_path / "home").exists() or not any((tmp_path / "home").iterdir())
    assert os.listdir(tmp_path / "nhap") and all(x.endswith(".json") for x in os.listdir(tmp_path / "nhap"))
