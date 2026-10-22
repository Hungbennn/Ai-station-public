"""D157: dữ liệu giả; không sysctl, proc_pidpath hay tín hiệu thật."""
from dataclasses import replace

import pytest

from tram.kiem import ngoai_le_uid as n
from tram.kiem.cay_tien_trinh import TienTrinh

T = TienTrinh(42, 1, 42, 503, 503, 123456)


def loc(ds, path="/usr/libexec/trustd", **kw):
    args = dict(ten="tram-kiem", ban="24G90", mot=lambda pid: T, duong=lambda pid: path)
    args.update(kw)
    return n.con_uid(503, lambda: ds, **args)


@pytest.mark.parametrize("path", sorted([
    "/usr/sbin/distnoted", "/usr/libexec/trustd", "/usr/libexec/secd", "/usr/libexec/pkd",
    "/usr/libexec/lsd", "/usr/libexec/containermanagerd",
    "/System/Library/Frameworks/CoreServices.framework/Frameworks/Metadata.framework/Versions/A/Support/"
    "mdworker_shared",
    "/System/Library/Frameworks/CoreServices.framework/Frameworks/Metadata.framework/Versions/A/Support/"
    "mdbulkimport",
    "/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/CarbonCore.framework/Versions/A/"
    "XPCServices/csnameddatad.xpc/Contents/MacOS/csnameddatad",
    "/System/Library/Frameworks/NetFS.framework/Versions/A/XPCServices/PlugInLibraryService.xpc/Contents/MacOS/"
    "PlugInLibraryService",
    "/System/Library/Frameworks/Contacts.framework/Support/contactsd",
]))
@pytest.mark.parametrize("ten", ["tram-kiem", "tram-quan-kiem"])
def test_muoi_mot_duong_dan_d157_d161_da_do_duoc_mien(path, ten):
    assert loc([T], path, ten=ten) == []


@pytest.mark.parametrize("path", ["trustd", "/tmp/trustd", "/usr/libexec/trustd --fake",
                                  "/usr/libexec/trustd/", "/usr/libexec/../libexec/trustd",
                                  "/usr/libexec/trustd\n/usr/libexec/secd", "/bin/sh", "/usr/bin/python3",
                                  "/usr/local/libexec/trustd", "/SystemX/helper", "/usr/sbinX/helper",
                                  "/usr/libexecX/helper", "/System/../tmp/helper", "/System/./helper",
                                  "/System//helper", "//System/helper", "/System/", "/usr/sbin",
                                  "/System/Volumes/Data/private/tmp/helper", "/System/Volumes/Data/Users/x/a",
                                  "/System/helper\x00"])
def test_gia_ten_argv_tien_to_khong_duoc_mien(path):
    assert loc([T], path) == [T]


@pytest.mark.parametrize("t", [replace(T, ppid=2), replace(T, uid=0), replace(T, ruid=0),
                               replace(T, sinh=None)])
@pytest.mark.parametrize("ten", ["tram-kiem", "tram-quan-kiem"])
def test_sai_cha_uid_hoac_thieu_dinh_danh_van_chan(t, ten):
    assert loc([t], ten=ten) == [t]


@pytest.mark.parametrize("ten", ["tram-khe1", "tram-khe2"])
def test_d162_khe_b_cung_ap_dieu_kien_goc_apple(ten):
    assert loc([T], "/usr/sbin/distnoted", ten=ten) == []


@pytest.mark.parametrize("ten", ["tram-kiem", "tram-quan-kiem"])
@pytest.mark.parametrize("path", ["/System/Library/new-helper", "/usr/libexec/new-helper", "/usr/sbin/new-helper"])
def test_d162_quy_tac_chung_khong_liet_ke_tung_executable(ten, path):
    assert loc([T], path, ten=ten) == []


