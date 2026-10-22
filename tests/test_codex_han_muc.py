import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tram.chay_cli.codex.han_muc import (NguonHanMucCodex, han_muc_app_server, han_muc_rollout,
                                         thong_diep_loi)
from tram.han_muc.luat import duoc_nhan
from tram.han_muc.mo_hinh import lam_moi
from tram.han_muc.nguon import NguonHanMuc

DL = Path(__file__).parent / "du_lieu" / "codex"
KHE = "C/codex-1"
LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
MAU = json.loads((DL / "app_server_rate_limits.json").read_text(encoding="utf-8"))


def _cs(hm):
    return {c.loai: (c.phan_tram, c.reset_luc) for c in hm.cua_so}


def test_app_server_theo_thoi_luong_khong_theo_primary():
    hm = han_muc_app_server(MAU["plus"], khe_id=KHE, bay_gio=LUC)
    assert hm.nguon == "app-server" and all(c.doc_luc == "2026-10-13T03:00:00Z" for c in hm.cua_so)
    assert _cs(hm) == {"5h": (62.0, "2026-10-13T05:00:00Z"), "tuan": (12.5, "2026-10-18T00:00:00Z")}
    pro = han_muc_app_server(MAU["prolite"], khe_id=KHE, bay_gio=LUC)
    assert _cs(pro) == {"tuan": (91.0, "2026-10-18T00:00:00Z")}                  # primary là cửa sổ tuần
    assert not duoc_nhan(lam_moi(pro, KHE, LUC), 0)
    assert [c.trang_thai for c in lam_moi(pro, KHE, LUC).cua_so] == ["biet", "chua_biet"]   # thiếu 5h → chưa biết


def test_cua_so_la_giu_ten_goc_truong_sai_bi_bo_khong_gia_0():
    hm = han_muc_app_server(MAU["la"], khe_id=KHE, bay_gio=LUC)
    assert _cs(hm) == {"primary:60m": (40.0, "2026-10-13T05:00:00Z")}
    for sai in ({}, {"rateLimits": None}, {"rateLimits": {"primary": None}}, {"rateLimits": []}):
        assert han_muc_app_server(sai, khe_id=KHE, bay_gio=LUC) is None


def test_rollout_dung_truong_snake_case_va_gio_cua_dong():
    dong = [json.loads(x) for x in (DL / "rollout.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [han_muc_rollout(d, khe_id=KHE, bay_gio=LUC) for d in dong[:2]] == [None, None]
    hm = han_muc_rollout(dong[2], khe_id=KHE, bay_gio=LUC)
    assert hm.nguon == "log" and _cs(hm)["5h"] == (62.0, "2026-10-13T05:00:00Z")
    assert hm.cua_so[0].doc_luc == "2026-10-13T02:41:10Z"
    assert han_muc_rollout(dong[3], khe_id=KHE, bay_gio=LUC).cua_so[0].doc_luc == "2026-10-13T03:00:00Z"


@pytest.mark.parametrize("dong, het", [
    ({"type": "error", "message": "You've hit your usage limit. Try again in 2 hours."}, True),
    ({"type": "turn.failed", "error": {"message": "unexpected status 429 Too Many Requests"}}, True),
    ({"type": "turn.failed", "error": {"message": "stream disconnected"}}, False),
    ({"type": "item.completed", "item": {"type": "agent_message", "text": "usage limit của API là gì?"}}, False),
    ({"type": "error"}, False),
])
def test_het_han_muc_chi_tu_thong_diep_loi(dong, het):
    assert NguonHanMucCodex().het_han_muc(dong) is het


def test_nguon_dung_giao_dien_va_thong_diep_loi():
    n = NguonHanMucCodex()
    assert isinstance(n, NguonHanMuc)
    assert n.doc_dong({"type": "turn.completed", "usage": {}}, khe_id=KHE, bay_gio=LUC) is None
    assert thong_diep_loi({"type": "turn.failed", "error": "x"}) is None
    assert thong_diep_loi({"type": "error", "message": "a" * 500}) == "a" * 300
