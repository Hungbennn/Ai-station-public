"""Lát 1b-4 Task 4 (D23): nguồn có dấu hiệu bí mật bị bỏ CẢ nguồn trước LLM, embed, lưu. Sentinel (khoá GIẢ ghép lúc
chạy) không được xuất hiện ở client LLM giả, embedder giả, kho ký ức, nhật ký, sự kiện của memory, log, stdout."""
import argparse
import base64
import hashlib
import json
import threading
from datetime import datetime, timezone

import pytest

from bead_gia import KHOI_BAN_GIAO
from nho_gia import ClientGia, EmbedderGia, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.dich_vu import DichVuNho
from tram.nho.kho import KhoKyUc
from tram.nho.lenh import _thu
from tram.nho.loi_nap import la_nguon
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import BoDemDung
from tram.nho.tien_trinh import vong_nap
from tram.nho.vong import NguCanhNho, mot_luot
from tram.su_kien.kho import KhoSuKien

LUC, GID = "2026-10-14T02:00:00Z", "g-20261014-0007"
KHOA = "".join(["gh", "p_", "Sentinel", "0" * 28])                                       # khoa_da_biet
BAM = base64.urlsafe_b64encode(hashlib.sha256(b"sentinel-entropy").digest()).decode().rstrip("=")   # entropy_cao
MAT_KHAU = "".join(["pass", "word=", "Sentinel", "Mk"])                                   # gan_gia_tri
SENTINEL = ("Sentinel", BAM)
LENH = [{"lenh": "php artisan test", "ket_qua": "pass", "digest_log": "d1"}]


@pytest.fixture
def nc(tmp_path, monkeypatch):
    monkeypatch.setattr("tram.su_kien.kho.bay_gio", lambda: LUC)
    e, thu = EmbedderGia(), tmp_path / "nho"
    return NguCanhNho(kho=KhoKyUc(thu / "lancedb", so_chieu=e.so_chieu), embedder=e, client=ClientGia(),
                      kho_sk=KhoSuKien(tmp_path / "sk.db"), nhat_ky=NhatKy(thu / "nk.db"),
                      vai_tach=nap_vai("nho-tach"), vai_gop=nap_vai("nho-gop"), luat_cua=lambda ten: LuatDuAn(),
                      luc=lambda: "2026-10-15T02:00:00Z")


def ghi_nguon(k: KhoSuKien, *, sach_escalation=False) -> None:
    """id 1–4: bàn giao (QC đạt) lộ KHOA; 5: escalation lộ BAM (hoặc sạch); 6: spec trả về lộ MAT_KHAU."""
    bg = {**KHOI_BAN_GIAO, "luot": 2, "quyet_dinh": ["Dùng `php artisan test --filter`"],
          "vuong_mac": [f"Cấu hình CI cần {KHOA}"]}
    k.ghi("hr-codex", "giao.nhan", {"giao_id": GID, "luot": 2, "bead_id": "hr-1", "buoc": "code", "vai": "coder"},
          bead_id="hr-1", tac_nhan="tram/api")
    k.ghi("hr-codex", "bao.xong", {"giao_id": GID, "luot": 2, "ban_giao": bg, "commit": "abc1234",
                                   "request_id": "r-12345678", "noi_dung": ""},
          bead_id="hr-1", tac_nhan="tho/B/claude-1")
    k.ghi("hr-codex", "kiem.lai", {"giao_id": GID, "bead_id": "hr-1", "luot": 2, "commit": "abc1234",
                                   "digest_tieu_chi": "d", "dat": True, "ket_qua": LENH, "digest_log": [],
                                   "cham_cam": []}, bead_id="hr-1", tac_nhan="tram/giao-viec")
    k.ghi("hr-codex", "qc.ket_qua", {"giao_id": "g-20261014-0009", "bead_id": "hr-1", "commit_code": "abc1234",
                                     "commit_qc": "def5678", "ket_luan": "dat", "phat_hien": [], "ly_do": None},
          bead_id="hr-1", tac_nhan="tram/giao-viec")
    tra = "Hoa hồng tính trên giá sau giảm giá" if sach_escalation else f"Khoá môi trường thử: {BAM}"
    k.ghi("hr-codex", "escalation.dong", {"escalation_id": "hr-d9", "bead_goc": "hr-12", "giao_id": GID,
                                          "ly_do": "agent-can-hoi", "ma_thao_tac": "esc-1", "tra_loi": tra},
          bead_id="hr-12", tac_nhan="tram/giao-viec")
    k.ghi("hr-codex", "spec.tra_ve", {"gop_y": f"Thêm {MAT_KHAU} vào cấu hình", "ma_thao_tac": "m-1"},
          bead_id="hr-f1", tac_nhan="dai-ca/dashboard")


