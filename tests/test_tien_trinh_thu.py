"""Cleanup có hạn, không bỏ con sau khi con trước lỗi; tất cả process ở đây là giả."""
import pytest
from tien_trinh_thu import don_cac_con, quan_ly_con


class ConGia:
    def __init__(self, *, pid=1, song=True, li=False, hong=False):
        self.pid, self.song, self.li, self.hong = pid, song, li, hong
        self.nhat_ky = []

    def is_alive(self):
        self.nhat_ky.append("song")
        return self.song

    def terminate(self):
        self.nhat_ky.append("terminate")
        if self.hong:
            raise OSError("chi-tiet-khong-duoc-lo")

    def join(self, han):
        self.nhat_ky.append(("join", han))

    def kill(self):
        self.nhat_ky.append("kill")
        self.song = self.li


class HangGia:
    def __init__(self, hong=False):
        self.nhat_ky, self.hong = [], hong

    def cancel_join_thread(self):
        self.nhat_ky.append("cancel")
        if self.hong:
            raise OSError("chi-tiet-khong-duoc-lo")

    def close(self):
        self.nhat_ky.append("close")


def test_terminate_join_kill_join_dung_thu_tu():
    p = ConGia()
    don_cac_con([p])
    assert p.nhat_ky == ["song", "terminate", ("join", 2), "song", "kill", ("join", 2), "song"]
    assert not p.song


def test_con_chua_start_va_con_da_thoat_khong_nhan_signal():
    chua, xong = ConGia(pid=None), ConGia(song=False)
    don_cac_con([chua, xong])
    assert chua.nhat_ky == []
    assert xong.nhat_ky == ["song", ("join", 2), "song", "song"]


def test_terminate_du_thi_khong_kill():
    class ConDungMem(ConGia):
        def terminate(self):
            super().terminate()
            self.song = False

    p = ConDungMem()
    don_cac_con([p])
    assert p.nhat_ky == ["song", "terminate", ("join", 2), "song", "song"]
    assert not p.song


@pytest.mark.parametrize("kw", [{"li": True}, {"hong": True}])
def test_loi_con_dau_van_don_con_sau_va_queue(kw):
    a, b, hang = ConGia(**kw), ConGia(), HangGia()
    with pytest.raises(RuntimeError, match="Không dọn được tiến trình test") as loi:
        with quan_ly_con([a, b], hang):
            pass
    assert "chi-tiet" not in str(loi.value)
    assert not b.song and "kill" in b.nhat_ky
    assert hang.nhat_ky == ["cancel", "close"]


@pytest.mark.parametrize("loai", [AssertionError, RuntimeError, KeyboardInterrupt])
def test_loi_than_khong_bo_cleanup_va_duoc_truyen_lai(loai):
    p, hang = ConGia(), HangGia()
    with pytest.raises(loai, match="loi-than"):
        with quan_ly_con([p], hang):
            raise loai("loi-than")
    assert not p.song and hang.nhat_ky == ["cancel", "close"]


def test_cancel_queue_loi_van_close_va_bao_that_bai():
    hang = HangGia(hong=True)
    with pytest.raises(RuntimeError, match="Không đóng được queue test"):
        with quan_ly_con([], hang):
            pass
    assert hang.nhat_ky == ["cancel", "close"]
