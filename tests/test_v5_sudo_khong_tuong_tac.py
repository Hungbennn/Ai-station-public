import subprocess

import pytest

from test_kiem_cong import cau_hinh
from tram.chu.kiem_cach_ly import kiem_cach_ly
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.khach import DichKiemAm
from tram.tho.kiem_am import ThamDo, chay_tham_do
from tram.tho.kiem_cong import cach_ly, dang_nhap
from tram.tho.principal import doc_principal


def kiem_loi(chuoi):
    assert "sudo -v" in chuoi and "Terminal" in chuoi
    assert "Nếu sudo cần mật khẩu" in chuoi and "GIA_LAP_KHONG_DUOC_IN" not in chuoi


def cam(*a, **kw):
    pytest.fail("không được chạy tiếp sau lỗi UID")


@pytest.mark.parametrize("loi", [LoiDanhTinh, LoiThuHoi])
def test_uid_loi_huong_dan_va_khong_chay_tiep(tmp_path, tram_home_tam, loi):
    def xm(*a):
        raise loi("GIA_LAP_KHONG_DUOC_IN")
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    muc, ly = dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, xac_minh=xm, chay=cam)
    assert muc == "do"
    kiem_loi(ly)
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, xac_minh=xm, chay_td=cam, chup=cam,
                 dich=lambda: DichKiemAm("dai-ca@x", "b.ts.net", ()))
    assert len(ra) == 1 and ra[0].muc_do == "do"
    kiem_loi(ra[0].chi_tiet)
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {tram_kiem: user:tram-kiem}\n")
    van_ban, ma = kiem_cach_ly([], xac_minh=xm, chay_td=cam)
    assert ma == 1
    kiem_loi(van_ban)


@pytest.mark.parametrize("ket", [0, 1, OSError, LoiThuHoi])
def test_lenh_trang_thai_khong_nhan_mat_khau(tmp_path, ket):
    goi = []
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    def chay(argv, **kw):
        goi.append((argv, kw))
        if isinstance(ket, type):
            raise ket("GIA_LAP_KHONG_DUOC_IN")
        return subprocess.CompletedProcess(argv, ket, '{"loggedIn":true,"email":"GIA_LAP_KHONG_DUOC_IN"}',
                                           "GIA_LAP_KHONG_DUOC_IN")
    muc, ly = dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)
    assert muc == ("xanh" if ket == 0 else "do")
    argv, kw = goi[0]
    assert len(goi) == 1 and argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"]
    assert kw["timeout"] == 30 and kw["kill"].__self__.user == "tram-k-1"
    assert set(kw["env"]) == {"PATH", "LANG", "CLAUDE_CONFIG_DIR"}
    assert "input" not in kw and "stdin" not in kw and "-S" not in argv
    if ket == 0:
        assert "sudo -v" not in ly and "GIA_LAP_KHONG_DUOC_IN" not in ly
    else:
        kiem_loi(ly)


def test_sudo_tu_choi_tham_do_duong_khong_thanh_bi_chan():
    goi = []
    p = doc_principal("user:tram-k-1")
    def chay(argv, **kw):
        goi.append((argv, kw))
        return subprocess.CompletedProcess(argv, 1, "GIA_LAP_KHONG_DUOC_IN", "sudo: a password is required")
    ds = [ThamDo("âm", ["/bin/cat", "gia"], "doc"), ThamDo("dương", ["/usr/bin/true"], "ok")]
    ra = chay_tham_do(ds, boc=p.boc, env={"PATH": "/bin", "LANG": "C.UTF-8"}, kill=p.kill_nhom, chay=chay)
    assert len(goi) == 1 and goi[0][0][-1] == "/usr/bin/true"
    assert goi[0][0][:2] == ["/usr/bin/sudo", "-n"] and goi[0][1]["timeout"] == 30
    assert goi[0][1]["kill"].__self__ is p and all(not r.dat for r in ra)
    kiem_loi(ra[1].chi_tiet)
    assert "không kết luận" in ra[0].chi_tiet and "GIA_LAP_KHONG_DUOC_IN" not in repr(ra)
