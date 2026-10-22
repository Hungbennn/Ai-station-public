"""1b-3: một lượt thăng cấp — /chung hoặc /vai, chờ 7 ngày, không lặp, từ chối khi chạm luật của mọi dự án."""
from datetime import datetime, timedelta, timezone

import anthropic
import httpx2
import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import nho_lai
from tram.nho.thang_cap import id_thang_cap
from tram.nho.vong import NguCanhNho, mot_luot
from tram.nho.vong_thang_cap import mot_lan_thang_cap
from tram.su_kien.kho import KhoSuKien

BAY = datetime(2026, 10, 20, 20, 30, tzinfo=timezone.utc)
V1 = (1.0,) + (0.0,) * 15
CHUNG = "Chạy toàn bộ test trước khi bàn giao."
LUAT = {"hr": LuatDuAn(("Pay",), ("Sao Mai",)), "kt": LuatDuAn(("Ledger",), ())}
VAI_SOAN = nap_vai("nho-thang-cap")
ID = id_thang_cap("m-a|m-b")


def soan(noi_dung=CHUNG, ten_rieng=False):
    return tra_loi({"noi_dung": noi_dung, "nhan": ["test"], "co_ten_rieng": ten_rieng})


@pytest.fixture
def nc(tmp_path):
    e = EmbedderGia(vector={CHUNG: V1, "chạy test": V1})
    return NguCanhNho(kho=KhoKyUc(tmp_path / "lancedb", so_chieu=16), embedder=e, client=ClientGia(),
                      kho_sk=KhoSuKien(tmp_path / "sk.db"), nhat_ky=NhatKy(tmp_path / "nk.db"),
                      vai_tach=nap_vai("nho-tach"), vai_gop=nap_vai("nho-gop"), luat_cua=LUAT.__getitem__)


def hai_ban(nc, noi_a="hr: chạy php artisan test trước bàn giao", vai=None):
    for id, du_an, nd in (("m-a", "hr", noi_a), ("m-b", "kt", "kt: chạy pytest trước khi bàn giao")):
        n = {"loai": "ban_giao", "du_an": du_an, **({"vai": vai} if vai else {})}
        nc.kho.them(ky_uc(id, f"/du-an/{du_an}/cach-lam", vector=V1, noi_dung=nd, quan_trong=0.7 if id == "m-a" else 0.4,
                          nguon=(n,)))


def chay(nc, *tra):
    nc.client = ClientGia(*tra)
    return mot_lan_thang_cap(nc, BAY, vai_soan=VAI_SOAN, cac_du_an=lambda: ["hr", "kt", "_tram"])


def su_kien(nc, loai):
    return [s.du_lieu for s in nc.kho_sk.gan_day("_tram", loai, 99)]


def test_thang_cap_vao_chung_cho_7_ngay_roi_tu_co_hieu_luc(nc):
    hai_ban(nc)
    bc = chay(nc, soan())
    assert (bc.cap, bc.thang_cap, bc.tu_choi, bc.bo, bc.loi) == (1, 1, 0, 0, None)
    k = nc.kho.lay([ID])[ID]
    assert (k.pham_vi, k.noi_dung, k.nguon_dai_ca, k.quan_trong) == ("/chung", CHUNG, False, pytest.approx(0.7))
    assert k.nguon == ({"loai": "thang_cap", "id_goc": "m-a", "du_an": "hr"},
                       {"loai": "thang_cap", "id_goc": "m-b", "du_an": "kt"})
    assert (k.tao_luc, k.hieu_luc_tu) == ("2026-10-20T20:30:00Z", "2026-10-27T20:30:00Z")
    assert su_kien(nc, "nho.thang_cap") == [{"id": ID, "pham_vi": "/chung", "id_goc": ["m-a", "m-b"],
                                             "du_an": ["hr", "kt"], "hieu_luc_tu": "2026-10-27T20:30:00Z"}]
    assert [d["id"] for d in su_kien(nc, "nho.ghi")] == [ID]
    assert not any(x.da_xoa for x in nc.kho.lay(["m-a", "m-b"]).values())            # hai bản gốc giữ nguyên
    vung = ["/du-an/khac", "/vai/coder", "/chung"]
    assert nho_lai(nc.kho, nc.embedder, "chạy test", vung, bay_gio=BAY + timedelta(days=6)) == []
    assert [x.id for x in nho_lai(nc.kho, nc.embedder, "chạy test", vung, bay_gio=BAY + timedelta(days=8))] == [ID]


def test_khong_thang_cap_lai_ke_ca_khi_dai_ca_da_xoa_mem(nc):
    hai_ban(nc)
    chay(nc, soan())
    nc.kho.xoa_mem([ID])
    bc = chay(nc)
    assert bc.cap == 0 and nc.client.goi == [] and nc.kho.dem() == 3


