"""UID THỰC của principal (3C-B): đọc uid/ruid nhân ghi cho cây dò dưới `boc`, không tin env/argv. Ca thật chỉ chạy
`/bin/sleep` của chính user đang test với `boc` đồng nhất — phải BỊ TỪ CHỐI vì trùng người vận hành."""
import os
import subprocess

import pytest

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh, quan_sat, xac_minh_uid
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo


def _ngu(uid, ruid, pid=4243, cha=4242):
    return TienTrinh(pid, cha, 4242, uid, ruid)


def test_boc_dong_nhat_va_env_gia_mao_bi_tu_choi(monkeypatch):
    monkeypatch.setenv("USER", "tram-kiem")
    monkeypatch.setenv("LOGNAME", "tram-kiem")
    with pytest.raises(LoiDanhTinh, match="UID thực"):
        xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, tra_uid=lambda t: 64999)
    con = [x for x in subprocess.run(["/bin/ps", "-A", "-o", "ppid=,comm="], capture_output=True, text=True).stdout
           .splitlines() if x.split()[0] == str(os.getpid()) and x.endswith("sleep")]
    assert con == []                                        # tiến trình dò đã được thu hồi


def test_dung_uid_qua_quan_sat_gia():
    pty = [SUDO, TienTrinh(4250, 4242, 4250, 0, 0), _ngu(502, 502, 4251, cha=4250)]   # sudo → monitor pty → lệnh
    for cay in ([SUDO, _ngu(502, 502)], pty):
        assert xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, toi=501, tra_uid=lambda t: 502,
                            quan_sat_=lambda b, k: cay) == 502


@pytest.mark.parametrize("cay", [[SUDO, _ngu(502, 501)], [_ngu(501, 501)], [SUDO], [],
                                 [TienTrinh(9, 1, 9, 501, 501), _ngu(502, 502, cha=9)],
                                 [SUDO, _ngu(502, 502), _ngu(503, 503, 4244)]])
def test_sai_uid_hoac_cay_la_bi_tu_choi(cay):
    with pytest.raises(LoiDanhTinh):
        xac_minh_uid("tram-kiem", lambda a: a, kill_cuc_bo, toi=501, tra_uid=lambda t: 502, quan_sat_=lambda b, k: cay)


@pytest.mark.parametrize("tra", [lambda t: 0, lambda t: 501, lambda t: (_ for _ in ()).throw(KeyError(t))])
def test_tai_khoan_khong_hop_le_khong_spawn(tra):
    goi = []
    with pytest.raises(LoiDanhTinh):
        xac_minh_uid("x", lambda a: a, kill_cuc_bo, toi=501, tra_uid=tra, quan_sat_=lambda b, k: goi.append(1))
    assert goi == []


class _DaThoat(PopenGia):
    """Wrapper thoát ngay (vd. `sudo -n` bị từ chối): không bao giờ có tiến trình dò để đọc UID."""
    returncode = 1

    def wait(self, timeout=None):
        return 1

    def poll(self):
        return 1


def test_quan_sat_khong_thay_tien_trinh_do_hoac_khong_khoi_chay_duoc():
    with pytest.raises(LoiDanhTinh, match="không thấy"):
        quan_sat(lambda a: a, kill_cuc_bo, khoi=lambda argv, **kw: khoi_chay(argv, popen=lambda *x, **y: _DaThoat(),
                                                                             **kw), chup=lambda: [])
    with pytest.raises(LoiDanhTinh, match="không khởi chạy"):
        quan_sat(lambda a: ["/khong/co/chuong-trinh"], kill_cuc_bo)


def test_quan_sat_khong_thu_hoi_duoc_cay_do():
    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: PopenGia(), **kw)
    with pytest.raises(LoiThuHoi, match="thu hồi"):
        quan_sat(lambda a: a, lambda g, s: None, khoi=khoi, chup=lambda: [SUDO, _ngu(502, 502)])
