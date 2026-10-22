"""`chay_mot_lenh` trên primitive P1: chưa xác nhận thu hồi → "fail"; gốc treo sau SIGKILL vẫn trả về có hạn; hạn chờ
phải hữu hạn. Popen/ps/kill GIẢ — không sudo thật."""
import os
import time

import pytest

from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem


def _chay(tmp_path, argv, **kw):
    kw.setdefault("thoi_gian_cho", 20)
    return chay_mot_lenh("lệnh x", argv, cwd=tmp_path, env=moi_truong_kiem(os.environ),
                         log=tmp_path / "log/kiem/g-1-1.log", boc=lambda a: a, **kw)


class _NhomGia:
    """Lệnh xong mã 0 nhưng cây không xác nhận thu hồi được (vd. sudo root còn sống)."""
    p = type("P", (), {"returncode": 0})()

    def cho(self, giay):
        return 0

    def thu_hoi(self, **kw):
        return False


def test_khong_xac_nhan_thu_hoi_thi_fail(tmp_path):
    kq = _chay(tmp_path, ["x"], khoi=lambda argv, **kw: _NhomGia())
    assert kq.ket_qua == "fail" and kq.ma_thoat == 0 and kq.da_thu_hoi is False
    assert "KHÔNG xác nhận" in kq.tom_tat


def test_goc_treo_sau_sigkill_van_tra_ve_co_han(tmp_path):
    from test_vong_doi import SUDO, PopenGia
    from tram.kiem.vong_doi import khoi_chay

    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: PopenGia(), chup=lambda: [SUDO], **kw)

    def tu_choi(g, s):
        raise PermissionError
    t0 = time.monotonic()
    kq = _chay(tmp_path, ["sudo", "x"], thoi_gian_cho=0.2, cho_kill=0.2, kill=tu_choi, khoi=khoi)
    assert time.monotonic() - t0 < 5 and kq.het_gio and kq.ket_qua == "fail" and kq.da_thu_hoi is False



def test_han_khong_huu_han_bi_tu_choi_truoc_khi_chay(tmp_path):
    goi = []
    with pytest.raises(ValueError):
        _chay(tmp_path, ["x"], thoi_gian_cho=float("inf"), khoi=lambda *a, **k: goi.append(1))
    assert goi == []
