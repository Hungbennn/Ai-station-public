"""3C-D7: bộ đọc launchd của `tram-kiem` CHỈ cho định dạng đo ở G3 (máy B 18/10, 24G90). Fixture `du_lieu/launchd/`:
`user-503.txt`, `gui-503.txt` nguyên văn; `login-rut-gon.txt` = `print login/100003` (phiên GUI của người vận hành) RÚT
GỌN + khử thông tin cá nhân (bỏ khối environment, dịch vụ/tiến trình/endpoint ngoài `com.apple.*`). Ca "có job" ghép
dòng ĐO ĐƯỢC của miền login vào khung user đo được. `CongLich` dựng trực tiếp, `chay` giả, ngữ cảnh giả: không chạy
launchctl/sudo, không đọc OS."""
import re
import subprocess
from functools import partial
from pathlib import Path

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.launchd_dinh_dang import BAT_BUOC_USER, DONG_DV, tach
from tram.giao_viec.launchd_kiem import BANG_CHUNG_LOGIN, MOC_USER, doc_launchd
from tram.giao_viec.ngu_canh_kiem import NguCanh
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import launchd
from tram.kiem.cong_lich import CongLich

DL = Path(__file__).parent / "du_lieu" / "launchd"
USER, GUI, LOGIN = ((DL / t).read_text(encoding="utf-8") for t in ("user-503.txt", "gui-503.txt", "login-rut-gon.txt"))
PK = tu_cach_ly("user:tram-kiem")
NC = NguCanh("24G90", "0123456789abcdef", 503, 501, True)          # ngữ cảnh giả "đã đạt G3.9"
DV = [d for d in LOGIN.split("\n") if DONG_DV.fullmatch(d)]       # 4 dòng dịch vụ đo được (-, 0, (jt), -11)


def cong(*kq, uid=503):
    goi, con = [], list(kq)

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *con.pop(0))
    return CongLich(tuple(PK.boc_lenh([])), uid, chay), goi


def doc(c, *, nc=NC, moc=None, bang_chung=frozenset({NC}), pk=PK):
    return doc_launchd(pk, chay=c, ngu_canh=lambda ten: nc, moc=moc, bang_chung=bang_chung)


def ghep(khoa, dong, van_ban=USER):
    """Đổ dòng đo được vào khối rỗng `khoa` của `user-503.txt` (khối chưa có thì thêm trước `endpoints`)."""
    rong = f"\t{khoa} = {{\n\t}}\n"
    van_ban = van_ban if rong in van_ban else van_ban.replace("\tendpoints = {", rong + "\n\tendpoints = {")
    return van_ban.replace(rong, f"\t{khoa} = {{\n" + "".join(d + "\n" for d in dong) + "\t}\n")


def bo(khoa, van_ban=USER):
    """Xoá nguyên khoá `khoa` (dòng vô hướng, hoặc cả khối tới `\\t}` đầu tiên) khỏi `user-503.txt`."""
    i = van_ban.index(f"\n\t{khoa} = ") + 1
    j = van_ban.index("\n\t}\n", i) + 4 if van_ban[i:].split("\n", 1)[0].endswith("{") else van_ban.index("\n", i) + 1
    return van_ban[:i] + van_ban[j:]


def test_fixture_dung_ban_do_va_da_khu_thong_tin_ca_nhan():
    assert USER.startswith("user/503 = {\n\ttype = user\n\thandle = 503\n") and "\tservices = {\n\t}\n" in USER
    assert GUI == "Could not print domain: 125: Domain does not support specified action\n"
    assert "environment" not in LOGIN and "/" not in LOGIN.partition("\n")[2] and len(DV) == 4
    assert all(t.startswith("com.apple.") for t in re.findall(r"[A-Za-z]+\.[A-Za-z]+\.[\w.-]+", LOGIN))


def test_tach_doc_moi_kieu_khoi_da_do():
    k = tach(LOGIN, "gui/501")
    assert (k["type"], k["handle"], k["session"], k["properties"]) == ("login", "100003", "Aqua", "gui | gui login")
    assert len(k["services"]) == 4 and len(k["unmanaged processes"]) == 23 and k["endpoints"] == []
    u = tach(USER, "user/503")
    assert u["properties"] == "" and u["security context"] == ["\t\tuid = 503", "\t\tasid = 100172"]
    assert all(x in u for x in BAT_BUOC_USER)


