"""Review vòng 1 A04: mỗi loại thăm dò một bằng chứng riêng; lỗi hạ tầng (curl 7/28 + `000`, thiếu công cụ 127, 404/500,
mục tiêu không tồn tại, mã chưa phân loại) KHÔNG BAO GIỜ là "bị chặn"; kết quả chỉ mang lý do cố định — không chép
stdout/stderr (có thể chứa bí mật). Chạy và đối chứng GIẢ (CompletedProcess dựng tay) — không spawn, không Keychain."""
import subprocess

import pytest

from tram.kiem.vong_doi import kill_cuc_bo
from tram.tho.cham_tham_do import co_muc_keychain, mo_cong
from tram.tho.kiem_am import ThamDo, chay_tham_do, tham_do_day_du, tham_do_khe

BI_MAT = "tok-BI-MAT-123"
DUONG = ThamDo("hợp lệ", ["/usr/bin/true"], "ok")


def mot(t, ma, out="", err="", goi=None):
    """Chạy [dương, t] với kết quả GIẢ cho t; trả kết quả của t."""
    def chay(argv, **kw):
        (goi if goi is not None else []).append(argv)
        return subprocess.CompletedProcess(argv, *((0, "", "") if argv == DUONG.argv else (ma, out, err)))
    return chay_tham_do([DUONG, t], boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay)[1]


@pytest.mark.parametrize("ma, out, dat, ly", [
    (7, "000", False, "không kết luận"), (28, "000", False, "không kết luận"), (0, "000", False, "không kết luận"),
    (0, "404", False, "không kết luận"), (0, "500", False, "không kết luận"), (0, BI_MAT, False, "không kết luận"),
    (0, "403", True, "HTTP 403"), (0, "401", True, "HTTP 401"), (0, "200", False, "nhận"), (0, "422", False, "nhận")])
def test_http_chi_dat_khi_api_tu_choi(ma, out, dat, ly):
    k = mot(ThamDo("api", ["/usr/bin/curl"], "http"), ma, out, f"curl: lỗi {BI_MAT}")
    assert k.dat is dat and ly in k.chi_tiet and BI_MAT not in k.chi_tiet


@pytest.mark.parametrize("kieu, ma, err, dat", [
    ("doc", 1, "cat: x: Permission denied", True), ("doc", 1, "cat: x: No such file or directory", None),
    ("doc", 1, "cat: x: Is a directory", None), ("doc", 127, "env: cat: No such file", None), ("doc", 126, "", None),
    ("doc", -9, "", None), ("doc", 0, "", False), ("ghi", 1, "touch: x: Operation not permitted", True),
    ("sua", 1, "touch: x: Read-only file system", None),
    ("keychain", 44, "SecKeychainSearchCopyNext: The specified item could not be found in the keychain.", True),
    ("keychain", 44, "", None), ("keychain", 36, "User interaction is not allowed.", None), ("keychain", 0, "", False),
    ("nc", 1, "nc: connectx to 127.0.0.1 port 3306 (tcp) failed: Operation not permitted", True),
    ("nc", 1, "nc: connectx to 127.0.0.1 port 3306 (tcp) failed: Connection refused", None),
    ("tram", 1, "PermissionError: [Errno 13] Permission denied: '/x/su-kien.db'", True),
    ("tram", 127, "env: tram: No such file or directory", None)])
def test_am_chi_dat_khi_co_dau_hieu_tu_choi_quyen(kieu, ma, err, dat):
    k = mot(ThamDo("x", ["/bin/x"], kieu), ma, BI_MAT, f"{err} {BI_MAT}")
    assert k.dat is bool(dat) and BI_MAT not in k.chi_tiet
    assert ("không kết luận" in k.chi_tiet) is (dat is None)


@pytest.mark.parametrize("doi_chung", [lambda: False, lambda: 1 / 0])
def test_doi_chung_hong_thi_khong_chay_va_khong_ket_luan(doi_chung):
    goi = []
    k = mot(ThamDo("đọc", ["/bin/cat", "/x"], "doc", doi_chung), 1, "", "Permission denied", goi)
    assert k.dat is False and "đối chứng" in k.chi_tiet and goi == [DUONG.argv]


def test_bo_tham_do_doi_chung_dung_dich(tmp_path):
    (tep := tmp_path / "phieu.json").write_text("{}")
    rg = tham_do_khe(keychain=["tram-tho-token", "khong-co"], doc_cam=[tep, tmp_path / "khong-co", tmp_path],
                     ghi_cam=[tmp_path, tmp_path / "khong-co"], ghi_duoc=tmp_path, ghi_tep_cam=[tep],
                     co_muc=lambda k: k == "tram-tho-token")
    assert [(t.kieu, t.doi_chung()) for t in rg if t.kieu != "ok"] == [
        ("keychain", True), ("keychain", False), ("doc", True), ("doc", False), ("doc", True), ("ghi", True),
        ("ghi", False), ("sua", True)]
    assert rg[4].argv == ["/bin/ls", str(tmp_path)] and rg[2].argv == ["/bin/cat", str(tep)]   # thư mục: ls, không cat
    dd = tham_do_day_du(rut_gon=[], api="http://x", dai_ca_login="a", may_b="b", db=["127.0.0.1:3306", "h:1"],
                        tram_home_tram=tmp_path, mo=lambda d: d == "127.0.0.1:3306")
    assert [(t.kieu, t.doi_chung and t.doi_chung()) for t in dd if t.kieu != "ok"] == [
        ("http", None), ("nc", True), ("nc", False), ("tram", True)]


def test_doi_chung_keychain_khong_lay_mat_khau_va_cong_db():
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, 0 if argv[-1] == "co" else 44, b"", b"")
    assert co_muc_keychain("co", chay=chay) and not co_muc_keychain("khong", chay=chay) and "-w" not in goi[0]
    assert not co_muc_keychain("x", chay=lambda *a, **k: (_ for _ in ()).throw(OSError("security")))

    class Noi:
        def close(self):
            pass
    assert mo_cong("127.0.0.1:3306", noi=lambda dich, timeout: Noi())
    assert not mo_cong("127.0.0.1:3306", noi=lambda dich, timeout: (_ for _ in ()).throw(ConnectionRefusedError()))
