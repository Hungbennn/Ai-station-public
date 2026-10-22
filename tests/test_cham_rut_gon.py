"""Lát 1a-2: cột 2 do luật cứng luôn có câu hỏi; bead không chạm rào vẫn chấm đầy đủ (spec 0+1a §5.2 bước 4–5)."""
import json

from test_cham_ghi import BdGia
from test_claude import ClientGia, tra_loi
from test_soan_cau_hoi import DU_AN, DUNG_CHAM, VAI, Q, bead, cau_hoi, cham

from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.ghi import ghi_ket_qua
from tram.su_kien.kho import KhoSuKien


def test_vai_soan_truyen_vao_duoc_dung(tmp_path):
    c = ClientGia(cau_hoi(Q))
    p = cham(bead(), c, tmp_path, vai_soan=("9", "VAI SOẠN"))
    assert c.goi[0]["system"][0]["text"].startswith("VAI SOẠN") and p.du_lieu["phien_ban_vai_soan"] == "9"


def test_decision_mo_co_cau_hoi_khong_goi_llm(tmp_path):
    c = ClientGia()
    p = cham(bead(title="Chốt giá tour", issue_type="decision"), c, tmp_path)
    assert c.goi == [] and p.cau_hoi == ["Đại ca chốt quyết định này: Chốt giá tour"]
    assert p.du_lieu["bo_llm"] == "decision-mo" and p.du_lieu["nguon_cau_hoi"] == "du_phong"


def test_bead_khong_cham_rao_van_cham_day_du(tmp_path):
    c = ClientGia(tra_loi(json.dumps(DUNG_CHAM)))
    p = cham(bead(title="Sửa nút lưu"), c, tmp_path)
    assert p.cot == "ai-lam" and "che_do" not in p.du_lieu and p.du_lieu["do_tin_cay"] == 0.9
    assert c.goi[0]["output_config"]["effort"] == "medium" and c.goi[0]["system"][0]["text"].startswith("VAI CHẤM")


def test_notes_cot_2_luon_co_can_chot_khi_llm_loi(tmp_path):
    k, bd = KhoSuKien(tmp_path / "sk.db"), BdGia()
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=k, client=ClientGia(tra_loi("", stop="refusal")), vai=VAI)
    assert ghi_ket_qua(bd, k, "hr", bead(), p, thu=False)
    assert bd.goi[0][1] == ["cot:can-chot"] and " Cần chốt: (1) Việc này chạm tiền" in bd.goi[0][3]
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu
    assert sk["cau_hoi"] == p.cau_hoi and sk["nguon_cau_hoi"] == "du_phong"
