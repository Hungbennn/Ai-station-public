"""2f P3: GET /api/cai-dat, /api/san-sang — chỉ Đại ca, Host + CSP, không lộ bí mật, không chạy lệnh có tác dụng phụ."""
import json
import subprocess
from pathlib import Path

from api_gia import DAI_CA, LOGIN, MAY_B, tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from test_he_thong import ChayGia
from test_san_sang import BEADS
from tram.api.app import tao_app
from tram.cau_hinh.tram import CauHinhTelegram, CauHinhTram
from tram.suy import he_thong, san_sang
from tram.suy.he_thong import DocHeThong
from tram.suy.san_sang import BangSanSang

H = {"Tailscale-User-Login": LOGIN}
EMAIL_2, CHAT_ID, BAM = "bi-mat-2@example.com", "CHAT-987654321", "ab" * 32
BI_MAT_SEC = "BI-MAT-STDOUT \"acct\"<blob>=\"tram\" pid = 777"
DU_AN_YAML = ('ten: hr\nduong_dan: "{home}/Developer/hr-thu"\ngitnexus_repo: hr-graph\ntu_khoa_khach: [KHACH-BI-MAT]\n'
              'lenh_cho_phep: ["uv run pytest -q"]\nmoi_truong_kiem: {{file: "{mt}", dich: ".env.testing"}}\n'
              'hang_rao: {{tien: {{tu_khoa: [hoàn tiền, thuế], duong_dan: ["*Fin/*"]}}}}\n')

def _dung(tmp_path, monkeypatch, *, du_an_yaml=DU_AN_YAML, cau_hinh=f"ma_dai_ca_sha256: {BAM}\n"):
    lenh = []

    def cam(*a, **k):                                         # mọi lệnh thật đều bị ghi lại rồi chặn
        lenh.append(a)
        raise AssertionError("không được chạy lệnh thật")
    monkeypatch.setattr(subprocess, "run", cam)
    monkeypatch.setattr(subprocess, "Popen", cam)
    (tmp_path / "mt.env").write_text("DB_PASSWORD=MT-BI-MAT")
    (tmp_path / "repo" / "du-an").mkdir(parents=True)
    (tmp_path / "repo" / "du-an" / "hr.yaml").write_text(du_an_yaml.format(home=Path.home(), mt=tmp_path / "mt.env"))
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo"))
    (tmp_path / "tram-home").mkdir(exist_ok=True)
    (tmp_path / "tram-home" / "cau-hinh.yaml").write_text(cau_hinh)
    chay = ChayGia({"tram-telegram-bot-token": (0, BI_MAT_SEC), "gui/501/vn.tram.api": (0, "state = running\npid=777")})
    monkeypatch.setattr(he_thong, "_CHUNG", DocHeThong(chay=chay, home=tmp_path, uid=501))
    monkeypatch.setattr(san_sang, "CHUNG", BangSanSang(doc_bead=lambda: BEADS, which=lambda l: l != "ollama" or None))
    pt = tao_pt(tmp_path, {"hr": BdGia([])})
    pt.cau_hinh = CauHinhTram(dai_ca_logins=(LOGIN, EMAIL_2), ten_may_b=MAY_B,
                              telegram=CauHinhTelegram(CHAT_ID, "23:00-07:00"), dashboard_url="https://x.ts.net")
    return tao_app(pt), chay, lenh


def test_403_khi_khong_phai_dai_ca(tmp_path, monkeypatch):
    app, chay, lenh = _dung(tmp_path, monkeypatch)
    for h in ({}, {"Tailscale-User-Login": "nguoi-la@example.com"}, {**DAI_CA, "Tailscale-User-Login": "x@y.z"}):
        for duong in ("/api/cai-dat", "/api/san-sang"):
            r = goi(app, "GET", duong, headers=h)
            assert r.status == 403 and "content-security-policy" in r.headers and "Đại ca" in r.json()["detail"]
    assert chay.argv == [] and lenh == []


