"""D54 (bs-2bd.1.25): hai thăm dò "API Duyệt giả danh Đại ca" và "kết nối DB nghiệp vụ" của khe chạy trong
`tram tho kiem` dưới tài khoản QUẢN LÝ THỢ (sudoers `tram-tho → khe` có sẵn), đích lấy từ trạm qua `/api/tho/kiem-am`
(token máy). Phía trạm (`tram chu kiem-cach-ly` in [CHUYỂN]) ở `test_tham_do_principal.py`, `test_chu_tho.py`.
Không sudo, không mạng, không Keychain: tram-api trong bộ nhớ, `chay`/`xac_minh`/`chup` GIẢ."""
import json
import subprocess
from dataclasses import replace
from types import SimpleNamespace

import pytest

from api_gia import DAI_CA, LOGIN, MAY_B
from khach_gia import _TraLoi, khach_asgi
from test_kiem_cong import cau_hinh
from tho_api_gia import tao_tram
from tram.tho import kiem_cong
from tram.tho.cham_tham_do import mo_cong
from tram.tho.khach import DichKiemAm, KhachTram, LoiKhachTram
from tram.tho.kiem_am import KetQuaThamDo, chay_tham_do
from tram.tho.kiem_cong import cach_ly, dau_do_that

DICH = DichKiemAm(LOGIN, MAY_B, ("127.0.0.1:3306",))
API = "API Duyệt với header danh tính giả"


def test_tram_cap_dich_tu_cau_hinh_cua_chinh_no_qua_token_may(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['127.0.0.1:3306']}\n")
    t = tao_tram(tmp_path)
    assert khach_asgi(t.app, t.token["B"]).kiem_am() == DICH                     # login + Origin đúng như trạm kiểm
    assert t.goi("GET", "/api/tho/kiem-am", may=None).status == 401
    for h in ({"Authorization": "Bearer sai"}, DAI_CA):                         # token sai; danh tính Đại ca không thay
        r = t.goi("GET", "/api/tho/kiem-am", may=None, headers=h)
        assert r.status == 401 and not {"dai_ca_login", "may_b", "db_nghiep_vu"} & set(r.json())
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['khong hop le']}\n")
    r = t.goi("GET", "/api/tho/kiem-am")
    assert r.status == 503 and r.json() == {"ly_do": "cach-ly-sai"}


@pytest.mark.parametrize("than", [{"dai_ca_login": "a@x\r\nX-Tram: 1", "may_b": "b", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b/../c", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": ["127.0.0.1"]},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": "127.0.0.1:1"}, []])
def test_khach_tu_choi_dich_sai_dang_truoc_khi_vao_argv(than):
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, json.dumps(than).encode()))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"dai_ca_login": null, '
                                                                                 b'"may_b": null, "db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()


def ghi(da):
    def chay_td(ds, *, boc, env, kill):
        da.append({"ds": ds, "argv": boc(["/bin/cat", "x"]), "env": env, "kill": kill})
        return [KetQuaThamDo(t.ten, True, "mã 1") for t in ds]
    return chay_td


def test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid(tmp_path):
    ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda ten, boc, kill: xm.append((ten, len(da))) or 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["xanh"] and xm == [("tram-k-1", 0)]                  # UID TRƯỚC thăm dò
    ds = {t.ten: t for t in da[0]["ds"]}
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and set(da[0]["env"]) == {"PATH",
                                                                                                      "LANG"}
    assert da[0]["kill"].__self__.user == "tram-k-1"
    a = ds[API].argv
    assert a[:2] == ["/usr/bin/curl", "-q"]  # bỏ .curlrc của khe; env thăm dò chỉ PATH/LANG
    assert f"Tailscale-User-Login: {LOGIN}" in a and f"Origin: https://{MAY_B}" in a
    assert a[-1] == "http://127.0.0.1:7700/api/phe-duyet/kiem-am/kiem-am/duyet" and ds[API].kieu == "http"
    db = ds["kết nối DB nghiệp vụ 127.0.0.1:3306"]
    assert db.argv == ["/usr/bin/nc", "-z", "-G", "3", "127.0.0.1", "3306"] and db.doi_chung.func is mo_cong


