"""Primitive kiểm principal nội bộ (lát 3c; 3C-D6, hợp đồng P1 H7): dưới khoá, chỉ khi cổng chưa đóng; danh
tính bằng UID thực (sai → không probe nào chạy dưới `tram-kiem`, cổng đóng); thu hồi trước + sau; mọi probe qua
`boc_luot` của một lượt tạm (cả hai cơ chế), kể cả "hồ sơ chặn ghi ngoài lượt"; "dừng được" xanh khi `het_gio and
da_thu_hoi`, không luồng + join. Ca đóng cổng/không probe: `test_kiem_principal_dong.py`. Không sudo thật:
`chay`/`chay_lenh`/`xac_minh`/`thu_hoi` giả; mkdir/touch/rm chạy thật trong `tmp_path`."""
import os
import subprocess
import threading
from pathlib import Path

import pytest

from tram.giao_viec.cong_that import dung_cong
from tram.giao_viec.kiem_principal import kiem_principal
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.kiem.chay_lenh import KetQuaLenh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
SB = "/usr/bin/sandbox-exec"


def chay_gia(env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, ho_so=True, goi=None, pk=PK,
             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"):
    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`. Lệnh qua
    `boc_luot` (3C-D6, cả hai cơ chế): bỏ tiền tố + `-D LUOT/NHA` + `env HOME= TMPDIR=`; `ho_so` = hồ sơ chặn ghi ngoài
    `LUOT`/`NHA`."""
    goi = [] if goi is None else goi

    def chay(argv, **kw):
        goi.append(list(argv))
        lenh, cho = (argv[len(pk.boc):] if argv[:len(pk.boc)] == list(pk.boc) else list(argv)), None
        if "-D" in lenh and "/usr/bin/env" in lenh:
            cho = [Path(x.split("=", 1)[1]) for i, x in enumerate(lenh) if i and lenh[i - 1] == "-D"]
            lenh = lenh[lenh.index("/usr/bin/env") + 1:]
            while lenh and "=" in lenh[0]:
                lenh = lenh[1:]
        if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
            cam = ho_so and cho is not None and not all(any(Path(x).is_relative_to(c) for c in cho)
                                                        for x in lenh[1:] if x[0] == "/")
            return subprocess.run(lenh if ghi_duoc and not cam else ["/usr/bin/false"], capture_output=True, text=True)
        ra = {"/usr/bin/env": (0, env), "/bin/ls": (0 if doc_duoc else 1, ""), "/usr/bin/sudo": (0, sudo_l)}[lenh[0]]
        return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
    return chay


def dung_lenh(het_gio=True, da_thu_hoi=True, goi=None):
    def chay_lenh(lenh, argv, **kw):
        (goi if goi is not None else []).append((threading.current_thread(), kw["boc"](["/bin/sleep"])))
        return KetQuaLenh(lenh, "fail", "", "sha256:0", None, het_gio, da_thu_hoi)
    return chay_lenh


def kiem(tmp_path, *, chay=None, chay_lenh=None, xac_minh=lambda ten, boc, kill: 777, thu_hoi=lambda: None, pk=PK,
         **kw):
    return kiem_principal(pk, tmp_path, chay=chay or chay_gia(pk=pk), xac_minh=xac_minh,
                          chay_lenh=chay_lenh or dung_lenh(), thu_hoi=thu_hoi, uid_cua=lambda ten: os.getuid(), **kw)


def cong_tt():
    return dung_cong(PK, None, cac_du_an=list).trang_thai()["trang_thai"]


def muc(ds):
    return {m.muc: m.muc_do for m in ds}


@pytest.mark.parametrize("pk", [PK, tu_cach_ly("sandbox:tram-kiem")], ids=["user", "sandbox"])
def test_principal_dat_moi_muc_qua_luot_tam_duoi_khoa(tmp_path, pk):
    (tmp_path / "quyen").mkdir()
    for v in ("coder", "qc"):
        (tmp_path / "quyen" / f"{v}.json").write_text("{}")
    goi, lenh, thu = [], [], []
    ds = kiem(tmp_path, pk=pk, chay=chay_gia(goi=goi, pk=pk), chay_lenh=dung_lenh(goi=lenh),
              thu_hoi=lambda: thu.append(1))
    assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0 and thu == [1, 1]   # trước + sau probe
    assert sorted(p.name for p in tmp_path.iterdir()) == ["quyen", "tram-home"]          # lượt tạm đã dọn
    assert len([a for a in goi if "-D" in a]) == 8 and all("-D" in b for _, b in lenh)    # mọi probe qua boc_luot
    assert lenh[0][0] is threading.main_thread() and cong_tt() == "chua-mo"               # H7: không luồng + join


@pytest.mark.parametrize("sai, muc_do", [
    ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"), ({"doc_duoc": True}, "principal: không đọc kho trạm"),
    ({"ghi_duoc": False}, "principal: lượt tạm"), ({"ho_so": False}, "principal: hồ sơ chặn ghi ngoài lượt"),
    ({"sudo_l": "    (root) NOPASSWD: /usr/local/x\n"}, "principal: sudoers không NOPASSWD root")])
def test_principal_sai_tung_muc_la_do_va_van_don(tmp_path, sai, muc_do):
    m = muc(kiem(tmp_path, chay=chay_gia(**sai)))
    assert m[muc_do] == "do" and not list(tmp_path.glob("tram-giao-kiem-thu*"))
    assert cong_tt() == ("chua-mo" if "sudoers" in muc_do else "dong")        # probe đỏ → cổng đóng


def test_sudo_l_khong_thu_hoi_duoc_la_do_khong_vo(tmp_path):
    def chay(argv, **kw):
        if argv[0] == "/usr/bin/sudo" and argv[1:] == ["-n", "-l"]:
            raise LoiThuHoi("['sudo']: không xác nhận thu hồi cây tiến trình")
        return chay_gia()(argv, **kw)
    assert muc(kiem(tmp_path, chay=chay))["principal: sudoers không NOPASSWD root"] == "do"
