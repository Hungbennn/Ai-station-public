"""1b-3: Đại ca ghi tay — luật cứng (ép nghiep-vu / từ chối ngoài dự án), gộp cùng phạm vi, idempotent theo mã."""
import anthropic
import httpx2
import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.embed import LoiEmbedder
from tram.nho.ghi_tay import KetQuaGhiTay, NguCanhGhiTay, TuChoiGhi, XungDotGhi, ghi_tay, id_ghi_tay
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.pham_vi import LoiVungCap
from tram.su_kien.kho import KhoSuKien

LUAT = {"hr-codex": LuatDuAn(("Pay",), ("Sao Mai",)), "ke-toan": LuatDuAn(("Ledger",), ())}
LUC = "2026-10-20T03:00:00Z"
MA = "ma-ghi-0001"
CAU = "Chạy toàn bộ test trước khi bàn giao."


@pytest.fixture
def nc(tmp_path):
    e = EmbedderGia(vector={CAU: (1.0, 0.0) + (0.0,) * 14, "Gộp: chạy test và lint.": (0.0, 1.0) + (0.0,) * 14})
    return NguCanhGhiTay(kho=KhoKyUc(tmp_path / "lancedb", so_chieu=16), embedder=e, client=ClientGia(),
                         vai_gop=nap_vai("nho-gop"), nhat_ky=NhatKy(tmp_path / "nk.db"),
                         kho_sk=KhoSuKien(tmp_path / "sk.db"), luat_cua=LUAT.__getitem__,
                         cac_du_an=lambda: sorted(LUAT), luc=lambda: LUC)


def ghi(nc, pham_vi="/chung", noi_dung=CAU, ma=MA, nhan=("test",)):
    return ghi_tay(nc, noi_dung=noi_dung, pham_vi=pham_vi, nhan=list(nhan), ma_thao_tac=ma)


def su_kien(nc, du_an, loai):
    return [s.du_lieu for s in nc.kho_sk.gan_day(du_an, loai, 99)]


def test_ghi_chung_khong_cham_luat(nc):
    kq = ghi(nc)
    assert kq == KetQuaGhiTay(id_ghi_tay(MA), "/chung", (), False)
    k = nc.kho.lay([kq.id])[kq.id]
    assert (k.noi_dung, k.nhan, k.quan_trong, k.nguon_dai_ca, k.tao_luc, k.hieu_luc_tu) == (
        CAU, ("test",), pytest.approx(0.8), True, LUC, LUC)
    assert k.nguon == ({"loai": "dai_ca_ghi", "ma_thao_tac": MA},)
    assert su_kien(nc, "_tram", "nho.ghi") == [{"id": kq.id, "pham_vi": "/chung", "nguon": list(k.nguon)}]
    assert nc.client.goi == [] and nc.nhat_ky.lay("ghi:" + MA).trang_thai == "xong"


def test_gui_lai_cung_ma_tra_ket_qua_cu_khong_lam_lai(nc):
    ghi(nc)
    nc.embedder.goi.clear()
    assert ghi(nc) == KetQuaGhiTay(id_ghi_tay(MA), "/chung", (), True)
    assert nc.embedder.goi == [] and nc.kho.dem() == 1 and len(su_kien(nc, "_tram", "nho.ghi")) == 1
    with pytest.raises(XungDotGhi):
        ghi(nc, noi_dung="khác hẳn")


@pytest.mark.parametrize("pv, cau, ly", [("/chung", "Sửa Ledger phải chạy lại báo cáo", "tên module (Ledger)"),
                                         ("/vai/coder", "Phí 100k mỗi lần gọi", "số tiền (100k)"),
                                         ("/chung", "Gửi Sao Mai bản nháp", "tên khách (Sao Mai)")])
def test_ngoai_du_an_cham_luat_moi_du_an_thi_tu_choi(nc, pv, cau, ly):
    with pytest.raises(TuChoiGhi) as e:
        ghi(nc, pv, cau)
    assert ly in e.value.ly_do
    assert su_kien(nc, "_tram", "nho.tu_choi") == [{"ly_do": ly, "nguon": "dai_ca_ghi", "pham_vi": pv}]
    assert nc.kho.dem() == 0 and nc.embedder.goi == [] and nc.nhat_ky.lay("ghi:" + MA) is None


