"""`thuc_hien` (khuôn `tram chu cai-dat*`): lệnh dọn có `sudo` cũng được bỏ qua lỗi (lát 3c). Trước đây `sudo launchctl
bootout system/vn.tram.tho` chạy với check=True nên lần cài ĐẦU (dịch vụ chưa nạp) dừng trước `bootstrap`."""
from tram.chu.cai_dat import KeHoach, bo_qua_loi, thuc_hien


def test_bootout_va_pkill_qua_sudo_khong_check():
    lenh = [["sudo", "launchctl", "bootout", "system/vn.tram.tho"], ["launchctl", "bootout", "gui/501/vn.tram.api"],
            ["sudo", "pkill", "-KILL", "-u", "tram-kiem"], ["sudo", "launchctl", "bootstrap", "system", "/L/x.plist"],
            ["sudo", "install", "-m", "0440", "a", "b"], ["pkill", "-x", "y"], ["sudo"]]
    goi = []
    thuc_hien(KeHoach({}, lenh, []), chay=lambda c, check: goi.append(check))
    assert goi == [False, False, False, True, True, False, True]
    assert not bo_qua_loi(["sudo", "rm", "-f", "/etc/sudoers.d/tram-tho"])
