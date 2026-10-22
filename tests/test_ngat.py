"""bs-863.19 + B03 (vòng 1), R2-02 (vòng 2): SIGTERM/SIGINT ở CLI cha thành ngắt có kiểm soát; `hoan()` (MỘT cơ chế,
do plan A tạo) chỉ GHI tín hiệu và phát lại QUA handler của `term_thanh_ngat` khi ra khỏi khối ngoài cùng; handler
cũ của cả hai tín hiệu luôn được khôi phục. KHÔNG gửi tín hiệu thật — `giao` gọi handler ĐANG CÀI (như nhân giao tín
hiệu cho luồng chính: trong `hoan()` là bộ ghi, ngoài `hoan()` là handler của `term_thanh_ngat`)."""
import signal
import threading

import pytest

from tram.kiem.ngat import NgatTerm, hoan, term_thanh_ngat


def giao(so):
    signal.getsignal(so)(so, None)


@pytest.mark.parametrize("so, loi", [(signal.SIGTERM, NgatTerm), (signal.SIGINT, KeyboardInterrupt)])
def test_trong_khoi_tin_hieu_thanh_ngat_ra_khoi_thi_khoi_phuc(so, loi):
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    with pytest.raises(loi) as e:
        with term_thanh_ngat():
            giao(so)
    assert type(e.value) is loi and issubclass(NgatTerm, KeyboardInterrupt)
    assert {s: signal.getsignal(s) for s in truoc} == truoc


def test_loi_bat_ky_trong_khoi_van_khoi_phuc_ca_hai_handler():
    goi = []
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    dat = lambda so, h: goi.append((so, h)) or f"CU-{so}"                      # noqa: E731
    with pytest.raises(RuntimeError):
        with term_thanh_ngat(dat=dat):
            raise RuntimeError("x")
    assert [g[0] for g in goi] == [signal.SIGTERM, signal.SIGINT, signal.SIGINT, signal.SIGTERM]
    assert [g[1] for g in goi[2:]] == [truoc[signal.SIGINT], truoc[signal.SIGTERM]]


@pytest.mark.parametrize("luc", [2, 3])
def test_ngat_giua_cai_hay_khoi_phuc_handler_khong_de_lai_handler(luc):
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    goi = []

    def dat(s, h):
        cu = signal.signal(s, h)
        goi.append(s)
        if len(goi) == luc:
            raise KeyboardInterrupt()
        return cu

    try:
        with pytest.raises(KeyboardInterrupt):
            with term_thanh_ngat(dat=dat):
                pass
        assert {s: signal.getsignal(s) for s in truoc} == truoc
    finally:
        for s, h in truoc.items():
            signal.signal(s, h)


@pytest.mark.parametrize("than_loi", [False, True])
def test_hoan_ghi_tin_hieu_dau_va_phat_lai_qua_term_thanh_ngat_khi_ra_khoi_khoi_ngoai_cung(than_loi):
    da = []
    with pytest.raises(NgatTerm):
        with term_thanh_ngat():
            with hoan():
                with hoan():
                    giao(signal.SIGTERM)                       # giữa ranh giới sở hữu: chỉ ghi
                    giao(signal.SIGINT)                        # tín hiệu sau không thay tín hiệu đầu
                    da.append("trong")
                da.append("ra-khoi-trong")                     # khối trong ra: chưa ném
                if than_loi:
                    raise OSError("lỗi thân khối")             # ngắt đang chờ vẫn thắng — không bị nuốt
            da.append("KHONG-TOI")
    assert da == ["trong", "ra-khoi-trong"]


def test_luong_phu_hoan_khong_doi_handler_khong_hoan():
    with term_thanh_ngat():
        cai, thay = signal.getsignal(signal.SIGTERM), []

        def chay():
            with hoan():
                thay.append(signal.getsignal(signal.SIGTERM))
        t = threading.Thread(target=chay)
        t.start()
        t.join()
        assert thay == [cai] and signal.getsignal(signal.SIGTERM) is cai