@pytest.mark.parametrize("ten", [None, "hungle", "tram-tho", "tram-khe3", "tram-kiem-gia"])
def test_khong_tu_mien_tai_khoan_khac(ten):
    assert loc([T], ten=ten, mot=lambda pid: pytest.fail("không đọc"),
               duong=lambda pid: pytest.fail("không đọc")) == [T]


def test_duong_nhan_khong_duoc_resolve_symlink_de_cho_qua(monkeypatch):
    # Kernel trả đường ở ngoài ba gốc: dù realpath của máy test nói khác cũng phải chặn.
    monkeypatch.setattr(n.os.path, "realpath", lambda path: "/usr/libexec/trustd")
    assert loc([T], "/tmp/link-to-trustd") == [T]


def test_d162_dung_uid_tai_khoan_dang_kiem_khong_viet_cung_503():
    t = replace(T, uid=712, ruid=712)
    assert n.con_uid(712, lambda: [t], ten="tram-quan-kiem", ban="24G90", mot=lambda pid: t,
                     duong=lambda pid: "/usr/libexec/new-helper") == []


@pytest.mark.parametrize("ban", ["24G91", "", "24G90\n"])
@pytest.mark.parametrize("ten", ["tram-kiem", "tram-quan-kiem"])
def test_build_khac_dong_ke_ca_bang_rong(ban, ten):
    with pytest.raises(OSError, match="đo lại"):
        loc([], ban=ban, ten=ten)


@pytest.mark.parametrize("moi", [None, replace(T, sinh=123457), replace(T, uid=0), replace(T, ppid=2)])
def test_doi_danh_tinh_giua_doc_path_tinh_la_con(moi):
    """Đo 20/10: sau kill -1 tiến trình đổi/thoát giữa hai lần đọc — còn tàn dư, vòng chờ chụp lại; không miễn."""
    anh = [T, moi]
    assert loc([T], mot=lambda pid: anh.pop(0)) == [T]


def test_loi_doc_kernel_khong_bien_thanh_sach():
    def loi(pid):
        raise OSError("denied")
    with pytest.raises(OSError):
        loc([T], duong=loi)


def test_uid_khac_khong_bi_tinh_va_khong_doc_path():
    assert loc([replace(T, uid=501, ruid=501)], duong=lambda pid: pytest.fail("không đọc")) == []


@pytest.mark.parametrize("nbytes,path", [(0, b""), (-1, b""), (4096, b"/usr/libexec/trustd"),
                                        (6, b"trustd")])
def test_libproc_loi_hoac_duong_dan_tuong_doi_dong(nbytes, path, monkeypatch):
    from types import SimpleNamespace

    def read(pid, buf, size):
        buf.value = path
        return nbytes
    monkeypatch.setattr(n.ctypes, "CDLL", lambda *a, **kw: SimpleNamespace(proc_pidpath=read))
    with pytest.raises(OSError):
        n.duong_nhan(42)


def test_libproc_doc_nguyen_van_khong_dung_argv(monkeypatch):
    from types import SimpleNamespace

    def read(pid, buf, size):
        assert pid == 42 and size == 4096
        buf.value = b"/usr/libexec/trustd"
        return len(buf.value)
    monkeypatch.setattr(n.ctypes, "CDLL", lambda *a, **kw: SimpleNamespace(proc_pidpath=read))
    assert n.duong_nhan(42) == "/usr/libexec/trustd"


def test_doi_danh_tinh_truoc_doc_khong_doc_path():
    assert loc([T], mot=lambda pid: None, duong=lambda pid: pytest.fail("không đọc")) == [T]


def test_dang_thoat_esrch_tinh_la_con_de_vong_cho_chup_lai():
    """Đo 20/10: sau kill -1, proc_pidpath trả ESRCH cho tiến trình đang thoát — còn tàn dư, không ném."""
    def thoat(pid):
        raise OSError(n.errno.ESRCH, "không đọc được executable của nhân")
    assert loc([T], duong=thoat) == [T]
