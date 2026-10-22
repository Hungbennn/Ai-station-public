import json
from pathlib import Path
from types import SimpleNamespace as NS

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.ghi import do_he_vua_sua, dong_ghi_chu, ghi_ket_qua, kiem_sua_tay
from tram.llm.claude import LoiChamLLM
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "ERP")
VAI = ("1", "VAI")


def bead(title="Sửa nút", labels=(), updated_at="2026-10-12T00:00:00Z"):
    return Bead("hr-1", title, "", "", "", "", "open", "task", tuple(labels), (), updated_at)


class ClientGia:
    def __init__(self, du_lieu=None, loi=False):
        self.du_lieu, self.loi = du_lieu, loi
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        if self.loi:
            return NS(stop_reason="refusal", content=[], usage=NS(input_tokens=1, output_tokens=1, cache_read_input_tokens=0))
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(self.du_lieu))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


class BdGia:
    def __init__(self):
        self.goi = []

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None):
        self.goi.append((bead_id, list(them), list(bo), ghi_chu))


def kq_llm(cot="ai-lam", tin=0.9, **d):
    base = {"cot": cot, "ly_do": "Lý do LLM", "thieu": [] if cot == "ai-lam" else ["x"],
            "cau_hoi_can_chot": [], "do_tin_cay": tin}
    return {**base, **d}


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def test_cham_binh_thuong(tmp_path):
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho(tmp_path), client=ClientGia(kq_llm()), vai=VAI)
    assert p.cot == "ai-lam" and p.du_lieu["phien_ban_vai"] == "1"


def test_luat_cung_ep_cot_2_du_llm_noi_cot_1(tmp_path):
    p = cham_mot_bead(bead(title="hoa hồng"), du_an=DU_AN, theo_id={}, kho=kho(tmp_path),
                      client=ClientGia(kq_llm("ai-lam")), vai=VAI)
    assert p.cot == "can-chot" and "Chạm hàng rào" in p.ly_do


def test_luat_cung_van_cot_2_khi_llm_hong(tmp_path):
    p = cham_mot_bead(bead(title="hoa hồng"), du_an=DU_AN, theo_id={}, kho=kho(tmp_path),
                      client=ClientGia(loi=True), vai=VAI)
    assert p.cot == "can-chot" and p.du_lieu["llm_loi"]


def test_llm_hong_khong_co_luat_thi_nem_loi(tmp_path):
    import pytest
    with pytest.raises(LoiChamLLM):
        cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho(tmp_path), client=ClientGia(loi=True), vai=VAI)


def test_tin_cay_thap_ha_ve_cot_2(tmp_path):
    p = cham_mot_bead(bead(), du_an=DU_AN, theo_id={}, kho=kho(tmp_path),
                      client=ClientGia(kq_llm(tin=0.4)), vai=VAI)
    assert p.cot == "can-chot" and p.ly_do.startswith("AI chưa chắc")


def test_dong_ghi_chu_gio_vn():
    s = dong_ghi_chu("can-chot", "Thiếu tiêu chí.", ["Q1?", "Q2?"], "2026-10-12T14:40:00Z")
    assert s == "[tram/cham-cot 2026-10-12 21:40] cột 2 — Thiếu tiêu chí. Cần chốt: (1) Q1? (2) Q2?"


def _phan(cot="ai-lam", ly_do="A"):
    from tram.cham_cot.cham import PhanCot
    return PhanCot(cot, ly_do, [], {}, 1, 1, 1)


def test_ghi_lan_dau_them_nhan_va_notes(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    assert ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=False)
    assert bd.goi[0][1] == ["cot:ai-lam"] and bd.goi[0][3].startswith("[tram/cham-cot")


def test_khong_doi_thi_khong_goi_bd(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=False)
    assert not ghi_ket_qua(bd, k, "hr", bead(labels=["cot:ai-lam"]), _phan(), thu=False)
    assert len(bd.goi) == 1


def test_doi_cot_thi_bo_nhan_cu(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=False)
    ghi_ket_qua(bd, k, "hr", bead(labels=["cot:ai-lam"]), _phan("can-chot", "B"), thu=False)
    assert bd.goi[1][1:3] == (["cot:can-chot"], ["cot:ai-lam"])


def test_che_do_thu_khong_goi_bd(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    assert not ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=True)
    assert bd.goi == [] and k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu["da_ghi"] is False