@pytest.mark.parametrize("sua", [lambda s: s.replace("user/503 = {", "user/504 = {"),
                                 lambda s: s.replace("\tendpoints = {", "\tpending jobs = {\n\t}\n\tendpoints = {"),
                                 lambda s: s.replace("\tsession = Background\n", "\tsession = Background\n" * 2),
                                 lambda s: s.replace("\tservices = {\n\t}", "\tservices = {\n\n\t}"),
                                 lambda s: s.rstrip("\n").removesuffix("}"), lambda s: s.replace("\t}\n", "", 1),
                                 lambda s: s.replace("\ttype = user", "type = user"),
                                 lambda s: s.replace("\tservices = {\n\t}", "\tservices = 0"),
                                 lambda s: s.replace("\ttype = user", "\ttype = {\n\t}"),
                                 lambda s: s.replace("\thandle = 503", "\thandle = 503x"),
                                 lambda s: s.replace("\tdeath port = 0x0", "\tdeath port = 0"),
                                 lambda s: s.replace("\tcreator = launchctl[85554]", "\tcreator = launchctl")])
def test_tach_lech_bo_cuc_da_do_thi_nem(sua):
    with pytest.raises(ValueError):
        tach(sua(USER), "user/503")


def test_user_503_do_that_sach_va_khong_bao_gio_in_login():
    c, goi = cong((0, USER, ""), (125, "", GUI))
    doc(c)
    assert goi == [PK.boc_lenh(["/bin/launchctl", "print", "user/503"]), PK.boc_lenh(["/bin/launchctl", "print",
                                                                                      "gui/503"])]
    assert not any("login" in a for argv in goi for a in argv)


@pytest.mark.parametrize("khoa", BAT_BUOC_USER)
def test_thieu_khoi_hay_khoa_bat_buoc_la_khong_quan_sat_duoc(khoa):
    assert khoa not in tach(bo(khoa), "user/503")                  # tach vẫn đọc được — xet_user phải từ chối
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, bo(khoa), ""))[0])


@pytest.mark.parametrize("van_ban, khop", [
    (ghep("unmanaged processes", tach(LOGIN, "gui/501")["unmanaged processes"]), "'unmanaged processes' có 23 dòng"),
    (ghep("endpoints", ['\t\t"com.apple.tsm.portname" = {', "\t\t}"]), "'endpoints' có 2"),
    (ghep("disabled services", tach(LOGIN, "gui/501")["disabled services"]), "'disabled services' có 2"),
    (ghep("environment", ["\t\tTRAM_THU => 1"]), "'environment' có 1")])
def test_user_503_co_job_tien_trinh_hay_trang_thai_thi_nem_khong_chep_nhan(van_ban, khop):
    with pytest.raises(LoiBanChep, match=khop) as e:
        doc(cong((0, van_ban, ""))[0])
    assert "com.apple" not in str(e.value) and "TRAM_THU" not in str(e.value)


def test_dich_vu_ngoai_moc_loai_ra_chi_g3_moi_bat():
    """Đại ca 20/10: dịch vụ nền ngoài danh sách tự loại ra (cập nhật macOS sinh thêm); kịch bản G3 vẫn bắt được."""
    from tram.giao_viec.launchd_kiem import xet_user
    doc(cong((0, ghep("services", DV[:2]), ""), (125, GUI, ""))[0])
    with pytest.raises(LoiBanChep, match="2 dịch vụ"):
        xet_user(ghep("services", DV[:2]), 503, frozenset())


@pytest.mark.parametrize("sua", [lambda s: s.replace("domain.user.503", "domain.user.504"),
                                 lambda s: s.replace("bootstrap", "khac"),
                                 lambda s: s.replace("(unknown)", "khac"),
                                 lambda s: "\t\trac", lambda s: ""])
def test_task_special_ports_lech_mau_da_do_thi_dong(sua):
    cu = "\n".join(tach(USER, "user/503")["task-special ports"])
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, USER.replace(cu, sua(cu)), ""))[0])


@pytest.mark.parametrize("van_ban", [LOGIN, USER.replace("handle = 503", "handle = 504"), USER.replace(
    "Background", "Aqua"), USER.replace("uid = 503", "uid = 501"), ghep("services", ["\t\t0 - com.apple.x"]), ""])
def test_khong_phai_mien_rieng_cua_tram_kiem_hay_lech_dang_thi_nem(van_ban):
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, van_ban, ""))[0])


@pytest.mark.parametrize("kq, khop", [([(1, "", "")], "user/503: launchctl print mã 1"),
                                      ([(0, USER, ""), (0, LOGIN, "")], "có miền GUI"),
                                      ([(0, USER, ""), (125, "", "Could not print domain: 125\n")], "mã 125"),
                                      ([(0, USER, ""), (113, "", GUI)], "mã 113")])