def test_ban_goc_cham_luat_cua_du_an_khac_thi_tu_choi_khong_goi_llm(nc):
    hai_ban(nc, noi_a="hr: sửa Ledger thì chạy lại test")
    bc = chay(nc)
    assert (bc.tu_choi, bc.thang_cap) == (1, 0) and nc.client.goi == []
    assert su_kien(nc, "nho.tu_choi") == [{"ly_do": "tên module (Ledger)", "nguon": "thang_cap",
                                           "id_goc": ["m-a", "m-b"]}]
    assert nc.nhat_ky.cac_cap() == {"m-a|m-b": "tu_choi"} and chay(nc).cap == 0


@pytest.mark.parametrize("tra, ly", [(soan("Phí 100k mỗi lần chạy test."), "số tiền (100k)"),
                                     (soan("Như hr, chạy test trước khi bàn giao."), "tên dự án (hr)"),
                                     (soan(ten_rieng=True), "tên khách (LLM báo có tên riêng)")])
def test_noi_dung_soan_cham_luat_hoac_lo_ten_du_an_thi_tu_choi(nc, tra, ly):
    hai_ban(nc)
    bc = chay(nc, tra)
    assert bc.tu_choi == 1 and su_kien(nc, "nho.tu_choi")[0]["ly_do"] == ly and nc.kho.dem() == 2


def test_llm_khong_thay_bai_hoc_chung_thi_bo_khong_thu_lai(nc):
    hai_ban(nc)
    bc = chay(nc, soan(""))
    assert (bc.bo, bc.tu_choi) == (1, 0) and su_kien(nc, "nho.tu_choi") == []
    assert nc.nhat_ky.cac_cap() == {"m-a|m-b": "bo"}


def test_cung_vai_thi_vao_vai(nc):
    hai_ban(nc, vai="coder")
    chay(nc, soan())
    assert nc.kho.lay([ID])[ID].pham_vi == "/vai/coder"


def test_chi_gop_voi_ban_dang_cho(nc):
    hai_ban(nc)
    nc.kho.them(ky_uc("m-hl", "/chung", vector=V1, tao_luc="2026-10-01T00:00:00Z"))           # đang hiệu lực
    nc.kho.them(ky_uc("m-cho", "/chung", vector=V1, tao_luc="2026-10-19T00:00:00Z",
                      hieu_luc_tu="2026-10-26T00:00:00Z", nguon=({"loai": "thang_cap", "id_goc": "m-x"},)))
    bc = chay(nc, soan(), tra_loi({"quyet_dinh": [{"id": "m-cho", "hanh_dong": "thay"}], "noi_dung_gop": "",
                                   "co_ten_rieng": False}))
    assert bc.thang_cap == 1 and len(nc.client.goi) == 2
    assert '"m-hl"' not in nc.client.goi[1]["messages"][0]["content"]
    assert nc.kho.lay(["m-cho"])["m-cho"].da_xoa and not nc.kho.lay(["m-hl"])["m-hl"].da_xoa
    assert su_kien(nc, "nho.gop") == [{"cu": ["m-cho"], "moi": ID}]


def test_claude_loi_hoac_yaml_hong_dung_luot_khong_ghi_so(nc):
    hai_ban(nc)
    bc = chay(nc, anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")))
    assert bc.loi.startswith("APIConnectionError") and nc.nhat_ky.cac_cap() == {} and nc.kho.dem() == 2

    def hong(ten):
        raise ValueError("yaml hỏng")
    nc.luat_cua = hong
    bc = chay(nc)
    assert bc.loi == "ValueError: yaml hỏng" and nc.client.goi == []


def test_crash_sau_nhat_ky_truoc_su_kien_thi_luot_nap_lam_tiep(nc, monkeypatch):
    hai_ban(nc)
    monkeypatch.setattr("tram.nho.vong_thang_cap.ap_dung", lambda *a, **k: (_ for _ in ()).throw(OSError("đĩa")))
    assert chay(nc, soan()).loi == "OSError: đĩa" and nc.kho.lay([ID]) == {}
    monkeypatch.undo()
    mot_luot(nc)                                                  # luồng nạp: làm tiếp thao tác dở
    assert nc.kho.lay([ID])[ID].pham_vi == "/chung" and len(su_kien(nc, "nho.thang_cap")) == 1
    assert chay(nc).cap == 0


def test_xoa_sau_tim_cap_khong_thang_cap(nc, monkeypatch):
    import tram.nho.vong_thang_cap as v
    hai_ban(nc)
    tim = v.tim_cap
    def tim_roi_xoa(*a, **kw):
        ds = tim(*a, **kw)
        nc.kho.xoa_mem([ds[0].a.id])
        return ds
    monkeypatch.setattr(v, "tim_cap", tim_roi_xoa)
    bc = chay(nc, soan())
    assert bc.thang_cap == 0 and nc.client.goi == []


def test_cap_da_ghi_so_sau_tim_khong_lam_lai(nc, monkeypatch):
    import tram.nho.vong_thang_cap as v
    hai_ban(nc)
    tim = v.tim_cap
    def tim_roi_ghi_so(*a, **kw):
        ds = tim(*a, **kw)
        nc.nhat_ky.ghi_cap(ds[0].khoa, "xoa_cung")
        return ds
    monkeypatch.setattr(v, "tim_cap", tim_roi_ghi_so)
    assert chay(nc, soan()).thang_cap == 0
