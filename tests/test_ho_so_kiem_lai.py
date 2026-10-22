"""3C-D1 (C01, D45): mọi lệnh dưới `tram-kiem` trong MỘT lượt chạy trong hồ sơ Seatbelt cấm mặc định — chỉ ghi được
bản chép và nhà của chính lượt đó (`-D LUOT/NHA`), không tạo job launchd, không chạy công cụ lập lịch, không tạo bộ nhớ
chia sẻ, không nối dịch vụ loopback. Chỉ kiểm văn bản hồ sơ và argv — không chạy sandbox-exec/sudo (G4 chứng minh)."""
import fnmatch
import re
from pathlib import Path

from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.kiem.toolchain import bien_kiem
from tram.tho.principal import SANDBOX_EXEC
from tram.tho.quyen_kiem import HO_SO_KIEM, LICH, MACH_CHO, dong_sudoers_kiem, ho_so_tram_kiem

WT = Path("/Users/Shared/tram-kiem/g-1-ab12cd34")


def ho_so(tmp_path):
    return ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                           goc=tmp_path.resolve(), cong=[7700])


def test_cam_mac_dinh_chi_ghi_va_doc_lai_ban_chep_va_nha_cua_luot(tmp_path):
    hs, g = ho_so(tmp_path), tmp_path.resolve()
    assert hs.startswith("(version 1)\n(deny default)\n") and "(allow default)" not in hs
    luot = '(subpath (param "LUOT")) (subpath (param "NHA"))'
    ghi = [d for d in hs.splitlines() if re.search(r"\(allow [^)]*file-write", d)]
    assert ghi == [f"(allow file-write* {luot})", '(allow file-write-data file-ioctl (literal "/dev/null") '
                   '(literal "/dev/zero"))']                     # gốc chung KHÔNG ghi được — lượt khác không với tới
    d = hs.splitlines()
    assert d.index('(allow file-read*)') < d.index('(deny file-read* (subpath "/Users"))')
    assert d.index(f'(deny file-read* (subpath "{g}"))') < d.index(f"(allow file-read* {luot})")
    assert '(deny file-read* (subpath "/Users/dai-ca/.tram") (subpath "/Users/tram-tho/.tram"))' in d


def test_khong_tao_job_khong_chay_cong_cu_lap_lich_khong_ipc(tmp_path):
    hs = ho_so(tmp_path).splitlines()
    assert "(deny job-creation)" in hs and not any("job-creation" in d and "allow" in d or "ipc-" in d for d in hs)
    cam = hs.index("(deny process-exec " + " ".join(f'(literal "{x}")' for x in LICH) + ")")
    assert cam > hs.index("(allow process-exec)")                  # luật sau thắng luật trước (SBPL)
    assert {"/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/bin/launchctl", "/usr/bin/osascript"} <= set(LICH)
    tim = [d for d in hs if d.startswith("(allow mach-lookup")]
    assert tim == ["(allow mach-lookup " + " ".join(f'(global-name "{m}")' for m in MACH_CHO) + ")"]
    assert not any("SecurityServer" in m or "pasteboard" in m or "cfprefsd" in m for m in MACH_CHO)


def test_khong_mang_chi_unix_socket_trong_luot(tmp_path):
    mang = [d for d in ho_so(tmp_path).splitlines() if "network" in d]
    assert mang == ['(allow network-outbound (remote unix-socket (subpath (param "LUOT"))))']


def test_boc_luot_user_boc_moi_lenh_trong_ho_so_co_tham_so_va_nha_cua_luot():
    pk = tu_cach_ly("user:tram-kiem")
    a, n = pk.boc_luot(WT)(["/bin/rm", "-rf", str(WT)]), len(pk.boc)
    assert a[:n] == list(pk.boc) and a[n:n + 3] == [SANDBOX_EXEC, "-f", str(HO_SO_KIEM)]
    assert a[n + 3:] == ["-D", f"LUOT={WT}", "-D", f"NHA={WT}.nha", "/usr/bin/env", f"HOME={WT}.nha",
                         f"TMPDIR={WT}.nha/tmp/", *[f"{k}={v}" for k, v in bien_kiem(f"{WT}.nha").items()],
                         "/bin/rm", "-rf", str(WT)]
    assert pk.boc_lenh(["/bin/kill"]) == [*pk.boc, "/bin/kill"]


def test_boc_luot_sandbox_khong_long_hai_lan_va_khop_sudoers():
    pk = tu_cach_ly("sandbox:tram-kiem")
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="sandbox").split("SETENV: ", 1)[1]
    for a in (pk.boc_luot(WT)(["/usr/bin/tar", "-x"]), pk.boc_lenh(["/bin/kill", "-KILL", "-1"])):
        assert a.count(SANDBOX_EXEC) == 1 and fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau)
    argv = pk.boc_luot(WT)(["x"])
    i = argv.index("/usr/bin/env")
    assert argv[i - 2:i + 1] == ["-D", f"NHA={WT}.nha", "/usr/bin/env"]
    assert pk.boc_lenh(["x"])[-5:] == ["-D", "LUOT=/var/empty", "-D", "NHA=/var/empty", "x"]  # hồ sơ ghim cần tham số
