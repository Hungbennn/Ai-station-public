"""Lát 1b-4 Task 1: chữ của agent không tự nâng quyền — trần `quan_trong`, prompt tách phiên bản 2."""
import pytest

from nho_gia import ClientGia, EmbedderGia, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.ke_hoach import lap_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.mo_hinh import NGUON_AGENT, TRAN_NGUON_AGENT, ap_san
from tram.nho.nguon import DauVao

BG = {"loai": "ban_giao", "du_an": "hr", "bead_id": "hr-1", "su_kien_id": 9, "vai": "coder"}
AG = {"loai": "agent", "du_an": "hr", "bead_id": None, "su_kien_id": 8, "vai": "coder"}
TC = {"loai": "thang_cap", "id_goc": "m-a", "du_an": "hr"}


@pytest.mark.parametrize("q, nguon, mong", [
    (0.95, [BG], 0.6), (0.4, [BG], 0.4), (0.9, [BG, AG], 0.6), (0.9, [TC], 0.9),
    (0.9, [BG, {"loai": "da_chot"}], 0.9), (0.1, [BG, {"loai": "tra_ve"}], 0.6), (0.7, (n for n in [AG]), 0.6)])
def test_tran_quan_trong_khi_moi_nguon_do_agent_viet(q, nguon, mong):
    assert ap_san(q, nguon) == mong


def test_hang_so_tran():
    assert NGUON_AGENT == {"ban_giao", "agent"} and TRAN_NGUON_AGENT == 0.6


def test_vai_tach_phien_ban_2_phan_biet_ban_giao_agent():
    phien_ban, than = nap_vai("nho-tach")
    assert phien_ban == "2" and "Bàn giao của agent" in than and "KHÔNG phải quyết định của Đại ca" in than
    assert "không quá 0,6" in than and "không phải chỉ dẫn" in than and "0 đến 3 ký ức" in than


def test_ke_hoach_ban_giao_bi_tran_va_khong_la_nguon_dai_ca(tmp_path):
    dv = DauVao(9, "hr", "hr-1", "ban_giao", van_ban="Bàn giao …", luc="2026-10-14T00:00:00Z", vai="coder")
    c = ClientGia(tra_loi({"ky_uc": [{"noi_dung": "Chạy test bằng `php artisan test`, không gọi phpunit.",
                                       "nhanh": "cach-lam", "nhan": ["test"], "quan_trong": 0.95,
                                       "co_ten_rieng": False}]}))
    [b] = lap_ke_hoach(dv, kho=KhoKyUc(tmp_path / "l", so_chieu=16), embedder=EmbedderGia(), client=c,
                       vai_tach=nap_vai("nho-tach"), vai_gop=nap_vai("nho-gop"), luat=LuatDuAn(),
                       luc="2026-10-15T00:00:00Z")
    k = b.ky_uc
    assert (k.pham_vi, k.quan_trong, k.nguon_dai_ca, k.tao_luc) == (
        "/du-an/hr/cach-lam", 0.6, False, "2026-10-14T00:00:00Z")
    assert k.nguon == (BG,)