def test_du_an_cach_lam_cham_luat_ep_nghiep_vu(nc):
    kq = ghi(nc, "/du-an/hr-codex/cach-lam", "Module Pay cần chạy migrate trước")
    assert kq.pham_vi == "/du-an/hr-codex/nghiep-vu"
    assert su_kien(nc, "hr-codex", "nho.ghi")[0]["pham_vi"] == "/du-an/hr-codex/nghiep-vu"
    assert ghi(nc, "/du-an/ke-toan/cach-lam", "Module Pay ở dự án khác", ma="ma-ghi-0002").pham_vi == \
        "/du-an/ke-toan/cach-lam"                              # chỉ luật của chính dự án đó


def test_cau_hinh_du_an_hong_thi_tu_choi(nc):
    def hong(ten):
        raise ValueError("yaml hỏng")
    nc.luat_cua = hong
    with pytest.raises(TuChoiGhi) as e:
        ghi(nc)
    assert "không đọc được cấu hình dự án" in e.value.ly_do[0] and nc.kho.dem() == 0


@pytest.mark.parametrize("pv", ["/du-an/hr-codex", "/", "/vai", "/du-an/hr-codex/khac", "/chung/x"])
def test_pham_vi_sai_dang(nc, pv):
    with pytest.raises(LoiVungCap):
        ghi(nc, pv)
    assert nc.kho.dem() == 0 and su_kien(nc, "_tram", "nho.tu_choi") == []


def test_dai_ca_gop_ban_cu_cung_pham_vi_embed_lai_va_hop_nguon(nc):
    v = nc.embedder.embed([CAU])[0]
    nc.kho.them(ky_uc("m-cu", "/chung", vector=v, quan_trong=0.9, nguon=({"loai": "dai_ca_ghi", "ma_thao_tac": "x"},)))
    nc.kho.them(ky_uc("m-vai", "/vai/coder", vector=v))                     # khác phạm vi: không phải ứng viên
    nc.embedder.goi.clear()
    nc.client = ClientGia(tra_loi({"quyet_dinh": [{"id": "m-cu", "hanh_dong": "gop"}],
                                   "noi_dung_gop": "Gộp: chạy test và lint.", "co_ten_rieng": False}))
    kq = ghi(nc)
    k = nc.kho.lay([kq.id])[kq.id]
    assert kq.xoa == ("m-cu",) and k.noi_dung == "Gộp: chạy test và lint." and k.quan_trong == pytest.approx(0.9)
    assert nc.embedder.goi == [[CAU], ["Gộp: chạy test và lint."]] and k.vector[1] == pytest.approx(1.0)
    assert k.nguon == ({"loai": "dai_ca_ghi", "ma_thao_tac": MA}, {"loai": "dai_ca_ghi", "ma_thao_tac": "x"})
    assert nc.kho.lay(["m-cu"])["m-cu"].da_xoa and not nc.kho.lay(["m-vai"])["m-vai"].da_xoa
    assert su_kien(nc, "_tram", "nho.gop") == [{"cu": ["m-cu"], "moi": kq.id}]


def test_embedder_hoac_claude_loi_thi_khong_ghi_gi(nc):
    nc.embedder.loi_tu_lan = 1
    with pytest.raises(LoiEmbedder):
        ghi(nc)
    nc.embedder.loi_tu_lan = None
    nc.kho.them(ky_uc("m-cu", "/chung", vector=nc.embedder.embed([CAU])[0]))
    nc.client = ClientGia(anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")))
    with pytest.raises(anthropic.APIError):
        ghi(nc)
    assert nc.kho.dem() == 1 and not nc.kho.lay(["m-cu"])["m-cu"].da_xoa and nc.nhat_ky.lay("ghi:" + MA) is None


def test_gui_lai_sau_xoa_cung_khong_tao_lai(nc):
    kq = ghi(nc)
    nc.kho.xoa_mem([kq.id])
    nc.kho.xoa_cung([kq.id])
    nc.nhat_ky.xoa_noi_dung_ke_hoach(kq.id)
    nc.embedder.goi.clear()
    assert ghi(nc) == KetQuaGhiTay(kq.id, kq.pham_vi, kq.xoa, True)
    assert nc.kho.dem() == 0 and nc.embedder.goi == []
