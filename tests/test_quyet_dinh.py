"""Chấm một bead đưa decision đã đóng (qua `blocks`) vào prompt v2 — spec 0+1a §5.3."""
import json
from pathlib import Path
from types import SimpleNamespace as NS

from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.cham import cham_mot_bead
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "ERP")
KQ = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}


class ClientGhiLai:
    def __init__(self):
        self.goi = []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.goi.append(kw)
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(KQ))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


def _bead(*phu_thuoc):
    return Bead("hr-1", "Đổi cách tính hoa hồng", "", "", "", "", "open", "task", (),
                tuple(phu_thuoc), "2026-10-13T00:00:00Z")


def _dec(id, status="closed", close_reason="Trên giá sau giảm"):
    return Bead(id, "Chốt hoa hồng", "Tính trên giá nào?", "", "", "", status, "decision", (), (),
                "2026-10-13T00:00:00Z", close_reason=close_reason)


def test_cham_dua_decision_da_dong_vao_prompt(tmp_path):
    c = ClientGhiLai()
    theo_id = {"hr-d": _dec("hr-d"), "hr-mo": _dec("hr-mo", status="open", close_reason="")}
    p = cham_mot_bead(_bead(PhuThuoc("hr-d", "blocks"), PhuThuoc("hr-mo", "blocks")), du_an=DU_AN,
                      theo_id=theo_id, kho=KhoSuKien(tmp_path / "sk.db"), client=c, vai=("2", "VAI"))
    noi_dung = c.goi[0]["messages"][0]["content"]
    assert '"close_reason": "Trên giá sau giảm"' in noi_dung and '"id": "hr-mo"' not in noi_dung
    assert p.du_lieu["quyet_dinh"] == ["hr-d"]


def test_cham_khong_co_decision(tmp_path):
    # Lát 1a-2: bead chạm rào chưa chốt đi chế độ rút gọn — ca này dùng dự án không hàng rào để vào chấm đầy đủ.
    c = ClientGhiLai()
    p = cham_mot_bead(_bead(), du_an=DuAn("hr", Path("/r"), None, {}, "ERP"), theo_id={},
                      kho=KhoSuKien(tmp_path / "sk.db"), client=c, vai=("2", "VAI"))
    assert p.du_lieu["quyet_dinh"] == [] and "- (không có)" in c.goi[0]["messages"][0]["content"]
