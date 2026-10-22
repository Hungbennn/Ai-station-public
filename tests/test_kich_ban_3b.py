"""Kịch bản giả lập lát 3b (spec 3 §9.2, §15 mục 2 phần 3b): trạm cấp mã → Mac thợ D dang-ky qua HTTP thật của app
(trong bộ nhớ) → chủ bật khe bằng phiên passkey → nhịp Codex có hạn mức app-server → luật nhận việc → gỡ máy."""
import io
import json
import urllib.error
from contextlib import closing
from datetime import timedelta
from pathlib import Path

import pytest

from api_gia import DAI_CA
from asgi_gia import goi
from passkey_phien_gia import dang_nhap_app
from phieu_gia import de_xuat
from tho_api_gia import tao_tram
from tho_dk_gia import URL, dau_do
from tram.chay_cli.codex.han_muc import han_muc_app_server
from tram.phieu.khe import khe_dang_bat, phien_ban_khe
from tram.phieu.ma_ghep import cap_ma_ghep
from tram.phieu.may import go_may
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram
from tram.tho.ke_hoach_dk import lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe
from tram.tho.thuc_hien_dk import HieuUng, dang_ky_that, ghep_that, thuc_hien_dk

MAU = json.loads((Path(__file__).parent / "du_lieu/codex/app_server_rate_limits.json").read_text(encoding="utf-8"))


class _Ph(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _mo(app):
    def mo(yc, timeout):
        r = goi(app, yc.get_method(), yc.full_url.removeprefix(URL), json_body=json.loads(yc.data),
                headers={k: v for k, v in yc.header_items() if k.lower() == "authorization"})
        if r.status >= 400:
            raise urllib.error.HTTPError(yc.full_url, r.status, "x", {}, io.BytesIO(r.body))
        return _Ph(r.status, r.body)
    return mo


def test_ghep_dang_ky_nhip_codex_roi_go_may(tmp_path):
    hm_hien = [MAU["prolite"]]
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat() if khe == "D/codex-1" else None, dang_ky=False)
    ma = cap_ma_ghep(t.kho(), "D", luc=t.gio[0]).ma
    kh = lap_ke_hoach_dk(URL, [doc_khe("codex-1:codex:coder:Codex 1")], thu_muc_khe=tmp_path / "khe", nho=True,
                         dd=dau_do(tmp_path))
    keychain, mo = {}, _mo(t.app)
    hu = HieuUng(ghep=lambda u, m: ghep_that(u, m, mo=mo), ghi_token=lambda m, tok: keychain.update({m: tok}),
                 dang_ky=lambda u, m, tok, khe: dang_ky_that(u, m, tok, khe, mo=mo), chay=lambda *a, **k: None)
    assert thuc_hien_dk(kh, ma, hu) == "D"
    ch = nap_cau_hinh_tho(kh.tho_yaml)
    assert ch.tram_api == URL and ch.khe_id(ch.khe[0]) == "D/codex-1"
    t.token["D"] = keychain["D"]
    assert [k["khe_id"] for k in t.goi("GET", "/api/tho/ping", "D").json()["khe"]] == ["D/codex-1"]
    with pytest.raises(LoiKhachTram, match="403"):
        ghep_that(URL, ma, mo=mo)                                              # mã đã dùng

    # Passkey: đăng ký thông tin không cấp quyền chạy; chủ phải bật khe qua cửa P (D138).
    with closing(t.kho()) as kho:
        assert not khe_dang_bat(kho, "D/codex-1")
        v = phien_ban_khe(kho, "D/codex-1")
    bat = {"ma_thao_tac": "ma-bat-khe-d-3b", "expected_version": v}
    assert goi(t.app, "POST", "/api/khe/D/codex-1/bat", json_body=bat, headers=DAI_CA).status == 403
    dang_nhap_app(t.app, tmp_path / "pk-test.db")
    assert goi(t.app, "POST", "/api/khe/D/codex-1/bat", json_body=bat, headers=DAI_CA).status == 200
    with closing(t.kho()) as kho:
        assert khe_dang_bat(kho, "D/codex-1")

    def nhip():
        hm = han_muc_app_server(hm_hien[0], khe_id="D/codex-1", bay_gio=t.gio[0])
        r = t.goi("POST", "/api/tho/nhip", "D", json_body={"khe_id": "D/codex-1", "buoc_tho": "ranh",
                                                         "han_muc": hm.model_dump()}, headers={"Cookie": ""})
        assert r.status == 200                                               # token máy đủ, không cần phiên người
        return r.json()
    assert nhip() == {"tiep_tuc": True, "phieu": None}                          # tuần đã biết 91% → không nhận (H4)
    hm_hien[0] = MAU["plus"]
    t.toi(seconds=30)
    assert nhip()["phieu"]["khe_id"] == "D/codex-1"                             # 62% / 12,5% → nhận phiếu
    with closing(t.kho()) as kho:
        ghi = kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'khe.han_muc' ORDER BY id").fetchall()
        assert [json.loads(x[0])["nguon"] for x in ghi] == ["app-server", "app-server"]
        assert go_may(kho, "D", luc=t.gio[0] + timedelta(minutes=1)) == 1
    assert t.goi("GET", "/api/tho/ping", "D").status == 401
