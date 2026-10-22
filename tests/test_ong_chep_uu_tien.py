"""B02 (vòng 1): ống `git archive | tar` — nguồn CHƯA xác nhận thu hồi thắng MỌI lỗi khác (đích xong/lỗi/không khởi
chạy, đóng ống lỗi), không nối chuỗi lỗi bên dưới, cổng đóng vì bản chép; MỘT hạn cho cả ống: đích nhận đúng phần còn
lại, chuẩn bị nguồn tiêu hết hạn thì không chạy đích. Tiến trình thật chỉ là `git archive` + `python -c` của user test
trong tmp_path; nguồn "không thu hồi được" là Nhom GIẢ."""
import os
import subprocess
import time

import pytest

from test_ban_chep_pipeline_han import PY, TAR, boc_tar, ong  # noqa: F401 — fixture `ong` dùng chung
from test_kiem_lai_cong import chay as chay_cong, cong
from test_kiem_lai_principal import m  # noqa: F401 — fixture `m` dùng chung
from test_vong_doi import _song
from tram.giao_viec import ban_chep, cay_kiem, ong_chep
from tram.giao_viec.ban_chep import LoiBanChep, chep_ban
from tram.kiem.vong_doi import Nhom


class _OngLoi:
    """Ống THẬT của nguồn, nhưng `close` ném (lỗi đóng ống mang byte môi trường)."""
    def __init__(self, f):
        self.f = f

    def fileno(self):
        return self.f.fileno()

    def close(self):
        self.f.close()
        raise OSError("đóng ống: BI_MAT_ENV")


def _nguon_khong_thu_hoi(monkeypatch, dong_loi: bool, goi: list):
    r, w = os.pipe()
    os.close(w)

    class NguonGia(Nhom):
        def __init__(self):
            f = os.fdopen(r, "rb")
            self.p = type("P", (), {"stdout": _OngLoi(f) if dong_loi else f, "pid": 0})()

        def cho(self, giay):
            return 0

        def thu_hoi(self, **kw):
            goi.append("thu")
            return False
    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: NguonGia())


def _dich_loi(monkeypatch):
    that = ban_chep.chay_gioi_han

    def chay(argv, **kw):
        if argv[0] == TAR:
            raise OSError("tar: BI_MAT_ENV")                        # lỗi đích có thể mang byte môi trường
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)


@pytest.mark.parametrize("dich", ["xong", "loi", "khong_chay", "dong_ong_loi"])
def test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac(ong, monkeypatch, dich):
    """B02: nguồn trả thu_hoi False — dù đích xong, lỗi (mang byte env), không khởi chạy hay đóng ống lỗi — kết quả
    LUÔN là `LoiBanChep` "thu hồi CHƯA", không nối chuỗi lỗi bên dưới."""
    k, sha, wt, _ = ong
    goi = []
    _nguon_khong_thu_hoi(monkeypatch, dich == "dong_ong_loi", goi)
    if dich == "loi":
        _dich_loi(monkeypatch)
    tar = {"khong_chay": ["/khong-co/tar"]}.get(dich, [PY, "-c", "import sys; sys.stdin.buffer.read()"])
    with pytest.raises(LoiBanChep, match="thu hồi CHƯA") as e:
        chep_ban(k.kho, sha, wt, boc=(lambda a: a) if dich == "loi" else boc_tar(tar))
    assert goi == ["thu"] and "BI_MAT_ENV" not in f"{e.value}{e.value!r}"
    assert e.value.__cause__ is None and e.value.__suppress_context__


def test_dich_loi_va_nguon_chua_thu_hoi_thi_cong_dong_vi_nguon(m, monkeypatch):
    """B02: tổ hợp nguy hiểm ở mức `kiem_lai` — cổng đóng với lý do là bản chép chưa thu hồi (LoiBanChep), không phải
    lỗi của đích."""
    goi, c = [], cong(m[2])
    _nguon_khong_thu_hoi(monkeypatch, False, goi)
    _dich_loi(monkeypatch)
    with pytest.raises(LoiBanChep, match="thu hồi CHƯA"):
        chay_cong(m, c)
    assert goi == ["thu"] and c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"}


def test_dich_nhan_phan_han_con_lai_chuan_bi_het_han_thi_khong_chay_dich(ong, monkeypatch):
    """B02: MỘT hạn cho cả ống (THOI_GIAN = 1 s) tính trước khi chuẩn bị nguồn — đích nhận đúng phần còn lại; chuẩn bị
    đã tiêu hết hạn → không chạy đích, nguồn vẫn thu hồi, ném TimeoutExpired."""
    k, sha, wt, nguon = ong
    goc, cham, han = cay_kiem.chuan_bi_thuoc_tinh, [0.4], []
    monkeypatch.setattr(cay_kiem, "chuan_bi_thuoc_tinh", lambda kho: time.sleep(cham[0]) or goc(kho))

    that = ban_chep.chay_gioi_han

    class Dung(Exception):
        pass

    def chay(argv, **kw):
        if "stdin" in kw:                                           # đích của ống
            han.append(kw.get("timeout"))
            raise Dung
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)
    with pytest.raises(Dung):
        chep_ban(k.kho, sha, wt, boc=lambda a: a)
    assert han and 0 < han[0] <= 0.6 and not _song(nguon[0].p.pid)
    cham[0], han[:] = 1.2, []
    with pytest.raises(subprocess.TimeoutExpired):
        chep_ban(k.kho, sha, wt.with_name("g-1-cd"), boc=lambda a: a)
    assert han == [] and not _song(nguon[1].p.pid) and nguon[1].p.stdout.closed
