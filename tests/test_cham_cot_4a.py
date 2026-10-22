"""Sửa nhỏ ở 1a cùng 4a (spec 4 §5.1, §14 mục 5, 7; #10): bỏ qua bead có phiếu hiệu lực, chấm lại khi phiếu kết
thúc; `theo-plan` vào nhãn bỏ qua; decision mở không gọi LLM."""
import json
from types import SimpleNamespace as NS

from kho_phieu_gia import LUC, dat_phieu
from test_quet_yeu_cau import DU_AN, DUNG, VAI, BdGia, b, kho_moc
from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.quet import quet
from tram.phieu.ket_thuc import thu_hoi
from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien


class ClientDem:
    def __init__(self, khi_goi=None):
        self.goi, self.khi_goi = 0, khi_goi
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.goi += 1
        if self.khi_goi:
            self.khi_goi()
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(DUNG))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


def chay(k, bd, c):
    return quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, thu=False)


def test_decision_mo_khong_goi_llm(tmp_path):
    c = ClientDem()
    p = cham_mot_bead(b("hr-d", issue_type="decision"), du_an=DU_AN, theo_id={}, kho=KhoSuKien(tmp_path / "k.db"),
                      client=c, vai=VAI)
    assert c.goi == 0 and p.cot == "can-chot" and p.du_lieu["bo_llm"] == "decision-mo"


def test_theo_plan_bi_bo_qua(tmp_path):
    c = ClientDem()
    bc = chay(kho_moc(tmp_path), BdGia([b("hr-1", labels=["theo-plan"])]), c)
    assert c.goi == 0 and bc.bo_qua["nhan"] == 1


def test_co_phieu_hieu_luc_bo_qua_roi_cham_lai_khi_phieu_ket_thuc(tmp_path):
    k, kp = kho_moc(tmp_path), KhoPhieu(tmp_path / "sk.db")
    p = dat_phieu(kp, du_an="hr", bead_id="hr-1")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m1"}, bead_id="hr-1", tac_nhan="dai-ca")
    bd, c = BdGia([b("hr-1", updated_at="2026-10-13T00:00:00Z")]), ClientDem()
    bc = chay(k, bd, c)
    assert c.goi == 0 and bc.bo_qua["phieu"] == 1 and k.yeu_cau.dang_cho("hr") == {}   # yêu cầu cũ đã xong
    with kp.giao_dich():
        thu_hoi(kp, kp.lay(p.giao_id), ly_do="mat-nhip", luc=LUC)                      # phần 3 ghi yêu cầu chấm lại
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    bc = chay(k, bd, c)
    assert c.goi == 1 and [d.bead_id for d in bc.dong] == ["hr-1"] and k.yeu_cau.dang_cho("hr") == {}


def test_phieu_cap_trong_luc_cham_thi_huy_khong_ghi(tmp_path):
    k, kp = kho_moc(tmp_path), KhoPhieu(tmp_path / "sk.db")
    bd = BdGia([b("hr-1", updated_at="2026-10-13T00:00:00Z")])
    c = ClientDem(khi_goi=lambda: dat_phieu(kp, du_an="hr", bead_id="hr-1"))
    bc = chay(k, bd, c)
    assert c.goi == 1 and bd.goi == [] and bc.bo_qua["co_phieu_hieu_luc"] == 1
    assert k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu["huy"] == "co_phieu_hieu_luc"


def test_chua_co_bang_phieu_thi_khong_co_phieu(tmp_path):
    assert KhoSuKien(tmp_path / "moi.db").yeu_cau.dang_co_phieu("hr", "hr-1") is False