def test_ma_thoat_hay_mien_gui_khac_ban_do_thi_nem(kq, khop):
    with pytest.raises(LoiBanChep, match=khop):
        doc(cong(*kq)[0])


def test_loi_chay_thanh_thong_bao_co_dinh():
    def treo(argv, **kw):
        raise subprocess.TimeoutExpired(["launchctl"], 120)
    with pytest.raises(LoiBanChep, match=r"không xác nhận được \(TimeoutExpired\)"):
        doc(CongLich(tuple(PK.boc_lenh([])), 503, treo))


def test_moc_may_b():
    assert set(MOC_USER) == {"24G90"} and len(MOC_USER["24G90"]) == 49    # G3.8 21:06 18/10 (D157)
    assert all(x.startswith("com.apple.") for x in MOC_USER["24G90"])
    assert BANG_CHUNG_LOGIN == frozenset()                         # G3.9 chưa đo: mọi ngữ cảnh đều đóng


@pytest.mark.parametrize("nc, khop", [(NguCanh("24G90", "0123456789abcdef", 503, 501, False), "G3.9"),
                                      (NguCanh("24G90", "fedcba9876543210", 503, 501, True), "G3.9"),
                                      (NguCanh("24G90", "0123456789abcdef", 503, 504, True), "G3.9"),
                                      (NguCanh("25A354", "0123456789abcdef", 503, 501, True), "chưa có mốc")])
def test_ngu_canh_khac_bang_chung_hay_ban_chua_co_moc_thi_nem_truoc_moi_lenh(nc, khop):
    c, goi = cong()
    with pytest.raises(LoiBanChep, match=khop):
        doc(c, nc=nc)
    with pytest.raises(LoiBanChep, match="G3.9"):
        doc(c, bang_chung=frozenset())
    with pytest.raises(LoiBanChep, match="sandbox"):
        doc(c, pk=tu_cach_ly("sandbox:tram-kiem"))
    assert goi == []


@pytest.mark.parametrize("loi", [KeyError("tram-kiem"), OSError("gethostuuid lỗi"), ValueError("plist")])
def test_khong_doc_duoc_ngu_canh_thi_nem(loi):
    def hong(ten):
        raise loi
    c, goi = cong()
    with pytest.raises(LoiBanChep, match="không xác định được ngữ cảnh"):
        doc_launchd(PK, chay=c, ngu_canh=hong, bang_chung=frozenset({NC}))
    assert goi == []


def test_uid_da_chung_minh_khac_ngu_canh_thi_nem():
    c, goi = cong(uid=504)
    with pytest.raises(LoiBanChep, match="UID đã chứng minh khác"):
        doc(c)
    assert goi == []


def test_cong_luot_dong_khi_user_503_de_lai_trang_thai(tmp_path):
    d = partial(doc, cong((0, ghep("environment", ["\t\tTRAM_THU => 1"]), ""))[0])
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[partial(launchd, PK, doc=lambda pk: d())],
                 ngu=lambda s: None)
    with pytest.raises(CongDong):
        c.mo_lai()
    assert c.trang_thai()["trang_thai"] == "dong" and "'environment' có 1" in c.trang_thai()["ly_do"]


def test_mdworker_shared_theo_mau_hep():
    from tram.giao_viec.launchd_moc import MAU_USER
    for n in ("01000000-0100", "02000000-0200", "03000000-0900"):
        assert MAU_USER.fullmatch(f"com.apple.mdworker.shared.{n}-0000-0000-000000000000")
    for la in ("com.apple.mdworker.shared.evil", "com.apple.mdworker.shared.01000000-0100-0000-0000-000000000001",
               "x.com.apple.mdworker.shared.01000000-0100-0000-0000-000000000000"):
        assert not MAU_USER.fullmatch(la)


def test_endpoint_apple_cho_qua_endpoint_la_thi_khong():
    from tram.giao_viec.launchd_moc import DONG_ENDPOINT
    assert DONG_ENDPOINT.fullmatch("\t\t0x12968b    M   A   com.apple.distributed_notifications@Uv3")
    assert DONG_ENDPOINT.fullmatch("\t\t       0    M   D   com.apple.lsd.openurl")
    assert not DONG_ENDPOINT.fullmatch("\t\t       0    M   D   vn.tram.g3b.lan.user")
    assert not DONG_ENDPOINT.fullmatch("\t\t       0    M   D   com.apple.x evil")
