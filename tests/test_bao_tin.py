import http.client
import json
import subprocess
import urllib.error
from datetime import datetime, timezone

import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.bao_tin.luu import doc_json, ghi_json
from tram.bao_tin.telegram import LoiTelegram, doc_token, gui_telegram
from tram.bao_tin.vong import NguCanhBaoTin, chay_mai, mot_vong, tao_ngu_canh_that
from tram.su_kien.kho import KhoSuKien

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


class PhanHoiGia:
    def __init__(self, du_lieu):
        self._d = json.dumps(du_lieu).encode()

    def read(self):
        return self._d

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_gui_telegram_dung_yeu_cau():
    goi = []

    def mo(yc, timeout):
        goi.append((yc, timeout))
        return PhanHoiGia({"ok": True})

    gui_telegram("123:ABC", "42", "[tram] hr · 1 cờ đỏ (hr-1)", mo=mo)
    yc, timeout = goi[0]
    assert yc.full_url == "https://api.telegram.org/bot123:ABC/sendMessage" and yc.get_method() == "POST"
    assert json.loads(yc.data) == {"chat_id": "42", "text": "[tram] hr · 1 cờ đỏ (hr-1)",
                                   "disable_web_page_preview": True}
    assert timeout == 10.0


def test_gui_telegram_loi_che_token():
    def mo(yc, timeout):
        raise urllib.error.URLError(f"không tới được {yc.full_url}")

    with pytest.raises(LoiTelegram) as e:
        gui_telegram("123:ABC", "42", "x", mo=mo)
    assert "123:ABC" not in str(e.value) and "***" in str(e.value) and e.value.__cause__ is None
    with pytest.raises(LoiTelegram):
        gui_telegram("t", "42", "x", mo=lambda yc, timeout: PhanHoiGia({"ok": False, "description": "chat not found"}))


@pytest.mark.parametrize("loi", [lambda url: http.client.IncompleteRead(b"{\"ok\": tr", 20),
                                 lambda url: http.client.HTTPException(f"hỏng ở {url}")])
def test_gui_telegram_http_exception_thanh_loi_telegram_che_token(loi):
    class DocHong(PhanHoiGia):
        def read(self):
            raise loi(self.url)

    def mo(yc, timeout):
        r = DocHong({})
        r.url = yc.full_url
        return r

    with pytest.raises(LoiTelegram) as e:
        gui_telegram("123:ABC", "42", "x", mo=mo)
    assert "123:ABC" not in str(e.value) and e.value.__cause__ is None


def test_doc_token_env_roi_keychain(monkeypatch):
    monkeypatch.setenv("TRAM_TELEGRAM_BOT_TOKEN", " abc ")
    assert doc_token(chay=lambda *a, **k: pytest.fail("không được gọi Keychain")) == "abc"
    monkeypatch.delenv("TRAM_TELEGRAM_BOT_TOKEN")
    assert doc_token(chay=lambda lenh, **k: subprocess.CompletedProcess(lenh, 0, "tok\n", "")) == "tok"
    assert doc_token(chay=lambda lenh, **k: subprocess.CompletedProcess(lenh, 44, "", "")) is None


def test_luu_json_nguyen_tu_va_file_hong(tmp_path):
    p = tmp_path / "a" / "x.json"
    assert doc_json(p, {"mac": 1}) == {"mac": 1}
    ghi_json(p, {"ă": 2})
    assert doc_json(p, None) == {"ă": 2} and not list(p.parent.glob("*.tam"))
    p.write_text("{hỏng", encoding="utf-8")
    assert doc_json(p, "md") == "md"


def _nc(tmp_path, bd, gui):
    return NguCanhBaoTin(kho=KhoSuKien(tmp_path / "sk.db"), tao_bd=lambda ten: bd, gui=gui,
                         thu_muc=tmp_path / "bao-tin", dashboard_url="https://may-b.tail.ts.net/",
                         bay_gio=lambda: T0)


def test_mot_vong_tu_moc_den_tin(tmp_path):
    da_gui, bd = [], BdGia([bead("hr-1")])
    nc = _nc(tmp_path, bd, da_gui.append)
    nc.kho.ghi("hr", "quet.xong", {})              # sự kiện cũ trước khi dịch vụ chạy
    assert mot_vong(nc) == 0                       # lần đầu: chỉ đặt mốc
    nc.kho.ghi("hr", "quet.xong", {})
    assert mot_vong(nc) == 0                       # ảnh đầu của dự án: làm mốc, không báo
    bd.beads["hr-1"] = bead("hr-1", labels=["cot:cho-review"], updated_at="2026-10-13T02:00:00Z")
    nc.kho.ghi("hr", "quet.xong", {})
    assert mot_vong(nc) == 1
    assert da_gui == ["[tram] hr · 1 việc chờ review (hr-1) → https://may-b.tail.ts.net/"]
    assert mot_vong(nc) == 0


def test_mot_vong_gui_loi_thi_vong_sau_gui_lai(tmp_path, capsys):
    loi, da_gui = {"con": True}, []

    def gui(van_ban):
        if loi["con"]:
            raise LoiTelegram("Gửi Telegram lỗi: ***")
        da_gui.append(van_ban)

    nc = _nc(tmp_path, BdGia(), gui)
    mot_vong(nc)
    nc.kho.ghi("_tram", "estop.bat", {"ly_do": "x"})
    assert mot_vong(nc) == 0 and "Gửi Telegram lỗi" in capsys.readouterr().err
    assert json.loads((tmp_path / "bao-tin" / "moc.json").read_text())["sau_id"] == 1   # mốc tiến, tin nằm ở hàng chờ
    loi["con"] = False
    assert mot_vong(nc) == 1 and da_gui == ["[tram] estop BẬT → https://may-b.tail.ts.net/"]
    assert mot_vong(nc) == 0


def test_chay_mai_nuot_loi_tung_vong(monkeypatch, capsys):
    import tram.bao_tin.vong as v
    dem = []
    monkeypatch.setattr(v, "mot_vong", lambda nc: (dem.append(1), 1 / 0))
    v.chay_mai(object(), nghi=lambda s: None, so_vong=2)
    assert len(dem) == 2 and "ZeroDivisionError" in capsys.readouterr().err


def test_tao_ngu_canh_that_thieu_chat_id_la_none(tram_home_tam):
    assert tao_ngu_canh_that() is None
