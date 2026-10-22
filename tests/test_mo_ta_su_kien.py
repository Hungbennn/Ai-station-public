"""Lát 2f (D39, khảo sát A3): mô tả sự kiện dựng từ mẫu cố định theo loại — không bao giờ lộ chữ tự do."""
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.su_kien.kho import SuKien
from tram.suy.mo_ta_su_kien import mo_ta
from tram.suy.su_kien_gan_day import CHE_NHO, gan_day

BI_MAT = "sk-ant-api03-BIMAT"


def sk(loai, du_lieu, tac_nhan="tram/api", id=1):
    return SuKien("2026-10-15T15:14:00Z", "hr", "hr-1", loai, tac_nhan, du_lieu, id)


def test_mau_theo_loai_nhu_mockup():
    assert mo_ta(sk("giao.nhan", {"khe_id": "B/claude-1", "buoc": "code", "luot": 1})) == "→ B/claude-1 · code"
    assert mo_ta(sk("chay.bat_dau", {"khe_id": "B/claude-1", "luot": 2, "lan": 1})) == "B/claude-1 · lượt 2"
    assert mo_ta(sk("cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": BI_MAT})) == "→ cột 1"
    assert mo_ta(sk("khe.cau_dao_ngat", {"khe_id": "B/claude-4", "ly_do": "het-han-muc"})) == \
        "B/claude-4 · cầu dao ngắt (hết hạn mức)"
    assert mo_ta(sk("pr.khong_xac_minh", {"pr": 12, "ly_do": "khong-phai-merge-commit"})) == \
        "PR #12 — không phải merge commit (squash / rebase)"
    assert mo_ta(sk("qc.ket_qua", {"ket_luan": "dat"})) == "QC đạt"
    assert mo_ta(sk("bao.can_hoi", {"loai_hoi": "can_quyet_dinh", "noi_dung": BI_MAT}, "tho/B/codex-1")) == \
        "B/codex-1 hỏi Đại ca (cần quyết định)"


def test_khong_bao_gio_lo_chu_tu_do():
    tu_do = [("khe.tat", {"khe_id": "B/claude-3", "vi_sao": BI_MAT}), ("cot.tra_ve", {"gop_y": BI_MAT}),
             ("quet.loi", {"loi": BI_MAT}), ("escalation.dong", {"escalation_id": "hr-9", "tra_loi": BI_MAT}),
             ("nho.tu_choi", {"ly_do": BI_MAT, "nguon": "dai_ca_ghi"}), ("bao.xong", {"luot": 1, "noi_dung": BI_MAT}),
             ("nho.agent_ghi", {"noi_dung": BI_MAT}), ("giao.ket_thuc", {"buoc": "code", "loi": [BI_MAT], "luot": 1}),
             ("cot.dai_ca_sua", {"cot_moi": "cot:can-chot", "vi_sao": BI_MAT, "tieu_de": BI_MAT})]
    for loai, d in tu_do:
        assert BI_MAT not in mo_ta(sk(loai, d)) and mo_ta(sk(loai, d)), loai
    assert mo_ta(sk("giao.nhan", {"khe_id": "B/x; rm -rf", "buoc": "lạ"})) == "→ ? · ?"
    assert mo_ta(sk("loai.la", {"a": 1})) == ""


def test_nho_bo_bi_mat_theo_mau_1b4():
    d = {"su_kien_id": 42, "loai_nguon": "ban_giao", "nhom": {"khoa_da_biet": 2, "entropy_cao": 1}}
    assert mo_ta(sk("nho.bo_bi_mat", d)) == \
        "Bỏ nguồn bàn giao (sự kiện #42) vì có dấu hiệu bí mật: khoá đã biết ×2, chuỗi entropy cao ×1"


def test_gan_day_moi_nhat_truoc_bo_nhip_che_nho(tmp_path):
    _, pt = tao_app_gia(tmp_path, {"hr": BdGia([])})
    kho = pt.mo_kho()
    kho.ghi("hr", "giao.nhan", {"khe_id": "B/claude-1", "buoc": "code"}, bead_id="hr-1")
    kho.ghi("_tram", "dieu_phoi.nhip", {"su_kien": "Stop", "phien": "0" * 16})
    kho.ghi("hr", "nho.ghi", {"id": "m-1", "pham_vi": "/du-an/hr/cach-lam", "nguon": []}, bead_id="hr-1")
    ds = gan_day(kho, 5, la_dai_ca=False)
    assert [s["loai"] for s in ds] == ["nho.ghi", "giao.nhan"]
    assert ds[0]["mo_ta"] == CHE_NHO and ds[1]["mo_ta"] == "→ B/claude-1 · code"
    assert set(ds[1]) == {"id", "luc", "loai", "du_an", "bead_id", "tac_nhan", "mo_ta"}
    assert gan_day(kho, 1, la_dai_ca=True)[0]["mo_ta"] == "ghi ký ức m-1 vào /du-an/hr/cach-lam"


def test_api_nho_su_kien_co_mo_ta(tmp_path):
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia([])})
    pt.mo_kho().ghi("hr", "nho.xoa", {"id": "m-1", "pham_vi": "/du-an/hr/cach-lam"}, bead_id="hr-1")
    r = goi(app, "GET", "/api/nho/su-kien", headers=DAI_CA)
    assert r.json()["su_kien"][0]["mo_ta"] == "xoá mềm ký ức m-1"
