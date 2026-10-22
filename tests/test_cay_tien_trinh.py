"""Ảnh chụp tiến trình và cây con của MỘT lần chạy (lát P1): chỉ đọc `ps` (cột số), không gửi tín hiệu."""
import subprocess
import sys
import time

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he, doc_ps, mo_ho
from tram.kiem.lenh_ngan import chay_ngan

PS = (b"    0     0     0     0     0\n"
      b"    1     0     1     0     0\n"
      b"  500     1   500   501   501\n"
      b"  600   500   600     0   501\n"
      b"  601   600   601   502   502\n"
      b"  602   601   602   502   502\n"
      b"  603     1   601   502   502\n"
      b"  700     1   700   502   502\n")


def test_doc_ps_chi_cot_so():
    ds = doc_ps(PS)
    assert ds[4] == TienTrinh(601, 600, 601, 502, 502) and len(ds) == 8


@pytest.mark.parametrize("hong", [b"abc 1 1 1 1\n", b"1 2 3\n", b"5 1 -7 0 0\n", b"5 1 5 0 0 x\n",
                                  b"5 1 5 0 0\r9 5 1 501 501\n"])
def test_doc_ps_dong_hong_hoac_gia_mao_thi_nem(hong):
    with pytest.raises(ValueError):
        doc_ps(PS + hong)


def test_cay_theo_ppid_va_nhom_co_thanh_vien_da_chung_minh():
    ds = doc_ps(PS)
    # gốc 600 còn sống: con 601 (nhóm mới, như pty của sudo), cháu 602 (phiên mới), 603 mồ côi nhưng cùng nhóm với 601
    assert [t.pid for t in cay(ds, 600, set())] == [600, 601, 602, 603]
    assert cay(ds, None, set()) == [] and 500 not in {t.pid for t in cay(ds, 600, set())}


def test_cay_sau_khi_goc_gat_chi_theo_dinh_danh_da_thay():
    ds = [TienTrinh(601, 1, 601, 502, 502, 11), TienTrinh(602, 601, 602, 502, 502, 12),
          TienTrinh(603, 1, 601, 502, 502, 13), TienTrinh(700, 1, 700, 502, 502, 14)]
    # 601 đã thấy (cùng sinh) → nó, con 602 và 603 cùng nhóm với nó; 700 không thuộc cây
    assert [t.pid for t in cay(ds, None, {(601, 11)})] == [601, 602, 603]
    # cùng số 601 nhưng sinh khác: lần sống khác — không nhận, kể cả 603 mang số nhóm đó
    assert cay(ds, None, {(601, 99)}) == []
    assert [t.pid for t in mo_ho(ds, [], {601})] == [601, 603]
    assert mo_ho(ds, cay(ds, None, {(601, 11)}), {601, 0, 1}) == []


def test_chup_he_doc_ps_that_thay_tien_trinh_con_cua_minh():
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        con = cay(chup_he(), p.pid, set())
        assert [t.pid for t in con] == [p.pid] and con[0].pgid == p.pid
    finally:
        p.kill()
        p.wait(5)


def test_chup_he_ps_loi_thi_nem():
    def chay(argv, **kw):
        assert argv[0] == "/bin/ps" and kw == {"timeout": 5, "doc": True}
        return None, b""
    with pytest.raises(OSError):
        chup_he(chay=chay)


def test_chay_ngan_qua_han_tra_ve_ngay_khong_cho():
    t0 = time.monotonic()
    assert chay_ngan([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.3) == (None, b"")
    assert time.monotonic() - t0 < 3
    assert chay_ngan([sys.executable, "-c", "print(7)"], timeout=10, doc=True) == (0, b"7\n")
