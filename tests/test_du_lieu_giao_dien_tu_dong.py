"""TM-4: dữ liệu GIẢ cho kiểm tay trang Tự động (`tests/chay_thu_giao_dien.py`) — cài đặt thật qua hàm TM-1 (`luu.py`),
khoá TM-2/TM-3 chưa có (`cho_dai_ca`, `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`, dòng Phê duyệt) là bản giả và
KHÔNG đè khoá/hàng thật khi TM-2/TM-3 đã ghép (Codex vòng 1, mục Nhỏ), trừ cờ xem `--gia-deploy` (`ep=True`)."""
from du_lieu_giao_dien import RONG, gieo_tu_dong, them_gia, them_phe_duyet_gia
from tram.phieu.kho import KhoPhieu
from tram.suy import phe_duyet
from tram.tu_dong.luu import doc_trang_thai, lich_su_doi


def test_gieo_tu_dong_dung_trang_thai_mockup(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    gieo_tu_dong(kho)
    tt = doc_trang_thai(kho.db, "tram")
    assert tt.cai_dat.tu_merge and not tt.cai_dat.tu_deploy and tt.cai_dat.du_lenh and tt.tam_dung_du_an is None
    assert [d["doi"][0]["truong"] for d in lich_su_doi(kho.db, "tram")] == ["tu_merge", "lenh_kiem_song", "lenh_deploy"]
    assert doc_trang_thai(kho.db, "hr-codex").phien_ban == "0"
    kho.close()


def test_khoa_that_thang_khoa_gia():
    ct = them_gia("tram", {"du_an": "tram", "dem_hong": 2})
    assert ct["dem_hong"] == 2 and ct["san_sang"]["so_merge"] == 2 and len(ct["cho_dai_ca"]) == 4
    # dạng TM-2 (`tram/suy/tu_merge.py`): mã + nhãn + mức của `tu_merge_xet.NHAN` / `MUC`
    assert ct["cho_dai_ca"][2]["ly_do"] == [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca",
                                            "muc": "loi"}]
    assert all({"bead_id", "tieu_de", "luc"} <= set(c) for c in ct["cho_dai_ca"])
    # dạng TM-3 (`tram/deploy/hien_thi.py`): sáu khoá, `loai` ∈ LOAI_LICH_SU (+ `huy` nếu Đại ca chọn câu 5a), `ai` ∈ AI
    assert all(set(r) == {"luc", "loai", "bead_id", "commit", "chi_tiet", "ai"} for r in ct["lich_su"])
    assert {r["ai"] for r in ct["lich_su"]} <= {"dai_ca", "dai_ca_bam", "tu_deploy", "tram"}
    assert [r["ai"] for r in ct["lich_su"] if r["loai"] == "san_sang"] == ["tram"]
    assert set(ct["san_sang"]) == {"commit", "so_merge", "bead_ids", "luc", "commit_dang_chay"}
    assert {r["loai"] for r in ct["lich_su"]} >= {"tu_merge", "san_sang", "deploy_lui", "deploy_dat"}
    assert them_gia("tram", {"ten": "tram"}, tom_tat=True) == {"ten": "tram", "san_sang": True, "dem_hong": 1}
    assert them_gia("ke-toan", {}) == {"cho_dai_ca": [], "san_sang": None, "dang_deploy": None, "lich_su": [],
                                       "dem_hong": 0}
    # TM-3 đã ghép (khoá thật có, `san_sang: None`): mặc định thật thắng; `ep` (--gia-deploy) giả thay cho dự án giả
    assert them_gia("tram", {"du_an": "tram", "san_sang": None})["san_sang"] is None
    assert them_gia("tram", {"du_an": "tram", "san_sang": None}, ep=True)["san_sang"] == ct["san_sang"]
    assert them_gia("ke-toan", {"san_sang": None}, ep=True) == RONG


def test_phe_duyet_gia_khong_noi_khi_da_co_hang_that(monkeypatch):
    monkeypatch.setattr(phe_duyet, "THU_TU", tuple(l for l in phe_duyet.THU_TU if l != "san-sang-deploy"))
    ct = them_gia("tram", {"du_an": "tram"})
    [m] = them_phe_duyet_gia([])                                            # trạm chưa có TM-3: thêm một dòng giả
    assert (m["loai"], m["du_an"], m["updated_at"]) == ("san-sang-deploy", "tram", ct["san_sang"]["luc"])
    assert m["chi_tiet"] == ct["san_sang"]                                  # TM-3: chi_tiet = toàn bộ san_sang
    that = {**m, "updated_at": "2026-10-18T10:00:00Z", "chi_tiet": {"commit": "b" * 40, "so_merge": 1}}
    khac = {**m, "loai": "escalation", "bead_id": "bs-1"}
    assert them_phe_duyet_gia([khac, that]) == [khac, that]                 # đã có hàng thật của tram: không nối
    assert them_phe_duyet_gia([khac, that], ep=True) == [khac, m]           # --gia-deploy: thay, không trùng
    monkeypatch.setattr(phe_duyet, "THU_TU", (*phe_duyet.THU_TU, "san-sang-deploy"))
    assert them_phe_duyet_gia([khac]) == [khac]                             # TM-3 đã ghép: chỉ trạng thái thật
