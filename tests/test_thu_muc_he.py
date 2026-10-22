"""Phần còn giữ của r47 T11 (C01 hàng 6; dot6-Q01): dọn `DARWIN_USER_*` của `tram-kiem` dưới chính nó rồi xác nhận
rỗng — MÃ LỖI của getconf/xoá/xác nhận đều chặn, kể cả khi stdout trông hợp lệ hay rỗng. Runner giả, không sudo."""
import subprocess

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import thu_hoi_theo_uid
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.thu_muc_he import THU_MUC_HE, don_thu_muc_he
from tram.kiem.cong_lich import CongLich

PK = tu_cach_ly("user:tram-kiem")
GOC = "/private/var/folders/ab/xyz/"


KHO = "com.apple.LaunchServices.dv"


def gia(hong=None, duong=GOC, muc=("rac",), kho=(KHO,), con_lai=(), loi_rm=""):
    """Máy giả: mỗi thư mục DARWIN_USER_* có `muc` thường + `kho` của Apple (`com.apple.*`, không được đụng)."""
    goi, fs = [], {}

    def chay(argv, **kw):
        goi.append(argv)
        assert argv[:len(PK.boc)] == list(PK.boc) and kw == {"capture_output": True, "text": True, "timeout": 120}
        x = argv[len(PK.boc):]
        if x[0] == "/usr/bin/getconf":
            p = duong + {"DARWIN_USER_DIR": "0/", "DARWIN_USER_TEMP_DIR": "T/"}.get(x[-1], "C/")
            fs.setdefault(p.rstrip("/"), set(muc) | set(kho))   # getconf vẫn in đường dẫn hợp lệ dù mã lỗi
            return subprocess.CompletedProcess(argv, int(hong == "getconf"), p, "")
        if x[:2] == ["/bin/ls", "-1A"]:
            ds = sorted(fs[x[2]]) + list(con_lai)
            return subprocess.CompletedProcess(argv, int(hong == "ls"), "".join(d + "\n" for d in ds), "")
        if x[0] in ("/usr/bin/chflags", "/bin/chmod"):
            assert all(not q.rsplit("/", 1)[1].startswith("com.apple.") for q in x[4:])
            return subprocess.CompletedProcess(argv, int(hong == "khoa"), "", "")
        assert x[:3] == ["/bin/rm", "-rf", "--"]
        for q in x[3:]:
            d, t = q.rsplit("/", 1)
            assert not t.startswith("com.apple.")               # không bao giờ đụng đồ của Apple
            fs[d].discard(t)
        return subprocess.CompletedProcess(argv, int(hong == "rm"), "", loi_rm)
    return goi, chay


def test_don_ba_thu_muc_bo_qua_do_cua_apple():
    goi, chay = gia(kho=(KHO, "com.apple.aned", "com.apple.xyz"))
    don_thu_muc_he(PK, chay)
    x = [a[len(PK.boc):] for a in goi]
    assert [a[-1] for a in x if a[0] == "/usr/bin/getconf"] == list(THU_MUC_HE)
    assert ["/usr/bin/chflags", "-R", "nouchg,nouappnd", "--", GOC + "0/rac"] in x
    assert ["/bin/chmod", "-R", "u+rwX", "--", GOC + "0/rac"] in x
    assert ["/bin/rm", "-rf", "--", GOC + "0/rac"] in x


def test_chi_con_do_apple_thi_khong_goi_rm():
    goi, chay = gia(muc=())
    don_thu_muc_he(PK, chay)
    assert not [a for a in goi if a[len(PK.boc)] in ("/bin/rm", "/bin/chmod", "/usr/bin/chflags")]


def test_go_co_quyen_loi_khong_chan_rm_va_liet_ke_lai_quyet():
    don_thu_muc_he(PK, gia("khoa")[1])


def test_rm_loi_bao_kem_stderr():
    with pytest.raises(LoiBanChep, match="Permission denied"):
        don_thu_muc_he(PK, gia("rm", loi_rm="rm: /x/T/a/b: Permission denied\n")[1])


@pytest.mark.parametrize("hong", ["getconf", "ls", "rm"])
def test_lenh_loi_stdout_hop_le_hay_rong_khong_duoc_coi_la_da_don(hong):
    with pytest.raises(LoiBanChep):
        don_thu_muc_he(PK, gia(hong)[1])


@pytest.mark.parametrize("sai", [{"duong": "/tmp/x/"}, {"duong": "/private/var/folders/../../etc/"},
                                 {"duong": "/var/folders/ab/"}, {"con_lai": ("rac2",)}])
def test_duong_dan_la_hoac_con_muc_thi_nem(sai):
    with pytest.raises(LoiBanChep):
        don_thu_muc_he(PK, gia(**sai)[1])


def test_loi_cua_cong_lich_thanh_loi_ban_chep_va_sandbox_bo_qua():
    def treo(argv, **kw):
        raise subprocess.TimeoutExpired(["sudo"], 120)
    with pytest.raises(LoiBanChep, match="TimeoutExpired"):
        don_thu_muc_he(PK, treo)
    goi, chay = gia()
    don_thu_muc_he(tu_cach_ly("sandbox:tram-kiem"), chay)          # hồ sơ ghim cấm ghi ở đây cho mọi lệnh
    assert goi == []


def test_thu_hoi_theo_uid_mac_dinh_don_qua_cung_cong_lich():
    goi, chay = gia()
    giet = []

    def chay_cong(argv, **kw):
        return giet.append(argv) or subprocess.CompletedProcess(argv, 0) if argv[-1] == "-1" else chay(argv, **kw)
    thu_hoi_theo_uid(PK, mo_cong=lambda t, b, k: CongLich(tuple(b([])), 777, chay_cong), cho_het=lambda uid: None)
    assert giet == [PK.boc_lenh(["/bin/kill", "-KILL", "-1"])] and len(goi) == 18
