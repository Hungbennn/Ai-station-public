import signal

import pytest
from tram.kiem.han_tong import chay_han_tong
from tram.kiem.ngat import NgatTerm, term_thanh_ngat


def giao(so):
    signal.getsignal(so)(so, None)                                  # như nhân giao tín hiệu: chạy handler ĐANG CÀI


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("loi", [KeyboardInterrupt, RuntimeError])
def test_ngat_van_thu_hoi_roi_don(tmp_path, sach, loi):
    goi = []
    dau = tmp_path / "dau"
    class N:
        def cho(self, han):
            raise loi("khong-in-noi-dung")
        def thu_hoi(self):
            goi.append("thu")
            return sach
    def don():
        goi.append("don")
        return True
    with pytest.raises(loi):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau,
                      don=don, khoi=lambda *a, **kw: N())
    assert goi == ["thu", "don"]
    assert dau.exists() is (not sach)


def test_thu_hoi_nem_van_don_va_giu_dau(tmp_path):
    goi = []
    class N:
        def cho(self, han):
            return 0
        def thu_hoi(self):
            raise RuntimeError("loi-thu-hoi")
    with pytest.raises(RuntimeError):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None,
                      dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=lambda *a, **kw: N())
    assert goi == [1] and (tmp_path / "dau").exists()


@pytest.mark.parametrize("o", ["thu_hoi", "don"])
def test_ngat_lan_hai_trong_luc_don_van_giu_dau(tmp_path, o):
    """bs-863.19: Ctrl-C/SIGTERM lần hai giữa lúc thu hồi hoặc dọn — `don` vẫn được gọi sau thu hồi, dấu GIỮ."""
    goi, dau = [], tmp_path / "dau"

    class N:
        def cho(self, han):
            raise KeyboardInterrupt

        def thu_hoi(self):
            goi.append("thu")
            if o == "thu_hoi":
                raise KeyboardInterrupt
            return True

    def don():
        goi.append("don")
        if o == "don":
            raise KeyboardInterrupt
        return True
    with pytest.raises(KeyboardInterrupt):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=don, khoi=lambda *a, **kw: N())
    assert goi == ["thu", "don"] and dau.exists()


def test_ngat_toi_giua_luc_spawn_chi_nem_khi_con_da_co_chu(tmp_path):
    """B03: SIGTERM tới khi `khoi` đã Popen, chưa trả Nhom — hoãn; ném khi `n` đã có chủ: thu hồi, dọn, xoá dấu."""
    goi, dau = [], tmp_path / "dau"

    class N:
        def cho(self, han):
            goi.append("cho")

        def thu_hoi(self):
            goi.append("thu")
            return True
    with term_thanh_ngat():
        def khoi(*a, **kw):
            giao(signal.SIGTERM)
            goi.append("khoi-xong")
            return N()
        with pytest.raises(NgatTerm):
            chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True,
                          khoi=khoi)
    assert goi == ["khoi-xong", "thu", "don"] and not dau.exists()


def test_khoi_nem_loi_khac_oserror_thi_van_don_nhung_giu_dau(tmp_path):
    """Hợp đồng `khoi_chay` (V2-0/A03) bị vi phạm — vd. dựng theo dõi hỏng SAU Popen, ném RuntimeError: không biết con
    còn hay không → `don` vẫn chạy, dấu GIỮ (cổng đóng), lỗi nổi lên."""
    goi, dau = [], tmp_path / "dau"

    def khoi(*a, **kw):
        raise RuntimeError("theo dõi hỏng sau Popen")
    with pytest.raises(RuntimeError):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True, khoi=khoi)
    assert goi == ["don"] and dau.exists()


def test_ngat_lan_hai_trong_luc_thu_hoi_khong_cat_ngang(tmp_path):
    """B03: SIGTERM lần hai tới giữa lúc thu hồi — thu hồi chạy hết (hữu hạn), dọn, rồi mới ném một lần."""
    goi, dau = [], tmp_path / "dau"
    with term_thanh_ngat():
        class N:
            def cho(self, han):
                giao(signal.SIGTERM)                     # lần một: ngoài ranh giới hoãn → ném ngay

            def thu_hoi(self):
                giao(signal.SIGTERM)                     # lần hai: hoãn
                goi.append("thu-xong")
                return True
        with pytest.raises(NgatTerm):
            chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True,
                          khoi=lambda *a, **kw: N())
    assert goi == ["thu-xong", "don"] and not dau.exists()
