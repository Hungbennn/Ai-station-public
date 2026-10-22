"""Gộp nhịp nguyên tử giữa hai kết nối (plan 2e Task 2; review đợt 4 F10) — không gọi mạng, SQLite tạm."""
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
from threading import Event
from types import SimpleNamespace

from tram.api import dieu_phoi
from tram.api.dieu_phoi import ThanNhipDieuPhoi, ghi_nhip
from tram.su_kien.kho import KhoSuKien
from tram.suy.dieu_phoi import DU_AN_HE, LOAI


def test_ghi_gop_nguyen_tu_giua_hai_ket_noi(tmp_path, monkeypatch):
    p = tmp_path / "sk.db"
    pt = SimpleNamespace(mo_kho=lambda: KhoSuKien(p), dong_ho=lambda: datetime.now(timezone.utc))
    than = ThanNhipDieuPhoi(su_kien="Stop", phien="a" * 16)
    doc_that, da_doc = dieu_phoi.doc_nhip, Event()

    def doc_roi_dung(kho, luc):
        ds = doc_that(kho, luc)
        if not da_doc.is_set():                    # lời gọi đầu: đã đọc "chưa có", dừng 0,3 s TRƯỚC khi ghi
            da_doc.set()
            time.sleep(0.3)
        return ds

    monkeypatch.setattr(dieu_phoi, "doc_nhip", doc_roi_dung)
    with ThreadPoolExecutor(max_workers=2) as ex:
        dau = ex.submit(ghi_nhip, pt, than)
        assert da_doc.wait(5)
        sau = ex.submit(ghi_nhip, pt, than)          # bản không khoá: đọc "chưa có" trong 0,3 s đó → ghi đôi
        assert sorted([dau.result(5), sau.result(15)]) == [False, True]
    with closing(KhoSuKien(p)) as kho:
        assert len(kho.gan_day(DU_AN_HE, LOAI, 10)) == 1
    assert ghi_nhip(pt, than) is False               # nhánh không ghi: rollback, đóng kết nối
    with closing(KhoSuKien(p)) as kho:
        kho._db.execute("PRAGMA busy_timeout=0")
        kho.ghi(DU_AN_HE, "thu.khoa", {})              # không còn ai giữ khoá ghi: ghi ngay, không "database is locked"
