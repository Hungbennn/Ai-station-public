"""Dừng memory service an toàn (bs-hpc.13): SIGTERM của launchd và ngày bảo trì ghi bền."""
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from test_nho_tien_trinh import DEM_VN, mt
from tram.nho.tien_trinh import vong_nap


def test_hai_lan_khoi_dong_cung_ngay_chi_bao_tri_mot_lan(tmp_path):
    nc, dv = mt(tmp_path / "nho")
    for gio in (21, 22):                                   # 04:30 rồi 05:30 giờ VN ngày 14 — hai tiến trình nối nhau
        dung = threading.Event()

        def dong_ho(gio=gio):
            dung.set()
            return DEM_VN.replace(hour=gio)
        vong_nap(nc, dv, dung=dung, thu_muc=tmp_path / "nho", dich=tmp_path / "sl", chu_ky=0, dong_ho=dong_ho)
    assert [p.name for p in (tmp_path / "sl").iterdir()] == ["nho-20261013-213000"]


CON = """
import sys, threading
import uvicorn
from nho_gia import ky_uc
from test_nho_tien_trinh import mt
from tram.nho.khoa import khoa_dich_vu, thu_muc_nho
from tram.nho.tien_trinh import chay_dich_vu
nc, dv = mt(thu_muc_nho())
nc.kho.them(ky_uc("m-1", vector=nc.embedder.embed(["1"])[0]))
dv.dem_dung.ghi_nhan(["m-1", "m-1"])
def http(app, **kw):
    print("san-sang", flush=True)
    uvicorn.run(app, **kw)
ma = chay_dich_vu(cong=0, tao=lambda: (nc, dv), chay_http=http, dich=thu_muc_nho().parent / "sl")
print("nap-con-chay", any(t.name == "nap-ky-uc" for t in threading.enumerate()))
with khoa_dich_vu(thu_muc_nho()) as duoc:
    print("khoa-nha", duoc)
print("so-lan-dung", nc.kho.lay(["m-1"])["m-1"].so_lan_dung)
sys.exit(ma)
"""


def test_sigterm_thoat_0_chay_finally_xa_bo_dem(tram_home_tam):
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(Path(__file__).parent), os.environ.get("PYTHONPATH", "")])}
    p = subprocess.Popen([sys.executable, "-c", CON], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    try:
        assert p.stdout.readline().strip() == "san-sang"
        time.sleep(1.5)                                    # để uvicorn cài bộ bắt tín hiệu và mở cổng
        p.send_signal(signal.SIGTERM)
        ra, loi = p.communicate(timeout=30)
    finally:
        p.kill()
    assert p.returncode == 0, loi[-2000:]
    assert ra.split("\n")[:3] == ["nap-con-chay False", "khoa-nha True", "so-lan-dung 2"]
