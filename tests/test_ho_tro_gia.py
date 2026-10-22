import pytest
from fastapi import FastAPI, Request

from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from tram.ban_giao.schema import doc_khoi_ban_giao
from tram.beads.bd import KhongThayBead, LoiBd


def test_asgi_gia_get_post_va_header():
    app = FastAPI()

    @app.get("/a")
    def a(request: Request, q: str = ""):
        return {"q": q, "h": request.headers.get("x-thu")}

    @app.post("/b")
    async def b(request: Request):
        return {"than": await request.json()}

    r = goi(app, "GET", "/a?q=1", headers={"X-Thu": "co"})
    assert r.status == 200 and r.json() == {"q": "1", "h": "co"}
    r = goi(app, "POST", "/b", json_body={"x": "ă"})
    assert r.status == 200 and r.json() == {"than": {"x": "ă"}}
    assert goi(app, "GET", "/khong-co").status == 404


def test_bead_gia_mac_dinh_va_chan():
    b = bead("hr-9", labels=["cot:ai-lam"], chan_boi=["hr-1"], priority=1)
    assert b.id == "hr-9" and b.labels == ("cot:ai-lam",)
    assert b.phu_thuoc[0].depends_on_id == "hr-1" and b.phu_thuoc[0].loai == "blocks"
    assert b.priority == 1 and b.close_reason == ""
    assert doc_khoi_ban_giao(notes_ban_giao()).pr == "https://github.com/o/r/pull/7"


def test_bd_gia_ghi_nhan_tao_dong_noi():
    bd = BdGia([bead("hr-1", labels=["cot:ai-lam"])])
    bd.cap_nhat_nhan("hr-1", them=["cot:can-chot"], bo=["cot:ai-lam"], ghi_chu="n")
    b = bd.mot("hr-1")
    assert b.labels == ("cot:can-chot",) and b.notes == "n" and b.updated_at > "2026-10-13T01:00:00Z"
    moi = bd.tao("Chốt: x", loai="decision", mo_ta="m")
    bd.dong(moi, "đáp")
    bd.them_phu_thuoc("hr-1", moi)
    assert bd.mot(moi).status == "closed" and bd.mot(moi).close_reason == "đáp"
    assert bd.mot("hr-1").phu_thuoc[-1].depends_on_id == moi
    assert [g[0] for g in bd.goi] == ["cap_nhat_nhan", "tao", "dong", "them_phu_thuoc"]


def test_bd_gia_loi_truoc_va_sau():
    bd = BdGia([bead("hr-1")], ra_loi_truoc={"dong": 1}, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        bd.dong("hr-1", "x")
    assert bd.mot("hr-1").status == "open"
    with pytest.raises(LoiBd):
        bd.tao("t", loai="decision", mo_ta="m")
    assert bd.so_lan("tao") == 1 and len(bd.beads) == 2      # đã tạo rồi mới lỗi
    bd.dong("hr-1", "x")
    assert bd.mot("hr-1").status == "closed"
    with pytest.raises(KhongThayBead):
        bd.mot("hr-99")
