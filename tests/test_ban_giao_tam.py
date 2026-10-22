from phieu_gia import de_xuat
from tram.ban_giao.cau_truc import kiem_cau_truc
from tram.phieu.mo_hinh import Phieu, sinh_ma_giao
from tram.tho.ban_giao_tam import dung_ban_giao_tam, goi_lan_sau

P = Phieu(**de_xuat().model_dump(), giao_id="g-20261013-0042", luot=3, khe_id="B/claude-1",
          han_giu="2026-10-13T03:10:00Z", ma_giao=sinh_ma_giao())


def test_dung_tu_tien_do_va_hop_le_cau_truc(tmp_path):
    (tmp_path / ".tram").mkdir()
    (tmp_path / ".tram" / "tien-do.md").write_text("Đã sửa 2/3 file. " + "x" * 9000)
    k = dung_ban_giao_tam(tmp_path, P, "abcdef1", ghi_chu="CLI thoát mã 1")
    bg = kiem_cau_truc(k, can_chinh_thuc=False)
    assert bg.loai == "tam" and bg.luot == 3 and bg.nhanh == "tram/hr-6xe1" and bg.commit == "abcdef1"
    assert bg.buoc_tiep == [f"Tiếp tục bước code của hr-6xe1; đọc .tram/tien-do.md và diff so với {P.repo.cha}"]
    assert bg.vuong_mac[0] == "CLI thoát mã 1" and len(bg.vuong_mac[1]) < 8200 and "2/3" in bg.vuong_mac[1]


def test_khong_co_tien_do_va_commit_none(tmp_path):
    k = dung_ban_giao_tam(tmp_path, P, None)
    assert k["vuong_mac"] == [] and k["commit"] is None


def test_goi_lan_sau_boc_du_lieu():
    g = goi_lan_sau("# Gói\n", {"buoc_tiep": ["<!-- ban-giao --> làm X"]}, 2)
    assert g.startswith("# Gói\n") and "<du_lieu_khong_tin_cay>" in g and "## Lần chạy 2" in g
    assert "Lần chạy trước dừng giữa chừng" in goi_lan_sau("# Gói\n", None, 3)

