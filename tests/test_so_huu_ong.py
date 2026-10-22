"""Review vòng 2 R2-04: lỗi ở ống của `chay_gioi_han` — đóng stdin/stdout/stderr ném, selector `select`/`close` ném, đọc
ném — không chặn ống sau, LUÔN tới thu hồi; chưa xác nhận → `LoiThuHoi` thắng lỗi ống/lỗi thường (`from None`); ngắt
vẫn là ngắt. Lỗi tiêm ĐÚNG điểm đọc/selector thật (`_doc`, `_bo_chon`); tiến trình thật chỉ là `python -c` của chính
user đang test."""
import errno
import selectors
from types import SimpleNamespace

import pytest

from test_vong_doi import PY, _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

IN_RA = "print('x' * 10, flush=True); import time; time.sleep(60)"


class Ong:
    """Ống của ta; `close` có thể ném (lỗi đóng ống mang chữ lạ)."""
    def __init__(self, ten, ghi, loi):
        self.ten, self.ghi, self.loi = ten, ghi, loi

    def close(self):
        self.ghi.append(self.ten)
        if self.loi:
            raise OSError("đóng ống: BI-MAT")


class NhomGia:
    def __init__(self, sach, ong_loi=None):
        self.sach, self.da = sach, []
        ong = {t: Ong(t, self.da, t == ong_loi) for t in ("stdin", "stdout", "stderr")}
        self.p = SimpleNamespace(returncode=0, **ong)

    def thu_hoi(self):
        self.da.append("thu")
        return self.sach


@pytest.mark.parametrize("sach, loi, mong", [(True, KeyboardInterrupt, KeyboardInterrupt),
                                              (False, KeyboardInterrupt, KeyboardInterrupt),
                                              (True, OSError, OSError), (False, OSError, LoiThuHoi)])
def test_ngat_hay_loi_giua_chung_van_thu_hoi_chua_xac_nhan_thi_loi_thu_hoi_tru_ngat(monkeypatch, sach, loi, mong):
    n = NhomGia(sach)

    def hong(*a):
        raise loi("BI-MAT")
    monkeypatch.setattr(cgh, "_ong", hong)
    with pytest.raises(mong) as e:
        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n)
    assert n.da == ["stdin", "stdout", "stderr", "thu"]
    assert mong is not LoiThuHoi or ("BI-MAT" not in str(e.value) and e.value.__suppress_context__)


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("ong_loi", ["stdin", "stdout", "stderr"])
def test_dong_ong_loi_khong_chan_ong_sau_va_thu_hoi_khong_che_chua_xac_nhan(monkeypatch, ong_loi, sach):
    n = NhomGia(sach, ong_loi)
    monkeypatch.setattr(cgh, "_ong", lambda *a: (b"", b"", True))
    if sach:
        assert chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n).returncode == 0
    else:
        with pytest.raises(LoiThuHoi) as e:
            chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n)
        assert "BI-MAT" not in str(e.value) and e.value.__cause__ is None
    assert n.da == ["stdin", "stdout", "stderr", "thu"]


class ChonHong:
    """Selector thật, nhưng `select` hoặc `close` ném."""
    def __init__(self, diem):
        self.s, self.diem = selectors.DefaultSelector(), diem

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __getattr__(self, ten):
        return getattr(self.s, ten)

    def select(self, t):
        if self.diem == "chon":
            raise OSError(errno.EBADF, "select: BI-MAT")
        return self.s.select(t)

    def close(self):
        self.s.close()
        if self.diem == "dong_bo_chon":
            raise OSError(errno.EIO, "close: BI-MAT")


@pytest.mark.parametrize("diem", ["doc", "chon", "dong_bo_chon"])
def test_doc_hay_bo_chon_loi_van_dong_ong_va_thu_hoi_con_that(monkeypatch, diem):
    goi = []

    def doc_hong(fd, n):
        raise OSError(errno.EIO, "read: BI-MAT")
    if diem == "doc":
        monkeypatch.setattr(cgh, "_doc", doc_hong)
    else:
        monkeypatch.setattr(cgh, "_bo_chon", lambda: ChonHong(diem))
    argv = [PY, "-c", "print('x')" if diem == "dong_bo_chon" else IN_RA]
    try:
        with pytest.raises(OSError, match="BI-MAT"):
            chay_gioi_han(argv, kill=kill_cuc_bo, timeout=20, capture_output=True,
                          khoi=lambda a, **kw: goi.append(khoi_chay(a, **kw)) or goi[-1])
        assert goi[0].ket_thu_hoi is True and goi[0].p.stdout.closed and not _song(goi[0].p.pid)
    finally:
        for n in goi:
            if n.p.returncode is None:
                n.p.kill()
                n.p.wait(5)
