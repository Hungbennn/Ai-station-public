"""3C-D7 (review đợt 9 vòng 1 mục 4): ngữ cảnh vận hành do TRẠM tự đọc từ OS — chỉ đọc (plist của root, `gethostuuid`,
`SessionGetInfo` của chính tiến trình test); không env, không lệnh hệ thống, không sudo."""
import ctypes
import os
import plistlib
import re

import pytest

from tram.giao_viec.ngu_canh_kiem import NguCanh, ban_macos, ma_may, ngu_canh_hien_hanh, phien_do_hoa


def test_ban_macos_chi_nhan_build_hop_le(tmp_path):
    p = tmp_path / "SystemVersion.plist"
    p.write_bytes(plistlib.dumps({"ProductBuildVersion": "24G90", "ProductVersion": "15.6.1"}))
    assert ban_macos(p) == "24G90"
    for nd in (plistlib.dumps({"ProductBuildVersion": "24G90/../x"}), plistlib.dumps({"ProductVersion": "15"}),
               plistlib.dumps({"ProductBuildVersion": 24})):
        p.write_bytes(nd)
        with pytest.raises(ValueError):
            ban_macos(p)
    p.write_bytes(b"rac")
    with pytest.raises(ValueError):
        ban_macos(p)
    with pytest.raises(OSError):
        ban_macos(tmp_path / "khong-co")


def test_doc_that_tu_os_chi_doc():
    assert re.fullmatch(r"[0-9a-f]{16}", ma_may()) and ma_may() == ma_may()
    assert isinstance(phien_do_hoa(), bool) and ban_macos().isalnum()


def test_ngu_canh_hien_hanh_gan_uid_tram_va_tai_khoan_kiem():
    nc = ngu_canh_hien_hanh("root")
    assert isinstance(nc, NguCanh) and nc.uid_tram == os.getuid() and nc.uid_kiem == 0
    assert nc == NguCanh(ban_macos(), ma_may(), 0, os.getuid(), phien_do_hoa())
    with pytest.raises(KeyError):
        ngu_canh_hien_hanh("khong-co-tai-khoan-nay-3c-d7")


class ThuVienGia:
    """Thay `ctypes.CDLL` trong một test: `SessionGetInfo` ghi cờ phiên, `gethostuuid` trả mã."""
    def __init__(self, cot=0, ma=0):
        self.cot, self.ma = cot, ma

    def SessionGetInfo(self, phien, sid, cot):
        cot._obj.value = self.cot
        return self.ma

    def gethostuuid(self, buf, han):
        return self.ma


@pytest.mark.parametrize("cot, mong", [(0x6030, True), (0x0010, True), (0x6020, False), (0, False)])
def test_phien_do_hoa_chi_doc_co_sessionHasGraphicAccess(monkeypatch, cot, mong):
    monkeypatch.setattr(ctypes, "CDLL", lambda ten: ThuVienGia(cot))
    assert phien_do_hoa() is mong


def test_api_os_bao_loi_thi_nem(monkeypatch):
    monkeypatch.setattr(ctypes, "CDLL", lambda ten: ThuVienGia(0x10, ma=-1))
    with pytest.raises(OSError):
        phien_do_hoa()
    with pytest.raises(OSError):
        ma_may()
