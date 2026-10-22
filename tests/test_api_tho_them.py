"""`/api/tho/da-push`, `/api/tho/da-dong` qua HTTP trong bộ nhớ (spec 3 §6.4, §7.1) + lý do `bi` mới của 3a-2."""
from contextlib import closing

from cong_bo_gia import commit_tho, dung_ba_kho
from phieu_gia import de_xuat, khoa
from tho_api_gia import tao_tram
from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.cong_bo.nguon import NguonKhoTho, ref_tam_cua


def dung(tmp_path, monkeypatch, *, nguon=True):
    b = dung_ba_kho(tmp_path, monkeypatch)
    t = tao_tram(tmp_path)
    t.pt.chon_phieu = lambda khe_id, hm: de_xuat("hr-1", cha=b.cha, khoa_chong_trung=khoa("hr-1", b.cha))
    t.app.state.cong_bo = (CauHinhCongBo("kho-tho", thoi_gian_cho_giay=30),
                           NguonKhoTho({"B": b.tho.parent}) if nguon else None, lambda du_an: b.tram)
    p = t.goi("POST", "/api/tho/nhip", json_body={"khe_id": "B/claude-1", "buoc_tho": "ranh"}).json()["phieu"]
    return b, t, p


def than(p, commit, **kw):
    return {"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": p["luot"], "commit": commit,
            "ref_tam": ref_tam_cua("hr-1", p["luot"]), "request_id": "r-day-0001", **kw}


def test_da_push_cong_bo_qua_http(tmp_path, monkeypatch):
    b, t, p = dung(tmp_path, monkeypatch)
    c = commit_tho(b, ref_tam_cua("hr-1", p["luot"]), {"x.txt": "1"})
    r = t.goi("POST", "/api/tho/da-push", json_body=than(p, c))
    assert r.status == 200 and r.json() == {"cong_bo": True, "commit": c, "ref": "tram/hr-1"}
    assert t.goi("POST", "/api/tho/da-push", may=None, json_body=than(p, c)).status == 401
    assert t.goi("POST", "/api/tho/da-push", json_body=than(p, c, ref_tam="tram/luot/hr-1/7",
                                                            request_id="r-day-0002")).json() == {"ly_do": "ref-tam-sai"}
    r = t.goi("POST", "/api/tho/da-push", json_body=than(p, c, luot=5, ref_tam="tram/luot/hr-1/5",
                                                         request_id="r-day-0003"))
    assert r.status == 409 and r.json() == {"ly_do": "luot-cu"}
    assert t.goi("POST", "/api/tho/da-push", json_body=than(p, c, khe_id="B/claude-9")).status == 403


def test_da_push_chua_chot_phuong_an_503(tmp_path, monkeypatch):
    b, t, p = dung(tmp_path, monkeypatch, nguon=False)
    r = t.goi("POST", "/api/tho/da-push", json_body=than(p, "a" * 40))
    assert r.status == 503 and r.json() == {"ly_do": "chua-chot-phuong-an"}


def test_da_dong_va_ly_do_bi_moi(tmp_path, monkeypatch):
    b, t, p = dung(tmp_path, monkeypatch)
    with closing(t.kho()) as kho, kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "bead.dong", {"du_an": "hr-codex", "bead_id": "hr-9"}, luc=t.gio[0],
                        bead_id="hr-9", tac_nhan="tram/giao-viec")
    r = t.goi("POST", "/api/tho/da-dong", json_body={"bead": [{"du_an": "hr-codex", "bead_id": "hr-9"},
                                                              {"du_an": "hr-codex", "bead_id": "hr-1"}]})
    assert r.json() == {"dong": [{"du_an": "hr-codex", "bead_id": "hr-9"}]}
    assert t.goi("POST", "/api/tho/da-dong", json_body={"bead": [{"du_an": "HR", "bead_id": "x"}]}).status == 422
    r = t.goi("POST", "/api/tho/bao", json_body={"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": p["luot"],
                                                 "loai": "bi", "ly_do": "nhanh-bi-day-ngoai-luong",
                                                 "noi_dung": "ref công bố bị đẩy ngoài luồng", "request_id": "r-bi-0001"})
    assert r.status == 200 and r.json()["da_nhan"] is True