def test_421_host_la_va_csp(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    for duong in ("/api/cai-dat", "/api/san-sang"):
        r = goi(app, "GET", duong, headers={**H, "Host": "rebind.evil.example"})
        assert r.status == 421 and "content-security-policy" in r.headers
        r = goi(app, "GET", duong, headers=H)                 # GET không cần X-Tram / Origin
        assert r.status == 200 and "default-src 'none'" in r.headers["content-security-policy"]


def test_cai_dat_hinh_json(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    j = goi(app, "GET", "/api/cai-dat", headers=H).json()
    assert set(j) == {"du_an", "dich_vu", "telegram", "co", "keychain", "loi_cau_hinh"} and j["loi_cau_hinh"] == []
    assert j["du_an"] == [{"ten": "hr", "duong_dan": "~/Developer/hr-thu", "nhanh_chinh": "main",
                           "gitnexus": "hr-graph", "lenh_cho_phep": ["uv run pytest -q"], "moi_truong_kiem": True,
                           "hang_rao": [{"loai": "tien", "tu_khoa": ["hoàn tiền", "thuế"], "duong_dan": ["*Fin/*"]}],
                           "loi": None}]
    assert j["dich_vu"][0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": False, "dang_chay": True,
                               "kiem_duoc": True} and len(j["dich_vu"]) == 5
    assert j["telegram"]["co_chat_id"] is True and j["telegram"]["gio_yen_lang"] == "23:00-07:00" \
        and "cờ đỏ" in j["telegram"]["loai_tin"]
    co = {c["khoa"]: c for c in j["co"]}
    assert all(set(c) == {"khoa", "bat", "gia_tri", "ghi_chu"} and c["ghi_chu"] for c in j["co"])
    assert co["estop"]["bat"] is False and co["giao_viec.bat"]["bat"] is False and co["ma_dai_ca"]["bat"] is True
    assert co["dai_ca_logins"]["gia_tri"] == "2" and co["ma_dieu_phoi"]["bat"] is False
    assert co["cach_ly.kenh_ghi"]["gia_tri"] == "header" and co["cong_bo.phuong_an"]["gia_tri"] is None
    assert [k["trang_thai"] for k in j["keychain"]] == ["co", "khong_ro", "khong_ro", "khong_ro"]
    # G15/G13: kênh hợp lệ dùng enum unix-socket, không phải unix; kiểm cả hai trạng thái.
    from tram.cau_hinh.cach_ly import CauHinhCachLy
    from tram.suy import cai_dat as suy_cai_dat
    for kenh, bat in (("header", False), ("unix-socket", True)):
        monkeypatch.setattr(suy_cai_dat, "nap_cau_hinh_cach_ly", lambda: CauHinhCachLy(kenh_ghi=kenh))
        cs = {c["khoa"]: c for c in goi(app, "GET", "/api/cai-dat", headers=H).json()["co"]}
        assert cs["cach_ly.kenh_ghi"]["gia_tri"] == kenh and cs["cach_ly.kenh_ghi"]["bat"] is bat


def test_khong_lo_bi_mat(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    s = "".join(goi(app, "GET", d, headers=H).body.decode() for d in ("/api/cai-dat", "/api/san-sang"))
    for x in ("KHACH-BI-MAT", "MT-BI-MAT", "mt.env", EMAIL_2, LOGIN, CHAT_ID, BAM, "BI-MAT-STDOUT", "777",
              "MO-TA-BI-MAT", "NOTES-BI-MAT", "x.ts.net", MAY_B, "gui/501", "find-generic-password"):
        assert x not in s, x


def test_loi_cau_hinh_khong_hong_ca_trang(tmp_path, monkeypatch):
    hong = "dai_ca_logins: [lo@x.vn]\ngiao_viec: {bat: [\n"           # YAML hỏng: lỗi không được chép dòng có email
    app, _, _ = _dung(tmp_path, monkeypatch, du_an_yaml="ten: hr\ntu_khoa_khach: [KHACH-BI-MAT\n", cau_hinh=hong)
    r = goi(app, "GET", "/api/cai-dat", headers=H)
    j, co = r.json(), {c["khoa"]: c for c in r.json()["co"]}
    assert r.status == 200 and co["giao_viec.bat"]["bat"] is None and co["cong_bo.phuong_an"]["bat"] is None
    assert co["estop"]["bat"] is False and len(j["dich_vu"]) == 5 and len(j["loi_cau_hinh"]) == 3
    assert all(len(x) <= 200 for x in j["loi_cau_hinh"]) and j["du_an"][0]["loi"] == "YAML hỏng ở dòng 3"
    assert "lo@x.vn" not in r.body.decode() and "KHACH-BI-MAT" not in r.body.decode()
    from tram.suy.cai_dat import mo_ta_loi

    for e in (ValueError("TEN-BI-MAT"), FileNotFoundError("/private/ENV-BI-MAT"), RuntimeError("NOI-DUNG-BI-MAT")):
        loi = mo_ta_loi(e)
        assert loi and "BI-MAT" not in loi and "/private/" not in loi


def test_khong_goi_lenh_co_tac_dung_phu(tmp_path, monkeypatch):
    app, chay, lenh = _dung(tmp_path, monkeypatch)
    for _ in range(2):
        for duong in ("/api/san-sang", "/api/cai-dat"):
            assert goi(app, "GET", duong, headers=H).status == 200
    assert lenh == []                                         # không có subprocess thật nào
    assert all(a[:2] in (["launchctl", "print"], ["security", "find-generic-password"]) for a in chay.argv)
    assert len(chay.argv) == 9                                # bộ đệm: các lần sau không chạy lại
    s = json.dumps(chay.argv)
    assert "sudo" not in s and "kiem" not in s and "-w" not in s and all(a[0] != "tram" for a in chay.argv)
    j = goi(app, "GET", "/api/san-sang", headers=H).json()
    assert set(j) == {"muc", "dem", "doc_luc", "loi"} and j["loi"] is None
    assert [m["ma"] for m in j["muc"] if m["nguon"] == "bead"] == ["bs-1", "bs-2", "bs-3", "bs-5", "bs-6"]


def test_estop_post_van_can_x_tram(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)                  # route chủ: thêm /api/cai-dat không nới POST estop
    than = {"ly_do": "thử", "ma_thao_tac": "ma-estop-0001", "expected_version": ""}
    for duong in ("/api/chu/estop", "/api/chu/tiep-tuc"):
        assert goi(app, "POST", duong, json_body=than, headers=H).status == 403
