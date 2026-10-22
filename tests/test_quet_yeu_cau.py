"""Yêu cầu chấm lại bền + kiểm lại trước khi ghi — các ca của spec 0+1a §5.6 thuộc lát 2a."""
import json
from pathlib import Path
from types import SimpleNamespace as NS

from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.chu import estop
from tram.cham_cot.quet import quet
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "ERP")
VAI = ("2", "VAI")
MOC = "2026-10-12T10:00:00Z"
DUNG = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}


def b(id, *chan, title="Việc", status="open", issue_type="task", labels=(), updated_at=MOC, close_reason=""):
    return Bead(id, title, "", "", "", "", status, issue_type, tuple(labels),
                tuple(PhuThuoc(x, "blocks") for x in chan), updated_at, close_reason=close_reason)


class BdGia:
    def __init__(self, beads, phien_ban=None, show_loi=False):
        self.beads, self.goi, self._phien_ban, self.show_loi = beads, [], phien_ban or {}, show_loi

    def tat_ca(self):
        return list(self.beads)

    def phien_ban(self, bead_id):
        if self.show_loi:
            from tram.beads.bd import LoiBd
            raise LoiBd(f"bd show {bead_id} lỗi 1: database locked")
        return self._phien_ban.get(bead_id) or next(x.updated_at for x in self.beads if x.id == bead_id)

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None):
        self.goi.append((bead_id, list(them), list(bo)))


class ClientGia:
    def __init__(self, loi=False):
        self.loi, self.goi = loi, []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.goi.append(kw["messages"][0]["content"])
        if self.loi:
            return NS(stop_reason="refusal", content=[], usage=NS(input_tokens=1, output_tokens=1,
                                                                  cache_read_input_tokens=0))
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(DUNG))],
                  usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0))


