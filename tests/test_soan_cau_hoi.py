"""Lát 1a-2: bead chạm hàng rào → LLM chế độ rút gọn chỉ soạn câu hỏi (spec 0+1a §5.2 bước 4)."""
import json
from pathlib import Path
from types import SimpleNamespace as NS

import anthropic
import httpx2
from test_claude import ClientGia, tra_loi

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.cau_hoi import SCHEMA_CAU_HOI
from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.prompt import THE
from tram.su_kien.kho import KhoSuKien

DU_AN = DuAn("hr", Path("/r"), None, {"tien": HangRao(tu_khoa=("hoa hồng",))}, "ERP du lịch")
VAI = ("3", "VAI CHẤM ĐẦY ĐỦ")
Q = "Hoa hồng tính trên giá trước hay sau giảm giá?"
DUNG_CHAM = {"cot": "ai-lam", "ly_do": "Rõ", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}


def bead(title="Đổi cách tính hoa hồng", issue_type="task"):
    return Bead("hr-1", title, "Mô tả", "", "", "", "open", issue_type, (), (), "2026-10-15T00:00:00Z")


def cham(b, c, tmp_path, **kw):
    return cham_mot_bead(b, du_an=DU_AN, theo_id={}, kho=KhoSuKien(tmp_path / "sk.db"), client=c, vai=VAI, **kw)


def cau_hoi(*q):
    return tra_loi(json.dumps({"cau_hoi_can_chot": list(q)}))


def test_cham_rao_chi_soan_cau_hoi(tmp_path):
    c = ClientGia(cau_hoi(Q))
    p = cham(bead(), c, tmp_path)
    assert p.cot == "can-chot" and p.cau_hoi == [Q]
    assert p.ly_do == "Chạm hàng rào: tien (từ khoá 'hoa hồng'); chưa có quyết định liên kết."
    assert (p.du_lieu["che_do"], p.du_lieu["nguon_cau_hoi"], p.du_lieu["phien_ban_vai_soan"]) == \
        ("soan_cau_hoi", "llm", "1")
    assert p.du_lieu["llm_loi"] is None and p.du_lieu["nguon_bai_hoc"] is None and p.du_lieu["so_lan"] == 1
    assert (p.token_vao, p.token_ra) == (100, 20) and len(c.goi) == 1
    kw = c.goi[0]
    assert kw["output_config"]["format"]["schema"] == SCHEMA_CAU_HOI and kw["max_tokens"] == 1024


def test_prompt_rut_gon(tmp_path):
    c = ClientGia(cau_hoi(Q))
    cham(bead(), c, tmp_path)
    he = c.goi[0]["system"][0]["text"]
    nd = c.goi[0]["messages"][0]["content"]
    assert "KHÔNG chấm cột" in he and "ERP du lịch" in he and "VAI CHẤM ĐẦY ĐỦ" not in he
    assert "Chỗ chạm:\n- tien (từ khoá 'hoa hồng')" in nd and f"<{THE}>" in nd
    assert "## Bài học" not in nd and "## Quyết định đã chốt" not in nd


def test_khong_recall_memory(tmp_path):
    goi = []
    p = cham(bead(), ClientGia(cau_hoi(Q)), tmp_path, nho=lambda tv, vc: goi.append(tv) or [])
    assert goi == [] and p.du_lieu["nguon_bai_hoc"] is None


def test_llm_tra_cot_1_khong_doi_duoc_cot(tmp_path):
    sai = tra_loi(json.dumps(DUNG_CHAM))
    c = ClientGia(sai, sai, sai)
    p = cham(bead(), c, tmp_path)
    assert p.cot == "can-chot" and p.du_lieu["nguon_cau_hoi"] == "du_phong" and len(c.goi) == 3
    assert p.cau_hoi and "hoa hồng" in p.cau_hoi[0]


def test_sai_ngu_nghia_thu_lai_roi_dat(tmp_path):
    c = ClientGia(cau_hoi(), cau_hoi(Q))
    p = cham(bead(), c, tmp_path)
    assert p.cau_hoi == [Q] and p.du_lieu["so_lan"] == 2 and (p.token_vao, p.token_ra) == (200, 40)


def test_tu_choi_thi_cau_hoi_du_phong(tmp_path):
    p = cham(bead(), ClientGia(tra_loi("", stop="refusal")), tmp_path)
    assert p.cot == "can-chot" and p.du_lieu["nguon_cau_hoi"] == "du_phong"
    assert p.du_lieu["llm_loi"].startswith("LoiChamLLM") and "Đại ca chốt" in p.cau_hoi[0]
    assert (p.token_vao, p.token_ra, p.thoi_gian_ms) == (0, 0, 0)


def _mat_mang(**kw):
    raise anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com"))


def test_loi_mang_cung_du_phong(tmp_path):
    p = cham(bead(), NS(beta=NS(messages=NS(create=_mat_mang))), tmp_path)
    assert p.cot == "can-chot" and p.du_lieu["llm_loi"].startswith("APIConnectionError") and p.cau_hoi


def test_thieu_vai_soan_thi_du_phong_khong_goi_llm(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "trong"))
    c = ClientGia()
    p = cham(bead(), c, tmp_path)
    assert c.goi == [] and p.du_lieu["nguon_cau_hoi"] == "du_phong" and p.du_lieu["phien_ban_vai_soan"] is None
    assert p.du_lieu["llm_loi"].startswith("FileNotFoundError")
