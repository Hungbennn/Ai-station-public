import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.embed import LoiEmbedder
from tram.nho.ke_hoach import lap_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.llm import LoiLLMNho
from tram.nho.luat import LuatDuAn
from tram.nho.mo_hinh import id_ky_uc
from tram.nho.nguon import DauVao

VT, VG = nap_vai("nho-tach"), nap_vai("nho-gop")
LUC = "2026-10-13T02:00:00Z"                  # giờ nạp (bây giờ)
LUC_SK = "2026-09-01T08:00:00Z"               # giờ sự kiện nguồn
LUAT = LuatDuAn(module=("Fin",))


def tach_ra(*ky):
    return tra_loi({"ky_uc": [{"noi_dung": n, "nhanh": nh, "nhan": [], "quan_trong": q, "co_ten_rieng": r}
                              for n, nh, q, r in ky]})


@pytest.fixture
def kho(tmp_path):
    return KhoKyUc(tmp_path / "lancedb", so_chieu=16)


def chay(kho, dv, client, e=None):
    return lap_ke_hoach(dv, kho=kho, embedder=e or EmbedderGia(), client=client, vai_tach=VT, vai_gop=VG,
                        luat=LUAT, luc=LUC)


def test_tat_dinh_khong_goi_llm_cach_lam_san_06_tao_luc_la_gio_su_kien(kho):
    dv = DauVao(812, "hr-codex", "hr-1", "dai_ca_sua", tat_dinh='"T": hệ xếp cot:ai-lam, Đại ca chuyển cot:can-chot.',
                luc=LUC_SK)
    c = ClientGia()
    [b] = chay(kho, dv, c)
    k = b.ky_uc
    assert c.goi == [] and b.xoa == () and k.id == id_ky_uc(812, 1, 0)
    assert (k.pham_vi, k.quan_trong, k.nguon_dai_ca, k.hieu_luc_tu, k.tao_luc, k.mo_hinh_embed) == (
        "/du-an/hr-codex/cach-lam", 0.6, True, LUC_SK, LUC_SK, "gia@1")
    assert k.nguon == ({"loai": "dai_ca_sua", "du_an": "hr-codex", "bead_id": "hr-1", "su_kien_id": 812},)


def test_da_chot_luon_nghiep_vu_san_08(kho):
    dv = DauVao(5, "hr", "hr-1", "da_chot", van_ban="Hỏi/Đáp", ep_nghiep_vu=True)
    [b] = chay(kho, dv, ClientGia(tach_ra(("Hoa hồng tính trên giá sau giảm", "cach-lam", 0.3, False))))
    assert b.ky_uc.pham_vi == "/du-an/hr/nghiep-vu" and b.ky_uc.quan_trong == 0.8


@pytest.mark.parametrize("noi_dung, ten_rieng", [("Phụ thu 50k", False), ("Sửa form Fin", False), ("Đoàn A", True)])
def test_luat_cung_ghi_de_nhanh_cua_llm(kho, noi_dung, ten_rieng):
    dv = DauVao(6, "hr", "hr-1", "tra_ve", van_ban="góp ý")
    [b] = chay(kho, dv, ClientGia(tach_ra((noi_dung, "cach-lam", 0.5, ten_rieng))))
    assert b.ky_uc.pham_vi == "/du-an/hr/nghiep-vu"


def test_gop_trong_cung_pham_vi_embed_lai_noi_dung_cuoi_va_hop_nguon(kho):
    e = EmbedderGia(vector={"Chạy test bằng artisan": [1] + [0] * 15, "Câu gộp": [0, 1] + [0] * 14})
    cu = ky_uc("cu", "/du-an/hr/cach-lam", vector=e.embed(["Chạy test bằng artisan"])[0], quan_trong=0.9,
               nguon=({"loai": "tra_ve", "du_an": "hr", "bead_id": "hr-0", "su_kien_id": 1},))
    kho.them(cu)
    kho.them(ky_uc("khac-pv", "/du-an/hr/nghiep-vu", vector=cu.vector))       # khác phạm vi: không là ứng viên
    dv = DauVao(7, "hr", "hr-1", "tra_ve", van_ban="góp ý", luc=LUC_SK)
    c = ClientGia(tach_ra(("Chạy test bằng artisan", "cach-lam", 0.5, False)),
                  tra_loi({"quyet_dinh": [{"id": "cu", "hanh_dong": "gop"}], "noi_dung_gop": "Câu gộp",
                           "co_ten_rieng": False}))
    [b] = chay(kho, dv, c, e)
    assert b.xoa == ("cu",) and b.ky_uc.noi_dung == "Câu gộp" and b.ky_uc.quan_trong == pytest.approx(0.9)
    assert b.ky_uc.vector == e.embed(["Câu gộp"])[0] and b.ky_uc.tao_luc == b.ky_uc.hieu_luc_tu == LUC  # bản gộp
    assert [n["su_kien_id"] for n in b.ky_uc.nguon] == [7, 1] and b.ky_uc.nguon_dai_ca
    assert '"id": "cu"' in c.goi[1]["messages"][0]["content"] and "khac-pv" not in c.goi[1]["messages"][0]["content"]


def test_khong_co_gi_dang_nho_thi_ke_hoach_rong(kho):
    assert chay(kho, DauVao(8, "hr", "hr-1", "tra_ve", van_ban="x"), ClientGia(tra_loi({"ky_uc": []}))) == []


def test_loi_tach_va_loi_embed_noi_len(kho):
    xau = tra_loi({"ky_uc": "x"})
    with pytest.raises(LoiLLMNho):
        chay(kho, DauVao(9, "hr", "hr-1", "tra_ve", van_ban="x"), ClientGia(xau, xau, xau))
    with pytest.raises(LoiEmbedder):
        chay(kho, DauVao(9, "hr", "hr-1", "dai_ca_sua", tat_dinh="x"), ClientGia(), EmbedderGia(loi_tu_lan=1))


def test_nhieu_ky_uc_tach_tu_mot_su_kien_khong_gop_lai_ban_cu_da_xoa(kho):
    """bs-hpc.11: bản cũ đã bị gộp/thay ở bước trước không còn là ứng viên của bước sau (tránh bản trùng)."""
    e = EmbedderGia(vector={"A": [1] + [0] * 15, "A2": [1, 0.01] + [0] * 14, "Câu gộp": [0, 1] + [0] * 14})
    kho.them(ky_uc("cu", "/du-an/hr/cach-lam", vector=e.embed(["A"])[0]))
    dv = DauVao(9, "hr", "hr-1", "tra_ve", van_ban="góp ý", luc=LUC_SK)
    c = ClientGia(tach_ra(("A", "cach-lam", 0.5, False), ("A2", "cach-lam", 0.5, False)),
                  tra_loi({"quyet_dinh": [{"id": "cu", "hanh_dong": "gop"}], "noi_dung_gop": "Câu gộp",
                           "co_ten_rieng": False}))
    b1, b2 = chay(kho, dv, c, e)
    assert b1.xoa == ("cu",) and b1.ky_uc.noi_dung == "Câu gộp"
    assert b2.xoa == () and b2.ky_uc.noi_dung == "A2" and len(c.goi) == 2