def kho_moc(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi_moc("hr", MOC)
    return k


def thu_lai(k, bead_id="hr-1"):
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m1"}, bead_id=bead_id, tac_nhan="dai-ca")


def chay(k, bd, c, thu=False, **kw):
    return quet(DU_AN, bd=bd, kho=k, client=c, vai=VAI, thu=thu, **kw)


def test_bead_3_loi_khong_doi_bam_thu_lai_cham_dung_mot_lan(tmp_path):
    k = kho_moc(tmp_path)
    for _ in range(3):
        k.ghi("hr", "cham_cot.loi", {"loi": "API lỗi"}, bead_id="hr-1")
    thu_lai(k)
    bd, c = BdGia([b("hr-1")]), ClientGia()
    assert [d.bead_id for d in chay(k, bd, c).dong] == ["hr-1"]
    chay(k, bd, c)
    assert len(c.goi) == 1 and k.yeu_cau.dang_cho("hr") == {}


def test_dong_decision_bang_bd_tay_bead_goc_khong_doi_duoc_cham_lai(tmp_path):
    k = kho_moc(tmp_path)
    viec = b("hr-1", "hr-d")
    chay(k, BdGia([b("hr-d", issue_type="decision"), viec]), ClientGia())  # lượt đầu: khởi tạo ảnh
    dong = b("hr-d", issue_type="decision", status="closed", close_reason="Tính trên giá sau giảm",
             updated_at="2026-10-12T11:00:00Z")
    c = ClientGia()
    bc = chay(k, BdGia([dong, viec]), c)
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and "Tính trên giá sau giảm" in c.goi[0]
    assert k.yeu_cau.dang_cho("hr") == {}


def test_mo_lai_decision_bead_duoc_cham_lai(tmp_path):
    k = kho_moc(tmp_path)
    viec = b("hr-1", "hr-d")
    chay(k, BdGia([b("hr-d", issue_type="decision", status="closed", close_reason="Có"), viec]), ClientGia())
    mo = b("hr-d", issue_type="decision", updated_at="2026-10-12T11:00:00Z")
    bc = chay(k, BdGia([mo, viec]), ClientGia())
    assert "hr-1" in [d.bead_id for d in bc.dong]


def test_phu_thuoc_khong_co_trong_snapshot_khong_tinh_la_chot(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    bc = chay(k, BdGia([b("hr-1", "hr-mat", title="Đổi hoa hồng")]), ClientGia(), tat_ca=True)
    assert bc.dong[0].cot == "can-chot" and "Chạm hàng rào" in bc.dong[0].ly_do


def test_bead_doi_trong_luc_cham_bo_ket_qua_giu_yeu_cau(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    bd, c = BdGia([b("hr-1")], phien_ban={"hr-1": "2026-10-12T10:05:00Z"}), ClientGia()
    bc = chay(k, bd, c)
    assert len(c.goi) == 1 and bd.goi == [] and bc.dong == [] and bc.bo_qua["bead_doi_khi_cham"] == 1
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua")
    assert sk.du_lieu["huy"] == "bead_doi_khi_cham" and sk.du_lieu["da_ghi"] is False
    bd2 = BdGia([b("hr-1", updated_at="2026-10-12T10:05:00Z")])
    assert [d.bead_id for d in chay(k, bd2, c).dong] == ["hr-1"] and bd2.goi
    assert k.yeu_cau.dang_cho("hr") == {}


def test_cham_loi_danh_dau_xong_luot_sau_van_cham_nho_chuoi_loi(tmp_path):
    # Ca §5.6 "chấm lỗi không làm mất yêu cầu chấm lại" theo nghĩa không mất khả năng chấm lại (G7).
    k = kho_moc(tmp_path)
    thu_lai(k)
    bc = chay(k, BdGia([b("hr-1")]), ClientGia(loi=True))
    assert bc.loi and k.dem_loi_lien_tiep("hr", "hr-1") == 1 and k.yeu_cau.dang_cho("hr") == {}
    c = ClientGia()
    assert [d.bead_id for d in chay(k, BdGia([b("hr-1")]), c).dong] == ["hr-1"] and len(c.goi) == 1


def test_bead_bo_qua_co_dinh_danh_dau_xong_khong_cham(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k, "hr-e")
    thu_lai(k, "hr-k")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert set(k.yeu_cau.dang_cho("hr")) == {"hr-e", "hr-k"}
    c = ClientGia()
    chay(k, BdGia([b("hr-e", issue_type="epic"), b("hr-k", labels=["cot-khoa"])]), c)
    assert c.goi == [] and k.yeu_cau.dang_cho("hr") == {}


def test_yeu_cau_cua_bead_khong_con_trong_snapshot_danh_dau_xong(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k, "hr-xoa")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-xoa"]
    chay(k, BdGia([b("hr-1")]), ClientGia())
    assert k.yeu_cau.dang_cho("hr") == {}


def test_che_do_thu_thay_yeu_cau_nhung_khong_tieu(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    c = ClientGia()
    assert [d.bead_id for d in chay(k, BdGia([b("hr-1")]), c, thu=True).dong] == ["hr-1"]
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    assert [d.bead_id for d in chay(k, BdGia([b("hr-1")]), c).dong] == ["hr-1"]
    assert len(c.goi) == 2 and k.yeu_cau.dang_cho("hr") == {}


def test_estop_giu_nguyen_yeu_cau(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    estop.bat("thử")
    try:
        assert chay(k, BdGia([b("hr-1")]), ClientGia()) is None
    finally:
        estop.tat()
    c = ClientGia()
    assert [d.bead_id for d in chay(k, BdGia([b("hr-1")]), c).dong] == ["hr-1"]


def test_dai_ca_sua_tay_khi_co_yeu_cau_thi_khoa_va_giu_yeu_cau(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    bd, c = BdGia([b("hr-1", labels=["cot:ai-lam"])]), ClientGia()
    bc = chay(k, bd, c)
    assert c.goi == [] and bc.bo_qua["dai_ca_sua"] == 1 and bd.goi[0][1] == ["cot-khoa"]
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    chay(k, BdGia([b("hr-1", labels=["cot:ai-lam", "cot-khoa"])]), c)
    assert k.yeu_cau.dang_cho("hr") == {}


def test_bd_list_json_hong_qua_Bd_that_ghi_quet_loi(tmp_path):
    from tram.beads.bd import Bd
    k = KhoSuKien(tmp_path / "sk.db")
    bc = chay(k, Bd(Path("/r"), runner=lambda args: "{hỏng"), ClientGia())
    assert bc.loi and k.gan_day("hr", "quet.loi", 1)[0].du_lieu["loi"].startswith("bd list: JSON")


def test_bd_show_loi_sau_khi_llm_tra_loi_thi_huy_giu_yeu_cau(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    bd = BdGia([b("hr-1")], show_loi=True)
    bc = chay(k, bd, ClientGia())
    assert bd.goi == [] and bc.loi == [] and bc.bo_qua["khong_doc_duoc_version"] == 1
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua")
    assert sk.du_lieu["huy"] == "khong_doc_duoc_version" and k.gan_day("hr", "cham_cot.ket_qua", 1)[0].id == sk.id
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    assert [d.bead_id for d in chay(k, BdGia([b("hr-1")]), ClientGia()).dong] == ["hr-1"]
    assert k.yeu_cau.dang_cho("hr") == {}


def test_huy_khi_khong_co_yeu_cau_van_duoc_cham_lai_luot_sau(tmp_path):
    k = kho_moc(tmp_path)
    moi = b("hr-1", updated_at="2026-10-12T11:00:00Z")  # đổi sau mốc → chấm theo mốc, không có yêu cầu
    chay(k, BdGia([moi], show_loi=True), ClientGia())
    c = ClientGia()
    bc = chay(k, BdGia([moi]), c)  # mốc đã qua 11:00, nhưng sự kiện huỷ đã thành yêu cầu
    assert [d.bead_id for d in bc.dong] == ["hr-1"] and len(c.goi) == 1


def test_huy_lien_tiep_cham_tran_thi_dung_goi_llm(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    bd, c = BdGia([b("hr-1")], phien_ban={"hr-1": "2026-10-12T10:05:00Z"}), ClientGia()
    for _ in range(3):
        chay(k, bd, c)
    loi = k.moi_nhat("hr", "hr-1", "cham_cot.loi")
    assert loi.du_lieu["loi"] == "kết quả bị huỷ 3 lần liền (bead_doi_khi_cham)" and k.yeu_cau.dang_cho("hr") == {}
    for _ in range(7):
        chay(k, bd, c)
    # 3 lần huỷ tới trần, rồi chuỗi lỗi §6.3 thử thêm 2 lần (mỗi lần chạm trần ngay) và đóng băng ở 3 lỗi.
    assert len(c.goi) == 5 and k.dem_loi_lien_tiep("hr", "hr-1") == 3


class BdKhoaLoi(BdGia):
    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None):
        from tram.beads.bd import LoiBd
        raise LoiBd("bd update lỗi 1: database locked")


def test_yeu_cau_ma_bd_hong_khi_khoa_tra_ve_chuoi_loi_khong_lap_mai(tmp_path):
    k = kho_moc(tmp_path)
    thu_lai(k)
    c = ClientGia()
    for _ in range(6):  # bead bị sửa tay (nhãn hệ chưa từng ghi) → gắn cot-khoa → bd hỏng
        chay(k, BdKhoaLoi([b("hr-1", labels=["cot:ai-lam"])]), c)
    assert len(k.gan_day("hr", "cham_cot.loi", 10)) == 3 and k.gan_day("hr", "cham_cot.bo_qua", 10)
    assert k.yeu_cau.dang_cho("hr") == {} and c.goi == []


def test_ly_do_huy_rong_bi_tu_choi(tmp_path, monkeypatch):
    import pytest

    import tram.cham_cot.mot_bead as mot_bead
    monkeypatch.setattr(mot_bead, "kiem_lai_truoc_ghi", lambda bd, bead: "")
    with pytest.raises(ValueError):
        chay(kho_moc(tmp_path), BdGia([b("hr-1", updated_at="2026-10-12T11:00:00Z")]), ClientGia())
