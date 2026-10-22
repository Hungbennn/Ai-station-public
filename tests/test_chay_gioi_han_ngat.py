"""B03 (vòng 1), R2-02/R2-03 (vòng 2): `chay_gioi_han` (thân hàm của A-T4 + `stdin=`) dưới `term_thanh_ngat`. SIGTERM
THẬT (`raise_signal` vào CHÍNH tiến trình test) tới ngay sau Popen đi qua CẢ HAI lớp — bộ ghi của `hoan()` trong
`khoi_chay` (A) rồi handler `term_thanh_ngat` (B) khi `Nhom` đã ở `chu` — con vẫn bị đóng ống + thu hồi rồi `NgatTerm`
mới nổi lên. Lỗi/ngắt tiêm tại ĐIỂM ĐỌC THẬT (`_doc` trong vòng selector), ngắt lần hai lúc thu hồi: vẫn đóng ống +
thu hồi đúng một lần. Tiến trình thật chỉ là `python -c` của user test."""
import os
import signal
import subprocess
import sys
from types import SimpleNamespace

import pytest

from test_vong_doi import _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.ngat import NgatTerm, term_thanh_ngat
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable


def popen_term(goi):
    def popen(argv, **kw):
        p = subprocess.Popen(argv, **kw)
        goi.append(p)
        assert callable(signal.getsignal(signal.SIGTERM))           # bộ ghi của `hoan()` — không phải mặc định
        signal.raise_signal(signal.SIGTERM)
        return p
    return popen


def test_sigterm_that_ngay_sau_popen_qua_hai_lop_con_van_bi_thu_hoi():
    goi = []
    try:
        with term_thanh_ngat():
            with pytest.raises(NgatTerm):
                chay_gioi_han([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo, timeout=30,
                              capture_output=True, khoi=lambda a, **kw: khoi_chay(a, popen=popen_term(goi), **kw))
        assert not _song(goi[0].pid) and goi[0].stdout.closed and goi[0].returncode is not None
    finally:
        for p in goi:
            if p.poll() is None:
                p.kill()
                p.wait(5)


def nhom_gia(goi, sach, sau_thu=None):
    r, w = os.pipe()
    os.write(w, b"BI-MAT-ENV")                                       # có dữ liệu: selector báo đọc được ngay

    class N:
        p = SimpleNamespace(pid=4242, returncode=None, stdin=None, stdout=os.fdopen(r, "rb"), stderr=None)

        def thu_hoi(self):
            goi.append("thu")
            if sau_thu:
                sau_thu()
            return sach
    return N(), w


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("loi", [KeyboardInterrupt, OSError])
def test_loi_hay_ngat_tai_diem_doc_van_dong_ong_va_thu_hoi(monkeypatch, loi, sach):
    """`_doc` (os.read của vòng selector) ném: đóng ống của ta rồi thu hồi. Chưa xác nhận → `LoiThuHoi` THAY lỗi
    thường (không nối chuỗi); ngắt vẫn là ngắt."""
    goi = []
    n, w = nhom_gia(goi, sach)

    def doc(fd, k):
        raise loi("BI-MAT-ENV")
    monkeypatch.setattr(cgh, "_doc", doc)
    mong = LoiThuHoi if loi is OSError and not sach else loi
    try:
        with pytest.raises(mong) as e:
            chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=10, capture_output=True, khoi=lambda *a, **kw: n)
        assert goi == ["thu"] and n.p.stdout.closed
        assert mong is not LoiThuHoi or ("BI-MAT-ENV" not in str(e.value) and e.value.__suppress_context__)
    finally:
        os.close(w)


def test_sigterm_lan_hai_luc_thu_hoi_khong_cat_ngang_va_thang_loi_doc(monkeypatch):
    goi = []
    n, w = nhom_gia(goi, True, sau_thu=lambda: signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None))

    def doc(fd, k):
        raise OSError("đọc hỏng")
    monkeypatch.setattr(cgh, "_doc", doc)
    try:
        with term_thanh_ngat():
            with pytest.raises(NgatTerm):
                chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=10, capture_output=True, khoi=lambda *a, **kw: n)
        assert goi == ["thu"] and n.p.stdout.closed                  # thu hồi chạy hết MỘT lần, rồi mới ngắt
    finally:
        os.close(w)
