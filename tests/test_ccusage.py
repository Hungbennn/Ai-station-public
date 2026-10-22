"""ccusage KHÔNG được gọi thật — `chay` giả trả JSON mẫu (dạng giả định, chờ chạy thật — plan 2b G6)."""
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from tram.usage.bo_dem import BoDemCcusage
from tram.usage.ccusage import DocCcusage, KetQuaCcusage, doc_json_ccusage

MAU = {"daily": [{"date": "2026-10-12", "inputTokens": 1200, "outputTokens": 300, "cacheCreationTokens": 50,
                  "cacheReadTokens": 9000, "totalTokens": 10550, "totalCost": 0.123456, "modelsUsed": ["x"]}],
       "totals": {"totalCost": 0.123456}}
TU, DEN = date(2026, 10, 12), date(2026, 10, 13)


def _chay(phien_ban="17.2.1", ma=0, ra=json.dumps(MAU), goi=None):
    def chay(argv, **kw):
        if goi is not None:
            goi.append((argv, kw))
        if argv[1] == "--version":
            return subprocess.CompletedProcess(argv, 0, f"{phien_ban}\n", "")
        return subprocess.CompletedProcess(argv, ma, ra, "lỗi\x1b[31m đỏ")
    return chay


def test_doc_json_chuan_hoa_va_tu_choi_dang_la():
    assert doc_json_ccusage(json.dumps(MAU)) == [{"ngay": "2026-10-12", "token_vao": 1200, "token_ra": 300,
                                                  "token_cache_doc": 9000, "token_cache_ghi": 50,
                                                  "chi_phi_usd": 0.1235}]
    assert doc_json_ccusage('{"daily": [{"date": "2026-10-12"}]}')[0]["token_vao"] == 0
    for sai in ("không phải json", "[]", '{"daily": {}}', '{"daily": [{"date": "12/10"}]}',
                '{"daily": [{"date": "2026-10-12", "inputTokens": -1}]}',
                '{"daily": [{"date": "2026-10-12", "totalCost": "1"}]}',
                '{"daily": [{"date": "2026-02-30"}]}',
                '{"daily": [{"date": "2026-10-12", "totalCost": NaN}]}',
                '{"daily": [{"date": "2026-10-12", "inputTokens": Infinity}]}'):
        with pytest.raises(ValueError):
            doc_json_ccusage(sai)


def test_chay_dung_lenh_co_dinh_moi_truong_toi_thieu(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bi-mat")
    goi = []
    kq = DocCcusage(Path("/x/ccusage"), "17.2.1", chay=_chay(goi=goi)).theo_ngay(TU, DEN)
    assert kq.trang_thai == "ok" and kq.theo_ngay[0]["token_vao"] == 1200 and kq.phien_ban == "17.2.1"
    assert goi[1][0] == ["/x/ccusage", "daily", "--json", "--offline", "--since", "20261012", "--until", "20261013"]
    env = goi[1][1]["env"]
    assert set(env) == {"PATH", "HOME", "LANG", "TZ"} and "bi-mat" not in json.dumps(env)
    assert goi[1][1]["timeout"] == 60.0


@pytest.mark.parametrize("chay, chua", [
    (_chay(phien_ban="17.3.0"), "Phiên bản ccusage lệch (cần 17.2.1, thấy 17.3.0)"),
    (_chay(ma=2), "ccusage thoát mã 2"),
    (_chay(ra="{}"), "ccusage không đọc được (ValueError)"),
])
def test_loi_khong_nem_ra_ngoai(chay, chua):
    kq = DocCcusage(Path("/x/ccusage"), "17.2.1", chay=chay).theo_ngay(TU, DEN)
    assert kq.trang_thai == "loi" and kq.loi.startswith(chua) and "\x1b" not in kq.loi and kq.theo_ngay == ()


def test_khong_co_file_va_qua_gio():
    def het_gio(argv, **kw):
        raise subprocess.TimeoutExpired(argv, 60)
    assert DocCcusage(Path("/khong/co/ccusage"), "1.0.0").theo_ngay(TU, DEN).trang_thai == "loi"
    def lo_bi_mat(argv, **kw):
        if "--version" in argv:
            return subprocess.CompletedProcess(argv, 0, "1.0.0", "")
        return subprocess.CompletedProcess(argv, 2, "", "token=BI-MAT email@example.com")
    assert DocCcusage(Path("/x"), "1.0.0", chay=lo_bi_mat).theo_ngay(TU, DEN).loi == "ccusage thoát mã 2"
    def loi_bi_mat(argv, **kw):
        raise OSError("token=BI-MAT email@example.com")
    assert DocCcusage(Path("/x"), "1.0.0", chay=loi_bi_mat).theo_ngay(TU, DEN).loi == "ccusage không đọc được (OSError)"
    assert "TimeoutExpired" in DocCcusage(Path("/x"), "1.0.0", chay=het_gio).theo_ngay(TU, DEN).loi


def test_bo_dem_giu_ok_10_phut_loi_1_phut():
    dem, gio = [], [0.0]

    def doc(tu, den):
        dem.append((tu, den))
        return KetQuaCcusage("ok" if len(dem) != 3 else "loi", loi=None)
    bd = BoDemCcusage(doc, dong_ho=lambda: gio[0])
    bd.lay(TU, DEN)
    gio[0] = 599
    bd.lay(TU, DEN)
    assert len(dem) == 1
    bd.lay(TU, TU)                                   # khoảng khác: đọc riêng
    gio[0] = 600
    assert bd.lay(TU, DEN).trang_thai == "loi" and len(dem) == 3
    gio[0] = 659
    bd.lay(TU, DEN)
    gio[0] = 661
    bd.lay(TU, DEN)
    assert len(dem) == 4
    # Tiêm nguồn chậm: TTL tính từ hoàn tất, không từ lúc bắt đầu.
    def doc_cham(tu, den):
        gio[0] += 120
        return KetQuaCcusage("ok")
    cham = BoDemCcusage(doc_cham, dong_ho=lambda: gio[0])
    dau = cham.lay(TU, DEN)
    gio[0] += 599
    assert cham.lay(TU, DEN) is dau