def test_sua_tay_thi_khoa(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan("ai-lam"), thu=False)
    assert kiem_sua_tay(bd, k, "hr", bead(labels=["cot:can-chot"]), thu=False)
    assert bd.goi[-1][1] == ["cot-khoa"]
    sk = k.moi_nhat("hr", "hr-1", "cot.dai_ca_sua")
    assert sk.du_lieu["cot_he"] == "cot:ai-lam" and sk.du_lieu["cot_moi"] == "cot:can-chot"


def test_nhan_trung_he_thi_khong_khoa(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan("ai-lam"), thu=False)
    assert not kiem_sua_tay(bd, k, "hr", bead(labels=["cot:ai-lam"]), thu=False)


def test_nhan_ma_he_chua_tung_ghi_thi_khoa(tmp_path):
    assert kiem_sua_tay(BdGia(), kho(tmp_path), "hr", bead(labels=["cot:ai-lam"]), thu=False)


def test_do_he_vua_sua(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=False)
    luc = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").luc
    assert do_he_vua_sua(k, "hr", bead(updated_at=luc))
    assert not do_he_vua_sua(k, "hr", bead(updated_at="2099-01-01T00:00:00Z"))


def test_go_khoa_thi_cham_lai(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan("ai-lam"), thu=False)
    assert kiem_sua_tay(bd, k, "hr", bead(labels=["cot:can-chot"]), thu=False)
    so_goi = len(bd.goi)
    assert not kiem_sua_tay(bd, k, "hr", bead(labels=["cot:can-chot"]), thu=False)
    assert len(bd.goi) == so_goi and len(k.gan_day("hr", "cot.dai_ca_sua", 10)) == 1


def test_go_khoa_roi_doi_nhan_khac_thi_khoa_lai(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(), _phan("can-chot"), thu=False)
    assert kiem_sua_tay(bd, k, "hr", bead(labels=["cot:ai-lam"]), thu=False)
    ghi_ket_qua(bd, k, "hr", bead(labels=["cot:ai-lam"]), _phan("ai-lam", "B"), thu=False)
    assert kiem_sua_tay(bd, k, "hr", bead(labels=["cot:can-chot"]), thu=False)


def test_che_do_thu_phat_hien_sua_tay_khong_ghi_su_kien(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    assert kiem_sua_tay(bd, k, "hr", bead(labels=["cot:ai-lam"]), thu=True)
    assert bd.goi == [] and k.gan_day("hr", "cot.dai_ca_sua", 10) == []


# --- Lát 2a: thay toàn bộ nhãn cot:* (spec §5.4), huỷ kết quả (§5.6) ---

def test_hai_nhan_cot_sau_ghi_con_dung_mot(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    truoc = {"cot:ai-lam", "cot:can-chot", "qa"}
    ghi_ket_qua(bd, k, "hr", bead(labels=sorted(truoc)), _phan("can-chot"), thu=False)
    _, them, bo, _ = bd.goi[0]
    sau = (truoc | set(them)) - set(bo)
    assert sorted(n for n in sau if n.startswith("cot:")) == ["cot:can-chot"] and "qa" in sau


def test_nhan_cot_la_bi_go_du_nhan_dich_da_co(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    ghi_ket_qua(bd, k, "hr", bead(labels=["cot:ai-lam", "cot:la"]), _phan("ai-lam"), thu=False)
    assert bd.goi[0][1:3] == ([], ["cot:la"])


def test_nhieu_nhan_cot_ghi_nhan_lech_vao_su_kien(tmp_path):
    k = kho(tmp_path)
    ghi_ket_qua(BdGia(), k, "hr", bead(labels=["cot:ai-lam", "cot:can-chot"]), _phan("ai-lam"), thu=False)
    du_lieu = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu
    assert du_lieu["nhan_lech"] == ["cot:ai-lam", "cot:can-chot"]


def test_mot_nhan_cot_khong_ghi_nhan_lech(tmp_path):
    k = kho(tmp_path)
    ghi_ket_qua(BdGia(), k, "hr", bead(labels=["cot:ai-lam"]), _phan("can-chot"), thu=False)
    assert "nhan_lech" not in k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu


def test_ket_qua_bi_huy_khong_goi_bd_va_ghi_ly_do(tmp_path):
    k, bd = kho(tmp_path), BdGia()
    assert not ghi_ket_qua(bd, k, "hr", bead(), _phan(), thu=False, huy="bead_doi_khi_cham")
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua")
    assert bd.goi == [] and sk.du_lieu["da_ghi"] is False and sk.du_lieu["huy"] == "bead_doi_khi_cham"