def khong_lo(nc: NguCanhNho, thu: object, *van_ban: str) -> None:
    nho = [(s.loai, s.du_lieu) for s in nc.kho_sk.sau_id(0, 999) if s.tac_nhan == "tram/nho"]
    chu = [json.dumps(x, ensure_ascii=False, default=str) for x in (nc.client.goi, nc.embedder.goi, nho)]
    tep = b"".join(p.read_bytes() for p in thu.rglob("*") if p.is_file())        # LanceDB + nhật ký (ngoài sk.db)
    for s in SENTINEL:
        assert all(s not in x for x in [*chu, *van_ban]) and s.encode() not in tep


def test_bo_ca_nguon_khong_lo_o_dau_va_khong_thu_lai(nc, tmp_path, capsys):
    ghi_nguon(nc.kho_sk)
    assert not any(la_nguon(s, nc.kho_sk) for s in nc.kho_sk.sau_id(0, 99))
    dung = threading.Event()

    def dong_ho():
        dung.set()
        return datetime(2026, 10, 13, 5, 0, tzinfo=timezone.utc)                    # 12:00 VN: không bảo trì

    dv = DichVuNho(nc.kho, nc.embedder, lambda: nc.kho_sk, BoDemDung(), "tk")
    vong_nap(nc, dv, dung=dung, thu_muc=tmp_path / "nho", dich=tmp_path / "sl", chu_ky=0, dong_ho=dong_ho)
    log = capsys.readouterr()
    assert "bo=3" in log.err and nc.client.goi == [] and nc.embedder.goi == [] and nc.kho.dem() == 0
    assert nc.nhat_ky.moc() == 6 and nc.kho_sk.gan_day("hr-codex", "nho.loi_tach", 9) == []
    assert [(s.bead_id, s.du_lieu) for s in nc.kho_sk.sau_id(6, 99) if s.loai == "nho.bo_bi_mat"] == [
        ("hr-1", {"su_kien_id": 4, "loai_nguon": "ban_giao", "nhom": {"khoa_da_biet": 1}}),
        ("hr-12", {"su_kien_id": 5, "loai_nguon": "da_chot", "nhom": {"entropy_cao": 1}}),
        ("hr-f1", {"su_kien_id": 6, "loai_nguon": "tra_ve", "nhom": {"gan_gia_tri": 1}})]
    bc = mot_luot(nc)                                                                # không thử lại
    assert (bc.su_kien, bc.bo, bc.loi) == (0, 0, None) and nc.client.goi == []
    assert len(nc.kho_sk.gan_day("hr-codex", "nho.bo_bi_mat", 9)) == 3
    khong_lo(nc, tmp_path / "nho", log.out, log.err, str(bc))


def test_nguon_sach_cung_luot_van_nap(nc, tmp_path):
    ghi_nguon(nc.kho_sk, sach_escalation=True)
    nc.client = ClientGia(tra_loi({"ky_uc": [{"noi_dung": "Hoa hồng sale tính trên giá sau giảm giá.",
                                              "nhanh": "nghiep-vu", "nhan": [], "quan_trong": 0.9,
                                              "co_ten_rieng": False}]}))
    bc = mot_luot(nc)
    assert (bc.su_kien, bc.ky_uc_moi, bc.bo) == (1, 1, 2) and len(nc.client.goi) == 1
    khong_lo(nc, tmp_path / "nho")


def test_tram_nho_thu_bo_nguon_bi_mat_khong_goi_llm_khong_in(nc, monkeypatch, capsys):
    ghi_nguon(nc.kho_sk)
    c, truoc = ClientGia(), nc.kho_sk.id_moi_nhat()
    monkeypatch.setattr("tram.su_kien.kho.mo_kho", lambda: nc.kho_sk)
    monkeypatch.setattr("tram.llm.claude.tao_client", lambda: c)
    assert _thu(argparse.Namespace(du_an=None, tu_id=0, gioi_han=20)) == 0
    log = capsys.readouterr()
    assert log.out.count("BỎ VÌ CÓ DẤU HIỆU BÍ MẬT") == 3 and "Tổng: 0 ký ức dự kiến" in log.out
    assert ("- sự kiện 4 (qc.ket_qua, hr-1): BỎ VÌ CÓ DẤU HIỆU BÍ MẬT — nguồn ban_giao có dấu hiệu bí mật: "
            "khoa_da_biet ×1") in log.out
    assert c.goi == [] and nc.kho_sk.id_moi_nhat() == truoc                       # chế độ thử không ghi gì
    assert all(s not in log.out + log.err for s in SENTINEL)
