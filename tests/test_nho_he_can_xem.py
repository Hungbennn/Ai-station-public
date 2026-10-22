"""Memory 1b-1 (G9): lỗi nạp ký ức hiện ở 'Hệ cần xem' tới khi phục hồi, và báo Telegram như trạm lỗi."""
import pytest

from bead_gia import bead
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.su_kien.kho import KhoSuKien
from tram.suy.phe_duyet import gom_phe_duyet


@pytest.fixture
def k(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def he(k, beads=()):
    return [(m["bead_id"], m["tieu_de"], m["chi_tiet"]["su_kien"], m["chi_tiet"]["loi"])
            for m in gom_phe_duyet(["hr"], {"hr": list(beads)}, k) if m["loai"] == "he"]


def test_loi_nho_hien_he_can_xem_khi_chua_phuc_hoi(k):
    k.ghi("hr", "nho.loi_llm", {"su_kien_id": 7, "loi": "Connection error.\x1b[31m"}, bead_id="hr-7",
          tac_nhan="tram/nho")
    k.ghi("hr", "nho.loi_embedder", {"su_kien_id": 9, "loi": "Ollama /api/tags lỗi"}, bead_id="hr-9",
          tac_nhan="tram/nho")
    assert he(k, [bead("hr-7", title="Xuất PDF")]) == [            # không gắn bead_id: không có nút "Thử lại" 1a
        (None, "", "nho.loi_llm", "Nạp ký ức đứng ở bead hr-7 (sự kiện 7): Connection error.[31m"),
        (None, "", "nho.loi_embedder", "Nạp ký ức đứng ở bead hr-9 (sự kiện 9): Ollama /api/tags lỗi")]


def test_phuc_hoi_moi_hon_thi_an_theo_tung_loai(k):
    k.ghi("hr", "nho.loi_llm", {"su_kien_id": 7, "loi": "x"}, bead_id="hr-7")
    k.ghi("hr", "nho.loi_embedder", {"su_kien_id": 7, "loi": "y"}, bead_id="hr-7")
    k.ghi("hr", "nho.phuc_hoi", {"loai": "llm"}, bead_id="hr-7")
    assert [m[2] for m in he(k)] == ["nho.loi_embedder"]
    k.ghi("hr", "nho.phuc_hoi", {"loai": "embedder"}, bead_id="hr-7")
    assert he(k) == []
    k.ghi("hr", "nho.loi_llm", {"su_kien_id": 8, "loi": "z"}, bead_id="hr-8")       # đợt lỗi mới
    assert [m[2] for m in he(k)] == ["nho.loi_llm"]


def test_loi_nho_bao_telegram_nhu_tram_loi(k):
    k.ghi("hr", "nho.loi_llm", {"su_kien_id": 7, "loi": "x"}, bead_id="hr-7")
    k.ghi("hr", "nho.loi_embedder", {"su_kien_id": 7, "loi": "y"}, bead_id="hr-7")
    k.ghi("hr", "nho.phuc_hoi", {"loai": "llm"}, bead_id="hr-7")
    assert [t for s in k.sau_id(0, 9) for t in tin_tu_su_kien(s, k)] == [
        Tin("tram_loi", "hr", "hr-7"), Tin("tram_loi", "hr", "hr-7")]


def test_phuc_hoi_khong_bi_che_boi_nhieu_phuc_hoi_loai_khac(k):
    """bs-hpc.12: trước chỉ xét 20 nho.phuc_hoi gần nhất — 25 bản 'embedder' che mất bản 'llm'."""
    k.ghi("hr", "nho.loi_llm", {"su_kien_id": 7, "loi": "x"}, bead_id="hr-7")
    k.ghi("hr", "nho.phuc_hoi", {"loai": "llm"}, bead_id="hr-7")
    for _ in range(25):
        k.ghi("hr", "nho.phuc_hoi", {"loai": "embedder"}, bead_id="hr-7")
    assert he(k) == []
