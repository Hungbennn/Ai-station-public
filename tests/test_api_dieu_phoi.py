"""`POST /api/dieu-phoi/nhip` — đường ghi riêng của hook máy A (spec 2 §4, §5.5; plan 2e Task 2, G3–G13, G23)."""
from contextlib import closing

from api_gia import DAI_CA, MAY_B, tao_app_gia
from asgi_gia import goi
from tram.api.app import CAC_TUYEN
from tram.api.dieu_phoi import GioiHan
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop
from tram.chu.ma_dieu_phoi import ghi_bam
from tram.nho import ma_dai_ca
from tho_api_gia import tao_tram
from tram.su_kien.kho import KhoSuKien

MA, MA_DAI_CA = "ma-dieu-phoi-" + "z" * 40, "ma-dai-ca-" + "y" * 40
DUONG = "/api/dieu-phoi/nhip"
H = {**DAI_CA, "Authorization": f"Bearer {MA}"}
STOP = {"su_kien": "Stop", "phien": "a" * 16}
THAN = {"/api/ghep-may": {"ma": MA[:64]}}                     # qua lược đồ → xác thực


def dung(tmp_path, *, dat_ma=True):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DAI_CA))            # ~/.tram tạm (conftest: TRAM_HOME); mã Đại ca luôn có
    if dat_ma:
        ghi_bam(ma_dai_ca.bam(MA))
    return tao_app_gia(tmp_path, {})[0]


def nhip_da_ghi(tmp_path) -> list:
    kho = KhoSuKien(tmp_path / "sk.db")
    try:
        return kho.gan_day("_tram", "dieu_phoi.nhip", 10)
    finally:
        kho.close()


def cac_tuyen_ghi(router):
    for r in router.routes:
        if getattr(r, "original_router", None) is not None:                             # router con (include_router)
            yield from cac_tuyen_ghi(r.original_router)
        elif set(getattr(r, "methods", None) or ()) - {"GET", "HEAD"}:
            yield r


def test_nhip_hop_le_ghi_gop_va_den_sang(tmp_path):
    app = dung(tmp_path)
    r = goi(app, "POST", DUONG, json_body=STOP, headers=H)
    assert (r.status, r.json()) == (200, {"ghi": True})
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]                # header an toàn §4 mục 6
    assert goi(app, "POST", DUONG, json_body={**STOP, "su_kien": "UserPromptSubmit"}, headers=H).json() == {
        "ghi": False}                                                                    # gộp trong 60 giây
    (sk,) = nhip_da_ghi(tmp_path)
    assert (sk.du_an, sk.bead_id, sk.tac_nhan, sk.du_lieu) == ("_tram", None, "dai-ca/may-a", STOP)
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert dp["sang"] is True and dp["nhip_cuoi"] == sk.luc
    assert goi(app, "POST", DUONG, json_body={**STOP, "su_kien": "SessionEnd"}, headers=H).json() == {"ghi": True}
    assert {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]["sang"] is False


def test_tu_choi_khi_thieu_hoac_sai_bang_chung(tmp_path):
    app = dung(tmp_path)
    ca = {"không mã": DAI_CA, "sai mã": {**H, "Authorization": "Bearer " + "x" * 50},
          "mã Đại ca": {**H, "Authorization": f"Bearer {MA_DAI_CA}"}, "mã không Bearer": {**H, "Authorization": MA},
          "thiếu header Tailscale": {k: v for k, v in H.items() if k != "Tailscale-User-Login"},
          "login lạ": {**H, "Tailscale-User-Login": "ke-la@example.com"},
          "thiếu X-Tram": {k: v for k, v in H.items() if k != "X-Tram"},
          "Origin lạ": {**H, "Origin": "https://evil.example"}}
    ma_loi = {ten: goi(app, "POST", DUONG, json_body=STOP, headers=h) for ten, h in ca.items()}
    assert {ten: r.status for ten, r in ma_loi.items()} == {
        "không mã": 401, "sai mã": 401, "mã Đại ca": 401, "mã không Bearer": 401, "thiếu header Tailscale": 403,
        "login lạ": 403, "thiếu X-Tram": 403, "Origin lạ": 403}
    assert all(MA not in r.body.decode() and MA_DAI_CA not in r.body.decode() for r in ma_loi.values())
    assert goi(app, "POST", DUONG, json_body=STOP, headers={**H, "host": "evil.example"}).status == 421
    app.state.kenh_ghi = "unix-socket"                                                  # G29 3a-2: TCP bị chặn
    assert goi(app, "POST", DUONG, json_body=STOP, headers=H).status == 403
    assert nhip_da_ghi(tmp_path) == []
    assert goi(KenhUnix(app), "POST", DUONG, json_body=STOP, headers=H).status == 200


def test_chua_dat_ma_dieu_phoi_thi_tu_choi_moi_loi_goi(tmp_path):
    app = dung(tmp_path, dat_ma=False)
    for h in (H, {**H, "Authorization": f"Bearer {MA_DAI_CA}"}):                       # mã Đại ca không thay được
        r = goi(app, "POST", DUONG, json_body=STOP, headers=h)
        assert r.status == 401 and "dat-ma-dieu-phoi" in r.json()["detail"]
    assert nhip_da_ghi(tmp_path) == []


def test_ma_dieu_phoi_khong_mo_route_ghi_nao_khac(tmp_path):
    dung(tmp_path)
    t = tao_tram(tmp_path, token_noi_bo="tok-noi-bo", dang_ky=False)        # có kho phiếu + token máy thật
    chi_ma = {"Authorization": f"Bearer {MA}", "X-Tram": "1", "Origin": f"https://{MAY_B}"}
    tuyen = [r for rt in CAC_TUYEN for r in cac_tuyen_ghi(rt)]
    assert len(tuyen) > 20 and DUONG in {r.path for r in tuyen}
    ma = {f"{pt} {r.path}": goi(t.app, pt, r.path.replace("{", "").replace("}", ""), headers=chi_ma,
                                 json_body=THAN.get(r.path, {})).status
          for r in tuyen if r.path != DUONG for pt in sorted(r.methods - {"HEAD"})}
    assert {k: v for k, v in ma.items() if v not in (401, 403)} == {}
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        assert {s.loai for s in kho.sau_id(0, 100)} == {"may.ghep_sai"}                  # chỉ nhật ký từ chối
    assert not estop.dang_bat() and goi(t.app, "GET", DUONG, headers=H).status == 405


def test_gioi_han_kich_thuoc_luoc_do_va_tan_suat(tmp_path):
    app = dung(tmp_path)
    to = goi(app, "POST", DUONG, json_body={"su_kien": "Stop", "phien": "a" * 600}, headers=H)
    khai = goi(app, "POST", DUONG, json_body=STOP, headers={**H, "content-length": "10000"})
    assert (to.status, khai.status) == (413, 413)
    for than in ({"su_kien": "PreToolUse", "phien": "a" * 16}, {**STOP, "phien": "A" * 16}, {**STOP, "cwd": "/x"},
                 {"su_kien": "Stop"}):
        assert goi(app, "POST", DUONG, json_body=than, headers=H).status == 422
    t = [0.0]
    app.state.gioi_han_dieu_phoi = GioiHan(toi_da=3, dong_ho=lambda: t[0])
    assert [goi(app, "POST", DUONG, json_body=STOP, headers=h).status for h in (DAI_CA, H, H, H)] == [
        401, 200, 200, 429]                                                              # lời gọi hỏng cũng tính
    t[0] = 60.0
    assert goi(app, "POST", DUONG, json_body=STOP, headers=H).status == 200
