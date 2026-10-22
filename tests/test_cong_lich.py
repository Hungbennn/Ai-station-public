"""Cổng thao tác lịch (3C-B): spy chứng minh sai danh tính → KHÔNG gọi cron/at/launchctl; lệnh lịch ngoài tiền tố đã
xác minh bị từ chối trước khi chạy. Không có lệnh lịch thật nào được spawn trong file này."""
import pytest

from tram.kiem.cong_lich import CongLich, duoc_chay, mo_cong_lich
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import kill_cuc_bo

BOC = ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--")


def boc(argv):
    return [*BOC, *argv]


class Spy:
    def __init__(self):
        self.argv = []

    def __call__(self, argv, **kw):
        self.argv.append(list(argv))
        return "ok"


def _sai(*a):
    raise LoiDanhTinh("UID thực khác")


@pytest.mark.parametrize("xac_minh", [_sai, lambda *a: (_ for _ in ()).throw(LoiDanhTinh("quá hạn"))])
def test_sai_danh_tinh_khong_goi_lenh_nao(xac_minh):
    spy = Spy()
    with pytest.raises(LoiDanhTinh):
        cong = mo_cong_lich("tram-kiem", boc, kill_cuc_bo, chay=spy, xac_minh=xac_minh)
        cong(boc(["/usr/bin/crontab", "-l"]))
    assert spy.argv == []


def test_lenh_ngoai_principal_bi_chan_truoc_khi_chay():
    spy = Spy()
    cong = mo_cong_lich("tram-kiem", boc, kill_cuc_bo, chay=spy, xac_minh=lambda *a: 502)
    for sai in (["/usr/bin/crontab", "-r"], ["crontab", "-l"], ["/bin/launchctl", "bootout", "gui/501"],
                ["/usr/bin/sudo", "-n", "-u", "dai-ca", "--", "/usr/bin/atrm", "1"], ["/bin/sh", "-c", "at now"],
                ["/usr/bin/env", "batch"], ["/bin/sh", "-c", "echo x|crontab -"], list(BOC),
                ["/usr/bin/find", "/", "-exec", "/usr/bin/crontab", "-r", ";"], ["find", "/usr/lib/cron/jobs"]):
        with pytest.raises(LoiDanhTinh):
            cong(sai, capture_output=True, text=True, timeout=30)
    assert spy.argv == []
    assert cong(boc(["/usr/bin/crontab", "-l"]), timeout=30) == "ok"
    assert cong(["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]) == "ok"
    assert spy.argv == [boc(["/usr/bin/crontab", "-l"]), ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]
    assert cong.uid == 502 and cong.tien_to == BOC


@pytest.mark.parametrize("b", [lambda a: a, lambda a: ["/usr/bin/crontab", *a]])
def test_boc_rong_hoac_chua_lich_khong_mo_cong(b):
    goi = []
    with pytest.raises(LoiDanhTinh):
        mo_cong_lich("tram-kiem", b, kill_cuc_bo, chay=Spy(), xac_minh=lambda *a: goi.append(1) or 502)
    assert goi == []


def test_danh_sach_quan_sat_dong():
    assert duoc_chay(["/usr/bin/pgrep", "-f", "at"], BOC) and duoc_chay(["/bin/ps", "-A"], BOC)
    assert not duoc_chay(["/usr/bin/find", "/tmp", "-delete"], BOC) and not duoc_chay([], BOC)
    assert CongLich(BOC, 502, Spy())(boc(["/bin/launchctl", "print", "user/502"])) == "ok"
