"""Hook đèn Điều phối trên máy A (plan 2e Task 3, G15–G19, G23): không mạng thật, không Keychain thật, không đụng
~/.claude thật."""
import ast
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from tram.duong_dan import goc_repo

THU_MUC = goc_repo() / "may-a" / "hook-dieu-phoi"
KICH_BAN = THU_MUC / "hook_dieu_phoi.py"
MA, URL = "ma-dieu-phoi-" + "z" * 40, "https://may-b.tail.ts.net"
_spec = importlib.util.spec_from_file_location("hook_dieu_phoi", KICH_BAN)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)


class MoGia:
    def __init__(self, loi=None):
        self.goi, self.loi = [], loi

    def __call__(self, req, timeout):
        self.goi.append((req, timeout))
        if self.loi:
            raise self.loi
        return io.BytesIO(b'{"ghi": true}')


def vao(su_kien="UserPromptSubmit", **them):
    return io.StringIO(json.dumps({"hook_event_name": su_kien, "session_id": "phien-1", "cwd": "/Users/x/hr",
                                   "prompt": "lương tháng 10 của khách", **them}))


def test_gui_dung_yeu_cau_va_khong_lo_noi_dung_phien():
    mo = MoGia()
    assert hook.chay(vao(), {"TRAM_DIEU_PHOI_URL": URL + "/"}, mo=mo, lay=lambda _: MA) == 0
    ((req, timeout),) = mo.goi
    assert (req.full_url, req.get_method(), timeout) == (URL + "/api/dieu-phoi/nhip", "POST", 2)
    h = {k.lower(): v for k, v in req.header_items()}
    assert (h["authorization"], h["x-tram"], h["origin"]) == (f"Bearer {MA}", "1", URL)
    assert json.loads(req.data) == {"su_kien": "UserPromptSubmit",
                                    "phien": hashlib.sha256(b"phien-1").hexdigest()[:16]}
    assert b"luong" not in req.data and "lương".encode() not in req.data and b"/Users" not in req.data


def test_im_lang_khi_loi_mang_dau_vao_la_hoac_thieu_cau_hinh():
    env = {"TRAM_DIEU_PHOI_URL": URL}
    for loi in (urllib.error.URLError("tắt Tailscale"), TimeoutError(), urllib.error.HTTPError(URL, 401, "x", {},
                                                                                                None)):
        assert hook.chay(vao("Stop"), env, mo=MoGia(loi), lay=lambda _: MA) == 0
    mo = MoGia()
    for stdin, e in ((io.StringIO("không phải json"), env), (io.StringIO("[1]"), env), (vao("PreToolUse"), env),
                     (vao(session_id=7), env), (vao(), {"TRAM_DIEU_PHOI_URL": "http://may-b"}),
                     (vao(), {"TRAM_DIEU_PHOI_URL": URL + "/api"}),
                     (vao(), {"TRAM_DIEU_PHOI_URL": "https://u@may-b"}), (vao(), {})):
        assert hook.chay(stdin, e, mo=mo, lay=lambda _: MA) == 0
    assert hook.chay(vao(), env, mo=mo, lay=lambda _: None) == 0
    assert mo.goi == []


def test_lay_ma_tu_keychain_rieng_khong_qua_argv():
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, 0, MA + "\n", "")
    assert hook.lay_ma({"TRAM_DIEU_PHOI_MA": " " + MA + " "}, chay=chay) == MA and goi == []
    assert hook.lay_ma({"TRAM_DAI_CA_MA": "ma-dai-ca-" + "y" * 40}, chay=chay) == MA      # không dùng mã Đại ca
    assert goi == [["/usr/bin/security", "find-generic-password", "-s", "tram-dieu-phoi-ma", "-w"]]
    assert hook.lay_ma({}, chay=lambda a, **k: subprocess.CompletedProcess(a, 44, "", "khong co")) is None

    def hong(argv, **kw):
        raise FileNotFoundError(argv[0])
    assert hook.lay_ma({}, chay=hong) is None


def test_khong_proxy_khong_theo_chuyen_huong(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:3128")
    assert any(isinstance(x, urllib.request.ProxyHandler) for x in urllib.request.build_opener().handlers)
    xu_ly = hook.mo_mac_dinh().__self__.handlers
    assert not any(isinstance(x, urllib.request.ProxyHandler) for x in xu_ly)               # bỏ proxy của môi trường
    assert [type(x) for x in xu_ly if isinstance(x, urllib.request.HTTPRedirectHandler)] == [
        hook.KhongChuyenHuong]
    assert hook.KhongChuyenHuong().redirect_request(None, None, 302, "x", {}, "https://khac/") is None


def test_han_toan_bo_khi_mot_buoc_treo():
    bat_dau = time.monotonic()
    assert hook.chay_co_han(vao(), {}, han=0.2, viec=lambda *_: time.sleep(5)) == 0
    assert time.monotonic() - bat_dau < 1
    assert hook.HAN_TOAN_BO < 5                                                            # dưới `timeout: 5`


def test_chay_that_thoat_0_khong_in_gi_khi_tram_khong_voi_toi(tmp_path):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "TRAM_DIEU_PHOI_URL": "https://127.0.0.1:9",
           "TRAM_DIEU_PHOI_MA": MA}                  # cổng 9 cục bộ: bị từ chối ngay, không ra mạng; không Keychain
    bat_dau = time.monotonic()
    kq = subprocess.run([sys.executable, "-I", str(KICH_BAN)], input=vao().getvalue(), capture_output=True,
                        text=True, env=env, timeout=10)
    assert (kq.returncode, kq.stdout, kq.stderr) == (0, "", "") and time.monotonic() - bat_dau < 5


def test_python_3_9_va_mau_settings():
    ast.parse(KICH_BAN.read_text(encoding="utf-8"), feature_version=(3, 9))
    mau = json.loads((THU_MUC / "settings.mau.json").read_text(encoding="utf-8"))
    assert set(mau["hooks"]) == {"SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"}
    for nhom in mau["hooks"].values():
        ((lenh,),) = [x["hooks"] for x in nhom]
        assert "hook_dieu_phoi.py" in lenh["command"] and 0 < lenh["timeout"] <= 5
    assert set(mau["env"]) == {"TRAM_DIEU_PHOI_URL"} and mau["env"]["TRAM_DIEU_PHOI_URL"].startswith("https://")
    huong_dan = (THU_MUC / "HUONG-DAN.md").read_text(encoding="utf-8")
    assert "tram-dieu-phoi-ma" in huong_dan and "dat-ma-dieu-phoi" in huong_dan and "Terminal.app" in huong_dan
    assert "tram-dai-ca-ma" not in huong_dan and "Gộp" in huong_dan
