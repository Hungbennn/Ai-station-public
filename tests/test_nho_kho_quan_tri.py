"""1b-3: đọc toàn bảng không tìm vector, xoá cứng chỉ hàng đã xoá mềm, sổ cặp thăng cấp trong nhật ký."""
import threading

from nho_gia import EmbedderGia, ky_uc
from tram.nho.kho import KhoKyUc
from tram.nho.nhat_ky import NhatKy


def _kho(tmp_path):
    e = EmbedderGia()
    kho = KhoKyUc(tmp_path / "lancedb", so_chieu=e.so_chieu)
    for i, pv in enumerate(["/du-an/a/cach-lam", "/du-an/b/cach-lam", "/chung"]):
        kho.them(ky_uc(f"m-{i}", pv, vector=e.embed([str(i)])[0]))
    return kho


def test_quet_doc_moi_hang_khop_va_chon_cot(tmp_path):
    kho = _kho(tmp_path)
    assert sorted(h["id"] for h in kho.quet()) == ["m-0", "m-1", "m-2"]
    ds = kho.quet("pham_vi = '/chung'", cot=["id", "pham_vi"])
    assert ds == [{"id": "m-2", "pham_vi": "/chung"}]
    assert kho.quet("pham_vi = '/vai/x'") == []
    assert len(kho.quet()[0]["vector"]) == 16


def test_xoa_cung_chi_hang_da_xoa_mem(tmp_path):
    kho = _kho(tmp_path)
    assert kho.xoa_cung(["m-0"]) == 0 and kho.dem() == 3          # chưa xoá mềm: giữ nguyên
    kho.xoa_mem(["m-0", "m-1"])
    assert kho.xoa_cung(["m-0", "m-9"]) == 1 and kho.xoa_cung([]) == 0
    assert sorted(kho.lay(["m-0", "m-1", "m-2"])) == ["m-1", "m-2"]


def test_khoa_gop_rieng_voi_khoa_kho(tmp_path):
    kho = _kho(tmp_path)
    xong = []
    with kho.khoa_gop:
        t = threading.Thread(target=lambda: xong.append(len(kho.quet())))
        t.start()
        t.join(5)                       # đang giữ khoa_gop: đọc kho vẫn chạy (recall không bị chặn bởi gộp)
    assert xong == [3]


def test_so_cap_thang_cap_va_xoa_noi_dung_ke_hoach(tmp_path):
    nk = NhatKy(tmp_path / "nk.db")
    nk.ghi_cap("m-a|m-b", "tu_choi")
    nk.ghi_cap("m-a|m-b", "bo")                                    # đã có: giữ trạng thái đầu
    nk.ghi_cap("m-c|m-d", "xoa_cung")
    assert nk.cac_cap() == {"m-a|m-b": "tu_choi", "m-c|m-d": "xoa_cung"}
    nk.bat_dau("1:1", 1, {"buoc": [{"ky_uc": {"id": "m-x", "noi_dung": "bí mật"}}]})
    nk.hoan_tat("1:1", 1)
    nk.bat_dau("2:1", 2, {"buoc": [{"ky_uc": {"id": "m-x", "noi_dung": "đang dở"}}]})
    assert nk.xoa_noi_dung_ke_hoach("m-x") == 1 and nk.xoa_noi_dung_ke_hoach("m-xy") == 0
    assert nk.lay("1:1").ke_hoach["buoc"][0]["ky_uc"] == {"id": "m-x"}
    assert nk.lay("2:1").ke_hoach["buoc"]


def test_xoa_cung_khong_xoa_ke_hoach_chi_tham_chieu_id(tmp_path):
    nk = NhatKy(tmp_path / "nk.db")
    kh = {"buoc": [{"ky_uc": {"id": "m-y", "noi_dung": "giữ nguyên"}, "xoa": ["m-x"]}]}
    nk.bat_dau("3:1", 3, kh)
    nk.hoan_tat("3:1", 3)
    assert nk.xoa_noi_dung_ke_hoach("m-x") == 0
    assert nk.lay("3:1").ke_hoach == kh
