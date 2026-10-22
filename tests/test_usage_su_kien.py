from datetime import date, datetime

from kho_phieu_gia import kho_tam
from tram.usage.su_kien import doc_dong_usage, moc_utc, tong_hop

GIA = {"claude-sonnet-5-5": {"vao": 3.0, "ra": 15.0, "cache_doc": 0.3, "cache_ghi": 3.75}}


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        for luc, du_an, loai, dl, cot in [
            ("2026-10-12T16:30:00Z", "hr-codex", "chay.xong", {"khe_id": "B/claude-1", "token_cache_doc": 1000,
                                                               "token_cache_ghi": 0}, (1000, 200, "claude-x")),
            ("2026-10-12T17:30:00Z", "hr-codex", "chay.xong", {"khe_id": "B/claude-2", "token_cache_doc": "rác"},
             (2000, 400, "claude-sonnet-5-5")),
            ("2026-10-12T18:00:00Z", "erp", "cham_cot.ket_qua", {"cot": "ai-lam"}, (500, 100, "claude-sonnet-5-5")),
            ("2026-10-12T19:00:00Z", "erp", "cham_cot.loi", {"loi": "x"}, (9, 9, None)),       # loại khác: bỏ
            ("2026-10-14T17:00:00Z", "erp", "cham_cot.ket_qua", {}, (7, 7, None)),             # ngoài khoảng
        ]:
            kho.ghi_su_kien(du_an, loai, dl, luc=datetime.fromisoformat(luc), bead_id="b", token_vao=cot[0], token_ra=cot[1],
                            mo_hinh=cot[2])
    return kho


def test_moc_ngay_theo_gio_viet_nam():
    assert moc_utc(date(2026, 10, 13)) == "2026-10-12T17:00:00Z"


def test_doc_dong_dung_khoang_va_ngay_vn(tmp_path):
    ds = doc_dong_usage(_kho(tmp_path).db, date(2026, 10, 12), date(2026, 10, 14))
    assert [(d.ngay.isoformat(), d.nguon, d.du_an) for d in ds] == [
        ("2026-10-12", "B/claude-1", "hr-codex"), ("2026-10-13", "B/claude-2", "hr-codex"),
        ("2026-10-13", "cham-cot", "erp")]
    assert (ds[0].token_cache_doc, ds[1].token_cache_doc, ds[2].token_cache_ghi) == (1000, 0, 0)


def test_tong_hop_theo_ngay_tuan_nguon_du_an_va_chi_phi(tmp_path):
    th = tong_hop(doc_dong_usage(_kho(tmp_path).db, date(2026, 10, 12), date(2026, 10, 13)), GIA)
    ngay = {x["khoa"]: x for x in th["theo_ngay"]}
    assert ngay["2026-10-12"]["chi_phi_usd"] is None and ngay["2026-10-12"]["thieu_gia"] == 1
    assert ngay["2026-10-13"]["token_vao"] == 2500 and ngay["2026-10-13"]["so_lan"] == 2
    assert ngay["2026-10-13"]["chi_phi_usd"] == round((2500 * 3 + 500 * 15) / 1e6, 4)
    assert [x["khoa"] for x in th["theo_tuan"]] == ["2026-W42"] and th["theo_tuan"][0]["thieu_gia"] == 1
    assert [x["khoa"] for x in th["theo_nguon"]] == ["B/claude-1", "B/claude-2", "cham-cot"]
    assert {x["khoa"]: x["token_ra"] for x in th["theo_du_an"]} == {"erp": 100, "hr-codex": 600}
    assert tong_hop([], GIA) == {"theo_ngay": [], "theo_tuan": [], "theo_nguon": [], "theo_du_an": []}
