"""Kênh API ghi (spec 2 §4 mục 2b, H9): ở chế độ `unix-socket`, header danh tính gửi qua TCP bị từ chối."""
import socket
import tempfile
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from tram.api import kenh_ghi
from tram.api.kenh_ghi import KHOA_SCOPE, KenhUnix, chay_api, chay_hai_cong

DUYET = "/api/phe-duyet/hr/hr-1/duyet"


def test_mac_dinh_header_giu_hanh_vi_2a(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    assert goi(app, "POST", DUYET, json_body={}, headers=DAI_CA).status != 403      # qua kênh, tới kiểm dự án/thân


def test_p_can_passkey_tren_ca_tcp_va_socket(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    app.state.kenh_ghi = "unix-socket"
    dung = {**DAI_CA, "Cookie": app.state.cookie_test}
    thieu = {**DAI_CA, "Cookie": ""}
    for client in (app, KenhUnix(app)):
        r = goi(client, "POST", DUYET, json_body={}, headers=thieu)
        assert r.status == 403 and r.json()["detail"] == "Cần phiên passkey"
        assert goi(client, "POST", DUYET, json_body={}, headers=dung).status == 422
        r = goi(client, "POST", DUYET, json_body={}, headers={"Cookie": app.state.cookie_test})
        assert r.status == 403


def test_chay_hai_cong_that_qua_unix_socket():
    app = FastAPI()

    @app.get("/kenh")
    def kenh(request: Request) -> dict:
        return {"kenh": request.scope.get(KHOA_SCOPE)}
    sock, dung = Path(tempfile.mkdtemp(prefix="tk")) / "api" / "a.sock", threading.Event()
    th = threading.Thread(target=chay_hai_cong, args=(app,), kwargs={"host": "127.0.0.1", "cong": 0, "socket": sock,
                                                                     "dung": dung}, daemon=True)
    th.start()
    het = time.monotonic() + 10
    while not sock.exists() and time.monotonic() < het:
        time.sleep(0.05)
    s = socket.socket(socket.AF_UNIX)
    s.connect(str(sock))
    s.sendall(b"GET /kenh HTTP/1.1\r\nHost: may-b\r\nConnection: close\r\n\r\n")
    tra = b""
    while chunk := s.recv(4096):
        tra += chunk
    s.close()
    assert tra.startswith(b"HTTP/1.1 200") and b'"kenh":"unix"' in tra
    assert oct(sock.parent.stat().st_mode)[-3:] == "700" and app.state.kenh_ghi == "unix-socket"
    dung.set()
    th.join(timeout=10)
    assert not th.is_alive()


def test_chay_api_theo_cau_hinh(tram_home_tam, monkeypatch):
    import uvicorn
    goi_ = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: goi_.append(("tcp", kw["port"])))
    monkeypatch.setattr(kenh_ghi, "chay_hai_cong", lambda app, **kw: goi_.append(("hai", kw["socket"])))
    chay_api(FastAPI(), host="127.0.0.1", cong=7700)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {kenh_ghi: unix-socket}\n")
    chay_api(FastAPI(), host="127.0.0.1", cong=7700)
    assert goi_ == [("tcp", 7700), ("hai", tram_home_tam / "api" / "api.sock")]