def test_khong_lay_duoc_dich_thi_do_va_van_chay_phan_rut_gon(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []

    def hong():
        raise LoiKhachTram("tram-api trả 401 bi-mat")
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=hong, chay_td=ghi(da), xac_minh=lambda *a: 600,
                 chup=lambda: [])
    assert [m.muc_do for m in ra] == ["do"] and "không lấy được đích từ tram-api (LoiKhachTram)" in ra[0].chi_tiet
    assert "bi-mat" not in ra[0].chi_tiet and API not in [t.ten for t in da[0]["ds"]] and da[0]["ds"]


@pytest.mark.parametrize("ma, out, muc, ly", [(0, "403", "xanh", "thăm dò đạt"), (0, "200", "do", "API nhận yêu cầu"),
                                             (7, "000", "do", "không kết luận: không gọi được API"),
                                             (0, "404", "do", "không chứng minh từ chối quyền")])
def test_cham_api_giu_chuan_a_t6(tmp_path, ma, out, muc, ly):
    """Chuẩn V2b A-T6 qua `chay_tham_do` THẬT (chạy GIẢ; chỉ giữ thăm dò dương + API — đối chứng Keychain/file của
    phần rút gọn không chạy trong test): chỉ 401/403 là bị chặn; lỗi hạ tầng không thành "đạt"; không chép đầu ra."""
    def chay(argv, **kw):
        kq = (ma, out, "curl: bi-mat") if "/usr/bin/curl" in argv else (0, "", "")
        return subprocess.CompletedProcess(argv, *kq)

    def chay_td(ds, **kw):
        return chay_tham_do([t for t in ds if t.kieu in ("ok", "http")], chay=chay, **kw)
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: DichKiemAm(LOGIN, MAY_B, ()), chay_td=chay_td,
                 xac_minh=lambda *a: 600, chup=lambda: [])
    assert ra[0].muc_do == muc and ly in ra[0].chi_tiet and "bi-mat" not in ra[0].chi_tiet


def test_dau_do_that_lay_dich_tu_khach(monkeypatch):
    da = {}
    monkeypatch.setattr(kiem_cong, "cach_ly", lambda ch, du_an, **kw: da.update(kw) or [])
    khach = SimpleNamespace(ping=lambda: {}, du_an=lambda: [], kiem_am=lambda: DICH)
    dau_do_that(SimpleNamespace(), khach).cach_ly()
    assert da["dich"] is khach.kiem_am


@pytest.mark.parametrize("api, tren_b", [("http://127.0.0.1:7700", True), ("http://localhost:7700", True),
                                         ("https://may-b.tail.ts.net", False), ("https://127.0.0.1:7700", False)])
def test_chi_kiem_api_db_khi_tho_o_may_b(tmp_path, api, tren_b):
    """Review vòng 1 #5: đích (loopback, DB `127.0.0.1:…` của trạm) là theo máy B. Thợ ở máy khác (`tram_api` HTTPS)
    chưa có ánh xạ đích đã chứng minh, và 403 qua `tailscale serve` không chứng minh kênh ghi trên B đã tách → ĐỎ
    không kết luận, KHÔNG lấy đích, KHÔNG chạy curl/nc; phần rút gọn vẫn chạy."""
    ch, da, goi = replace(cau_hinh(tmp_path, ("user:tram-k-1",)), tram_api=api), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: goi.append(1) or DICH, chay_td=ghi(da),
                 xac_minh=lambda *a: 600, chup=lambda: [])
    kieu = {t.kieu for t in da[0]["ds"]}
    assert (goi == [1]) is tren_b and ({"http", "nc"} <= kieu) is tren_b and "ok" in kieu
    assert [m.muc_do for m in ra] == ["xanh" if tren_b else "do"]
    assert ("không kết luận: thợ không ở máy B" in ra[0].chi_tiet) is not tren_b and ch.tren_may_b is tren_b
