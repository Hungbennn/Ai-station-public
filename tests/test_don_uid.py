"""Review vòng 1 A01/A02 (V2-0, D53): dọn theo PHẠM VI UID của khe — `kill -KILL -1` CHẠY DƯỚI chính principal (nhân
chỉ gửi tới tiến trình cùng UID: không thể trúng tài khoản khác dù số PID/nhóm đã cấp lại), rồi chứng minh bằng bảng
tiến trình của nhân không còn tiến trình nào có uid/uid thực của khe. Bước nào không chứng minh được → `LoiThuHoi`.
Xác minh UID, lệnh chạy và bảng tiến trình đều GIẢ — test KHÔNG BAO GIỜ chạy kill -1 thật."""
import os
import subprocess

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.don_uid import GIET, don_uid
from tram.tho.principal import Principal

PR = Principal("user", "tram-k-c-codex-1")
UID = 600 if os.getuid() != 600 else 601


class May:
    """`chay` ghi lại lệnh (không spawn); `chup` trả lần lượt các ảnh (ảnh cuối lặp lại)."""
    def __init__(self, *anh, loi=None):
        self.goi, self.anh, self.loi = [], list(anh) or [[]], loi

    def chay(self, argv, **kw):
        self.goi.append((argv, kw))
        if self.loi is not None:
            raise self.loi
        return subprocess.CompletedProcess(argv, 1, b"", b"")         # mã thoát không là bằng chứng

    def chup(self):
        return self.anh.pop(0) if len(self.anh) > 1 else self.anh[0]


def don(may, pr=PR, xac_minh=lambda *a: UID, **kw):
    return don_uid(pr, xac_minh=xac_minh, chay=may.chay, chup=may.chup, ngu=lambda s: None, **kw)


def test_kill_1_duoi_principal_roi_bang_khong_con_ai_cua_uid():
    may = May([TienTrinh(7000, 1, 7000, UID, UID, 1), TienTrinh(7001, 1, 7001, 501, 501, 2)],
              [TienTrinh(7001, 1, 7001, 501, 501, 2)])                # tiến trình của tài khoản khác không tính
    don(may)
    ((argv, kw),) = may.goi
    assert GIET == ["/bin/kill", "-KILL", "-1"] and argv == PR.boc(GIET) and argv[:5] == ["/usr/bin/sudo", "-n", "-H",
                                                                                            "-u", PR.user]
    assert kw["kill"] == PR.kill_nhom and kw["env"] == {"PATH": "/usr/bin:/bin"} and kw["timeout"] == 10


def test_con_tien_trinh_cua_uid_sau_han_thi_loi_thu_hoi():
    may = May([TienTrinh(7000, 1, 7000, 0, UID, 1)])                   # setuid root, uid thực của khe: vẫn tính
    with pytest.raises(LoiThuHoi, match="còn 1"):
        don(may, han=0.05)


def _loi_danh_tinh(*a):
    raise LoiDanhTinh("x")


@pytest.mark.parametrize("pr, xm", [(Principal("sandbox", "tram-exec"), lambda *a: UID), (PR, _loi_danh_tinh),
                                    (PR, lambda *a: os.getuid()), (PR, lambda *a: 0)])
def test_khong_chung_minh_duoc_uid_rieng_thi_khong_kill_va_loi_thu_hoi(pr, xm):
    may = May()
    with pytest.raises(LoiThuHoi):
        don(may, pr=pr, xac_minh=xm)
    assert may.goi == []


@pytest.mark.parametrize("loi", [OSError("spawn"), subprocess.TimeoutExpired("kill", 10), LoiThuHoi("x")])
def test_kill_khong_xac_nhan_thi_loi_thu_hoi(loi):
    with pytest.raises(LoiThuHoi):
        don(May(loi=loi))


def test_khong_doc_duoc_bang_thi_loi_thu_hoi():
    may = May()
    may.chup = lambda: (_ for _ in ()).throw(OSError("sysctl"))
    with pytest.raises(LoiThuHoi):
        don(may)
