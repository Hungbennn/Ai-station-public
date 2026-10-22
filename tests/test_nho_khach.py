import io
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace as NS

import pytest

from tram.nho.khach import LoiNhoKhach, doc_token, goi_nho, nho_lai_http, tao_nho_lai


class TraLoi(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def mo_tra(du_lieu, ghi=None):
    def mo(yc, timeout):
        if ghi is not None:
            ghi.append((yc.full_url, dict(yc.header_items()), json.loads(yc.data), timeout))
        if isinstance(du_lieu, Exception):
            raise du_lieu
        return TraLoi(json.dumps(du_lieu).encode())
    return mo


def test_doc_token_chi_tu_keychain_khong_doc_bien_moi_truong(monkeypatch):
    monkeypatch.setenv("TRAM_NHO_TOKEN", "khong-duoc-dung")
    goi = []
    assert doc_token(chay=lambda c, **k: goi.append(c) or NS(returncode=0, stdout="xyz\n")) == "xyz"
    assert goi[0] == ["security", "find-generic-password", "-s", "tram-nho-token", "-w"]
    assert doc_token(chay=lambda c, **k: NS(returncode=44, stdout="")) is None


def test_nho_lai_gui_bearer_vung_cap_va_timeout_2s():
    ghi = []
    kq = nho_lai_http("hoa hồng", ["/du-an/hr", "/vai/cham-cot", "/chung"], token="tk",
                      mo=mo_tra({"ky_uc": [{"id": "m-1", "noi_dung": "A", "pham_vi": "/chung", "nguon": "x"}]}, ghi))
    assert kq == [{"id": "m-1", "noi_dung": "A", "pham_vi": "/chung"}]          # bỏ mọi trường khác
    url, hdr, than, cho = ghi[0]
    assert url == "http://127.0.0.1:7710/nho-lai" and hdr["Authorization"] == "Bearer tk" and cho == 2.0
    assert than == {"truy_van": "hoa hồng", "vung_cap": ["/du-an/hr", "/vai/cham-cot", "/chung"]}


@pytest.mark.parametrize("loi", [
    urllib.error.URLError("refused"), TimeoutError(), urllib.error.HTTPError("u", 401, "x", {}, None)])
def test_loi_mang_thanh_loi_nho_khach(loi):
    with pytest.raises(LoiNhoKhach) as e:
        goi_nho("/nho-lai", {}, token="bi-mat", mo=mo_tra(loi))
    assert "bi-mat" not in str(e.value)


@pytest.mark.parametrize("tra", [{}, {"ky_uc": "x"}, {"ky_uc": [{"id": 1}]}, {"ky_uc": [3]}])
def test_du_lieu_sai_dang(tra):
    with pytest.raises(LoiNhoKhach):
        nho_lai_http("q", ["/chung"], token="t", mo=mo_tra(tra))


def test_tao_nho_lai_khong_token_thi_none():
    assert tao_nho_lai(chay=lambda c, **k: NS(returncode=44, stdout="")) is None
    f = tao_nho_lai(chay=lambda c, **k: NS(returncode=0, stdout="t"), mo=mo_tra({"ky_uc": []}))
    assert f("q", ["/chung"]) == []


@pytest.mark.parametrize("tra", [[], None, {"ky_uc": 5}, {"ky_uc": [{"noi_dung": "A"}]},
                                 {"ky_uc": [{"id": "m-1", "noi_dung": "A", "pham_vi": 7}]}])
def test_json_khong_phai_object_hoac_thieu_truong_thanh_loi_nho_khach(tra):
    """bs-hpc.7: `[]`/`null` từng làm `.get` ném AttributeError lan ra hỏng lượt quét."""
    with pytest.raises(LoiNhoKhach):
        nho_lai_http("q", ["/chung"], token="t", mo=mo_tra(tra))


class NhoGiot:
    """Phản hồi nhỏ giọt: mỗi lần đọc trả 1 byte và tốn 0,3 giây trên đồng hồ tiêm (không ngủ thật)."""
    def __init__(self, dong_ho, than=b'{"ky_uc": []}' + b" " * 100):
        self.dong_ho, self.than, self.so_lan_doc = dong_ho, than, 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        self.so_lan_doc += 1
        self.dong_ho.t += 0.3
        b, self.than = self.than[:1], self.than[1:]
        return b


def test_han_2_giay_la_han_tong_ca_khi_server_nho_giot():
    dong_ho = NS(t=100.0)
    tl = NhoGiot(dong_ho)
    with pytest.raises(LoiNhoKhach):
        nho_lai_http("q", ["/chung"], token="t", mo=lambda yc, timeout: tl, dong_ho=lambda: dong_ho.t)
    assert dong_ho.t - 100.0 <= 2.0 + 0.3 and tl.so_lan_doc <= 7


THAN_THAT = json.dumps({"ky_uc": [{"id": "m-1", "noi_dung": "x", "pham_vi": "/du-an/a/cach-lam"}]}).encode()


@pytest.fixture
def server_that():
    """Server HTTP thật trên 127.0.0.1 (cổng 0); `cau_hinh["dong"]` chọn có gửi `Connection: close` hay không."""
    cau_hinh = {"dong": True}

    class XuLy(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(THAN_THAT)))
            if cau_hinh["dong"]:
                self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(THAN_THAT)

        def log_message(self, *a):
            pass

    sv = ThreadingHTTPServer(("127.0.0.1", 0), XuLy)
    threading.Thread(target=sv.serve_forever, daemon=True).start()
    yield cau_hinh, f"http://127.0.0.1:{sv.server_address[1]}"
    sv.shutdown()
    sv.server_close()


@pytest.mark.parametrize("dong", [True, False], ids=["connection-close", "keep-alive"])
def test_goi_server_http_that_khong_loi_ebadf(server_that, dong):
    """bs-hpc.15: với `Connection: close` http.client đóng socket trước khi đọc thân; settimeout từng ném EBADF."""
    cau_hinh, url = server_that
    cau_hinh["dong"] = dong
    kq = nho_lai_http("q", ["/chung"], token="t", url=url, mo=urllib.request.urlopen)
    assert kq == [{"id": "m-1", "noi_dung": "x", "pham_vi": "/du-an/a/cach-lam"}]
